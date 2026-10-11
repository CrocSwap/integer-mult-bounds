"""Future-only serialized-field and instruction audit, adapting PR444 ideas.

Attribution: chafreaky/OpenAI Codex PR444, head8c4242ea61c67827fe62b07b2edc093d7ddfa631,
audit blob b256e112b0d51dd3ffb34eb3e1516084a8965485; Apache-2.0.
This strengthens serialization conformance, not the conditional hosted compiler.
"""
import argparse,copy,gzip,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
if not __debug__:raise SystemExit('Assertions required')
rd=lambda p:json.loads(p.read_text())
gz=lambda p:json.loads(gzip.decompress(p.read_bytes()))
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()

def fields(t,parent):
    mutable={'version','schedule','live','hosting','calls','helper_route','banks_per_stage'}
    assert set(t)==set(parent)|{'hosting'}
    assert {k:v for k,v in t.items()if k not in mutable}=={k:v for k,v in parent.items()if k not in mutable}
    sched=copy.deepcopy(parent['schedule']);idx=0
    for event in sched:
        if event['kind']=='idle':event['idx']=idx;idx+=1
    assert t['schedule']==sched
    assert len(t['calls'])==len(parent['calls'])
    local=240+740
    for c,p in zip(t['calls'],parent['calls']):
        assert set(c)==set(p)
        assert {k:v for k,v in c.items()if k!='owners'}=={k:v for k,v in p.items()if k!='owners'}
        assert len(c['owners'])==local and c['owners'][:240]==p['owners'][:240]
        for owner in c['owners']:
            assert isinstance(owner,list)and len(owner)==2 and isinstance(owner[0],int)
            assert isinstance(owner[1],list)and owner[1]
    assert t['private_centre_reserve']==9

def streamed_local_digest(t):
    # Specified local-call stream only: separately bind full schedule and fields.
    h=hashlib.sha256();count=0;local=len(t['calls'][0]['owners'])
    for c in t['calls']:
        for z in t['local_programs'][c['orientation']]:
            assert z[0]in(0,1,2,3) and len(z)==(6 if z[0]in(0,1)else 7) and 0<=z[1]<local
            x=[z[0],c['owners'][z[1]]]
            if z[0]==0:x.extend(z[2:])
            else:
                assert 0<=z[2]<=local
                x.append(c['owners'][z[2]]if z[2]<local else[t['live'],['private',0]])
                x.extend(z[3:])
            h.update(json.dumps(x,separators=(',',':')).encode()+b'\n');count+=1
    return h.hexdigest(),count

def main():
    ap=argparse.ArgumentParser();ap.add_argument('parent',type=Path);ap.add_argument('hosted',type=Path);ap.add_argument('--assignment-audit',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    parent=gz(a.parent/'GLOBAL-TEMPLATE.json.gz');t=gz(a.hosted/'GLOBAL-TEMPLATE.json.gz');g=rd(a.hosted/'GLOBAL.json');fields(t,parent)
    def assignment(candidate):
        with tempfile.TemporaryDirectory(prefix='serialization-audit-')as td:
            d=Path(td);raw=canonical(candidate);gg=copy.deepcopy(g);gg['template_sha256']=hashlib.sha256(raw).hexdigest();(d/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0));(d/'GLOBAL.json').write_text(json.dumps(gg))
            return subprocess.run([sys.executable,'-B',str(a.assignment_audit),str(a.parent),str(d),'--out',str(d/'RESULT.json')],capture_output=True,text=True)
    assert assignment(t).returncode==0
    def owner(q,kind):return next(o for c in q['calls']for o in c['owners'][240:]if o[1][0]==kind)
    controls=[
      ('outside_window',lambda q:q['hosting']['slots'][0].__setitem__(4,99)),
      ('copy_index',lambda q:q['hosting']['slots'][0].__setitem__(1,240)),
      ('negative_offset',lambda q:q['hosting']['slots'][0].__setitem__(2,-1)),
      ('residual_width',lambda q:q['hosting']['slots'][0].__setitem__(3,q['hosting']['slots'][0][3]+1)),
      ('duplicate_helper',lambda q:q['hosting']['slots'].append(q['hosting']['slots'][0])),
      ('omitted_helper',lambda q:q['hosting']['slots'].pop()),
      ('replica_owner',lambda q:owner(q,'hosted').__setitem__(0,owner(q,'hosted')[0]+960)),
      ('bank_slot',lambda q:owner(q,'bank')[1].__setitem__(1,64)),
      ('call_orientation',lambda q:q['calls'][0].__setitem__('orientation','reverse')),
      ('duplicate_call',lambda q:q['calls'].__setitem__(1,q['calls'][0])),
      ('idle_rank',lambda q:next(e for e in q['schedule']if e['kind']=='idle').__setitem__('rank',1)),
      ('understated_stock',lambda q:q.__setitem__('live',q['live']-1)),
      ('private_reserve',lambda q:q.__setitem__('private_centre_reserve',8)),
      ('unexpected_field',lambda q:q.__setitem__('undeclared_primitive',True))]
    rejected=[]
    for name,mutate in controls:
        q=copy.deepcopy(t);mutate(q)
        try:fields(q,parent)
        except AssertionError:rejected.append(name);continue
        r=assignment(q);assert r.returncode!=0 and 'AssertionError'in r.stderr and 'FileNotFoundError'not in r.stderr,name;rejected.append(name)
    digest,n=streamed_local_digest(t);parent_digest,parent_n=streamed_local_digest(parent);assert n==parent_n and digest!=parent_digest
    result=dict(status='PASS_SOURCE_SERIALIZED_FIELDS_LOCAL_STREAM_DIGEST_AND14_MUTATIONS',local_call_instruction_sha256=digest,parent_local_call_instruction_sha256=parent_digest,local_call_instructions=n,schedule_canonical_sha256=hashlib.sha256(canonical(t['schedule'])).hexdigest(),template_canonical_sha256=hashlib.sha256(canonical(t)).hexdigest(),mutations_rejected=rejected,attribution='PR444 chafreaky/OpenAI Codex immutable-field, streamed-instruction digest and mutation-audit ideas; independently adapted to own signed75 T64 supplier.',scope='Local-call instruction serialization and full schedule/immutable field conformance. Digest is not a hash of fully expanded idle/bridge/sigma/selector primitives and does not discharge their conditional compiler admission.')
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()
