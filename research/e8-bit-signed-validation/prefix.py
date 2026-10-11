"""Independent full seven-stage scalar prefix and F2-column replay.
Prepared with OpenAI Codex assistance. Apache-2.0; inherited E8 notices apply.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import struct
import sys
assert __debug__

def source_template(path, expected_sha256):
    """Observe returned locals of the unchanged checked source template only."""
    path=Path(path);assert sha256(path.read_bytes()).hexdigest()==expected_sha256
    spec=importlib.util.spec_from_file_location('signed_validation_bridged',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    captured={}
    def observe(frame,event,arg):
        if frame.f_code is module.check.__code__ and event=='return':
            captured.update(stages=list(frame.f_locals['stages']),log=list(frame.f_locals['log']),
                endpoint={str(k):str(v)for k,v in frame.f_locals['S'].items()})
    previous=sys.getprofile();sys.setprofile(observe)
    try:checked=module.check(3,8)
    finally:sys.setprofile(previous)
    assert checked['stages']==checked['invocations']==7 and checked['gates']==12 and checked['m']==56
    active=[];reverse=[];bridges={};stage=-1
    role=lambda pair:2*(pair[1]-1)+int(pair[0]=='Y')
    for entry in captured['log']:
        if entry[0]in('F','B'):
            stage+=1;kind,pair=entry
            assert captured['stages'][stage]==(stage,kind,pair)
            xy=(role(('X',pair)),role(('Y',pair)))
            active.append(xy if kind=='F'else xy[::-1]);reverse.append(kind=='B')
        else:
            kind,dst,src,sign=entry;assert kind=='G'and sign in(-1,1)and stage>=0
            bridges.setdefault(stage,[]).append((role(dst),role(src),sign))
    assert stage==6
    exchanges=[]
    for pair in range(1,4):
        assert captured['endpoint'][str(('X',pair))]=='-y'+str(pair)
        assert captured['endpoint'][str(('Y',pair))]=='x'+str(pair)
        exchanges.append((role(('X',pair)),role(('Y',pair))))
    schedule=dict(active=active,reverse=reverse,bridges=bridges,terminal_exchanges=exchanges,
        source_log=captured['log'],source_stages=captured['stages'],checked_idle=checked)
    assert sha256(path.read_bytes()).hexdigest()==expected_sha256
    return schedule,dict(bridged_source_sha256=expected_sha256,
        generated_schedule_sha256=sha256(json.dumps(schedule,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        capture='Return-event observation of only unchanged bridged.check(3,8); all its frame and symbolic endpoint assertions execute.')


def run(records, template, binding):
    raw=Path(records).read_bytes()
    events=list(struct.iter_unpack('<6i',raw))
    v,R,K,S,T=120,822,3,7,7
    one=2*K*v+R;live=T*one;temp=live;local=2*v+R
    active=template['active'];bridges=template['bridges']
    assert len(active)==S and len(template['reverse'])==S
    value=[1<<i for i in range(live)]+[0];norm=[1]*live+[0];peak=1;stages=[];copies=adds=0
    for stage in range(S):
     rev=template['reverse'][stage]
     for rep in range(T):
      def addr(r):
       if r==local:return temp
       if r<2*v:return rep*one+active[stage][r//v]*v+r%v
       return rep*one+2*K*v+r-2*v
      opened=None
      for op,a,b,c,f,z in reversed(events)if rev else events:
       if op==0:continue
       if op==1:
        d,s=addr(a),addr(b);assert d!=s and d!=temp
        if s==temp:assert opened is not None
        if opened is not None:assert d!=opened
        norm[d]+=abs(c)*norm[s];peak=max(peak,norm[d]);adds+=1
        if c&1:value[d]^=value[s]
       elif op==(3 if rev else 2):
        assert opened is None and b==local and norm[temp]==0 and value[temp]==0
        opened=addr(a);norm[temp]=norm[opened];value[temp]=value[opened];copies+=1
       else:
        assert op==(2 if rev else 3) and opened==addr(a)
        assert value[temp]==value[opened]
        norm[temp]=value[temp]=0;opened=None
      assert opened is None
      assert all(value[rep*one+r]==1<<(rep*one+r) for r in range(2*K*v,one))
     for rep in range(T):
      for d,s,c in bridges.get(stage,[]):
       for i in range(v):
        dst,src=rep*one+d*v+i,rep*one+s*v+i
        value[dst]^=value[src];norm[dst]+=abs(c)*norm[src];peak=max(peak,norm[dst]);adds+=1
     stages.append(dict(stage=stage,peak=peak))
    for rep in range(T):
     for left,right in template['terminal_exchanges']:
      for i in range(v):
       x=rep*one+left*v+i;y=rep*one+right*v+i
       value[x],value[y]=value[y],value[x];norm[x],norm[y]=norm[y],norm[x]
    assert value==[1<<i for i in range(live)]+[0]
    assert copies==S*T*9 and peak<2**104
    return dict(status="PASS_EXACT_SEVEN_STAGE_SCALAR_F2_COLUMNS_AND_CANCELLATION_FREE_PREFIX",record_sha256=sha256(raw).hexdigest(),formal_columns=live,helper_inputs=T*R,copies=copies,additions=adds,stages=stages,payload_prefix=peak,bits=peak.bit_length(),threshold=2**104,source_template_binding=binding,scope="Literal input scalar schedule over all seven replicas, generated from the checked unchanged bridged template with every bridge and terminal exchange. Endpoint comparison is over F2; this is not a separately emitted global IR or chart/compiler proof.")
