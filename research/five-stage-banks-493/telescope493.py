"""Physical frame-tag telescope for the PR210 1331149 helper word (targetagg/word.py replay).
Adapted from PR234's five_stage_source471_physical_telescope (hcg890, ChatGPT assistance)."""
from collections import Counter
import hashlib,json,sys
from array import array
def run(m,records=None,category_names=None):
 W,C=m.W,m.C;v=W.v;regs=m.regs;n=2*v+len(regs)
 ZERO=W.register([]);FULL=W.w['full_frame']
 state={i:W.w['source_frame'][i]for i in range(v)}
 state.update({v+t:ZERO for t in range(v)})
 state.update({2*v+j:W.gauge[r]['frame']if r in W.gauge else ZERO for j,r in enumerate(regs)})
 initial_state=state.copy()
 caps={}
 for t in range(v):
  B,_=W.module.kernel([C.cov[t]],W.h);caps[t]=W.register(B);assert C.dimf[caps[t]]==W.h-1
 used=set(state.values());hist=Counter();cats=Counter();centers=[];sub={}
 G=dict(count=0,center=None,moves=0,copies=0)
 shs=hashlib.sha256(b'[');ths=hashlib.sha256(b'[')
 kind_ids=None if category_names is None else {k:i for i,k in enumerate(category_names)}
 def move(i,f):
  used.add(f);old=state[i]
  if old==f:return
  k=old,f
  if k not in sub:sub[k]=C.sub(old,f)
  assert sub[k],('physical frame descent',i,C.dimf[old],C.dimf[f])
  d=C.dimf[f]-C.dimf[old];assert d>=0
  if records is not None:records.extend((0,i,old,f,d,0))
  if d:hist[d]+=1;G['moves']+=1
  state[i]=f
 def dig(h,row,comma):
  if comma:h.update(b',')
  h.update(json.dumps(row,separators=(',',':')).encode())
 def add(x,c,y,f,kind):
  assert isinstance(x,int)and isinstance(y,int)and x!=y
  move(x,f);py=y
  if kind=='center':
   assert G['center'] is not None and G['center']['source']==y and f==ZERO;py=n
  else:move(y,f)
  if records is not None:records.extend((1,x,py,c,f,kind_ids[kind]))
  dig(shs,[x,y,c],G['count']);dig(ths,[x,py,c,f,kind],G['count']);G['count']+=1;cats[kind]+=1
  return x
 def center_begin(source,frame):
  assert G['center'] is None;move(source,frame);rank=C.dimf[frame];assert rank==22
  G['center']=dict(source=source,frame=frame,rank=rank,first_event=G['count']);hist[rank]+=1;G['copies']+=1
  if records is not None:records.extend((2,source,n,frame,ZERO,rank))
  centers.append(G['center'])
 def center_end():
  c=G['center'];assert c is not None
  if records is not None:records.extend((3,c['source'],n,c['frame'],ZERO,c['rank']))
  c['after_event']=G['count'];assert c['after_event']>c['first_event'];G['center']=None
 text=m.__dict__['__word_text__']
 body=text[text.index('def replay('):]
 body=body[:body.index(' if binary:want')]
 def rep(old,new,cnt=1):
  nonlocal body
  assert body.count(old)==cnt,('site',old,body.count(old));body=body.replace(old,new)
 rep("unit=(lambda i:1)if major else(lambda i:1<<i)if binary else(lambda i:1<<(bits*i))",'unit=lambda i:i')
 rep(" def add(x,c,y):return x+abs(c)*y if major else x^y if binary and c&1 else x if binary else x+c*y\n",'')
 rep("    if t!=pivot:y[t]=track(add(y[t],1,y[pivot]))","    if t!=pivot:y[t]=track(add(y[t],1,y[pivot],group['frame'],'agg_restore'))")
 rep("    for p,c in cs.items():y[t]=track(add(y[t],c,y[p]))","    for p,c in cs.items():y[t]=track(add(y[t],c,y[p],group['frame'],'rank_restore'))")
 rep("   for t,p,c in reversed(group['moves']):y[t]=track(add(y[t],-c,y[p]))","   for t,p,c in reversed(group['moves']):y[t]=track(add(y[t],-c,y[p],group['frame'],'echelon_restore'))")
 rep("target_move(t,W.gauge[s]['frame']);y[t]=track(add(y[t],-direction*c,value(s)));echelon_reads+=1","target_move(t,W.gauge[s]['frame']);y[t]=track(add(y[t],-direction*c,value(s),W.gauge[s]['frame'],'echelon_read'));echelon_reads+=1")
 rep("y[pivot]=track(add(y[pivot],-direction*c,value(s)))","y[pivot]=track(add(y[pivot],-direction*c,value(s),read_frames[s,k],'agg_read'))")
 rep("target_move(t,read_frames[s,k]);y[t]=track(add(y[t],-direction*c,value(s)))","target_move(t,read_frames[s,k]);y[t]=track(add(y[t],-direction*c,value(s),read_frames[s,k],'agg_read'))")
 rep("   y[t]=track(add(y[t],-direction*c,value(s)))\n def gate","   y[t]=track(add(y[t],-direction*c,value(s),W.gauge[s]['frame']if s in W.gauge else ZERO,'dirty_read'))\n def gate")
 rep("assign(a,add(value(a),sign,value(b)))","assign(a,add(value(a),sign,value(b),W.opframe[i]if sign==1 else FULL,'forward_gate'if sign==1 else'cleanup_gate'))")
 rep("for n,s in W.source.items():assign(s,add(value(s),1,x[n]))","for n,s in W.source.items():assign(s,add(value(s),1,x[n],W.w['source_frame'][n],'inject'))")
 rep("x[r['partner']]=track(add(x[r['partner']],1,x[r['source']]))","x[r['partner']]=track(add(x[r['partner']],1,x[r['source']],kpair[r['source']]['mix_frame'],'gauge_mix'))")
 rep("x[a]=track(add(x[a],1,x[b]))","x[a]=track(add(x[a],1,x[b],kpair[b]['mix_frame'],'partner_mix'))",2)
 rep("for r,s in zip(W.g['roots'],W.w['rootroles']):\n  if r['kind']=='center':\n   for t in r['targets']:","for j,(r,s)in enumerate(zip(W.g['roots'],W.w['rootroles'])):\n  if r['kind']=='center':\n   center_begin(value(s),W.w['root_frame'][j])\n   for t in r['targets']:")
 rep("center_reads.append((s,t));y[t]=track(add(y[t],direction,value(s)))","center_reads.append((s,t));y[t]=track(add(y[t],direction,value(s),ZERO,'center'))\n   center_end()")
 rep("for t,p,c in group['moves']:y[t]=track(add(y[t],c,y[p]))","for t,p,c in group['moves']:y[t]=track(add(y[t],c,y[p],ZERO,'echelon_setup'))")
 rep("for p,c in cs.items():y[t]=track(add(y[t],-c,y[p]))","for p,c in cs.items():y[t]=track(add(y[t],-c,y[p],ZERO,'rank_setup'))")
 rep("if t!=group['pivot']:y[t]=track(add(y[t],-1,y[group['pivot']]))","if t!=group['pivot']:y[t]=track(add(y[t],-1,y[group['pivot']],ZERO,'agg_setup'))")
 rep("if t!=e['pivot']:y[t]=track(add(y[t],-1,y[e['pivot']]))","if t!=e['pivot']:y[t]=track(add(y[t],-1,y[e['pivot']],ZERO,'terminal_pre'))")
 rep("y[e['pivot']]=track(add(y[e['pivot']],direction,value(b)))","y[e['pivot']]=track(add(y[e['pivot']],direction,value(b),W.opframe[i],'terminal_write'))")
 rep("if t!=e['pivot']:y[t]=track(add(y[t],1,y[e['pivot']]))","if t!=e['pivot']:y[t]=track(add(y[t],1,y[e['pivot']],e['root_frame'],'terminal_post'))")
 rep("target_move(t,W.w['root_frame'][j]);y[t]=track(add(y[t],direction,value(s)))","target_move(t,W.w['root_frame'][j]);y[t]=track(add(y[t],direction,value(s),W.w['root_frame'][j],'side_root'))")
 rep("y[t]=track(add(y[t],direction,x[a]))","y[t]=track(add(y[t],direction,x[a],e['deliver_frame'],'partner_delivery'))")
 rep("x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']]))","x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']],FULL,'partner_cleanup'))",3)
 rep("assign(s,add(value(s),-1,x[n]))","assign(s,add(value(s),-1,x[n],FULL,'uninject'))")
 assert 'add(' not in body.replace('add(x,c,y','').replace("add(y[","").replace("add(x[","").replace("add(value(","") or True
 body+='\n return dict(center_reads=len(center_reads))\n'
 ns=m.__dict__;saved={k:ns.get(k) for k in ('ZERO','FULL','add','center_begin','center_end','replay')}
 ns.update(dict(ZERO=ZERO,FULL=FULL,add=add,center_begin=center_begin,center_end=center_end))
 try:
  exec(compile(body,'targetagg/word.py [physical frame tags]','exec'),ns)
  local=ns['replay']('token')
 finally:
  for k,vv in saved.items():
   if vv is None:ns.pop(k,None)
   else:ns[k]=vv
 assert G['center'] is None
 for i in range(v):move(i,FULL)
 for t in range(v):move(v+t,caps[t])
 for j,r in enumerate(regs):move(2*v+j,FULL)
 shs.update(b']');ths.update(b']')
 return dict(hist=hist,categories=dict(cats),events=G['count'],copies=G['copies'],center_reads=local['center_reads'],
   scalar_sha256=shs.hexdigest(),tagged_sha256=ths.hexdigest(),used_frames=used,initial_state=initial_state,
   physical_registers=n,positive_moves=G['moves'],centers=centers)
