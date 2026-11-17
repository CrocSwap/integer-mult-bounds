# SPDX-License-Identifier: Apache-2.0
"""Evidence-only controls: no science, process launch or source-row replay."""
import copy, hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
P=Path(__file__).resolve().parent; A=P.parent.parent
spec=importlib.util.spec_from_file_location('journal_consumer',P/'check_recovered_journal.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);d=Path(self.tmp.name)
  sources={'signed_terminal':A/'e4-signed-controller/recovered-executable/runs/attempt-01/SUPERVISOR-TERMINAL.json','signed_execution':A/'e4-signed-controller/recovered-executable/runs/attempt-01/SIGNED-EXECUTION.json','signed_audit':A/'e4-signed-controller/recovered-executable/runs/attempt-01/SIGNED-AUDIT.jsonl','signed_journal':A/'e4-signed-journal-recovery/ORIGINAL-UNIT-JOURNAL.jsonl','signed_retirement':A/'e4-signed-journal-recovery/HOST-RETIREMENT.json'}
  self.paths={k:d/k for k in sources}
  for k,p in sources.items():self.paths[k].write_bytes(p.read_bytes())
  self.hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in self.paths.items()}
  for k,v in self.hashes.items():self.assertEqual(v,m.FIXED[k])
  self.hashes.update(signed_binding='a7cf71e28722a9f22b2c2161d1d319f39f363743091146b69196e67a7c5529c5',signed_result='6fe1f74fb37f6882108702429ec9783e79af7e5737d60530d50b7ad02e29f534')
  self.r={k+'_sha256':v for k,v in self.hashes.items() if k in sources}
  self.r.update(original_error={'stage':'supervisor','error':"ValueError('final cgroup absent')"},journal_invocation_id='668d934ed2d440c89a4f038823b0cabf',initial_limits_pass=True,original_readback_limits_pass=False,exit_code=0,run_id='f6c24629d235470b86c46703ad59fb22',native_run_id='c2e263c03ed18855afd4125d42981d71a27151b81d00ed05b133966629394cf4',execution_wall_seconds=(62620753024-62041006386)/1e6,aggregate_cpu_usec=562277967,peak_memory_bytes=591405056,peak_swap_bytes=0)
 def call(self):m.signed_recovery(self.r,self.paths,self.hashes)
 def test_positive(self):self.call()
 def test_false_claims(self):
  for key,value in [('original_readback_limits_pass',True),('initial_limits_pass',False),('readback_limits_pass',True),('original_supervisor_pass',True),('exit_code',1),('journal_invocation_id','other'),('peak_swap_bytes',1),('execution_wall_seconds',1),('aggregate_cpu_usec',1),('signed_audit_sha256','wrong')]:
   old=copy.deepcopy(self.r);self.r[key]=value
   with self.assertRaises((ValueError,KeyError),msg=key):self.call()
   self.r=old
 def test_evidence_substitution(self):
  j=[json.loads(x) for x in self.paths['signed_journal'].read_text().splitlines()];j[3]['CPU_USAGE_NSEC']='1';self.paths['signed_journal'].write_text('\n'.join(json.dumps(x) for x in j)+'\n')
  with self.assertRaises(ValueError):self.call()
 def test_math_body_unchanged(self):
  before=(P.parent/'recovered-native/check_recovered.py').read_text();after=(P/'check_recovered_journal.py').read_text()
  self.assertEqual(before[before.index(" source=json.loads(gzip.decompress"):before.index(" return {'schema':'e4-resource-price-consumer")],after[after.index(" source=json.loads(gzip.decompress"):after.index(" return {'schema':'e4-resource-price-consumer")])
if __name__=='__main__':unittest.main()
