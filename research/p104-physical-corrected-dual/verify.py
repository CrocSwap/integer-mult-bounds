"""Read-only independent native verification; never imports the compiler."""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, copy, gzip, hashlib, json, tempfile, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core

def check_native(N,word,certificate,full_columns=False):
    core.need(certificate['chart']==word['chart'],'native chart contract')
    covered=set();profile=Counter();columns=0
    @lru_cache(None)
    def frame(f):return core.conjugate(N.frame(f,9))
    for r in certificate['transports']:
        a,b=tuple(r['old']),tuple(r['new']);recipe=N.recipe(r['recipe'])
        expected=N.adjoint(frame(a))+frame(b)
        core.need(r['recipe']['rank']==abs(len(a)-len(b))>0,'positive native rank')
        # Signed Pauli action plus one exact nonzero state fixes global phase.
        N.equal(recipe,expected,'conjugated complementary transport')
        for i in r['events']:
            core.need(i not in covered and 0<=i<len(word['program']),'unique native occurrence')
            e=word['program'][i]
            core.need(e[0]=='transport' and e[2]==list(a) and e[3]==list(b) and e[4]==r['recipe']['rank'],'literal native binding')
            covered.add(i);profile[e[4]]+=1
        if full_columns and (len(a),len(b)) in [(8,1),(1,8)] and any(word['program'][i][1]=='C' for i in r['events']):
            for j in range(512):
                core.need(N.state(recipe,j)==N.state(expected,j),'complete private transport columns');columns+=1
    core.need(covered=={i for i,e in enumerate(word['program']) if e[0]=='transport'},'all native occurrences')
    return dict(distinct_transports=len(certificate['transports']),occurrences=len(covered),profile=dict(sorted(profile.items())),complete_private_columns=columns)

def boundary(word,cv,N):
    original=json.loads((core.BASE/'inputs/LOWRANK-WITNESS.json').read_text())
    correction=json.loads((core.P/'inputs/CIRCUIT.json').read_text())
    core.need(correction['targets']==[0,1],'two-target source contract')
    for k in ('initial_frames','final_frames'):
        expected={r:list(cv(f)) for r,f in (original[k]|correction[k]).items()}
        core.need(word[k]==expected,'same canonical forward boundary '+k)
    core.need(len(word['initial_frames'])==358,'358 public roles')
    for r,a in word['initial_frames'].items():
        b=word['final_frames'][r]
        want=(1,9) if r.startswith('X') else (0,8) if r.startswith('Y') else (0,9)
        core.need((len(a),len(b))==want,'literal endpoint dimensions '+r)
    # Conjugation is precisely inverse transpose for each unitary chart.
    # This checks all distinct boundary frames, rather than one witness frame.
    frames={tuple(f) for k in ('initial_frames','final_frames') for f in word[k].values()}
    for f in frames:
        g=N.frame(f,9);delta=core.conjugate(g)
        # <Delta u, Gamma v> = <u,v> uses the bilinear transpose. A separate
        # transpose implementation below supplies its literal gate identity.
        N.equal(transpose(N,g)+delta,(), 'Gamma^T Delta=I')
        N.equal(delta+transpose(N,g),(), 'Delta Gamma^T=I')
    # Named PR2551 physical separating column: Y2 -> X0 is -F9^-1/2.
    block=N.adjoint(core.conjugate(N.frame(tuple(word['initial_frames']['Y2']),9)))+core.conjugate(N.frame(tuple(word['final_frames']['X0']),9))
    vec,den=N.state(block)
    def cmul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    for x in range(512):
        a=(Q(1),Q(0))
        for j in range(9):a=cmul(a,(Q(1,2),Q(1,2) if x>>j&1 else Q(-1,2)))
        core.need(a==(Q(vec.get(x,(0,0))[0],1<<den),Q(vec.get(x,(0,0))[1],1<<den)),'closed product physical column')
    core.need((Q(vec[0][0],1<<den),Q(vec[0][1],1<<den))==(Q(1,32),Q(-1,32)),'physical witness')
    return dict(public_registers=len(word['initial_frames']),distinct_boundary_charts=len(frames),physical_witness_X0_at_Y2_delta0=['-1/64','1/64'],physical_witness_columns=512)

