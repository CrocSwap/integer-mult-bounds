#!/usr/bin/env python3
"""Run the frozen historical test module against one replay arm.

argv[1] is the repository root and argv[2] is the arm: `historical` imports
the frozen scripts/experiments modules; `fast` preloads the package shim so
the test module's own `from binary_frame_replay import replay` resolves to
the optimized adapter. The test module itself is loaded unmodified either
way. Prints one JSON line with the wall time and the exact test outcome.
"""
import json
import os
import sys
import time
import unittest
from pathlib import Path

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

root = Path(sys.argv[1])
arm = sys.argv[2]
if arm not in ('historical', 'fast'):
    raise SystemExit('arm must be historical or fast')
sys.path.insert(0, str(root / 'research/joint-dual-replay-fast'))
sys.path.insert(0, str(root / 'scripts/experiments'))
if arm == 'fast':
    sys.path.insert(0, str(root / 'research/joint-dual-replay-fast/shim'))
import binary_frame_replay
import binary_frame_profile_prepare
sys.path.insert(0, str(root / 'tests'))
import test_joint_reclaim

start = time.perf_counter()
suite = unittest.TestLoader().loadTestsFromModule(test_joint_reclaim)
result = unittest.TextTestRunner(stream=open(os.devnull, 'w'), verbosity=0).run(suite)
seconds = time.perf_counter() - start
print(json.dumps(dict(arm=arm, seconds=seconds, tests=result.testsRun,
                      failures=len(result.failures), errors=len(result.errors),
                      replay_module=binary_frame_replay.__file__)))
