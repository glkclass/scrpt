import sys
import copy

sys.path.extend(['/home/anton/design/scrpt', '/home/anton/design/ESCORT65/digital/design/tb'])

from functools import reduce

from log_util import get_logger

log = get_logger(__name__)
log.setLevel("DEBUG")


def generate_vector_crc(polynomial, n_data_bits, lsb=True):
    """
    Generate vector CRC calculation scheme based on 'polynomial' of size N <= 64.
    Using generated scheme CRC will be calculated for input data[n_data_bits] vector at once.
    We use scheme which requires 'n shifts for n bits' i.e. doesn't require additional shifts at the end.

    Args:
        'polynomial'    -   (N+1)-bit polynomial representation (highest and lowest degrees are present)
        'n_data_bits'   -   data vector width
        'lsb' == True   -   Data is applied LSB else MSB.
    Return:
        List[n_data_bits] of dict {'c': [..], d:[..]} with appropriate crc or data indices to be xor-ed.

    For example:
    Polynomial = 0x149F <=> x^12 + x^10 + x^7 + x^4 + x^3 + x^2 + x^1 + 1
    n_data_bits = 8
    """

    def update_crc_scheme(crc, idx_src, crc_new, idx_dst):
        for foo in ['c', 'd']:
            for bar in crc[idx_src][foo]:
                if bar in crc_new[idx_dst][foo]:
                    crc_new[idx_dst][foo].remove(bar)  # imitate xor of two same values
                else:
                    crc_new[idx_dst][foo].append(bar)
            crc_new[idx_dst][foo].sort()  # just for better visualization

    # convert polynomial to list of degrees
    poly = []
    for i in range(64 + 1):
        poly.append(polynomial & 1)
        polynomial = polynomial >> 1
        if polynomial == 0:
            break
    poly = poly[:-1]
    n_crc = len(poly)
    assert n_crc > 0, "Too short 'Polynomial' length"
    # log.debug(f'poly[0:{n_crc-1}] = {poly}')

    crc_new = [{'c': [], 'd':[]} for i in range(n_crc)]
    crc = [{'c': [i], 'd':[]} for i in range(n_crc)]
    data_bits_range = range(n_data_bits) if lsb else reversed(range(n_data_bits))
    for i in data_bits_range:
        # crc bit #0
        crc_new[0]['d'].append(i)
        update_crc_scheme(crc, -1, crc_new, 0)

        # rest of crc bits
        for j in range(1, n_crc):
            update_crc_scheme(crc, j-1, crc_new, j)  # previous crc bit
            if poly[j] == 1:
                # feedback
                crc_new[j]['d'].append(i)
                update_crc_scheme(crc, -1, crc_new, j)  # last(high) crc bit

        crc = copy.deepcopy(crc_new)
        crc_new = [{'c': [], 'd':[]} for i in range(n_crc)]
    # for j in range(n_crc):  log.debug(f'crc scheme [{j}] = {crc[j]}')
    return crc



def calc_vector_crc(data, data_width, crc_scheme, crc_init=0):
    """
    Calculate vector CRC based on 'crc_scheme' generated in advance.
    The order of Data processing (LSB or MSB ) is defined when 'crc_scheme' is generated

    Args:
        'data'          - array of data_width-bit values.
        'crc_scheme'    - Vector crc calculation scheme. May be generated by generate_vector_crc()
        'crc_init'      - N-bit init value. N = length(crc_scheme), is a size of CRC
    Return:
        N-bit CRC value
    """

    def calc_crc_bit(foo):
        qux = 0
        for bar in (('d', d), ('c', crc)):
            for idx in foo[bar[0]]:
                assert idx < len(bar[1])
                qux = qux ^ bar[1][idx]
        return qux

    assert isinstance(crc_scheme, (list, tuple)), "'crc_scheme' should be a list/tuple"
    assert isinstance(data, (list, tuple)), "'data' should be a list/tuple"
    assert isinstance(crc_init, int), "'crc_init' should be an int"

    crc_size = len(crc_scheme)
    crc = [(crc_init >> i) & 1 for i in range(crc_size)]

    for item in data:
        d = [(item >> i) & 1 for i in range(data_width)]
        crc_new = list(map(calc_crc_bit, crc_scheme))
        crc = crc_new
        # log.debug(list(crc_new))

    crc = [crc[i] << i for i in range(crc_size)]
    crc_value = reduce(lambda a, b: a + b, crc)
    # log.debug(f"0x{crc_value:04x} <=> 0b{crc_value:016b}")
    return crc_value


