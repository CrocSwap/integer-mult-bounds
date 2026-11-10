"""Read-only adapter for separately authored exact checks."""
from pathlib import Path
import importlib.util,json,hashlib
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent

def module(name):
 spec=importlib.util.spec_from_file_location('independent_'+name,HERE/'review'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 for f,h in json.loads((HERE/'review/PINS.json').read_text()).items():assert hashlib.sha256((HERE/'review'/f).read_bytes()).hexdigest()==h
 root=module('root');tariff=module('tariff')
 for g in[3,9,18]:
  got=json.loads(json.dumps(root.audit(HERE/f'root_L{g}.json')));assert got==json.loads((HERE/f'review/ROOT-L{g}.json').read_text())
 got=json.loads(json.dumps(tariff.audit(HERE/'root_L18.json',HERE/'caller_L18.json')));assert got==json.loads((HERE/'review/TARIFF-L18.json').read_text())
 import sys,io,contextlib
 native=module('native_screen');before=sys.argv[:];buf=io.StringIO()
 try:
  sys.argv=['native_screen','--word',str(HERE/'inputs/final_native.json.gz'),'--caller',str(HERE/'caller_L18.json'),'--base-invoice',str(HERE/'inputs/base_invoice.json')]
  with contextlib.redirect_stdout(buf):native.main()
 finally:sys.argv=before
 assert json.loads(buf.getvalue())==json.loads((HERE/'review/NATIVE-SCREEN.json').read_text())
 print('PASS_INDEPENDENT_CONNECTED_ROOT')
