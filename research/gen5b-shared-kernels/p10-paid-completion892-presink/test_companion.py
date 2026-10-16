"""Portable dependency, provenance, arithmetic and emitted-word regressions."""
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
import copy,hashlib,json,subprocess,sys,tempfile,unittest
import companion as packet
packet.require_assertions()
class CompanionTests(unittest.TestCase):
 def test_predecessor_identity(self):
  self.assertEqual(packet.sha(packet.BASE_CODE/'FILES.json'),packet.BASE_FILES_SHA)
  self.assertTrue(packet.verify_base())
 def test_wrong_predecessor_pin_rejected(self):
  with patch.object(packet,'BASE_FILES_SHA','0'*64):
   with self.assertRaises(AssertionError):packet.verify_base_code()
  import run_checks
  with tempfile.TemporaryDirectory() as folder, patch.object(packet,'HERE',Path(folder)):
   with self.assertRaises(AssertionError):run_checks.check_packet()
 def test_all_eight_sources(self):
  self.assertEqual(len(packet.source_pins()['files']),8);packet.verify_sources()
 def test_source_byte_mutation_rejected(self):
  for row in packet.source_pins()['files']:
   raw=(packet.INPUTS/row['label']).read_bytes()
   with self.assertRaises(AssertionError):packet.check_source_bytes(raw+b' ',row)
 def test_source_git_blob_mutation_rejected(self):
  row=copy.deepcopy(packet.source_pins()['files'][0]);raw=(packet.INPUTS/row['label']).read_bytes();row['sha']='0'*40
  with self.assertRaises(AssertionError):packet.check_source_bytes(raw,row)
 def test_upstream_python_is_inert(self):
  labels=[r['label']for r in packet.source_pins()['files']]
  self.assertTrue(any(s.endswith('.py.txt')for s in labels));self.assertFalse(any(s.endswith('.py')for s in labels))
 def test_all_experiment_producers_bound(self):
  value=packet.verify_experiment()
  self.assertEqual(set(value['producer_hashes']),{p.name for p in(packet.HERE/'experiment').glob('*.py')})
 def test_stale_experiment_producer_rejected(self):
  original=packet.read;value=copy.deepcopy(original(packet.EXPERIMENT/'MANIFEST.json'));value['producer_hashes']['check_composition.py']='0'*64
  def altered(path):return value if Path(path)==packet.EXPERIMENT/'MANIFEST.json'else original(path)
  with patch.object(packet,'read',side_effect=altered):
   with self.assertRaises(AssertionError):packet.verify_experiment()
 def test_missing_experiment_producer_rejected(self):
  original=packet.read;value=copy.deepcopy(original(packet.EXPERIMENT/'MANIFEST.json'));value['producer_hashes'].pop('check_composition.py')
  def altered(path):return value if Path(path)==packet.EXPERIMENT/'MANIFEST.json'else original(path)
  with patch.object(packet,'read',side_effect=altered):
   with self.assertRaises(AssertionError):packet.verify_experiment()
 def test_all_17_hard_controls(self):
  value=packet.read(packet.EXPERIMENT/'CONTROLS.json');self.assertEqual(value['count'],17);self.assertEqual(len(set(value['controls'])),17)
 def test_complete_literal_invoice(self):
  value=packet.read(packet.AUDIT/'BANK-PRICE-AUDIT.json')
  self.assertEqual(tuple(value[k]for k in['stock','calls','rank_mass','max_rank','phases','paid_completions','completion_rank']),(658255,15006605,65703100,42,725,5,20))
  self.assertEqual(value['selector_calls'],295864873940);self.assertEqual(value['finite_coefficient'],25478454083580596)
 def test_exact_price_and_adjacent_rejection(self):
  value=packet.read(packet.AUDIT/'BANK-PRICE-AUDIT.json')
  self.assertEqual(Fraction(value['kappa']),Fraction(770008089898797,10**18));self.assertTrue(value['all47exact_slacks_reproduced']);self.assertTrue(value['adjacent_kappa_rejected'])
  self.assertEqual(list(map(Fraction,value['root_bracket'])),[Fraction(770601459593856,10**18),Fraction(770601459593857,10**18)])
 def test_all_global_records_and_bindings(self):
  value=packet.read(packet.AUDIT/'GLOBAL-AUDIT.json');result=packet.read(packet.LOWERING/'RESULT.json')
  self.assertEqual(value['all_local_records'],389222);self.assertEqual(value['all_global_stage_records'],116772600);self.assertEqual(value['all_namespaces'],300)
  self.assertEqual(value['global_result_sha256'],packet.sha(packet.LOWERING/'RESULT.json'));self.assertEqual(value['program_binding'],result['full_program_sha256'])
 def test_all_100_positive_copy_overrides(self):
  value=packet.read(packet.LOWERING/'PROJECTOR-CONTROLS.json')
  self.assertEqual(value['positive_copied_work_descriptors'],100);self.assertTrue(value['negative_forward_copy_direction_rejected'])
  matrices=packet.read(packet.AUDIT/'GLOBAL-AUDIT.json')['actual_positive_center_projector_checks'];self.assertEqual(len(matrices),20)
  self.assertTrue(all(r['rational_idempotent']and r['negative_projector_rejected']and r['negative_D_not_involution']for r in matrices))
 def test_five_paid_rank20_projectors(self):
  value=packet.read(packet.LOWERING/'PROJECTOR-CONTROLS.json')
  self.assertEqual(value['exact200column_completion_projectors'],5)
  for k in['all_VU_minus2I_checked','wrong_completion_coefficient_rejected','same_bank_route_conjugation_checked','all_completion_fees_checked']:self.assertTrue(value[k])
 def test_path_normalization_includes_keys(self):
  value={str(packet.LOWERING/'RESULT.json'):[str(packet.BASE_FRAME/'RESULT.json'),str(packet.INPUTS/'x')]}
  self.assertEqual(packet.portable(value),{'$OUTPUT/lowering/RESULT.json':['$BASE_OUTPUT/frame/RESULT.json','$INPUTS/x']})
 def test_all_entrypoints_reject_optimized_python(self):
  names=['acquire_inputs.py','run_checks.py']+[str(p.relative_to(packet.HERE))for folder in['experiment','admission','lowering','audit']for p in sorted((packet.HERE/folder).glob('*.py'))if p.name!='retained_ir_helpers.py']
  for name in names:
   result=subprocess.run([sys.executable,'-O',str(packet.HERE/name)],env=packet.child_env(),capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0,name);self.assertIn('Assertions must be enabled',result.stderr,name)
if __name__=='__main__':unittest.main()
