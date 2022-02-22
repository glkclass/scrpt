# import os
# import os.path as osp
import re
import time
import sys
sys.path.append('/home/anton/.config/sublime-text/Packages/Todo/scrpt')

import util
import log_util
from file import load

log = log_util.get_logger(__name__, 'check_mbist.log')
log.setLevel("INFO")

cfg = load('check_mbist.json', 'json')

seed = round(time.time())
log.info(f"Time seed: {seed}")
seed = seed % 10000000
fault_seeds = []
print_log = 0
run_cmd_tmpl = cfg['run_cmd']
n_tests = cfg['n_tests'] if len(cfg['seed']) == 0 else len(cfg['seed'])
log.info(f'Num of tests to be executed: {n_tests}')

for idx in range(n_tests):
    seed = cfg['seed'][idx] if len(cfg['seed']) > 0 else seed + 1
    tme = time.time()

    run_cmd = run_cmd_tmpl % (cfg['sim_dir'], seed, ' '.join(cfg['src_list']))
    foo = util.subprocess_call(run_cmd)

    stdout = foo.stdout.split('\n')
    for line in stdout:
        if re.search(cfg['test_finished_marker'], line):
            log.info(f"""Test: {idx}  Faults detected: {len(fault_seeds)}  Seed: {seed}  Dur: {round(time.time() - tme):2}s {line}""")
            if re.search(cfg['test_mismatch_marker'], line):
                log.info(foo.stdout)
                fault_seeds.append(seed)
            break
    else:
        # Can't find test stop marker: something went wrong (elaboration fail, test hangs, ...)
        log.info("Can't find test stop marker: something went wrong")
        log.info(foo.stdout)
        fault_seeds.append(seed)
        break

    if print_log == 1:
        stdout = '\n'.join(foo.stdout.split('\n')[0:300])
        log.info(stdout)

    if len(fault_seeds) > cfg['num_fault_max']:
        break

log.info(f'Finished. Tests run: {n_tests}. Faults detected: {len(fault_seeds)}')
if len(fault_seeds) > 0:
    log.error(f'Fault seeds: {fault_seeds}')