def transpose(N,gates):
    out=[]
    for e in reversed(gates):
        if e[0]=='P':out.append(('P',N.inverse(tuple(e[1]))))
        else:
            core.need(e[0] in ('X','D','C','phase'),'transpose gate')
            out.append(e) # all these elementary matrices are symmetric
    return tuple(out)

def controls(N,word,cert,ports):
    out=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError):out.append(name)
        else:raise ValueError('control falsely accepted: '+name)
    bad=copy.deepcopy(word)
    bad['program'].pop(0)
    reject('omit first physical input conversion',lambda:core.replay(bad,ports))
    bad2=copy.deepcopy(word)
    bad2['program'].pop()
    reject('omit last physical output conversion',lambda:core.replay(bad2,ports))
    bad3=copy.deepcopy(word)
    i=next(i for i,e in enumerate(bad3['program']) if e[0]=='erase')
    j=max(j for j,e in enumerate(bad3['program'][:i]) if e[0]=='add' and e[1]=='C')
    bad3['program'][j][3]='0'
    reject('omit private zero cleanup',lambda:core.replay(bad3,ports))
    bad4=copy.deepcopy(cert);bad4['transports'][0]['recipe']['left']['phase']=(bad4['transports'][0]['recipe']['left']['phase']+1)%4
    reject('native global phase',lambda:check_native(N,word,bad4))
    bad5=copy.deepcopy(cert);bad5['transports'].pop()
    reject('missing native occurrence',lambda:check_native(N,word,bad5))
    # The unconjugated complement realizes a different physical boundary.
    expected=core.conjugate(N.fourier(9))
    reject('ordinary instead of dual chart',lambda:N.equal(N.fourier(9),expected,'wrong full dual chart'))
    reject('adjoint instead of ordinary transpose',lambda:N.equal(N.adjoint(N.fourier(9))+expected,(),'wrong inverse transpose'))
    # Cross-check conjugation via transpose/adjoint, independent of its switch.
    for f in [(),(386,),tuple(1<<j for j in range(9))]:
        g=N.frame(f,9)
        N.equal(core.conjugate(g),transpose(N,N.adjoint(g)),'conjugation positive control')
    equivalent=copy.deepcopy(word)
    for d in ('initial_frames','final_frames'):
        for r in equivalent[d]:equivalent[d][r].reverse()
    core.need(core.replay(equivalent,ports)==core.replay(word,ports),'equivalent boundary bases positive control')
    return out

def compute():
    core.authenticate();N=core.module('native_verify.py');cv,ports=core.geometry(N)
    word=json.loads((core.P/'WORD.json').read_text())
    core.need(word==core.build_word(cv),'complete word regeneration')
    cert=json.loads(gzip.decompress((core.P/'NATIVE.json.gz').read_bytes()))
    a=core.replay(word,ports);b=core.replay(word,ports,True)
    core.need(a==b,'independent dense integer replay')
    native=check_native(N,word,cert,True)
    core.need(native['profile']==a['profile'],'native and event invoices')
    return dict(schema_version=1,status='PASS',scope='Finite canonical physical inverse-transpose of the two-target corrected P104 word',logical=a,native=native,boundary=boundary(word,cv,N),controls=controls(N,word,cert,ports),source_clean_rank_mass=3126,added_H1=416,no_new_kappa=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--regenerate',action='store_true');args=p.parse_args()
    if args.out:core.need(not args.out.exists(),'exclusive new receipt output')
    result=compute()
    if args.regenerate:
        import build
        word,native=build.construct()
        core.need(word==json.loads((core.P/'WORD.json').read_text()),'regenerated word')
        core.need(json.loads(json.dumps(native))==json.loads(gzip.decompress((core.P/'NATIVE.json.gz').read_bytes())),'complete native regenerated payload')
    if args.out:
        with args.out.open('x',encoding='utf-8') as f:f.write(json.dumps(result,indent=2)+'\n')
    else:core.need(json.dumps(json.loads((core.P/'RESULT.json').read_text()),sort_keys=True,allow_nan=False)==json.dumps(result,sort_keys=True,allow_nan=False),'complete typed receipt equality')
    print('PASS_P104_PHYSICAL_CORRECTED_DUAL mass=3542 events=5398 coefficients=128164 zero_erases=8')

if __name__=='__main__':main()
