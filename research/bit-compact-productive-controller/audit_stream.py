"""Read the emitted candidate stream without importing its producer.

This checks the decoded RAW map and finite FRAME/owner/lease conditions.
The all-function conclusion additionally uses the common-FRAME lemma and
the independently recorded physical main polynomial identity, not RAW rank.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import argparse,gzip,json


def need(v,m):
    if not v:raise ValueError(m)


def audit(repo_root,local_dir,global_dir,mutant=None):
    repo_root,local_dir,global_dir=map(Path,(repo_root,local_dir,global_dir))
    w=json.loads(gzip.decompress((local_dir/'WORD.json.gz').read_bytes()))
    frames=json.loads((repo_root/'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json').read_bytes())['frames']
    calls=json.loads((global_dir/'CALLS.json').read_bytes())
    result=json.loads((global_dir/'RESULT.json').read_bytes())
    if mutant=='duplicate_owner':calls[1]['helper_owner_begin']=calls[0]['helper_owner_begin']
    if mutant=='full8_credit':
        result['targets']['8']+=72;result['targets']['4']-=72
    need(len(calls)==18,'18 independent native invocations')
    owned=[i for call in calls for i in range(call['helper_owner_begin'],call['helper_owner_begin']+436)]
    need(len(owned)==len(set(owned))==7848 and set(owned)==set(range(3552,11400)),'injective fresh helper ownership')
    n=11400;values=[1<<i for i in range(n)]+[0];versions=[0]*(n+1)
    lease=None;state=None;current=None;seen=[];paid=Counter();counts=Counter();mutated=False;raw_hash=sha256()
    def enter(stage):
        nonlocal current,state
        if current is not None and current['stage']==stage:return
        finish()
        need(stage not in seen,'a native invocation is not resumed after it returned')
        current=next(c for c in calls if c['stage']==stage);seen.append(stage)
        x,y=2*current['pair'],2*current['pair']+1
        if current['reverse']:x,y=y,x
        current=dict(current,x=x,y=y)
        state=list(w['final'] if current['reverse'] else w['start'])+[None]
        need(all(values[i]==1<<i for i in range(current['helper_owner_begin'],current['helper_owner_begin']+436)),'all new helper inputs are independent arbitrary RAW')
    def local(role):
        need(current is not None,'local event has an actual native invocation')
        if role==n:return 658
        bank,port=divmod(role,111)
        if bank==current['x']:return port
        if bank==current['y']:return 111+port
        r=role-current['helper_owner_begin']
        need(0<=r<436,'current owner belongs to this native invocation')
        return 222+r
    def finish():
        nonlocal state,current
        if current is None:return
        need(lease is None and values[n]==0,'local private returned zero')
        need(state==list(w['start'] if current['reverse'] else w['final'])+[None],'all actual local endpoint FRAMEs')
        current=None;state=None
    with gzip.open(global_dir/'EXPANDED-PROGRAM.jsonl.gz','rb') as stream:
        for idx,line in enumerate(stream):
            raw_hash.update(line);e=json.loads(line);kind=e[0]
            if mutant=='omit_clear' and kind=='LOCAL_PAID_CLEAR' and not mutated:
                mutated=True;continue
            if mutant=='wrong_nested_frame' and kind=='LOCAL_QUERY' and not mutated:
                e[4]=e[3];mutated=True
            counts[kind]+=1
            if kind.startswith('LOCAL_'):enter(e[1] if kind!='LOCAL_ADD' else e[4][0])
            elif current is not None:finish()
            if kind in ('ADD','LOCAL_ADD','THIN_ADD'):
                _,d,s,c,meta=e
                need(0<=d<n and 0<=s<=n and d!=s and c in(-1,1),'literal paid signed ADD')
                need(lease is None or d!=lease[0],'no SOURCE VALUE write during capture')
                if s==n:need(lease is not None,'private read is within the lease')
                if kind=='LOCAL_ADD':
                    need(state[local(d)]==state[local(s)]==meta[1],'actual common FRAME for every ADD')
                values[d]^=values[s];versions[d]+=1
            elif kind=='LOCAL_QUERY':
                _,stage,role,before,after,rank,reverse=e;r=local(role)
                need(lease is None and state[r]==before,'QUERY state/capture immutable')
                lo,hi=(frames[str(after)],frames[str(before)]) if reverse else (frames[str(before)],frames[str(after)])
                need(0<rank<8 and hi['dim']-lo['dim']==rank,'proper literal residual rank')
                need(all(sum(x*y for x,y in zip(u,v))==0 for u in lo['B'] for v in hi['A']),'exact rational nested residual')
                state[r]=after;versions[role]+=1;paid[rank]+=1
            elif kind in ('LOCAL_COPY_QUERY','THIN_COPY'):
                if kind=='LOCAL_COPY_QUERY':
                    _,stage,role,private,f,recv,rank,reverse=e
                    need(state[local(role)]==f and frames[str(f)]['dim']==7 and recv==0 and rank==7,'actual SOURCE cap and receiver')
                    state[658]=0;paid[7]+=1
                else:_,stage,role,private,port,ver=e;need(versions[role]==ver,'actual thin SOURCE version')
                need(private==n and lease is None and values[n]==0,'one actual owned zero stream')
                values[n]=values[role];lease=(role,versions[role],kind,idx)
                if mutant=='source_write_in_lease' and not mutated:
                    versions[role]+=1;mutated=True
            elif kind in ('LOCAL_PAID_CLEAR','THIN_PAID_CLEAR'):
                need(lease is not None,'no missing capture or duplicate CLEAR')
                role,version,capture,begin=lease
                need(versions[role]==version and values[n]==values[role],'complete RAW copied original unchanged')
                if kind=='LOCAL_PAID_CLEAR':
                    _,stage,src,private,f,recv,reverse=e
                    need(capture=='LOCAL_COPY_QUERY' and src==role and private==n and state[658]==recv==0 and state[local(src)]==f,'literal local CLEAR binding')
                    state[658]=None
                else:need(capture=='THIN_COPY' and e[2]==n,'thin owned CLEAR')
                values[n]=0;lease=None
            elif kind=='THIN_PAID_QUERY':
                need(lease is not None and lease[2]=='THIN_COPY' and e[2]==n and e[4]==1,'one proper thin QUERY on captured stream');paid[1]+=1
            elif kind in ('PAID_PORT_ROUTE','PAID_WHOLE_IDLE'):
                need(lease is None,'no lease crosses a route/whole idle')
                role=e[2] if kind=='PAID_PORT_ROUTE' else e[1];versions[role]+=1
                if kind=='PAID_WHOLE_IDLE':paid[e[3]]+=1
            else:raise ValueError('unknown expanded literal opcode '+kind)
    finish()
    need(lease is None and values==[1<<i for i in range(n)]+[0],'all11400 independent decodedRAW and privatezero')
    need(len(seen)==18 and counts['LOCAL_PAID_CLEAR']==162 and counts['THIN_PAID_CLEAR']==1665,'every owned private lifetime closed')
    need(dict(sorted(paid.items()))=={int(k):v for k,v in result['paid'].items()},'actual QUERY invoice')
    need(result['targets']['4']==72 and result['targets']['8']==7776,'no full8 credit for the four partial jobs')
    need(counts['PAID_PORT_ROUTE']==7548 and sum(counts.values())==446400,'all fixed routes and literal records retained')
    need(raw_hash.hexdigest()==result['expanded_event_sha256'],'stream bound to actual replay receipt')
    return dict(status='PASS_EMITTED_STREAM_SEPARATE_INTERPRETER',columns=n,query_count=sum(paid.values()),events=sum(counts.values()),SOURCE_versions='all mutable/capture epochs checked',scope='decoded RAW plus exact current FRAME/owner/private; all-function map additionally uses the commonFRAME and physical main polynomial lemmas')


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,required=True);p.add_argument('--local-dir',type=Path,required=True);p.add_argument('--global-dir',type=Path,required=True)
    a=p.parse_args();r=audit(a.repo_root,a.local_dir,a.global_dir)
    controls={}
    for name in ('duplicate_owner','full8_credit','omit_clear','wrong_nested_frame','source_write_in_lease'):
        try:audit(a.repo_root,a.local_dir,a.global_dir,name)
        except ValueError as e:controls[name]=str(e)
        else:raise ValueError('mutant unexpectedly passed: '+name)
    print(json.dumps(dict(result=r,rejected_mutants=controls),indent=2))


if __name__=='__main__':main()
