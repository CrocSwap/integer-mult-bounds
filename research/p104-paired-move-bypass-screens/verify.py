#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the pinned source, geometry, full case receipts and controls."""
from contextlib import redirect_stdout
from hashlib import sha1,sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip,io,json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native_model,verify_geometry,receipt_screen,ancestry_screen,target_cut,target_cut_audit


def digest(path):return sha256(path.read_bytes()).hexdigest()

def run(module,argv):
 old=sys.argv;sys.argv=[str(HERE/(module.__name__+'.py')),*map(str,argv)]
 try:
  with redirect_stdout(io.StringIO()) as out:module.main()
  return out.getvalue()
 finally:sys.argv=old

def main():
 if sys.flags.optimize:raise RuntimeError('Assertions must be enabled')
 spec=json.loads((HERE/'SOURCES.json').read_text());source=HERE/'BINARY-CANDIDATE.json.gz'
 raw=source.read_bytes();base=spec['vendored_graph']
 assert sha256(raw).hexdigest()==base['sha256']
 assert sha256(gzip.decompress(raw)).hexdigest()==base['expanded_sha256']
 assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==base['git_blob']
 for name,expected in spec['retained_files_sha256'].items():assert digest(HERE/name)==expected,name
 with TemporaryDirectory(prefix='p104-paired-move-') as tmp:
  temp=Path(tmp);bad=temp/'bad.gz';mutated=bytearray(raw);mutated[len(mutated)//2]^=1;bad.write_bytes(mutated)
  try:native_model.load(bad)
  except ValueError:pass
  else:raise AssertionError('Corrupted source control was accepted')
  geometry=run(verify_geometry,[source]);print(geometry,end='')
  for module,expected in [(receipt_screen,'RECEIPT-RESULTS.json.gz'),(ancestry_screen,'ANCESTRY-RESULTS.json.gz'),(target_cut,'TARGET-CUT-RESULTS.json.gz')]:
   result=temp/(module.__name__+'.json')
   options=[source,'--output',result]
   if module is not target_cut:options.insert(1,'--control-all')
   output=run(module,options);computed=result.read_bytes();sealed=gzip.decompress((HERE/expected).read_bytes())
   assert computed==sealed,expected+' differs from deterministic replay'
   print(output,end='')
  print(run(target_cut_audit,[]),end='')
 print('PASS_P104_PAIRED_MOVE_SCREENS_AND_CONTROLS')

if __name__=='__main__':main()
