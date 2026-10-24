"""Read-only, source-bound mapping of final4610 helper phases to reviewed4470."""
import gzip, hashlib, json, pathlib, subprocess, time
from . import source
PINS={}
def read(p):
    raw=source.raw(p);PINS[p]=source.digest(raw)
    return json.loads(gzip.decompress(raw) if p.endswith('.gz') else raw)
def span(b):
    s={0}
    for x in b: s|={y^x for y in list(s)}
    assert len(s)==1<<len(b)
    return frozenset(s)
def pair(c,r): return tuple(tuple(c['frames'][c[k][r]]) for k in ('start','final'))
def run():
    t0=time.monotonic()
    c=read('research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    p=read('research/fresh-helper-boundary/CHANGES.json')
    for key,field in [('entrances','start'),('exits','final')]:
        for role,old,new in p[key]:
            assert c[field][role]==old
            c[field][role]=new
    c['frames'].append(read('research/missing-join-frame/PATCH.json')['new_basis'])
    p=read('research/joint-helper-lattice/PATCH.json')
    labels={span(b):i for i,b in enumerate(c['frames'])}
    for move in p['changes']:
        s=span(move['new'])
        if s not in labels:labels[s]=len(c['frames']);c['frames'].append(move['new'])
        i=labels[s]
        if move['phase'] in ('entrance','exit'):
            field='start' if move['phase']=='entrance' else 'final';r=move['ordinal']
            assert span(c['frames'][c[field][r]])==span(move['old'])
            c[field][r]=i
    native=read('research/joint-helper-lattice/NATIVE.json.gz')
    reviewed=read('docs/research/pr-intake-evidence/pr4470/REVIEWED-SOURCES.json')['files']
    manifest=read('certificates/frontier4470-source.json')['files']
    for p,h in PINS.copy().items():
        if p in reviewed:assert reviewed[p]==h
        if p in manifest:assert manifest[p]==h
    native_path='research/joint-helper-lattice/NATIVE.json.gz'
    assert reviewed[native_path]==PINS[native_path]==manifest[native_path]
    oldrecipes={(tuple(c['frames'][e['old']]),tuple(c['frames'][e['new']])):e for e in native['new_physical_edges_and_boundaries']}
    new=read('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')['canonical']
    ph=read('research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz')
    changed={r:h for h in ph['changed_helper_boundaries'] for r in h['helpers']}
    rows=[]
    for r in range(224,632):
        a,b=pair(new,r)
        assert span(a)<span(b)
        if (a,b)==pair(c,r):
            e=oldrecipes[a,b]
            assert e['rank']==len(b)-len(a)
            assert set(e['recipes'])=={'forward','backward'}
            rows.append(dict(role=r,source='reviewed4470',old=e['old'],new=e['new'],rank=e['rank']))
        else:
            e=changed[r]
            assert tuple(new['frames'][e['input']])==a and tuple(new['frames'][e['output']])==b
            assert e['rank']==len(b)-len(a)
            rows.append(dict(role=r,source='changed4610',old=e['input'],new=e['output'],rank=e['rank']))
    assert sum(x['source']=='reviewed4470' for x in rows)==382
    assert sum(x['source']=='changed4610' for x in rows)==26
    out=dict(status='PASS_EXACT_HELPER_PHASE_LINEAGE_MAP',base='ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c',scope='Exact ordered basis and field identity comparison plus authenticated prior receipt reuse; no phase theorem rerun.',unchanged_reviewed_helpers=382,changed_helpers=26,all_helpers=408,unchanged_distinct_pairs=len({pair(new,r) for r in range(224,632) if r not in changed}),rows=rows,source_sha256=PINS,seconds=time.monotonic()-t0)
    return out
