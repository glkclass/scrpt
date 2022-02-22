import sys
sys.path.extend(['/home/anton/.config/sublime-text/Packages/Todo/scrpt', '/home/anton/design/ESCORT65/digital/design/tb'])

from functools import reduce

from log_util import get_logger

log = get_logger(__name__)
log.setLevel("DEBUG")


def calc_crc(data, polynomial, crc_init):
    """
    Calculate N-bit CRC based on 'polynomial'. N <= 64.
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


def rdc_xor(a, b):
    return a ^ b


def conv_wordlist_2_bitstring(inp, word_width=8, dir=0):
    """Convert list of bytes to bit string and vice versa
    """
    assert word_width > 0, "'word_width' should be a positive value"
    if dir == 0:
        assert isinstance(inp, (list, tuple)), "For 'dir' = 0, 'inp' should be a list/tuple"
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
    # number of 8-bit values should be divided by 3. To be converted to 12-bit values.
    # data_arr = [0x45, 0x54, 0x89, 0x75, 0x34, 0x80, 0x26, 0x35, 0x73]
    data_arr = [0x00] * 27

    data_bitstring = conv_wordlist_2_bitstring(data_arr, 8, 0)

    foo = calc_crc(data_bitstring, poly_0x149F, 0xFFF)
    log.debug(f'0x{foo:0x}')

    foo = conv_wordlist_2_bitstring(data_bitstring, 12, 1)
    # log.debug([f'0x{item:0x}' for item in foo])
    foo = crc_12_0x149F(foo, 0xFFF)
    log.debug(f'0x{foo:0x}')
