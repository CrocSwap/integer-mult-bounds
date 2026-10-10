"""Preserve original verify.py; set only reproducible environmental flags."""
import argparse,runpy,sys
from pathlib import Path
if not __debug__ or sys.flags.optimize or sys.flags.utf8_mode!=1:raise SystemExit('normal UTF8 original replay required')
sys.set_int_max_str_digits(100000);sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
base=Path(__file__).resolve().parent.parent/'five-stage-gen5-collective-kernels'
sys.path.insert(0,str(base));sys.argv=[str(base/'verify.py'),'--output',a.output]
runpy.run_path(sys.argv[0],run_name='__main__')
