"""Select the frozen relative-interval dependency after folder reconciliation."""
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
sys.argv = [str(HERE / 'check.py'), '--parent', str(HERE.parent),
            '--cuts', str(HERE.parent / 'compiler-intervals'), *sys.argv[1:]]
runpy.run_path(str(HERE / 'check.py'), run_name='__main__')
