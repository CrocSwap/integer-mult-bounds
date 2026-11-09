#!/usr/bin/env python3
"""Runs the short checks in one command (standard library): second_engine.py, division_pass.py, check_caller_blocks.py, check_a6.py, ordinary.py.  python3 -I -B small_checks.py
Each is run on the package data and must end with its PASS line (ordinary.py: all three raw figures below 10^9).  Ends PASS_SMALL_CHECKS."""
import os, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); data = lambda n: os.path.join(HERE, 'data', n)
def run(script, *args):
    r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, script)] + list(args), capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-300:], flush=True); return r
for script, args, tail in (('second_engine.py', [data('word.json.gz')], 'PASS_SECOND_ENGINE'), ('division_pass.py', [], 'PASS_DIVISION_PASS'),
                           ('check_caller_blocks.py', [data('caller_old.json'), data('caller.json'), data('caller_6912_before.json'), data('caller_6912_after.json'), data('prior_word_6934.json.gz') + ':1125', data('word.json.gz') + ':1125'], 'PASS_CALLER_BLOCKS_JOINT'),
                           ('check_a6.py', [data('word.json.gz'), os.path.join(HERE, 'retained', 'native'), '2,3,5'], 'PASS_A6_CHECK')):
    r = run(script, *args)
    if r.returncode or not r.stdout.strip().endswith(tail): raise SystemExit('FAIL ' + script)
r = run('ordinary.py', data('word.json.gz'), data('caller.json'))
fig = [l for l in r.stdout.splitlines() if l.startswith('RAW ')]
if r.returncode or len(fig) != 3 or not all(l.endswith('True') for l in fig) or fig[0].split()[2] != '802809952' or fig[1].split()[2] != '815970652' or fig[2].split()[2] != '832255648': raise SystemExit('FAIL ordinary.py ' + str(fig))
print('PASS_SMALL_CHECKS')
