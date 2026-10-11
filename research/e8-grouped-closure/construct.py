from pathlib import Path
import hashlib,json,subprocess,sys
assert __debug__
ROOT=Path(__file__).resolve().parent
source,out=map(Path,sys.argv[1:3]);expected=json.loads((ROOT/'EXPECTED.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==expected['source_sha256'] and not out.exists();out.mkdir(parents=True)
checks=[]
for vendor,selection,src,dst,input_sha,output_sha in [('vendor416','SELECTION.json',source,out/'grouped',expected['source_sha256'],expected['grouped_sha256']),('vendor421','CAPACITY-SELECTION.json',out/'grouped/candidate.json',out/'capacity',expected['grouped_sha256'],expected['capacity_sha256']),('vendor423','ENLARGEMENT-SELECTION.json',out/'capacity/candidate.json',out/'enlarged',expected['capacity_sha256'],expected['candidate_sha256'])]:
 subprocess.run([sys.executable,'-B',str(ROOT/vendor/'construct.py'),str(src),str(ROOT/selection),str(dst),'--source-sha256',input_sha,'--expected-sha256',output_sha],check=True)
 receipt=json.loads((dst/'RECEIPT.json').read_text());assert (receipt.get('all1021raw_and_snapshot_columns_right_multiplied_by_literal_prepended_word') or receipt.get('all1021raw_and_snapshot_columns_unchanged')) and receipt['all_gauged_response_columns_zero'];checks.append(receipt)
(out/'candidate.json').write_bytes((out/'enlarged/candidate.json').read_bytes());assert sha(out/'candidate.json')==expected['candidate_sha256']
(out/'RESULT.json').write_text(json.dumps(dict(status='PASS_EXACT_GROUPED_CAPACITY_AND_ENLARGEMENT_ON_PR418',source_sha256=expected['source_sha256'],candidate_sha256=expected['candidate_sha256'],stages=checks),indent=2)+'\n')