def calc_crc(data, polynomial, crc_init):
    """
    Calculate N-bit CRC based on 'polynomial'. N <= 64.
    We use scheme which requires 'n shifts for n bits' i.e. doesn't require additional shifts at the end.
    For example: Polynomial = 0x149F <=> x^12 + x^10 + x^7 + x^4 + x^3 + x^2 + x^1 + 1
    'data' - array of 1-bit values. LSB-first (the first serial bit applied to LSFR is data[0]).
    'polynomial' - (N+1)-bit polynomial representation (highest and lowest degrees are present)
    'crc_init' - N-bit init value
    """
    assert isinstance(data, str), "'data' should be a string of bits"
    assert isinstance(crc_init, int), "'crc_init' should be an int"
    data = [int(item) for item in list(data)]
    # log.debug(f'data = {data}')
    # log.debug(f'polynomial = 0x{polynomial:0x}')

    # convert polynomial to list of degrees
    poly = []
    for i in range(64 + 1):
        poly.append(polynomial & 1)
        polynomial = polynomial >> 1
        if polynomial == 0:
            break
    poly = poly[:-1]
    n_crc = len(poly)
    assert n_crc > 0, "Too short 'Polynomial' length"
    # log.debug(f'poly[0:{n_crc}] = {poly}')

    # init crc register
    crc = []
    for i in range(n_crc):
        crc.append(crc_init & 1)
        crc_init = crc_init >> 1
    # log.debug(f'crc [0:{n_crc}] = {crc}')
    # log.debug(f'crc [0:{n_crc}] = 0x{reduce(lambda a, b: a + b, [crc[i] << i for i in range(n_crc)]):03x}')

    for data_bit in data:
        foo = data_bit ^ crc[-1]
        crc[1:] = [foo ^ crc[i - 1] if poly[i] == 1 else crc[i - 1] for i in range(1, n_crc)]
        crc[0] = foo
        # log.debug(f'crc [0:{n_crc}] = 0x{reduce(lambda a, b: a + b, [crc[i] << i for i in range(n_crc)]):03x}')

    crc = [crc[i] << i for i in range(n_crc)]
    crc_val = reduce(lambda a, b: a + b, crc)
    # log.debug(f'crc value = 0x{crc_val:03x}')
    return crc_val


def crc_12_0x149F(data, crc_init):
    """
    Calculate 12-bit CRC: x^12 + x^10 + x^7 + x^4 + x^3 + x^2 + x^1 + 1
    'data' - array of 12-bit values. MSB-first (the first serial bit applied to LSFR is data[i][11]).
    'crc_init' - 12-bit init int value
    """
    assert isinstance(data, (list, tuple)), "'data' should be a list/tuple"
    assert isinstance(crc_init, int), "'crc_init' should be an int"

    def rdc_xor(a, b):
        return a ^ b

    ci = [(crc_init >> i) & 1 for i in range(12)]
    # log.debug(f"{ci}")

    for item in data:
        # log.debug(f'{item:0x}')
        d = [(item >> i) & 1 for i in range(12)]
        # log.debug(f"{d}")
        ci1 = []
        ci1.append(reduce(rdc_xor, (
            d[11], d[10], d[6], d[5], d[4], d[2], d[0],
            ci[11], ci[10], ci[6], ci[5], ci[4], ci[2], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[7], d[4], d[3], d[2], d[1], d[0],
            ci[10], ci[7], ci[4], ci[3], ci[2], ci[1], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[8], d[6], d[3], d[1], d[0],
            ci[10], ci[8], ci[6], ci[3], ci[1], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[9], d[7], d[6], d[5], d[1], d[0],
            ci[10], ci[9], ci[7], ci[6], ci[5], ci[1], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[8], d[7], d[5], d[4], d[1], d[0],
            ci[8], ci[7], ci[5], ci[4], ci[1], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[9], d[8], d[6], d[5], d[2], d[1],
            ci[9], ci[8], ci[6], ci[5], ci[2], ci[1])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[9], d[7], d[6], d[3], d[2],
            ci[10], ci[9], ci[7], ci[6], ci[3], ci[2])))
        ci1.append(reduce(rdc_xor, (
            d[8], d[7], d[6], d[5], d[3], d[2], d[0],
            ci[8], ci[7], ci[6], ci[5], ci[3], ci[2], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[9], d[8], d[7], d[6], d[4], d[3], d[1],
            ci[9], ci[8], ci[7], ci[6], ci[4], ci[3], ci[1])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[9], d[8], d[7], d[5], d[4], d[2],
            ci[10], ci[9], ci[8], ci[7], ci[5], ci[4], ci[2])))
        ci1.append(reduce(rdc_xor, (
            d[9], d[8], d[4], d[3], d[2], d[0],
            ci[9], ci[8], ci[4], ci[3], ci[2], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[9], d[5], d[4], d[3], d[1],
            ci[10], ci[9], ci[5], ci[4], ci[3], ci[1])))
        ci = ci1.copy()
        # log.debug(f'crc [0:{12}] = 0x{reduce(lambda a, b: a + b, [ci[i] << i for i in range(12)]):03x}')

    ci = [ci[i] << i for i in range(12)]
    crc_value = reduce(lambda a, b: a + b, ci)
    # log.debug(f"0x{crc_value:03x} <=> 0b{crc_value:012b}")
    return crc_value

