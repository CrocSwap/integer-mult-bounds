#!/usr/bin/env python3
"""Single fixed #7624 splice: authenticated changed-route physical oracle.

Adapts DreamingOfClouds' #7617 check.py exact 9-bit Gaussian circuit tools.
Only a bounded differential route check; full native/width/service is separate.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

SOURCE_GZIP = 'bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
SOURCE_CANON = 'c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
SOURCE_BLOB = '81725205c5200d0cf34f9f2debef49d75273e4af'
ORACLE_SHA = '1def99322544e6205c37590d42c6f52d561d16dd05170d9a720793e43095a48c'
PATCH = {
38369: (['MOVE',902,3,618,False], ['MOVE',902,3,373,False]),
38623: (['MOVE',1091,373,618,False], None),
40279: (['ADD',1091,902,'1/2',618], ['ADD',1091,902,'1/2',373]),
40280: (['MOVE',1091,618,733,False], ['MOVE',1091,373,733,False]),
41663: (['MOVE',902,618,913,False], ['MOVE',902,373,913,False]),
}


def need(cond, msg):
    if not cond: raise ValueError(msg)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def sha(b): return hashlib.sha256(b).hexdigest()


def readgz(path):
    data = path.read_bytes()
    return data, json.loads(gzip.decompress(data))


def write(out, name, value):
    (out/name).write_bytes(canonical(value)+b'\n')


def load_oracle(path):
    raw = path.read_bytes()
    need(sha(raw) == ORACLE_SHA, 'authenticated #7617 oracle hash')
    # The retained script validates argv at import; its main guard is not run.
    saved = sys.argv
    try:
        sys.argv = [str(path), 'columns']
        spec = importlib.util.spec_from_file_location('p7617_physical_oracle',path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def routes(word, roles=None):
    by = collections.defaultdict(list)
    for event in word['program']:
        if event[0] == 'MOVE' and (roles is None or event[1] in roles):
            by[event[1]].append(tuple(event[2:4]))
    return dict(by)


def census(word):
    public = collections.Counter(); owned = collections.Counter()
    for event in word['program']:
        if event[0] == 'MOVE':
            (owned if event[4] else public)[tuple(event[2:4])] += 1
    return public, owned


def format_counts(c):
    return [{'from':a,'to':b,'occurrences':v} for (a,b),v in sorted(c.items())]


def require_source(gz, word):
    need(sha(gz)==SOURCE_GZIP and sha(canonical(word))==SOURCE_CANON, 'original word hash')
    need(hashlib.sha1(b'blob '+str(len(gz)).encode()+b'\0'+gz).hexdigest()==SOURCE_BLOB, 'original git blob')

def require_routes(pairs):
    need(pairs and {(3,618),(3,373),(373,618),(618,733),(373,733),(618,913),(373,913)} <= set(pairs), 'missing paid changed route')

def require_nested(O, frames, a, b):
    need(0 <= a < len(frames) and 0 <= b < len(frames), 'chart pair range')
    need(O.span(frames[a]) < O.span(frames[b]), 'public chart pair not strictly ascending')


def reject(label, fun):
    try: fun()
    except (ValueError, AssertionError): return {'name':label,'rejected':True}
    raise ValueError('control accepted: '+label)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--built',type=Path,required=True); p.add_argument('--exact',type=Path,required=True); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    status={'status':'INCOMPLETE','stage':'authenticate','completed_pairs':[]}
    def progress(): write(a.out,'status.json',status)
    progress(); start=time.monotonic()
    try:
        need(not sys.flags.optimize, 'physical oracle requires assertions enabled')
        gz, B = readgz(a.root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz')
        require_source(gz,B)
        need(B['public']==1501 and B['owned_fields']==68, '204-lifetime source header')
        candidate_gz, W = readgz(a.built/'candidate-word.json.gz')
        manifest = json.loads((a.built/'edit-manifest.json').read_text())
        need(manifest['schema'] == 'compose7624-edit-manifest/v1', 'edit manifest schema')
        need(manifest['source_canonical_sha256']==SOURCE_CANON and manifest['source_gzip_sha256']==SOURCE_GZIP and manifest['source_git_blob']==SOURCE_BLOB, 'manifest source pins')
        need(manifest['candidate_canonical_sha256']==sha(canonical(W)) and manifest['candidate_gzip_sha256']==sha(candidate_gz), 'manifest candidate pins')
        need(json.loads((a.built/'status.json').read_text())['status']=='CANDIDATE_BUILT_UNQUALIFIED', 'build status')
        need(len(B['program']) == 77372 and len(W['program']) == 77371, 'event counts')
        need(all(B[k]==W[k] for k in B if k!='program') and set(B)==set(W), 'header mismatch')
        rebuilt=[]
        for i,e in enumerate(B['program']):
            if i in PATCH:
                old,new=PATCH[i]; need(e==old,'original edit literal '+str(i))
                if new is not None: rebuilt.append(new)
            else: rebuilt.append(e)
        need(rebuilt==W['program'], 'candidate is not exact fixed splice')
        exact_bytes=(a.exact/'EXACT.json.gz').read_bytes()
        exact_status=json.loads((a.exact/'status.json').read_text())
        need(exact_status['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and sha(exact_bytes)==exact_status['exact_gzip_sha256'], 'exact receipt')
        raw_exact=gzip.decompress(exact_bytes); need(sha(raw_exact)==exact_status['exact_sha256'], 'exact content')
        X=json.loads(raw_exact); src=X['source']
        need(X['schema']=='compose7624-exact/v1' and src['original_canonical_sha256']==SOURCE_CANON and src['original_gzip_sha256']==SOURCE_GZIP and src['candidate_canonical_sha256']==sha(canonical(W)) and src['candidate_gzip_sha256']==sha(candidate_gz) and src['manifest_sha256']==sha((a.built/'edit-manifest.json').read_bytes()), 'exact source/candidate binding')
        need(X['census']['original']['lifetimes']==X['census']['candidate']['lifetimes']==204, '204 lifetimes')
        O=load_oracle(a.root.parent/'kappa-research-20261115b/inputs/pr7617/check.py')
        controls=[reject('corrupted_oracle_hash',lambda: need(sha((a.root.parent/'kappa-research-20261115b/inputs/pr7617/check.py').read_bytes()+b'!')==ORACLE_SHA,'hash'))]
        old_routes=routes(B,{902,1091}); new_routes=routes(W,{902,1091})
        need(set(old_routes)=={902,1091} and set(new_routes)=={902,1091},'changed roles absent')
        old_all=routes(B); new_all=routes(W)
        need(all(old_all.get(r)==new_all.get(r) for r in set(old_all)|set(new_all) if r not in (902,1091)), 'other MOVE route changed')
        old_pub,old_owned=census(B); new_pub,new_owned=census(W)
        need(old_owned==new_owned,'owned MOVE census changed')
        pairs=sorted({pair for route in old_routes.values() for pair in route} | {pair for route in new_routes.values() for pair in route})
        frames=B['frames']; need(all(x not in (None,) for x in pairs),'invalid pair')
        need(pairs and all(old_routes.values()) and all(new_routes.values()), 'empty changed route inventory')
        require_routes(pairs)
        need({str(k):[list(x) for x in v] for k,v in old_all.items()}==X['original']['routes'] and {str(k):[list(x) for x in v] for k,v in new_all.items()}==X['candidate']['routes'], 'exact current-frame route replay mismatch')
        controls.append(reject('missing_paid_route',lambda: require_routes(set(pairs)-{(3,373)})))
        controls.append(reject('wrong_source_pin',lambda: require_source(gz+b'!',B)))
        for x,y in pairs: require_nested(O,frames,x,y)
        # Fresh negative controls: geometry, a shifted offset and an unobservable
        # to Pauli action but observable absolute phase error.
        controls.append(reject('nonnested_719_128',lambda: require_nested(O,frames,719,128)))
        pair = (3,373)
        need(pair in pairs, 'expected new pair absent')
        def recipe():
            u,v=pair
            expected=O.dagger(O.frame_circuit(frames[u]))+O.frame_circuit(frames[v])
            return O.lower(O.frame_op(frames[u]).dag().then(O.frame_op(frames[v]))),expected
        def bad_offset():
            rec,expected=recipe(); rec['left']['offset'] ^= 1
            got=O.recipe_circuit(rec)
            need(O.tableau(got)==O.tableau(expected) and O.column(got,0)==O.column(expected,0),'offset corruption')
        controls.append(reject('offset_corruption',bad_offset))
        def bad_phase():
            rec,expected=recipe(); got=O.recipe_circuit(rec)+(('phase',2),)
            need(O.tableau(got)==O.tableau(expected),'global phase changed signed action')
            need(O.column(got,0)==O.column(expected,0),'global phase mismatch')
        controls.append(reject('global_phase_corruption',bad_phase))
        status.update(stage='changed_pair_columns', pair_count=len(pairs), completed_pairs=[],
                      source_sha256=SOURCE_CANON,candidate_sha256=sha(canonical(W)), controls=controls)
        progress()
        results=[]
        for x,y in pairs:
            t=time.monotonic()
            # This runs 18 signed Paulis, full 512 forward and 512 adjoint
            # exact Gaussian columns, and a wrong-global-phase control per pair.
            rank=O.pair_columns(frames,x,y,wrong_phase=True)
            need(rank==len(frames[y])-len(frames[x]), 'rank mismatch')
            results.append({'from':x,'to':y,'rank':rank,'forward_columns':512,'adjoint_columns':512,
                            'signed_paulis':18,'absolute_phase_checked':True,'wrong_phase_rejected':True,
                            'seconds':round(time.monotonic()-t,3)})
            status['completed_pairs']=[[r['from'],r['to']] for r in results]; progress()
        report={'status':'CHANGED_ROUTE_PHYSICAL_DIFFERENTIAL_PASS_UNQUALIFIED',
                'source_word_canonical_sha256':SOURCE_CANON,'candidate_word_canonical_sha256':sha(canonical(W)),
                'candidate_gzip_sha256':sha((a.built/'candidate-word.json.gz').read_bytes()),
                'adapted_oracle_sha256':ORACLE_SHA,'adapted_oracle':'#7617 check.py pair_columns and canonical frame compiler; DreamingOfClouds et al.',
                'old_routes':{str(k):v for k,v in old_routes.items()},'new_routes':{str(k):v for k,v in new_routes.items()},
                'changed_route_union':results,'route_pairs_tested':len(results),'forward_columns':len(results)*512,'adjoint_columns':len(results)*512,
                'current_public_pair_census':format_counts(old_pub),'candidate_public_pair_census':format_counts(new_pub),
                'current_owned_pair_census':format_counts(old_owned),'candidate_owned_pair_census':format_counts(new_owned),
                'current_public_distinct_pairs':len(old_pub),'candidate_public_distinct_pairs':len(new_pub),
                'controls':controls,'elapsed_seconds':round(time.monotonic()-start,3),
                'scope':'Only old and new pairs on roles 902/1091 tested; actual full pair census recorded, not fully revalidated. Canonical common-frame ADD covariance, spectator tensor extension and inherited all-width/all-column compiler assumptions remain premises. Reset/owned-erasure service is not proved. Native/signed/precision/tape/compiler/caller/prices remain unqualified.'}
        write(a.out,'PHYSICAL.json',report)
        status.update(status=report['status'],stage='complete',elapsed_seconds=report['elapsed_seconds']); progress()
        return 0
    except Exception as exc:
        status.update(status='REFUSED_OR_INCOMPLETE',error_type=type(exc).__name__,reason=str(exc),elapsed_seconds=round(time.monotonic()-start,3)); progress()
        return 1

if __name__=='__main__': sys.exit(main())
