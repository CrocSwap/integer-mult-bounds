#!/usr/bin/env python3
"""Rebuild a base graph, its whole-chain clones and alternative producers."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from alternative_producer_clones import opportunities,rewrite
from check_compiled_witness import check
from producer_search import digest
from rebuild_selected import rebuild

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
p.add_argument('--base-parent',type=Path,required=True);p.add_argument('--whole-selected',type=Path,required=True)
p.add_argument('--selected',type=Path,required=True);p.add_argument('--dirty',action='store_true')
a=p.parse_args();assert not a.work.exists();a.work.mkdir(parents=True)
whole=rebuild(a.source,a.work/'whole',a.base_parent,a.whole_selected,a.dirty)
row=dict(whole['producer']);selected=json.loads(a.selected.read_text())
if 'rows'in selected:
    assert len(selected['rows'])==1
    selected=selected['rows'][0]
limit=selected['producer']['configuration']['limit'];policy=selected['producer']['configuration'].get('selection_policy','conservative');matcher=a.work/'whole'/'builds'/'moment_match_rank_node'
stages=[]
for index,recorded in enumerate(selected['stages']):
    jobs,diagnostic,order,frames=opportunities(row,limit,policy)
    if recorded.get('terminal'):
        assert not jobs;break
    assert jobs==recorded['chosen'],'Exact alternative coefficient partition/controllers differ'
    target=a.work/'alternatives'/f'round-{index+1}';dag=rewrite(row,jobs,order,frames,target);witness=target/'selected-links.json'
    native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],capture_output=True,text=True,check=True)
    new=json.loads(native.stdout);assert new['R']==recorded['new_roles'];assert digest(dag)==recorded['new_dag_sha256']
    new.update(dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),
               witness_path=str(witness),witness_sha256=digest(witness),schedule='rank-node',
               configuration=dict(alternative_partitions=True,limit=limit,round=index+1))
    stages.append(dict(round=index+1,clones=len(jobs),R=new['R'],dag_sha256=new['dag_sha256']));row=new
expected=selected['producer']
for key in('dag_sha256','positive_sha256','witness_sha256','histogram'):assert row[key]==expected[key],key
audit=check(dict(producer=row),a.dirty)
result=dict(status='complete alternative-producer selected recovery PASS',producer=row,stages=stages,
            independent=audit,whole_rebuild=str(a.work/'whole'/'rebuild-result.json'),
            source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',command=sys.argv,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            fixture_sha256={p.name:digest(p)for p in(a.base_parent,a.whole_selected,a.selected)})
(a.work/'rebuild-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=result['status'],h=row['h'],R=row['R'],new_alternative_clones=sum(s['clones']for s in stages))),flush=True)
