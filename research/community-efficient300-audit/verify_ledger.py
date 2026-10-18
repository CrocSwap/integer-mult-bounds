import sys,pathlib,json,hashlib,collections
R=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from verify_pr_reconciliation import check_family_decision,check_review_completion
from reconcile_pr_queue import build
A=R/'research/community-efficient300-audit';ledger=json.loads((R/'docs/research/pr-ledger.json').read_text());build();assert ledger==json.loads((R/'docs/research/pr-ledger.json').read_text())
rows={r['number']:r for r in ledger['pull_requests']};family=json.loads((A/'DISPOSITIONS.json').read_text())['pull_requests'];assert len(family)==100
for row in family:
 check_family_decision(rows[row['number']],row);check_review_completion(rows[row['number']],row)
for name,digest in ledger['source_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
for n in (225,279,1015):
 assert rows[n]['disposition']=='incorporated',n
 assert any(e.get('kind')=='independent_consolidation' and e['evidence']=='research/community-efficient300-audit/PARENT-EVIDENCE.json' for e in rows[n]['evidence']),n
result={'status':'PASS','family_decisions':100,'source_hashes':len(ledger['source_sha256']),'parent_dispositions_preserved':[225,279,1015],'generator_matches':True,'scope':'Current family projection, generator equality and pinned ledger inputs. Does not rerun unrelated historical archive checks.'}
(A/'TARGETED-LEDGER-CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
