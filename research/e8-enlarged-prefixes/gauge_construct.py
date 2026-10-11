"""Raise selected read-only pivot entrances and relocate their literal shears.

Exact finite construction; source hashes, all raw columns, retained totals,
nested paths and chronological omission premise are checked independently.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy,hashlib,importlib.util,json,sys
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'e8-shared-donor-chains'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
F=module('immutable_frames',SOURCE/'frames/reconstruct.py')
ns={};rawop=ROOT.parent/'e8-response-resynth-bank64/vendor402/cxop.py'
exec(compile(rawop.read_text().split('\na, ta = op(')[0],str(rawop),'exec'),ns)
op=ns['op']
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source,out=map(Path,sys.argv[1:3]);assert not out.exists()
    witness=read(ROOT/'GAUGE-SELECTION.json');expected=read(ROOT/'GAUGE-EXPECTED.json')
    assert digest(source)==expected['source_sha256']
    base=read(source);c=copy.deepcopy(base)
    nmain=len(read(SOURCE/'inputs/candidate781.json')['A'])
    head=base['A'][:-nmain];targets={g[2] for g in head}
    removed=set();insertions={};ext=dict(base['ext']);selected=set()
    for plan in witness:
        pivot=plan['pivot'];assert pivot in ext and pivot not in targets and pivot not in selected
        selected.add(pivot)
        indices=[i for i,g in enumerate(head) if any(p==pivot for p,a,b in g[3])]
        assert indices==plan['removed'] and indices
        assert all(len(head[i][3])==1 and head[i][3][0][0]==pivot for i in indices)
        old=base['frames'][ext[pivot]];E=plan['best']['basis']
        assert F.inside(old,E) and len(E)>len(old)
        frame=next((i for i,b in enumerate(c['frames']) if b==E),len(c['frames']))
        if frame==len(c['frames']):c['frames'].append(E)
        ext[pivot]=frame;c['start'][pivot]=frame
        remaining=[i for i in range(len(head)) if i not in set(indices)]
        cut=plan['best']['cut'];anchor=remaining[cut] if cut<len(remaining) else len(head)
        assert anchor==plan['anchor']
        for i in indices:
            gate=copy.deepcopy(head[i]);gate[1]=frame
            insertions.setdefault(anchor,[]).append(gate)
        removed.update(indices)
    prefix=[]
    for i in range(len(head)+1):
        prefix.extend(insertions.get(i,[]))
        if i<len(head) and i not in removed:prefix.append(head[i])
    c['A']=prefix+base['A'][-nmain:];c['ext']=sorted([p,f] for p,f in ext.items())
    assert len(prefix)==len(head) and c['B']==base['B']
    visits=F.rehist_and_audit(c)
    before,btot=op(base);after,atot=op(c)
    assert before==after and btot==atot
    assert all(not after[t].get(p,Q(0)) for p in ext for t in range(c['v'],2*c['v']))
    written=set()
    for gate in prefix:
        assert gate[0]=='in'
        for p,a,b in gate[3]:assert p not in written
        written.add(gate[2])
    delta=F.histogram(c);delta.subtract(F.histogram(base));delta={k:v for k,v in delta.items() if v}
    assert delta=={int(k):v for k,v in expected['delta'].items()}
    assert sum(k*v for k,v in delta.items())==-sum(len(c['frames'][ext[p]])-len(base['frames'][dict(base['ext'])[p]]) for p in selected)
    controls=[]
    for pivot in selected:
        bad=copy.deepcopy(c)
        i=next(i for i,g in enumerate(prefix) if g[3][0][0]==pivot)
        bad['A'][i][1]=dict(base['ext'])[pivot]
        try:F.rehist_and_audit(bad)
        except AssertionError:controls.append('old-frame-after-raised-start-'+str(pivot))
        else:raise AssertionError('invalid old entrance frame accepted')
    bad=copy.deepcopy(c);i=next(i for i,g in enumerate(prefix) if g[3][0][0] in selected)
    bad['A'][i][3][0][1]*=-1
    wrong,wrongtot=op(bad);assert wrong!=before or wrongtot!=btot
    controls.append('flip-one-relocated-shear')
    raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode()
    assert hashlib.sha256(raw).hexdigest()==expected['candidate_sha256']
    out.mkdir(parents=True);(out/'candidate.json').write_bytes(raw)
    result=dict(status='PASS_EXACT_ENLARGED_ENTRANCES_COLUMNS_TOTALS_NESTED_PATHS',candidate_sha256=hashlib.sha256(raw).hexdigest(),source_sha256=digest(source),gauges=len(ext),enlarged_pivots=sorted(selected),entrance_gates=len(prefix),transitions=visits,local_delta=delta,ordered_sources_read_before_write=True,controls_rejected=controls,scope='Exact finite raw algebra and paid paths. Scalar charts, phase, global assembly, invoice and analytic interfaces require separate verification.')
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
