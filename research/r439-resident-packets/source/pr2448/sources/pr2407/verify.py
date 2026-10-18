#!/usr/bin/env python3
"""Exact finite R439 single-copy interleaving witness, not an optimum proof.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Primary suffix/interleaving checks adapt Sricharan Vagvala's PR2356 method.
Sagar Thakrar PR2115 and Charles Bethin PR2279 supply the split model; see README.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
EXPORT = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
OWNER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
PROFILE = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inputs():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    result = {}
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        require(sha(raw) == pin['sha256'], 'source SHA256: '+pin['path'])
        require(hashlib.sha1(b'blob %d\0'%len(raw)+raw).hexdigest() == pin['git_blob'], 'source Git blob')
        result[pin['path']] = raw
    require(set(result) == {WORD,EXPORT,OWNER}, 'complete source inventory')
    return result


def decompose(w, witness):
    v = w['v']
    require((v,w['R'],len(w['ret'])) == (111,439,9), 'fixed source dimensions')
    target = lambda r: v <= r < 2*v
    yy = lambda g: target(g[1]) and all(target(s) for s in g[2])
    reads = [i for i,g in enumerate(w['D']) if target(g[1]) and all(s>=2*v for s in g[2])]
    lo,hi = min(reads),max(reads)
    prep = [g for g in w['D'][:lo] if yy(g)]
    positions = [i for i,g in enumerate(w['D']) if i>hi and yy(g)]
    undo = [w['D'][i] for i in positions]
    require(len(prep)==len(undo)==306 and prep==undo[::-1], 'literal inverse target basis')
    require(not any(yy(g) for g in w['D'][lo:hi+1]), 'target basis and helper reads separated')
    require(all(f==0 and len(ss)==1 and d!=ss[0] for f,d,ss in prep+undo), 'zero-frame elementary undo')
    # The original D also has a helper-only restoration tail after this block.
    # No intervening gate may observe a target while the undo is relocated.
    moved = set(positions)
    require(all(not target(g[1]) and not any(target(s) for s in g[2])
                for i,g in enumerate(w['D']) if i>=positions[0] and i not in moved), 'D tail isolates targets')
    require(all(not target(g[1]) and not any(target(s) for s in g[2]) for g in w['A']), 'A isolates targets')
    require(all(not target(q) for q in w['ret']), 'retained sources isolated from target undo')
    keep = witness['keep_undo_indices']
    require(witness['order']=='ideal303' and keep==[31,51,52], 'fixed three-gate split')
    require(type(witness['column']) is int and 0<=witness['column']<9, 'retained column')
    kept = [undo[i] for i in keep]
    rest = [g for i,g in enumerate(undo) if i not in keep]
    def operator(gates):
        rows = [1<<i for i in range(v)]
        for _,d,(s,) in gates:
            rows[d-v] ^= rows[s-v]
        return rows
    require(operator(undo)==operator(kept+rest), 'split changes complete target operator')
    require(all(len(row)==len(set(row)) and all(type(j) is int and 0<=j<9 for j in row)
                for row in w['scatter']), 'scatter support')
    S = [sum(1<<j for j in row) for row in w['scatter']]
    P = S.copy()
    for _,d,(s,) in prep+kept:
        P[d-v] ^= P[s-v]
    taps = witness['taps']
    require(len(taps)==len({tuple(t) for t in taps}), 'distinct tap locations')
    require(all(len(t)==2 and all(type(z) is int for z in t) and 0<=t[0]<=len(rest) and 0<=t[1]<v for t in taps), 'tap domain')
    require(witness.get('optimality_claim') is False, 'no optimality claim')
    # Backward columns of the fixed suffix, with exact binary coefficients.
    cols = [1<<i for i in range(v)]
    suffix = {len(rest):cols.copy()}
    for cut in reversed(range(len(rest))):
        _,d,(s,) = rest[cut]
        cols[s-v] ^= cols[d-v]
        suffix[cut] = cols.copy()
    j = witness['column']
    wanted = sum(1<<i for i,row in enumerate(S) if row>>j&1)
    actual = 0
    for cut,i in taps:
        actual ^= suffix[cut][i]
    require(actual==wanted, 'tap response differs from required column')
    d = copy.deepcopy(w)
    d['D'] = [g for i,g in enumerate(w['D']) if i not in moved]+kept
    d['B'] = rest+w['B']
    d['scatter'] = [[j for j in range(9) if row>>j&1] for row in P]
    return d,rest,P,{'undo_gates':len(undo),'deferred_gates':len(rest),'kept_gates':len(kept),
                     'baseline_column_taps':sum(row>>j&1 for row in P),'candidate_column_taps':len(taps),
                     'target_column_hex':f'{wanted:028x}'}


def export(w,data,path):
    path.mkdir()
    (path/'word.json').write_text(json.dumps(w))
    (path/'export.py').write_bytes(data[EXPORT])
    subprocess.run([sys.executable,'-I','-B',str(path/'export.py'),str(path/'word.json'),str(path/'out')],
                   check=True,capture_output=True,timeout=120)
    rec = list(struct.iter_unpack('<6i',(path/'out/249-records.bin').read_bytes()))
    frames = json.loads((path/'out/frames.json').read_text())['frames']
    return rec,frames


def interleave(base,w,rest,P,witness):
    v = w['v']; n = 2*v+w['R']; j = witness['column']
    start = next(i for i,r in enumerate(base) if r[0]==2)
    stop = max(i for i,r in enumerate(base) if r[0]==3)+1
    undo_records = [(1,d,ss[0],1,0,4) for _,d,ss in rest]
    require(base[stop:stop+len(rest)]==undo_records, 'deferred undo records at scatter exit')
    copies = {r[1]:r for r in base if r[0]==2}
    erases = {r[1]:r for r in base if r[0]==3}
    replacement = []
    for k,q in enumerate(w['ret']):
        if k==j:
            continue
        replacement.append(copies[q])
        replacement.extend((1,v+i,n,1,0,3) for i,row in enumerate(P) if row>>k&1)
        replacement.append(erases[q])
    q = w['ret'][j]
    replacement.append(copies[q])
    for cut in range(len(rest)+1):
        replacement.extend((1,v+i,n,1,0,3) for c,i in witness['taps'] if c==cut)
        if cut<len(rest):
            replacement.append(undo_records[cut])
    replacement.append(erases[q])
    return base[:start]+replacement+base[stop+len(rest):]


def boundary(records,w,reverse=False):
    v = w['v']; n = 2*v+w['R']
    rows = [1<<i for i in range(n)]+[0]
    live = None
    for op,a,b,c,frame,phase in (reversed(records) if reverse else records):
        if reverse and op in (2,3):
            op=5-op
        if op==0:
            continue
        if op==1:
            require(c==1 and 0<=a<n and 0<=b<=n and a!=b,'ADD domain')
            rows[a]^=rows[b]
        elif op==2:
            require(live is None and b==n and rows[b]==0,'COPY occupied slot')
            rows[b]=rows[a]; live=(a,b)
        elif op==3:
            require(live==(a,b) and rows[a]==rows[b],'ERASE snapshot changed')
            rows[b]=0;live=None
        else:
            raise ValueError('unknown opcode')
    expected = [(1<<i)^(1<<(i-v)) if v<=i<2*v else 1<<i for i in range(n)]
    require(live is None and rows[-1]==0,'unrestored private slot')
    require(rows[:-1]==expected,'all-input dirty boundary')


def invoice(records,w,frames):
    n=2*w['v']+w['R'];cur=w['start'].copy()+[0]
    dim={int(k):f['dim'] for k,f in frames.items()}
    labels=[set(f) for f in w['frames']]
    profile=Counter();live=None
    for op,a,b,c,f,phase in records:
        if op==0:
            require(a<n and cur[a]==b and labels[b]<labels[c] and f==dim[c]-dim[b],'MOVE frame path')
            cur[a]=c;profile[f]+=1
        elif op==1:
            require(cur[a]==cur[b]==f and c==1,'ADD frame access')
        elif op==2:
            require(live is None and b==n and cur[a]==c and f==0 and phase==dim[c],'COPY frame/lifetime')
            cur[b]=f;live=(a,b);profile[phase]+=1
        elif op==3:
            require(live==(a,b) and cur[a]==c and cur[b]==f==0 and phase==0,'ERASE frame/lifetime')
            live=None
        else:
            raise ValueError('invoice opcode')
    require(live is None and cur[:n]==w['final'],'final frame state')
    require(dict(profile)==PROFILE,'paid profile changed')
    bounds=[]
    for reverse in (False,True):
        mass=[1]*n+[0];peak=1
        for op,a,b,c,_,_ in (reversed(records) if reverse else records):
            if reverse and op in (2,3):op=5-op
            if op==1:
                mass[a]+=abs(c)*mass[b];peak=max(peak,mass[a])
            elif op==2:mass[b]=mass[a]
            elif op==3:mass[b]=0
        bounds.append(peak)
    F,B=bounds; local=64*F**3*B**2; nine=(1<<18)*F**5*B**4
    require(local<1<<104 and nine<1<<192,'inherited precision guard')
    count=Counter(r[0] for r in records)
    require(count[2]==count[3]==9,'nine COPY/ERASE pairs')
    return {'ADDs':count[1],'scatter_ADDs':sum(r[0]==1 and r[5]==3 for r in records),
            'MOVEs':count[0],'COPYs':count[2],'ERASEs':count[3],'COPY_rank_sum':sum(r[5] for r in records if r[0]==2),
            'peak_live_copy_slots':1,'paid_profile':{str(k):v for k,v in sorted(profile.items())},
            'paid_rank_mass':sum(k*v for k,v in profile.items()),'F':F,'B':B,
            'local_bits':local.bit_length(),'nine_stage_bits':nine.bit_length(),
            'record_sha256':sha(b''.join(struct.pack('<6i',*r) for r in records))}


def rejects(label,fn,fragment):
    try:
        fn()
    except ValueError as exc:
        require(fragment in str(exc),label+' wrong rejection: '+str(exc))
        return label
    raise ValueError('control accepted: '+label)


def run(output=None):
    data=inputs();w=json.loads(gzip.decompress(data[WORD]));witness=json.loads((HERE/'WITNESS.json').read_text())
    baseline,rest,P,algebra=decompose(w,witness)
    owner=types.ModuleType('pinned_owner');exec(compile(data[OWNER],OWNER,'exec'),owner.__dict__)
    h,c,_=owner.Word(w).interface();flags=sorted(k for k,v in {**h,**c}.items() if not v)
    require(flags==['H2_D_frame0_targets_from_helpers','K_equals_D'],'original interface flags')
    with tempfile.TemporaryDirectory(prefix='r439-sprint-interleave-') as tmp:
        tmp=Path(tmp)
        original,frames=export(w,data,tmp/'original')
        fixed,_=export(baseline,data,tmp/'split')
        candidate=interleave(fixed,w,rest,P,witness)
        reports={}
        for name,records in [('original',original),('split94',fixed),('interleaved88',candidate)]:
            boundary(records,w);boundary(records,w,True)
            reports[name]=invoice(records,w,frames)
            require([r for r in records if r[0]==0]==[r for r in original if r[0]==0],'ordered MOVEs unchanged')
        require(reports['split94']['ADDs']==11067 and reports['split94']['scatter_ADDs']==94,'known split calibration')
        require(reports['interleaved88']['ADDs']==witness['expected_total_adds']==11061,'claimed complete ADDs')
        require(reports['interleaved88']['scatter_ADDs']==witness['expected_scatter_adds']==88,'claimed scatter ADDs')
        controls=[]
        bad=copy.deepcopy(witness);bad['taps']=bad['taps'][:-1]
        controls.append(rejects('omitted tap',lambda:decompose(w,bad),'tap response'))
        bad=copy.deepcopy(witness);bad['taps'][-1][0]=0
        controls.append(rejects('wrong noncommuting cut',lambda:decompose(w,bad),'tap response'))
        bad=copy.deepcopy(witness);bad['taps'][-1][1]=4
        controls.append(rejects('wrong target',lambda:decompose(w,bad),'tap response'))
        bad=copy.deepcopy(witness);bad['column']=1
        controls.append(rejects('wrong retained total',lambda:decompose(w,bad),'tap response'))
        late=next(i for i,r in enumerate(candidate) if r[0]==2 and r[1]==w['ret'][witness['column']])
        last=next(i for i in range(late+1,len(candidate)) if candidate[i][0]==3)
        undoidx=next(i for i in range(late,last) if candidate[i][0]==1 and candidate[i][5]==4)
        badrec=candidate[:undoidx]+candidate[undoidx+1:]
        controls.append(rejects('missing paid undo',lambda:boundary(badrec,w),'dirty boundary'))
        badrec=candidate[:late+1]+[candidate[late]]+candidate[late+1:]
        controls.append(rejects('overlapping COPY',lambda:boundary(badrec,w),'occupied slot'))
        badrec=candidate[:late+1]+[candidate[last]]+candidate[late+1:last]+candidate[last+1:]
        controls.append(rejects('premature ERASE',lambda:boundary(badrec,w),'dirty boundary'))
        badrec=candidate.copy();r=list(badrec[late+1]);r[4]=1;badrec[late+1]=tuple(r)
        controls.append(rejects('wrong tap frame',lambda:invoice(badrec,w,frames),'frame access'))
        badrec=candidate.copy();r=list(badrec[late]);r[5]-=1;badrec[late]=tuple(r)
        controls.append(rejects('underpriced COPY',lambda:invoice(badrec,w,frames),'COPY frame'))
        # Injections at a common cut commute; order is not part of the theorem.
        equivalent=copy.deepcopy(witness);equivalent['taps']=list(reversed(equivalent['taps']))
        decompose(w,equivalent)
        eq=interleave(fixed,w,rest,P,equivalent);boundary(eq,w);boundary(eq,w,True)
        require(invoice(eq,w,frames)['ADDs']==11061,'equivalent presentation')
        report={'status':'PASS_R439_SINGLE_COPY_INTERLEAVING','dirty_columns':661,'orientations':2,
                'algebra':algebra,'schedules':reports,'controls':controls,'equivalent_tap_order_passes':True,
                'source_interface_false':flags,'new_kappa_claim':False,'optimality_claim':False}
        if output is not None:
            output.mkdir(parents=True,exist_ok=False)
            (output/'records.bin').write_bytes(b''.join(struct.pack('<6i',*r) for r in candidate))
            (output/'frames.json').write_text(json.dumps(frames,sort_keys=True)+'\n')
            (output/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
        return report


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--output',type=Path)
    args=ap.parse_args();report=run(args.output)
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    else:require(report==json.loads((HERE/'RESULT.json').read_text()),'fixed result receipt mismatch')
    print('PASS_R439_SINGLE_COPY_INTERLEAVING scatter=94->88 ADDs=11067->11061 dirty_columns=661 controls='+str(len(report['controls']))+' no_new_kappa no_optimality_claim')


if __name__=='__main__':main()