def crc_12_0x120D(data, crc_init):
    """
    Calculate 12-bit CRC: x^12 + x^9 + x^3 + x^2 + 1
    'data' - array of 12 bit value. MSB-first (the first serial bit applied to LSFR is data[i][11]).
    'crc_init' - 12-bit init int value
    """
    assert isinstance(data, (list, tuple)), "'data' should be a list/tuple"
    assert isinstance(crc_init, int), "'crc_init' should be an int"

    def rdc_xor(a, b):
        return a ^ b

    ci = [(crc_init >> i) & 1 for i in range(12)]
    # log.debug(f"{ci}")

    for item in data:
        # log.debug(f'{item:0x}')
        d = [(item >> i) & 1 for i in range(12)]
        # log.debug(f"{d}")
        ci1 = []
        ci1.append(reduce(rdc_xor, (
            d[10], d[6], d[3], d[0], ci[10], ci[6], ci[3], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[11], d[7], d[4], d[1], ci[11], ci[7], ci[4], ci[1])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[8], d[6], d[5], d[3], d[2], d[0],
            ci[10], ci[8], ci[6], ci[5], ci[3], ci[2], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[11], d[10], d[9], d[7], d[4], d[1], d[0],
            ci[11], ci[10], ci[9], ci[7], ci[4], ci[1], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[11], d[10], d[8], d[5], d[2], d[1],
            ci[11], ci[10], ci[8], ci[5], ci[2], ci[1])))
        ci1.append(reduce(rdc_xor, (
            d[11], d[9], d[6], d[3], d[2],
            ci[11], ci[9], ci[6], ci[3], ci[2])))
        ci1.append(reduce(rdc_xor, (
            d[10], d[7], d[4], d[3], ci[10], ci[7], ci[4], ci[3])))
        ci1.append(reduce(rdc_xor, (
            d[11], d[8], d[5], d[4], ci[11], ci[8], ci[5], ci[4])))
        ci1.append(reduce(rdc_xor, (
            d[9], d[6], d[5], ci[9], ci[6], ci[5])))
        ci1.append(reduce(rdc_xor, (
            d[7], d[3], d[0], ci[7], ci[3], ci[0])))
        ci1.append(reduce(rdc_xor, (
            d[8], d[4], d[1], ci[8], ci[4], ci[1])))
        ci1.append(reduce(rdc_xor, (
            d[9], d[5], d[2], ci[9], ci[5], ci[2])))
        ci = ci1.copy()
        # log.debug(f"{ci}")

    ci = [ci[i] << i for i in range(12)]
    ci = reduce(lambda a, b: a + b, ci)
    # log.debug(f"0x{ci:0x} <=> 0b{ci:012b}")
    return ci

def conv_wordlist_2_bitstring(inp, word_width=8, dir=0):
    """Convert list of bytes to bit string and vice versa
    """
    assert word_width > 0, "'word_width' should be a positive value"
    if dir == 0:
        assert isinstance(inp, (list, tuple)), "For 'dir' = 0, 'inp' should be a list/tuple"
        # For better visualization the MSB of Word #0 will be located at position #0 of 'bitstr' and so on !!!
        bitstr = ''
        for word in inp:
            assert word < pow(2, word_width), "Too large word magnitude detected!"
            # log.debug(f'{byte:0x}')
            for i in range(word_width):
                foo = int((word >> (word_width - 1 - i)) & 1)
                # log.debug(foo)
                bitstr += str(foo)
            # log.debug(bitstr)
        return bitstr
    else:
        assert isinstance(inp, str), "For 'dir' != 0, 'inp' should be a string"
        wordlist = []
        bitarr = [int(item) for item in list(inp)]
        n_rem = len(bitarr) % word_width
        bitarr = bitarr + [0] * (word_width - n_rem) if n_rem > 0 else bitarr
        n_bits = len(bitarr)
        # log.debug(f'{inp}, size = {len(inp)}')
        # log.debug(f'{bitarr}, size =  {n_bits}')
        idx = 0
        while idx < n_bits:
            foo = [bitarr[i] << (word_width - 1 - (i - idx)) for i in range(idx, idx + word_width)]
            # log.debug(bitarr[idx: idx + word_width])
            # log.debug(foo)
            wordlist.append(reduce(lambda a, b: a + b, foo))
            idx += word_width
        return wordlist


if __name__ == "__main__":
    poly_0x149F = 0x149F
    poly_0x120D = 0x120D
    poly = poly_0x149F

    # number of 8-bit values should be divided by 3. To be converted to 12-bit values.
    data_arr = [0x7F, 0xD1, 0x00, 0x09, 0xB5, 0x88]
    # data_arr = [0x11] * 3

    data_bitstring = conv_wordlist_2_bitstring(data_arr, 8, 0)
    # log.debug(data_bitstring)

    foo = calc_crc(data_bitstring, poly, 0xFFF)
    log.debug(f'0x{foo:03x}')

    foo = conv_wordlist_2_bitstring(data_bitstring, 12, 1)
    # log.debug([f'0x{item:03x}' for item in foo])
    foo = crc_12_0x149F(foo, 0xFFF)
    log.debug(f'0x{foo:03x}')

    crc_scheme = generate_vector_crc(poly, 8, lsb=False)
    foo = calc_vector_crc(data_arr, 8, crc_scheme, 0xFFF)
    log.debug(f'0x{foo:03x}')
