#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run without -O; assertions are proof checks.')
subprocess.run([sys.executable,'-B',str(HERE/'reproduce.py')],check=True)
subprocess.run([sys.executable,'-I','-B',str(HERE/'frozen/verify_host3_odd.py'),str(HERE/'data/final.json.gz'),'1125'],check=True)
subprocess.run([sys.executable,'-B',str(HERE/'chart_delta.py'),str(HERE/'data/final.json.gz')],check=True)
print('PASS_SHARED_WIRE_SPLIT_NATIVE')
