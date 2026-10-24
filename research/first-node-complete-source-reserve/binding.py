"""Authenticate complete retained caller cohort before loading credited fixtures."""
import hashlib,json,importlib.util,sys
from contextlib import contextmanager
from types import ModuleType
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).resolve().parent

def need(ok,message):
 if not ok:raise RuntimeError(message)

def load():
 manifest=json.loads((PACKAGE/'SOURCES.json').read_text())
 for row in manifest['files']:
  if row['usage']!='input':continue
  data=(ROOT/row['path']).read_bytes()
  need(hashlib.sha256(data).hexdigest()==row['sha256'],'source SHA256')
  need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source blob')
 snapshot=json.loads((ROOT/'research/selected-node-count-storage/SNAPSHOT.json').read_text())
 cohort=ROOT/'research/selected-child-caller-lifetime/vendor'
 rows={Path(r['path']).name:r for r in snapshot['files']}
 for source in cohort.glob('*.py'):
  need(hashlib.sha256(source.read_bytes()).hexdigest()==rows[source.name]['sha256'],'PR2749 count cohort identity')
 folder=ROOT/'research/selected-child-caller-lifetime'
 old=sys.modules.get('runtime');oldpath=list(sys.path)
 try:
  for name,file in [('runtime','runtime.py'),('credited_caller_fixture','verify.py')]:
   spec=importlib.util.spec_from_file_location(name,folder/file);module=importlib.util.module_from_spec(spec)
   sys.modules[name]=module;spec.loader.exec_module(module)
  original_runtime=module.runtime
  @contextmanager
  def complete_runtime():
   with original_runtime() as m:
    saved=sys.modules.get('children')
    child=ModuleType('children');path=ROOT/'research/selected-coefficient-capacity-prefix/vendor/children.py'
    child.__file__=str(path);sys.modules['children']=child
    try:
     exec(compile(path.read_bytes(),str(path),'exec'),child.__dict__)
     m.children=child
     yield m
    finally:
     if saved is None:sys.modules.pop('children',None)
     else:sys.modules['children']=saved
  module.runtime=complete_runtime
  return module
 finally:
  sys.path[:]=oldpath
  if old is None:sys.modules.pop('runtime',None)
  else:sys.modules['runtime']=old
  sys.modules.pop('credited_caller_fixture',None)
