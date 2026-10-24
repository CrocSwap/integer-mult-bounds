"""Emit the complete guarded adaptive native word. Apache-2.0."""
from pathlib import Path
import types,sys,json,argparse
HERE=Path(__file__).resolve().parent
m=types.ModuleType('levi_native_emitter');m.__file__=str(HERE/'native_source.py');sys.modules[m.__name__]=m
exec(compile((HERE/'native_source.py').read_bytes(),m.__file__,'exec'),m.__dict__)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 words,chart,v,n=m.sources(m.authenticated());out,r=m.install(words,m.read('RESULT.json')['patches'],n.primitive_allowance)
 m.need(not a.output.exists(),'Choose a fresh output path; preserve existing artifacts')
 a.output.write_bytes(m.canonical(out)+b'\n');print(json.dumps({'status':'WROTE_LEVI_ADAPTIVE_NATIVE_WORD','semantic_sha256':m.digest(out)}))
