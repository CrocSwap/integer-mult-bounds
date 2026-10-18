"""Construct 18 disjoint target-prefix shears with exact dirty signed identity.
All frames inherited. Original helper frame visits are retained, even if empty.
The old-response K is inherited from the explicitly unchanged far-source map.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import gzip,json,copy,hashlib,sys,os
sys.dont_write_bytecode=True
BASE=Path(os.environ.get('OUTPUT_SHEAR_BASE',str(Path(__file__).resolve().parent.parent/'public/378/source/research/e8-complex-far-retiming')))
sys.path.insert(0,str(BASE/'code'))
from cxkernel import rehist
from importlib.util import spec_from_file_location,module_from_spec

def signed_rows(c):
    v,R=c['v'],c['R'];n=2*v+R;row=[{r:Q(1)} for r in range(n)]
    def add(a,b,q):
        for k,z in list(row[b].items()):
            z=row[a].get(k,Q(0))+q*z
            if z:row[a][k]=z
            else:row[a].pop(k,None)
    def phase(gs):
        for g in gs:
            for r,a,b in g[3]:add(r if g[0]=='out' else g[2],g[2] if g[0]=='out' else r,Q(a,b))
    phase(c['A'])
    for t,sc in enumerate(c['scat']['table']):
        for k,a,b in sc:add(v+t,c['ret'][k][1],Q(a,b))
    phase(c['B']);return row

def transform(c,selection):
    v,R=c['v'],c['R'];n=2*v+R;nA=len(c['A']);d=copy.deepcopy(c)
    assert (nA,len(c['B']),len(c['frames']))==(775,1226,948)
    flat=[];version=[0]*n
    for gi,g in enumerate(c['A']+c['B']):
        for r,a,b in g[3]:
            t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
            assert not(v<=s<2*v), 'Original targets must not be read'
            flat.append((gi,t,s,g[1],version[s],Q(a,b)));version[t]+=1
    used=set();destcuts={};addat=defaultdict(list);setups=[]
    for entry in selection:
        i,j,cut,E=(entry[k] for k in ('destination','donor_target','cut_group','recovery_frame'))
        assert not({i,j}&used) and i!=j and v<=i,j<2*v;used|={i,j}
        assert c['start'][i]==c['start'][j]==0
        destcuts[i]=cut;setups.append(['in',0,i,[[j,-1,1]]])
        rows={}
        for gi,t,s,f,ve,q in flat:
            if gi<nA or gi>cut or t!=i:continue
            key=s,ve,f
            if key not in rows:rows[key]=[Q(0),gi]
            rows[key][0]+=q
        jprefix=[]
        for gi,t,s,f,ve,q in flat:
            if gi<nA or gi>cut or t!=j:continue
            jprefix.append((gi,t,s,f,ve,q));key=s,ve,f
            if key not in rows:rows[key]=[Q(0),gi]
            rows[key][0]-=q
        assert len(jprefix)>=entry['prefix_target_deliveries'] and jprefix[-1][0]==cut and jprefix[-1][3]==E
        for (s,ve,f),(q,gi) in rows.items():
            if not q:continue
            # Unit-numerator expansion preserves the existing literal coeff compiler.
            assert q.denominator in (1,2,3,6)
            for _ in range(abs(q.numerator)):
                addat[gi].append(['in',f,i,[[s,1 if q>0 else -1,q.denominator]]])
        addat[cut].append(['in',E,i,[[j,1,1]]])
    B=list(setups)
    for bi,g in enumerate(c['B']):
        gi=nA+bi;g=copy.deepcopy(g)
        if g[0]=='out':
            g[3]=[z for z in g[3] if z[0] not in destcuts or gi>destcuts[z[0]]]
            B.append(g) # Retain the helper/source visit even when output terms vanish.
        elif g[2] in destcuts and gi<=destcuts[g[2]]:
            B.extend(['out',g[1],s,[],[]] for s,_,_ in g[3])
        else:B.append(g)
        B.extend(addat.get(gi,[]))
    d['B']=B;d['derived_from']=c['derived_from']+' | '+str(len(selection))+' exact disjoint target-prefix output shears'
    return rehist(d)

if __name__=='__main__':
    src=BASE/'data/gcert1-e8-r783-far.json.gz';raw=src.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='f2664ee7bcdfb55893abe9f1be8ee6a394a602e8262e611de2a0328bbd508aa7'
    sel=Path(os.environ.get('OUTPUT_SHEAR_SELECTION',str(Path(__file__).with_name('bit-complex-output-shear-selection.json'))))
    assert hashlib.sha256(sel.read_bytes()).hexdigest()=='cd29140b26eac395788c811e05be3ad68e831b34c5631798afd3d14ebedf4cce'
    selection=json.loads(sel.read_text());assert len(selection)==18;c=json.loads(gzip.decompress(raw));d=transform(c,selection)
    original_rows=signed_rows(c)
    assert original_rows==signed_rows(d),'Exact complete arbitrary-dirt rational scalar map mismatch'
    ablated=transform(c,[])
    assert ablated['A']==c['A'] and ablated['B']==c['B'] and ablated['blocks']==c['blocks']
    controls=[]
    bad=copy.deepcopy(d);bad['B'].pop(0)
    assert signed_rows(bad)!=original_rows;controls.append('first setup omitted changes independent target column')
    bad=copy.deepcopy(d);first=selection[0];at=next(k for k,g in enumerate(bad['B']) if g[0]=='in' and g[2]==first['destination'] and g[3]==[[first['donor_target'],1,1]])
    bad['B'].pop(at);assert signed_rows(bad)!=original_rows;controls.append('first restoration omitted changes complete signed map')
    wrong=copy.deepcopy(selection);wrong[1]['destination']=wrong[0]['destination']
    try:transform(c,wrong)
    except AssertionError:controls.append('overlapping target pairs rejected')
    else:raise AssertionError('overlapping pair witness accepted')
    def hist(c):
        H=Counter()
        for b in c['blocks'].values():H.update({int(k):n for k,n in b.items()})
        return H
    a,b=hist(c),hist(d);delta={r:b[r]-a[r] for r in a.keys()|b.keys() if a[r]!=b[r]}
    assert delta=={1:-5,2:-5,3:-4,4:-6,6:-9,7:15},delta
    data=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    (out/'gcert1-e8-r783-output-shear-pack.json').write_bytes(data)
    (out/'gcert1-e8-r783-output-shear-pack.json.gz').write_bytes(gzip.compress(data,mtime=0))
    result={'status':'PASS_18_DISJOINT_PREFIX_SHEARS_EXACT_SIGNED_DIRTY_MATRIX_AND_CHARGED_CHILD_PROFILE','source_gzip_sha256':hashlib.sha256(raw).hexdigest(),'candidate_json_sha256':hashlib.sha256(data).hexdigest(),'selection_sha256':hashlib.sha256(sel.read_bytes()).hexdigest(),'ablation':'All shears disabled: identical original A/B gates and actual child histogram; exact map unchanged','negative_controls':controls,'pairs':len(selection),'target_roles':2*len(selection),'all_live_columns':1023,'dirty_helper_columns':783,'local_histogram_delta':delta,'rank_mass_delta':0,'frames':len(d['frames']),'A':len(d['A']),'B':len(d['B']),'construction':'Every disjoint pair subtracts its donor target at ZERO before B; actual source/write-version/frame tokens synthesize exact prefix difference; restoration follows the last donor-prefix read at the inherited common frame. Removed input gates retain all original helper visits.','old_response':'The exact full signed scalar map equals the original far source, so its explicit original K and helper cleanup are unchanged. New Yâ†’Y main primitives require the separately audited compiler extension.','kappa_claimed':False}
    (out/'WITNESS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))


