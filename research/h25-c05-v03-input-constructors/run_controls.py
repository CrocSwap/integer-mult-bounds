"""Run only new source/data helpers and fresh fixtures, never archived inputs."""
from pathlib import Path
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SCRIPTS = {'v03':'tests/v03_constructor_test_v1.py',
           'header':'implementation/c05_header_edges_test_v1.py',
           'gcc':'implementation/c05_gcc_rules_tests_v1.py',
           'elf':'tests/c05_elf_edges_test_v1.py'}
if len(sys.argv)!=2 or sys.argv[1] not in SCRIPTS:
    raise SystemExit('Choose v03, header, gcc or elf')
target = ROOT / SCRIPTS[sys.argv[1]]
runpy.run_path(str(ROOT/'verify.py'),run_name='__main__')
sys.dont_write_bytecode = True
sys.pycache_prefix = tempfile.mkdtemp(prefix='c05-new-source-cache-',dir='/tmp')
sys.path.insert(0,str(ROOT/'implementation'))
sys.argv = [str(target)]
runpy.run_path(str(target),run_name='__main__')
