#!/usr/bin/env python3
"""Independent event owner/frame/def-use audit; never imports candidate Python.

--structure is a cheap contract probe. --exact is a coordinator-only full row
replay on arbitrary retained and owned entries. Mathematical scalar rows use
rational coefficients and reduced free words, not binary tableaux.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1] / 'repository'
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
CANDIDATE = 'research/kappa-joint-relations-20261023/WORD.json.gz'
PHASE = 'research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz'
HEAD = '4bd6efa51a495a7c7b7754915cf0244e7e60969e'
MAIN = '1ec1119972c9aefe42525172d07b332fcff81cb4'


def require(p, text):
    if not p:
        raise ValueError(text)


def read(p):
    data = p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix == '.gz' else data)


def role(x):
    require(isinstance(x, list) and len(x) == 2 and x[0] in ('L','C') and isinstance(x[1],int), 'Malformed role')
    return tuple(x)


def label(r):
    return '%s%d' % r


def relation_structure(source, candidate):
    """Align literal events, discovering edits instead of using WITNESS.json."""
    c = candidate['canonical']
    expected = dict(source['canonical']); expected.pop('local_profile')
    require(c == expected, 'Changed canonical frames/maps/adapters')
    require(candidate['programs']['forward'] == source['programs']['forward'], 'Changed forward program')
    owned_list = [role(x) for x in candidate['owned']['backward']]
    owned = set(owned_list)
    require(len(owned) == len(owned_list) == 17, '17 distinct owned roles required')
    require({r for r in owned if r[0]=='C'} == {('C',i) for i in range(9)}, 'Distinct C0..C8 required')
    pivots = sorted(r[1] for r in owned if r[0]=='L')
    require(len(pivots) == 8 and all(224 <= i < 632 and c['start'][i]==0 and c['final'][i]==1 for i in pivots), '8 owned cold full-ended helpers')
    require(len(c['frames'][1])-len(c['frames'][0]) == 9, 'Lost owned helpers must have rank nine')
    old = source['programs']['backward']; new = candidate['programs']['backward']
    k = 0; prepared={}; prep_ops=[]
    while k < len(new) and new[k][0]=='scalar':
        e=new[k]; g=e[1]; dst=role(g[1])
        require(e[2]==0 and dst in owned and dst[0]=='L', 'Preparation owner/frame')
        if g[0]=='clear':
            require(dst[1] not in prepared, 'Repeated pivot initial clear')
            prepared[dst[1]]=[]
        else:
            require(g[0]=='add' and dst[1] in prepared, 'Pivot read before initial clear')
            src=role(g[2]); require(src[0]=='L' and 224<=src[1]<632 and src not in owned and c['start'][src[1]]==0, 'Preparation must use independent common-frame helpers')
            q=Fraction(g[3],g[4]); require(q and q.denominator & (q.denominator-1)==0, 'Preparation dyadic coefficient')
            prepared[dst[1]].append([src[1],str(q)])
        prep_ops.append(k);k+=1
    require(set(prepared)==set(pivots) and all(prepared.values()), 'Every owned pivot prepared from retained helpers')
    require(k<len(new) and new[k]==old[0], 'Source start marker missing')
    snapshots={}; centers=[]; zeros=[]; source_map={};
    for j,e in enumerate(old):
        # Inserted snapshot pair follows precisely one already consumed source event.
        if k<len(new) and new[k]!=e and new[k][0]=='scalar' and new[k][1][0]=='clear' and new[k][1][1][0]=='C' and new[k][1][1][1]>0:
            slot=role(new[k][1][1]);frame=new[k][2]
            require(j>0 and slot not in snapshots and k+1<len(new), 'Reused live snapshot bank')
            g=new[k+1]
            require(g[0]=='scalar' and g[1][0]=='copy' and role(g[1][1])==slot and g[2]==frame, 'Snapshot requires immediate same-frame COPY')
            src=role(g[1][2]); require(src[0]=='L', 'Snapshot must read source data role')
            prior=old[j-1]
            require(prior[0]=='climb' and prior[2]==src[1] and prior[4]==frame, 'Snapshot must follow its copied source production in exact frame')
            snapshots[slot]={'slot':label(slot),'source_after':j-1,'copy_from':label(src),'frame':frame,'birth':k+1,'initial_clear':k,'reads':[]}
            k+=2
        require(k<len(new), 'Candidate ended before source')
        if new[k]==e:
            source_map[j]=k;k+=1;continue
        if e[0]=='center':
            require(e[1:3]==[0,0] and e[4]==8, 'Only original rank-eight C0 centers replaceable')
            f=e[3]; a=new[k:k+3]
            require(len(a)==3 and a[0]==['scalar',['clear',['C',0]],f] and a[1][0]=='scalar' and a[1][1][0]=='copy' and a[1][1][1]==['C',0] and a[1][2]==f, 'Center replacement must clear/COPY C0 in exact output frame')
            slot=role(a[1][1][2]); require(slot in snapshots and not snapshots[slot]['reads'] and snapshots[slot]['frame']==f, 'Live snapshot/frame/unique read')
            require(a[2]==['scalar',['clear',list(slot)],f], 'Snapshot must be erased after its last read')
            snapshots[slot]['reads'].append(k+1);snapshots[slot]['retire']=k+2;snapshots[slot]['center_source']=j
            centers.append({'source':j,'candidate':k,'slot':label(slot),'frame':f,'rank':8});k+=3
        elif e[0]=='climb':
            require(e[1]=='warp_retimed' and e[4:]==[1,1], 'Only later rank-one climb may be zero replacement')
            require(new[k]==['zero_retag',['L',e[2]],e[3],e[4]], 'Zero replacement must preserve role/exact frames')
            zeros.append({'source':j,'candidate':k,'role':label(('L',e[2])),'frame':e[3]});k+=1
        else:
            raise ValueError('Unlicensed change at source event %d, candidate event %d'%(j,k))
    tail=new[k:]
    require(tail==[['scalar',['clear',['L',i]],1] for i in pivots], 'Every owned pivot must be returned zero at exact full frame')
    require(len(snapshots)==len(centers)==len(zeros)==8, 'Exactly 8 snapshots/center replacements/zero replacements')
    require(all(len(x['reads'])==1 and x['birth']<x['reads'][0]<x['retire'] for x in snapshots.values()), 'Snapshot def-use-retire chronology')
    require(max(x['birth'] for x in snapshots.values())<min(x['reads'][0] for x in snapshots.values()), 'All eight snapshots are simultaneous before first use')
    # The source event at a snapshot may update another role; the actual frame
    # replay below verifies the copied role's current frame independently.
    return {'owned':owned,'pivots':pivots,'prepared':prepared,'snapshots':snapshots,'centers':centers,'zeros':zeros,'source_map':source_map,'tail_start':k}


def span_rank(basis):
    row={}
    for n in basis:
        require(isinstance(n,int) and 0<=n<512,'Frame basis vector range')
        for p in sorted(row,reverse=True):
            if n>>p&1:n^=row[p]
        require(n,'Dependent frame basis')
        row[n.bit_length()-1]=n
    return row


def subset(a,b):
    for n in a:
        for p in sorted(b,reverse=True):
            if n>>p&1:n^=b[p]
        if n:return False
    return True


def run_frames(c,program,owned,exact=False,backward=True):
    """Frame and syntactic owner check; exact=True proves complete row returns."""
    roles={('L',i) for i in range(632)}|owned
    frames={('L',i):f for i,f in enumerate(c['start'])}
    frames.update({r:None for r in owned if r[0]=='C'})
    initialized=set(roles)-owned
    # Each role, including every owner, starts with its own independent symbol.
    rows={r:{(r,()):Fraction(1)} for r in roles} if exact else None
    ever_cleared=set(); last_reads={}; last_writes={}; first_clear={}; last_clear={}; paid=Counter(); zero_sites=[]
    bases=[span_rank(x) for x in c['frames']]
    frame_cache={}
    def read_at(r,i):
        require(r in roles,'Undeclared/aliased source role')
        require(r in initialized,'Owned dirt read before legal erase')
        last_reads[r]=i
    def add(dst,src,q):
        for key,value in list(src.items()):
            new=dst.get(key,Fraction(0))+q*value
            if new:dst[key]=new
            else:dst.pop(key,None)
    for i,e in enumerate(program):
        kind=e[0]
        if kind=='scalar':
            g,f=e[1:];dst=role(g[1]); require(dst in roles and isinstance(f,int) and 0<=f<len(bases),'Scalar role/frame')
            if g[0]=='clear':
                require(dst in owned,'Borrowed field erased')
                initialized.add(dst);ever_cleared.add(dst);first_clear.setdefault(dst,i);last_clear[dst]=i
                frames[dst]=f
                if exact:rows[dst]={}
            else:
                require(dst in initialized,'Owned dirt read before legal erase');require(frames[dst]==f,'Scalar destination frame mismatch')
                if g[0]!='copy':read_at(dst,i)
                if g[0] in ('add','copy'):
                    src=role(g[2]);read_at(src,i)
                    require(src!=dst and frames[src]==f,'Scalar source alias/frame mismatch')
                    if g[0]=='copy':
                        require(dst in owned and last_writes.get(dst)==last_clear.get(dst),'COPY requires just-cleared owner')
                        if exact:
                            require(not rows[dst],'COPY overwrote nonzero owner');rows[dst]=dict(rows[src])
                    else:
                        q=Fraction(g[3],g[4]);require(q,'Zero ADD coefficient')
                        if exact:add(rows[dst],rows[src],q)
                elif g[0]=='scale':
                    q=Fraction(g[2],g[3]); require(q,'Zero SCALE coefficient')
                    if exact:rows[dst]={key:q*value for key,value in rows[dst].items()}
                else:raise ValueError('Unknown scalar opcode')
            last_writes[dst]=i
        elif kind=='warp':
            dst=role(e[1]);read_at(dst,i);op,old,new=e[2:]
            require(frames[dst]==old and 1<=abs(op)<=len(c['warps']),'Warp input frame/generator')
            if exact:
                # Distinct backward generators; prefix cancellation is exact
                # representation in the free group on the actual native maps.
                symbol=op+(1000000 if op>0 else -1000000) if backward else op
                rows[dst]={(r,word[1:] if word and word[0]==-symbol else (symbol,)+word):q for (r,word),q in rows[dst].items()}
            frames[dst]=new;last_writes[dst]=i
        elif kind in ('climb','center'):
            if kind=='climb':_,_,n,old,new,rank=e;dst=('L',n)
            else:_,n,old,new,rank=e;dst=('C',n)
            read_at(dst,i);require(frames[dst]==old,'Paid input frame')
            require(rank==abs(len(c['frames'][new])-len(c['frames'][old])),'Paid rank mismatch')
            key=(kind,old,new)
            if key not in frame_cache:
                frame_cache[key]=subset(c['frames'][old],bases[new]) or (kind=='center' and subset(c['frames'][new],bases[old]))
            require(frame_cache[key],'Paid frame inclusion')
            frames[dst]=new;last_writes[dst]=i;paid[rank]+=1
        elif kind=='zero_retag':
            _,r,old,new=e;dst=role(r);read_at(dst,i)
            require(frames[dst]==old,'Zero identity input frame')
            if exact:require(not rows[dst],'Zero identity has nonzero input row')
            frames[dst]=new;last_writes[dst]=i;zero_sites.append(i)
        else:require(kind in ('phase','adapter'),'Unknown opcode')
    require([frames[('L',i)] for i in range(632)]==c['final'],'Final borrowed/owned native frame mismatch')
    require(owned<=ever_cleared,'Owned entry dirt not legally erased')
    for r in owned:
        require(last_clear[r]==last_writes[r],'Owned output not zero at return')
    if exact:
        for r in sorted(roles):
            expected={}
            if r not in owned:
                expected[(r,())]=Fraction(1)
                if r[0]=='L' and ((backward and r[1]<112) or (not backward and 112<=r[1]<224)):
                    src=('L',r[1]+112 if backward else r[1]-112)
                    expected[(src,())]=Fraction(-1 if backward else 1)
            require(rows[r]==expected,'Wrong arbitrary-column endpoint '+label(r))
    return {'paid':dict(sorted(paid.items())),'zero_sites':zero_sites,
            'initial_columns':len(roles),'retained_arbitrary_columns':len(roles-owned),'owned_arbitrary_columns':len(owned),
            'all_exact_endpoints_checked':exact,'all_owned_last_writes_are_clears':True,
            'owned_def_use':[{'role':label(r),'first_clear':first_clear[r],'last_read':last_reads.get(r),'last_clear':last_clear[r],'return_frame':frames[r]} for r in sorted(owned)]}


def phase_binding(repo,source,candidate):
    receipt=read(repo/PHASE)
    payload=hashlib.sha256(gzip.decompress((repo/SOURCE).read_bytes())).hexdigest()
    require(receipt['actual_word_canonical_sha256']==payload and receipt['status']=='PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES','Absolute phase receipt/source binding')
    for d in ('forward','backward'):
        for kind in ('warp','phase','adapter'):
            require([e for e in source['programs'][d] if e[0]==kind]==[e for e in candidate['programs'][d] if e[0]==kind],'Changed phase/native/adapter sequence')
    return {'source_payload_sha256':payload,'receipt':PHASE,'source_absolute_phase_lowering_replayed':False,'exact_native_phase_adapter_order_preserved':True}


def check(repo,candidate,exact=False):
    source=read(repo/SOURCE)
    contract=relation_structure(source,candidate)
    run=run_frames(candidate['canonical'],candidate['programs']['backward'],contract['owned'],exact)
    forward=run_frames(candidate['canonical'],candidate['programs']['forward'],{('C',0)},exact,False)
    public={k:v for k,v in contract.items() if k not in ('owned','source_map','snapshots')}
    public['snapshots']={label(k):v for k,v in contract['snapshots'].items()}
    return {'contract':public,'backward':run,'forward':forward,'phase':phase_binding(repo,source,candidate)}


def mutations(repo,candidate):
    checks={}
    def reject(name,mutate):
        bad=copy.deepcopy(candidate);mutate(bad)
        try:check(repo,bad,False)
        except (ValueError,IndexError,KeyError) as err:checks[name]=str(err)
        else:raise ValueError('Mutation escaped: '+name)
    def program(x):return x['programs']['backward']
    def first_snapshot(x):return next(i for i,e in enumerate(program(x)) if e[0]=='scalar' and e[1][:2]==['copy',['C',1]])
    reject('borrowed_clear',lambda x: program(x)[0][1].__setitem__(1,['L',0]))
    reject('missing_initial_pivot_clear',lambda x: program(x).pop(0))
    reject('alias_owned_snapshot_bank',lambda x:x['owned']['backward'].__setitem__(2,['C',1]))
    def reuse(x):
        j=next(i for i,e in enumerate(program(x)) if e[0]=='scalar' and e[1][:2]==['copy',['C',2]])
        program(x)[j-1][1][1]=['C',1];program(x)[j][1][1]=['C',1]
    reject('reused_live_snapshot_bank',reuse)
    reject('wrong_snapshot_frame',lambda x:program(x)[first_snapshot(x)].__setitem__(2,0))
    reject('wrong_snapshot_source',lambda x:program(x)[first_snapshot(x)][1].__setitem__(2,['C',0]))
    reject('missing_owner_return',lambda x:program(x).pop())
    reject('missing_retained_output_operation',lambda x:program(x).pop(next(i for i,e in enumerate(program(x)) if e[0]=='scalar' and e[1][0]=='add' and e[1][1][0]=='L' and e[1][1][1]<224)))
    reject('undeclared_storage_alias',lambda x:program(x)[first_snapshot(x)][1].__setitem__(1,['C',9]))
    reject('changed_phase_marker',lambda x:program(x).pop(next(i for i,e in enumerate(program(x)) if e[0]=='phase')))
    reject('wrong_final_owned_frame',lambda x:program(x)[-1].__setitem__(2,0))
    reject('wrong_center_copy_gauge',lambda x:next(e for e in program(x) if e[0]=='scalar' and e[1][:2]==['copy',['C',0]]).__setitem__(2,0))
    return checks


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=REPO);parser.add_argument('--exact',action='store_true');parser.add_argument('--structure',action='store_true');parser.add_argument('--controls',action='store_true');parser.add_argument('--output',type=Path);parser.add_argument('--candidate',type=Path);parser.add_argument('--candidate-head',default=HEAD)
    a=parser.parse_args();candidate_path=a.candidate or a.repo/CANDIDATE;candidate=read(candidate_path)
    result={'status':'PASS_EXACT_RUNTIME_OWNERSHIP' if a.exact else 'PASS_STRUCTURAL_RUNTIME_OWNERSHIP','candidate_head':a.candidate_head,'candidate_word':str(candidate_path.resolve()),'candidate_word_sha256':hashlib.sha256(candidate_path.read_bytes()).hexdigest(),'canonical_main':MAIN,'scope':'Independent event parser; no author Python imports or WITNESS/RESULT counters used','result':check(a.repo,candidate,a.exact)}
    if a.controls:result['mutation_controls']=mutations(a.repo,candidate)
    data=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(data)
    print(data)


if __name__=='__main__':main()
