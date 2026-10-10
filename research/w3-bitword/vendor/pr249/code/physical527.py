"""Fresh source527 physical event lowering. Substantial OpenAI Codex assistance.
Derived from the PR234 physical telescope; see root provenance and notices.
"""
from pathlib import Path
from collections import Counter
from array import array
from types import SimpleNamespace
import ast,hashlib,json,gzip,sys,time
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
def run(context,source_text,output_dir=None,source_pins=None):
 D=Path(output_dir)if output_dir is not None else None
 if D is not None:D.mkdir(parents=True,exist_ok=True)
 m=SimpleNamespace(**context);W=m.W;C=m.C;v=W.v;regs=m.regs;n=2*v+len(regs)
 source=source_text;assert len(regs)==16587
 ZERO=W.register([]);FULL=W.w['full_frame']
 sha=lambda b:hashlib.sha256(b).hexdigest()
 def physical_id(s):
  r=W.phys[s];return m.borrow[r]if r in m.borrow else m.idx[r]
 def id_expr(node):
  if isinstance(node,ast.Subscript)and isinstance(node.value,ast.Name)and node.value.id in('x','y'):
   return node.slice if node.value.id=='x'else ast.BinOp(left=ast.Name(id='v',ctx=ast.Load()),op=ast.Add(),right=node.slice)
  if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='value':return ast.Call(func=ast.Name(id='physical_id',ctx=ast.Load()),args=node.args,keywords=[])
  raise AssertionError(('unrecognized physical address',ast.unparse(node)))
 def digest_add(h,row):
  h.update(json.dumps(row,separators=(',',':')).encode());h.update(b'\n')
 scalar_digest=hashlib.sha256();scalar_count=0;scalar_coeff=Counter()
 def observe(dst,c,src):
  nonlocal scalar_count
  assert dst!=src;digest_add(scalar_digest,[dst,src,c]);scalar_count+=1;scalar_coeff[abs(c)]+=1
 class Observe(ast.NodeTransformer):
  def visit_Call(self,node):
   self.generic_visit(node)
   if isinstance(node.func,ast.Name)and node.func.id=='add'and node.lineno<=205:
    dx,sy=id_expr(node.args[0]),id_expr(node.args[2]);node.func.id='observed_add';node.args += [dx,sy]
   return node
 q=Observe().visit(ast.parse(source));fn=q.body[0];i=next(i for i,z in enumerate(fn.body)if isinstance(z,ast.FunctionDef)and z.name=='add');fn.body.insert(i+1,ast.parse('def observed_add(x,c,y,dx,sy):\n observe(dx,c,sy)\n return add(x,c,y)').body[0]);ast.fix_missing_locations(q)
 m.physical_id=physical_id;m.observe=observe;exec(compile(q,'<portable527 scalar observer>','exec'),m.__dict__);scalar=m.replay();scalar_sha=scalar_digest.hexdigest();print('PASS independent F2 event observer',scalar_count,scalar_sha,dict(scalar_coeff),flush=True)
 state={i:W.w['source_frame'][i]for i in range(v)};state.update({v+t:ZERO for t in range(v)});state.update({2*v+j:W.gauge[r]['frame']if r in W.gauge else ZERO for j,r in enumerate(regs)});initial_state=state.copy();caps={t:W.register(W.module.kernel([C.cov[t]],W.h)[0])for t in range(v)}
 records=array('i');hist=Counter();categories=Counter();coefficients=Counter();centers=[];center=None;used_frames=set(state.values());subcache={};count=0;tag_hash=hashlib.sha256();projection=hashlib.sha256()
 # The line binding is checked against the exact generated source digest below.
 tags={43:("group['frame']",'equal_inverse'),50:("group['frame']",'rank_inverse'),56:("group['frame']",'echelon_inverse'),62:("W.gauge[s]['frame']",'paired_alias_corruption'),67:("W.gauge[s]['frame']",'fresh_source_read'),81:("W.gauge[s]['frame']",'echelon_read'),96:("read_frames[s,k]",'equal_read'),98:("read_frames[s,k]",'equal_corruption'),108:("W.gauge[s]['frame']if s in W.gauge else ZERO",'dirty_read'),113:("W.opframe[i]if sign==1 else FULL",'gate'),116:("W.w['source_frame'][n]",'inject'),120:("kpair[r['source']]['mix_frame']",'gauge_mix'),127:("kpair[b]['mix_frame']",'partner_mix'),133:('ZERO','center'),137:('ZERO','echelon_setup'),142:('ZERO','rank_setup'),147:('ZERO','equal_setup'),151:('ZERO','terminal_pre'),159:('f','anchor_inject'),166:('W.opframe[i]','terminal_write'),172:("e['root_frame']",'terminal_post'),181:("W.w['root_frame'][j]",'side_root'),184:("kpair[b]['mix_frame']",'partner_mix'),186:("e['deliver_frame']",'partner_delivery'),189:('FULL','partner_cleanup'),192:('FULL','partner_cleanup'),201:('FULL','anchor_restore'),204:('FULL','partner_cleanup'),205:('FULL','uninject')}
 category_names=sorted(set(k for f,k in tags.values())|{'forward_gate','cleanup_gate'});kind_ids={k:i for i,k in enumerate(category_names)}
 def move(i,f):
  used_frames.add(f);old=state[i]
  if old==f:return
  if(old,f)not in subcache:subcache[old,f]=C.sub(old,f)
  assert subcache[old,f],('physical descent',i,old,f,C.dimf[old],C.dimf[f])
  d=C.dimf[f]-C.dimf[old];assert d>=0
  records.extend((0,i,old,f,d,0))
  if d:hist[d]+=1
  state[i]=f
 def physical_add(x,c,y,f,kind):
  nonlocal count
  assert x!=y;move(x,f);physical_y=y
  if kind=='center':assert center is not None and center['source']==y and f==ZERO;physical_y=n
  else:move(y,f)
  records.extend((1,x,physical_y,c,f,kind_ids[kind]));digest_add(projection,[x,y,c]);digest_add(tag_hash,[x,physical_y,c,f,kind]);count+=1;categories[kind]+=1;coefficients[abs(c)]+=1
  return x
 def center_begin(source,frame):
  nonlocal center
  assert center is None;move(source,frame);rank=C.dimf[frame];assert rank==22;hist[rank]+=1
  center=dict(source=source,frame=frame,rank=rank,first_event=count,temporary=n,copy_output_frame=ZERO);centers.append(center);records.extend((2,source,n,frame,ZERO,rank))
 def center_end():
  nonlocal center
  assert center is not None;center['after_event']=count;center['scatter_reads']=count-center['first_event'];assert center['scatter_reads']==220
  records.extend((3,center['source'],n,center['frame'],ZERO,center['rank']));center=None
 class Tag(ast.NodeTransformer):
  def visit_Call(self,node):
   self.generic_visit(node)
   if isinstance(node.func,ast.Name)and node.func.id=='add'and node.lineno<=205:
    frame,kind=tags[node.lineno];node.func.id='physical_add';kindnode=ast.parse("'forward_gate'if sign==1 else'cleanup_gate'",mode='eval').body if kind=='gate'else ast.Constant(kind);node.args += [ast.parse(frame,mode='eval').body,kindnode]
   return node
 q=Tag().visit(ast.parse(source));fn=q.body[0];end=next(i for i,z in enumerate(fn.body)if isinstance(z,ast.If)and ast.unparse(z.test)=='binary');fn.body=fn.body[:end]+[ast.parse('return dict(center_reads=len(center_reads))').body[0]]
 fn.body=[z for z in fn.body if not(isinstance(z,ast.FunctionDef)and z.name=='add')]
 for node in ast.walk(fn):
  if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='unit'for t in node.targets):node.value=ast.parse('lambda i:i',mode='eval').body
  if isinstance(node,ast.FunctionDef)and node.name=='target_move':node.body.insert(0,ast.parse('move(v+t,f)').body[0])
  if isinstance(node,ast.FunctionDef)and node.name=='source_move':node.body.insert(0,ast.parse('move(physical_id(s),f)').body[0])
 # Modify the center loop without changing any scalar expression or event order.
 centerloop=next(z for z in fn.body if isinstance(z,ast.For)and z.lineno==129)
 centerloop.target=ast.parse('(j,(r,s))',mode='eval').body;centerloop.target.ctx=ast.Store();centerloop.target.elts[0].ctx=ast.Store();centerloop.target.elts[1].ctx=ast.Store()
 for z in centerloop.target.elts[1].elts:z.ctx=ast.Store()
 centerloop.iter=ast.Call(func=ast.Name(id='enumerate',ctx=ast.Load()),args=[centerloop.iter],keywords=[])
 block=centerloop.body[0];assert isinstance(block,ast.If);block.body.insert(0,ast.parse("center_begin(value(s),W.w['root_frame'][j])").body[0]);block.body.append(ast.parse('center_end()').body[0])
 ast.fix_missing_locations(q);body=ast.unparse(q);
 if D is not None:(D/'generated-physical-word.py').write_text(body+'\n')
 m.__dict__.update(dict(physical_id=physical_id,move=move,physical_add=physical_add,center_begin=center_begin,center_end=center_end,ZERO=ZERO,FULL=FULL))
 exec(compile(q,'<portable527 physical word>','exec'),m.__dict__);local=m.replay('token');assert center is None
 for i in range(v):move(i,FULL)
 for t in range(v):move(v+t,caps[t])
 for j,r in enumerate(regs):move(2*v+j,FULL)
 assert count==scalar_count and projection.hexdigest()==scalar_sha and coefficients==scalar_coeff
 assert len(centers)==24 and local['center_reads']==5280
 result=dict(status='PASS_PHYSICAL527_EXACT_SCALAR_PROJECTION_AND_MONOTONE_FRAME_TAGS',scalar_source_sha256=sha(source.encode()),scalar_projection_sha256=scalar_sha,tagged_scalar_sha256=tag_hash.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coefficients),categories=dict(categories),category_names=category_names,physical_registers=n,independent_dirty_registers=len(regs),source_heads=len(m.borrow),positive_rank_moves=sum(hist.values())-24,copied_centers=len(centers),copied_center_blocks=centers,center_scatter_reads=local['center_reads'],paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(k*v for k,v in hist.items()),initial_independent_entrances=dict(Counter(C.dimf[initial_state[2*v+j]]for j in range(len(regs))if C.dimf[initial_state[2*v+j]])),used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used_frames)],input_pins=dict(source_pins or {}),physical_emitter_sha256=sha(Path(__file__).read_bytes()))
 
 if D is not None:
  (D/'physical.json').write_text(json.dumps(result,indent=2)+'\n')
  (D/'records.bin.gz').write_bytes(gzip.compress(records.tobytes(),mtime=0))
 print('PASS PHYSICAL',count,'records',len(records)//6,'rankmass',result['paid_rank_mass'],'tagged',result['tagged_scalar_sha256'],flush=True)
 
 return dict(context=m.__dict__,W=W,C=C,records=records,physical=result,initial_state=initial_state,ZERO=ZERO,FULL=FULL,result=result,scalar_result=scalar)
