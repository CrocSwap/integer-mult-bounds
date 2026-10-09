import ast,hashlib,importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v) for v in x]
 return x
def write(p,x):
 with Path(p).open('x') as f:json.dump(js(x),f,indent=2,sort_keys=True);f.write('\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def functions(p,names,ctx):
 nodes=[x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef) and x.name in names]
 assert {x.name for x in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ctx)
def inventory(root):
 assert not root.is_symlink() and not any(p.is_symlink() for p in root.rglob('*')),'Symlink in retained inputs'
 return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}
def check_package():
 m=read(HERE/'MANIFEST.json')['files'];got=inventory(HERE)
 assert set(got)==set(m)|{'MANIFEST.json'} and all(got[n]==h for n,h in m.items()),'Package changed'
 return sha(HERE/'MANIFEST.json')
def source_pins(kind):
 return read(HERE/'SOURCES.json')[kind]['files']
def check_source(root,kind):
 root=Path(root)
 assert root.is_dir() and not root.is_symlink(),'Source root is missing or symlinked'
 pins=source_pins(kind)
 for name,h in pins.items():
  rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts
  path=root/rel
  assert not any(p.is_symlink() for p in [path,*path.parents] if p!=root.parent),'Source symlink: '+name
  assert path.is_file() and sha(path)==h,'Source drift: '+name
 return pins
def check_sources(c,b):
 return dict(complex=check_source(c,'complex'),bit=check_source(b,'bit'))
def canonical(result):
 # Execution bindings and display floats are recorded separately, never as math.
 return {k:js(v) for k,v in result.items() if k not in
         ('status','kappa_decimal','supplier_sha256','packing_sha256','scope')}
def fresh_output(path,inputs):
 path=Path(path)
 assert not path.is_symlink(),'Output symlink'
 out=path.resolve();assert not out.exists(),'Output already exists'
 for source in inputs:
  source=Path(source).resolve()
  assert out!=source and source not in out.parents,'Output inside protected input'
 return out
