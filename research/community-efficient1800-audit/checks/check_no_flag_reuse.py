"""Source-bound reuse of the already published full PR468 replay for PR720."""
from pathlib import Path
import json,subprocess,hashlib,gzip,sys,copy,math,collections,importlib.util
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');root=P/'sources/720';pkg=root/'research/three-register-no-target-flag';sys.path.insert(0,str(pkg));import verify as v
pins=v.source_check();bindings=[]
for name,digest in pins['files'].items():
 old=subprocess.check_output(['git','show',pins['base_commit']+':'+name],cwd=R);current=subprocess.check_output(['git','show','HEAD:'+name],cwd=R)
 assert old==current==(root/name).read_bytes() and hashlib.sha256(old).hexdigest()==digest
 bindings.append(dict(path=name,sha256=digest,base=pins['base_commit'],current_main_identical=True))
audit='research/community-notes-20261011-audit/'
raw=subprocess.check_output(['git','show','HEAD:'+audit+'pr468-replay.json'],cwd=R);retained=json.loads(raw);v.check_replay_result(retained,pins)
refs=[];engines=[]
for name in ['rational','f101']:
 path=audit+'pr468-'+name+'-results.jsonl.gz';data=subprocess.check_output(['git','show','HEAD:'+path],cwd=R);rows=[json.loads(line) for line in gzip.decompress(data).splitlines()];assert len(rows)==2276 and len({r['case'] for r in rows})==2276;rows.sort(key=lambda r:r['case']);assert [r['case'] for r in rows]==list(range(2276));assert all(r['robust']==0 and r.get('nonmonomial_diagonal',0)==0 for r in rows);engines.append(rows);refs.append(dict(path=path,sha256=hashlib.sha256(data).hexdigest()))
keys=('case','words','terminals','robust');canonical=[[{k:r[k] for k in keys} for r in rows] for rows in engines];assert canonical[0]==canonical[1]
digest=hashlib.sha256(json.dumps(canonical[0],sort_keys=True,separators=(',',':')).encode()).hexdigest();expected=json.loads((pkg/'REPLAY.json').read_text());assert digest==expected['per_family_semantics']['sha256'];assert sum(r['words'] for r in canonical[0])==21317520 and sum(r['terminals'] for r in canonical[0])==415398
# Reuse does not alter the new wrapper's acceptance gate. Exercise its rejection cases.
mutants=[]
for field in ['families','orders','diagonal_terminals','survivors']:
 d=copy.deepcopy(retained);d[field]+=1;mutants.append((field,d))
for field in ['all_per_case_counts_agree','core_positive_accepted','core_rank_two_mutation_rejected']:
 d=copy.deepcopy(retained);d[field]=False;mutants.append((field,d))
d=copy.deepcopy(retained);d['formal_controls']['modular_alias_rejected']=False;mutants.append(('formal_control',d))
d=copy.deepcopy(retained);d['source_sha256'].pop('catalogue.py');mutants.append(('missing_source',d))
d=copy.deepcopy(retained);d['source_sha256']['rational.cpp']='0'*64;mutants.append(('wrong_source',d))
d=copy.deepcopy(retained);d['catalogue_sha256']='0'*64;mutants.append(('wrong_catalogue',d))
for name,d in mutants:
 try:v.check_replay_result(d,pins)
 except ValueError:pass
 else:raise AssertionError('mutant accepted '+name)
record=dict(status='passed',source_bindings=bindings,retained_full_replay=dict(path=audit+'pr468-replay.json',sha256=hashlib.sha256(raw).hexdigest(),engine_logs=refs,per_family_semantic_sha256=digest,orders=21317520,families=2276,diagonal_terminals=415398,survivors=0),fresh_replay_validator_controls=len(mutants),proof_review='New any-length corank<=2 disjoint-subset proof, arbitrary2x2 target corollary and span-four block reduction reviewed. Inherited span-five filters inspected and target-flag independence checked. Prior complete engine code review/replay retained in docs/research/research-notes-20261011.md.',scope='Reuse authenticates all seven unchanged dependency sources, published maintainer replay and both complete per-case logs. No new C++ full-engine execution; fresh new-package finite certificate and separate polynomial/control checks required.')
(P/'provenance-720.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS_NO_FLAG_SOURCE_BOUND_REUSE sources=7 families=2276 orders=21317520 controls='+str(len(mutants)))
