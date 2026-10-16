#!/usr/bin/env python3
"""Deterministic two-worker witness for the inherited shared-temp rename race.

Only the scheduling of two literal writes/renames is controlled. No audit
predicate or mutation is altered. The same schedule must succeed after repair.
"""
import argparse
import tempfile
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'gmx-t74-borrow43-handoff/audit_fast.py'
OLD="_part.with_suffix('.tmp').write_text(_j.dumps([_idx[0],_own]));_part.with_suffix('.tmp').replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)"
NEW="_tmp=_part.with_name(_part.name+'.%d.%d.tmp'%(_AF_SHARD,os.getpid()));_tmp.write_text(_j.dumps([_idx[0],_own]));_tmp.replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)"


def worker(root,shard,unique,barrier):
    part=Path(root)/'.audit-fast-partial'
    own=[25,[[shard,'control-'+str(shard)]]]
    temp=part.with_name(part.name+'.%d.%d.tmp'%(shard,os.getpid())) if unique else part.with_suffix('.tmp')
    temp.write_text(json.dumps(own))
    # Both writes complete before either rename, a valid preemption schedule
    # between the original statement's write and rename operations.
    barrier.wait()
    try:
        temp.replace(part.with_name(part.name+'.%d'%shard))
        result=dict(shard=shard,status='renamed')
    except FileNotFoundError as exc:
        result=dict(shard=shard,status='FileNotFoundError',error=str(exc))
    (Path(root)/('worker-%d.json'%shard)).write_text(json.dumps(result))


def main():
    assert SOURCE.read_text().count(OLD)==1,'exact inherited writer preimage'
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path);args=parser.parse_args()
    if args.out:
        out=args.out.resolve();assert not out.exists() and not out.is_relative_to(HERE.parent.parent);out.mkdir(parents=True)
    else:
        out=Path(tempfile.mkdtemp(prefix='t124-shard-transport-'));assert not out.is_relative_to(HERE.parent.parent)
    ctx=mp.get_context('spawn');results={}
    for name,unique in [('inherited_shared_temp',False),('unique_shard_pid_temp',True)]:
        root=out/name;root.mkdir();barrier=ctx.Barrier(2)
        ps=[ctx.Process(target=worker,args=(root,k,unique,barrier)) for k in (3,4)]
        for p in ps:p.start()
        for p in ps:p.join();assert p.exitcode==0
        rows=[json.loads((root/('worker-%d.json'%k)).read_text()) for k in (3,4)]
        outputs={str(k):json.loads((root/('.audit-fast-partial.%d'%k)).read_text())
                 for k in (3,4) if (root/('.audit-fast-partial.%d'%k)).exists()}
        if unique:
            assert all(r['status']=='renamed' for r in rows)
            assert outputs=={str(k):[25,[[k,'control-'+str(k)]]] for k in (3,4)}
        else:
            assert sorted(r['status'] for r in rows)==['FileNotFoundError','renamed']
        results[name]=dict(workers=rows,final_payloads=outputs)
    receipt=dict(status='PASS_DETERMINISTIC_SHARED_TEMP_RACE_AND_UNIQUE_TEMP_REPAIR_CONTROL',
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        control_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        old_preimage=OLD,new_preimage=NEW,results=results,
        scope='A reproducible legal two-worker interleaving proves the inherited race and repaired transport. The original failing run discarded child stderr, so this does not identify its lost exception. All audit predicates and exact-once merge checks are unchanged.')
    (out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__=='__main__':main()
