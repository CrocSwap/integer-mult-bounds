from pathlib import Path
import hashlib,json,subprocess,sys
assert __debug__
ROOT=Path(__file__).resolve().parent
source,out=map(Path,sys.argv[1:3]);expected=json.loads((ROOT/'EXPECTED.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected['source_sha256']
subprocess.run([sys.executable,'-B',str(ROOT/'vendor416/construct.py'),str(source),str(ROOT/'SELECTION.json'),str(out),'--source-sha256',expected['source_sha256'],'--expected-sha256',expected['candidate_sha256']],check=True)
receipt=json.loads((out/'RECEIPT.json').read_text())
assert receipt['all1021raw_and_snapshot_columns_right_multiplied_by_literal_prepended_word'] and receipt['all_gauged_response_columns_zero']
receipt['status']='PASS_EXACT_PROPAGATED_ENTRANCES_ON_PR415'
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
