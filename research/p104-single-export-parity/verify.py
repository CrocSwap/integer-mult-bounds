#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate and replay both parity proofs, chart cut, and conditional price."""
from hashlib import sha1,sha256
from pathlib import Path
import gzip,json,subprocess,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

def main():
 if sys.flags.optimize:raise RuntimeError('Assertions must remain enabled')
 meta=json.loads((HERE/'SOURCES.json').read_bytes())
 for name,expected in meta['retained_files_sha256'].items():
  assert sha256((HERE/name).read_bytes()).hexdigest()==expected,name
 graph=HERE/'pinned'/'strong-bit.json.gz';raw=graph.read_bytes();g=meta['vendored_graph']
 assert sha256(raw).hexdigest()==g['sha256']
 assert sha256(gzip.decompress(raw)).hexdigest()==g['expanded_sha256']
 assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==g['git_blob']
 from shorter_ingress import projector,matrix_mul
 frames=json.loads(gzip.decompress(raw))['frames']
 small,mid,large=[projector(frames[str(i)]) for i in (326,531,1)]
 assert matrix_mul(small,mid)==matrix_mul(mid,small)==small
 assert matrix_mul(mid,large)==matrix_mul(large,mid)==mid
 print('PASS_RELAY_PROJECTOR_NESTING',flush=True)
 checks=[('carrier_invariant.py',[str(graph)],'CARRIER-INVARIANT.json','FORWARD_NOISE'),
         ('reverse_audit.py',[str(graph)],'REVERSE-RESULT.json','REVERSE_PARITY'),
         ('terminal_cut.py',[str(graph)],'TERMINAL-CUT.json','TERMINAL_INTERFACE_CUT'),
         ('shorter_ingress.py',[str(graph)],'SHORTER-INGRESS.json.gz','CHEAPER_INGRESS_CUT'),
         ('relay_example.py',[],'RELAY.json','RELAY_DIAGNOSTIC'),
         ('verify_funding.py',[],'FUNDING.json','CONDITIONAL_FUNDING')]
 for script,args,expected,label in checks:
  result=subprocess.run([sys.executable,'-I','-B',str(HERE/script),*args],
                        capture_output=True,text=True,timeout=480,check=True)
  actual=json.loads(result.stdout);expected_data=(HERE/expected).read_bytes()
  if expected.endswith('.gz'):expected_data=gzip.decompress(expected_data)
  witness=json.loads(expected_data)
  assert actual==witness,'replayed '+label+' does not match the checked receipt'
  print('PASS_'+label,flush=True)
 print('PASS_SINGLE_EXPORT_PARITY_AND_CONDITIONAL_FUNDING',flush=True)

if __name__=='__main__':main()
