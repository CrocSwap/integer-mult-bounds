import importlib.util,pathlib,gzip,tempfile
p=pathlib.Path('/tmp/pr-efficient1100/sources/2089/research/p104-tail-side-correction-seed749717/verify.py');spec=importlib.util.spec_from_file_location('v',p);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
with tempfile.TemporaryDirectory() as t:
 f=pathlib.Path(t)/'test.json.gz';a=gzip.compress(b'{"proof":1}\n',mtime=0);b=gzip.compress(b'{"proof":1}\n',mtime=42);f.write_bytes(a);v.write_stable(f,b);assert f.read_bytes()==a
 try:v.write_stable(f,gzip.compress(b'{"proof":2}\n',mtime=42))
 except ValueError:pass
 else:raise AssertionError('accepted changed mathematical payload')
 f=pathlib.Path(t)/'test.json';f.write_bytes(b'{"proof":1}\n')
 try:v.write_stable(f,b'{"proof":2}\n')
 except ValueError:pass
 else:raise AssertionError('accepted changed raw JSON')
print('PASS gzip header variation accepted; payload mutation and raw JSON mutation rejected; source containers preserved')
