"""Reproduce the four whole-helper placements without running a packing search."""
from collections import Counter, defaultdict
from pathlib import Path
import gzip
import hashlib
import json

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

P = Path(__file__).resolve().parent
BASE = 'research/complex-t16-rare-pattern-exchanges'


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(b):
    return hashlib.sha256(b).hexdigest()


def derive(main):
    baseline = main/BASE
    old = json.loads(gzip.decompress((baseline/'data/OWNERS.json.gz').read_bytes()))
    plan = json.loads((baseline/'data/PLAN.json').read_text())
    spec = json.loads((baseline/'data/SPEC.json').read_text())
    rows = [r.copy() for r in old]
    moves = json.loads((P/'MOVES.json').read_text())
    assert len(moves) == 4
    for move in moves:
        i = move['index']
        assert rows[i] == move['before']
        after = move['after']
        assert all(rows[i][k] == after[k] for k in ('stage','replica','time','helper','width'))
        rows[i] = after.copy()
    assert [i for i,(a,b) in enumerate(zip(old,rows)) if a!=b] == [2010,4474,34306,46308]

    def idle(roles):
        bins = defaultdict(set)
        families = defaultdict(set)
        for r in roles:
            call = (r['stage'],r['replica'])
            assert r['family'] not in families[call]
            families[call].add(r['family'])
            assert r['copy'] == 112*r['owner_replica']+r['port']
            cap,window = plan['windows'][f"{r['owner_replica']},{r['child']}"]
            assert r['time'] in window and r['offset']>=0 and r['offset']+r['width']<=cap
            key = (r['owner_replica'],r['child'],r['port'])
            cells = set(range(r['offset'],r['offset']+r['width']))
            assert not bins[key]&cells
            bins[key].update(cells)
        result = Counter()
        for key,(cap,_) in plan['windows'].items():
            owner,child = map(int,key.split(','))
            for port in range(112):
                used=bins[owner,child,port]
                assert used==set(range(len(used)))
                if len(used)<cap:result[cap-len(used)]+=1
        return result

    before,after = idle(old),idle(rows)
    assert before == Counter({1:2276,3:377,7:7,48:4866})
    assert after == Counter({1:2275,3:375,7:8,48:4866})
    profile = Counter({int(k):v for k,v in plan['profile'].items()})
    profile.subtract(before); profile.update(after)
    assert all(v>0 for v in profile.values())
    assert sum(r*n for r,n in profile.items()) == 1041408
    # Container bytes are immutable inputs. Regeneration checks the full payload,
    # then binds PLAN/SPEC to this committed container, independent of zlib version.
    container = (P/'data/OWNERS.json.gz').read_bytes()
    assert json.loads(gzip.decompress(container)) == rows
    profile = {str(k):v for k,v in sorted(profile.items())}
    plan.update(profile=profile,assignment_sha256=digest(container),assignment_content_sha256=digest(canonical(rows)))
    plan['replica_lift']['owners_file_sha256'] = digest(container)
    plan_bytes = (json.dumps(plan,indent=2)+'\n').encode()
    target = json.loads((P/'CANDIDATE.json').read_text())
    spec['data'] = dict(owners_sha256=digest(container),plan_sha256=digest(plan_bytes))
    spec['expected'].update(target['expected_updates'])
    assert spec['expected']['global_profile'] == profile
    assert spec['expected']['idle_remainder_profile'] == {str(k):v for k,v in sorted(after.items())}
    assert spec['expected']['cross_replica_helper_roles'] == sum(r['replica']!=r['owner_replica'] for r in rows)
    return container,plan_bytes,(json.dumps(spec,indent=2)+'\n').encode()


if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main',type=Path,default=P.parents[1])
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    blobs=derive(args.main.resolve())
    args.out.mkdir(parents=True,exist_ok=False)
    for name,blob in zip(('OWNERS.json.gz','PLAN.json','SPEC.json'),blobs):
        (args.out/name).write_bytes(blob)
    print('PASS_FOUR_HELPER_DATA_RECONSTRUCTION')
