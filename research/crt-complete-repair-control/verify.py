from pathlib import Path
import types,time,json,hashlib,argparse
p=Path(__file__).resolve().parent;r=p.parents[1]
def load(f):
 m=types.ModuleType(f.stem);m.__file__=str(f);exec(compile(f.read_bytes(),str(f),'exec'),m.__dict__);return m

def actual():
 m=load(p/'machine.py');crt=load(r/'research/unconditional-batched-crt/check_batched_crt.py');oracle=load(r/'research/crt-mask-repair-bridge/key_subroutine.py')
 rows=[crt.benes(crt.rotation(8,5,a))[2][1] for a in (0,2,4,0)];bits=tuple(b for row in rows for b in row);key=oracle.ReverseWordKey(2,bits)
 raw=[None]*4096;ideal=[None]*4096;holes=set()
 for x in range(4096):
  u,t,y=x>>10,(x>>8)&3,x&255
  v=crt.compact(u,t,y,lambda z:(bits[z&31],),positions=(2,),ybits=8)
  dest=(v[0]<<10)|(v[1]<<8)|v[2];raw[dest]=('R',x)
  ideal[(u<<10)|(t<<8)|(y^(bits[y&31]<<2))]=('R',x)
  if not crt.good(u,t,y,bits=2,positions=(2,),guard=6):holes.add(x)
 code,roles,stages=m.assemble(r);tapes={};tapes.update({x:['<',*('1'*v),'>','_'] for x,v in zip(('G','H','K','Y','J','B'),(2,2,6,8,2,0))});tapes['data']=['<',*raw,'>'];tapes['rom']=['L',*map(str,bits),'R'];tapes=m.prepare(roles,tapes)
 borrowed_before={x:list(tapes[x]) for x in ('G','H','K','Y','J','B','rom')}
 seen=[];phases={};key_start,key_end=stages['key_sites'][0];active={}
 def entry(pc,t,h,reg,steps,cells):
  q=int(''.join(t['work9'][1:13]),2);seen.append(q);active.update(q=q,start=h['work1'],steps=steps,cells=cells)
 def returned(pc,t,h,reg,steps,cells):
  want=key.key_of(f"{active['q']:012b}");got=''.join(t['work1'][active['start']:h['work1']]);
  if got!=want:raise ValueError(('actualkey',active['q'],got,want))
  if any(any(c!='_' for c in t[x]) or h[x] for x in t if x.startswith('key_')):raise ValueError('keycleanup')
 def phase(pc,t,h,reg,steps,cells):phases[pc]=(steps,cells)
 obs={key_start:entry,key_end:returned};obs.update({v:phase for k,v in stages.items() if k!='key_sites'})
 t=time.monotonic();out=m.execute(code,tapes,observe=obs);seconds=time.monotonic()-t
 if out['status']!='accept' or tapes['data']!=['<',*ideal,'>']:raise ValueError('fullendpoint')
 check_borrowed(borrowed_before,tapes)
 if seen!=sorted(holes):raise ValueError('actualholecalls')
 if any(out['heads'].values()):raise ValueError('heads')
 if any(any(v!='_' for v in tapes[x]) for x in roles):raise ValueError('privateblank')
 if any(v is not None for v in out['registers'].values()):raise ValueError('controlerase')
 return dict(status='PASS_ACTUAL_COMPLETE',program=len(code),steps=out['steps'],cells=out['cell_actions'],factor=m.control_bound(code),key_calls=len(seen),phases={str(k):list(v) for k,v in phases.items()},program_sha256=hashlib.sha256(json.dumps(code,separators=(',',':')).encode()).hexdigest())

def check_borrowed(before,tapes):
 for name,cells in before.items():
  if tapes[name]!=cells:raise ValueError('borrowed bytes changed '+name)

def need(ok,label):
 if not ok:raise ValueError(label)

def authenticate():
 hashes={}
 for row in json.loads((p/'SOURCES.json').read_text())['files']:
  if row['usage']!='input':continue
  raw=(r/row['path']).read_bytes();h=hashlib.sha256(raw).hexdigest()
  need(h==row['sha256'],'source hash '+row['path'])
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob')
  hashes[row['path']]=h
 return hashes

def controls():
 m=load(p/'machine.py');cm=load(p/'compiler.py');C=cm.C
 src={ns:(r/path).read_text() for ns,path in {'bridge':'research/crt-mask-repair-bridge/bridge.py','scanner':'research/crt-dense-guard-scan/machine.py'}.items()}
 def radix(fault=None):
  c=cm.Compiler(src,[]);flags=C(frozenset({'keep_buckets'}) if fault=='keep_buckets' else frozenset())
  c.call('bridge','sort_passes',[C('stencil'),C('bad'),C('b0'),C('b1'),flags],{});c.emit('halt','accept')
  keys=[6,1,7,0,5,2,4,3];cells=['<']
  for label,key in enumerate(keys):cells.extend([('R',label),*f'{key:03b}'])
  cells.append('>');tapes=dict(stencil=['<','1','1','1','>'],bad=cells,b0=['<'],b1=['<'])
  code=list(c.code)
  if fault=='skip_pass':tapes['stencil']=['<','1','1','>']
  result=m.execute(code,tapes,max_steps=100000)
  expected=['<']
  for label,key in sorted(enumerate(keys),key=lambda z:z[1]):expected.extend([('R',label),*f'{key:03b}'])
  expected.append('>')
  need(tapes['bad']==expected,'full key sort and key rotation')
  need(all(all(x=='_' for x in tapes[t][1:]) for t in ('b0','b1')),'bucket cleanup')
  need(not any(result['heads'].values()),'radix head return')
 radix();rejected=[]
 for label,text in [
  ('try_finally','def f(t):\n try:\n  t.read()\n finally:\n  t.write(1)\n'),
  ('while_else','def f(t):\n while False:\n  t.read()\n else:\n  t.write(1)\n'),
  ('for_else','def f(t):\n for x in (1,):\n  t.read()\n else:\n  t.write(1)\n'),
  ('nonempty_tape','def f(t):\n a = Tape(1)\n'),
  ('method_extra_arg','def f(t):\n t.read(1)\n')]:
  c=cm.Compiler({'probe':text},[])
  try:c.call('probe','f',[C('t')],{})
  except ValueError:rejected.append(label)
  else:raise ValueError('unsupported AST accepted '+label)

 for fault in ('keep_buckets','skip_pass'):
  try:radix(fault)
  except ValueError:rejected.append(fault)
  else:raise ValueError('missed '+fault)
 def carry(skip):
  c=cm.Compiler(src,[])
  for _ in range(5):c.emit('move',C('counter'),C(1))
  ret=c.call('scanner','increment_and_return',[C('counter'),C(skip)],{});c.emit('halt','accept')
  tapes={'counter':['<','1','1','1','1','>']};out=m.execute(c.code,tapes)
  need(tapes['counter']==['<','0','0','0','0','>'] and out['heads']['counter']==0 and out['registers'][ret[1]] is False,'complete carry wrap')
 carry(False)
 try:carry(True)
 except ValueError:rejected.append('carry_skipped_bit')
 else:raise ValueError('missed carry fault')
 code,roles,stages=m.assemble(r);factor=m.control_bound(code)
 bad=list(code);bad[0]=('jump',0)
 try:m.control_bound(bad)
 except ValueError:rejected.append('control_only_cycle')
 else:raise ValueError('cycle accepted')
 shared=['<','>'];borrowed={x:list(shared) for x in ('G','H','K','Y','J','B','data','rom')};borrowed['H']=borrowed['G']
 try:m.prepare(roles,borrowed)
 except ValueError:rejected.append('borrowed_role_alias')
 else:raise ValueError('alias accepted')
 # Actual producer/scanner/split path and positive-ROM key return, bounded at first call.
 def nested(skip_key=False):
  tapes={x:['<',*('1'*v),'>','_'] for x,v in zip(('G','H','K','Y','J','B'),(2,2,6,8,2,0))};tapes.update(data=['<',('R',123),'>'],rom=['L',*('1'*32),'R']);tapes=m.prepare(roles,tapes)
  short=list(code);entry,end=stages['key_sites'][0];short[end]=('halt','accept')
  if skip_key:short[entry]=('jump',end)
  out=m.execute(short,tapes,max_steps=4000000)
  key=load(r/'research/crt-mask-repair-bridge/key_subroutine.py').ReverseWordKey(2,(1,)*32).key_of('0'*12)
  need(tapes['work1'][1:14]==[('R',123),*key] and out['heads']['work1']==14,'direct nested key return and opaque prefix')
  need(all(all(v=='_' for v in tapes[x]) and out['heads'][x]==0 for x in tapes if x.startswith('key_')),'key private cleanup')
 nested()
 try:nested(True)
 except ValueError:rejected.append('skipped_nested_key')
 else:raise ValueError('skipped key accepted')
 before={'rom':['L','0','R']};changed={'rom':['L','1','R']}
 try:check_borrowed(before,changed)
 except ValueError:rejected.append('borrowed_rom_write')
 else:raise ValueError('borrowed corruption accepted')
 # Every emitted opcode has a finite instruction interpretation, never a source callback.
 allowed={'read','write','move','copy','not','field','record','eq','ne','in','notin','xorbit','andbit','orbit','branch','jump','halt'}
 need(all(i[0] in allowed for i in code),'instruction allowlist')
 need(code==m.assemble(r)[0],'deterministic static program')
 return dict(rejected=rejected,control_factor=factor,program_instructions=len(code))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--light',action='store_true');ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
 sources=authenticate();checks=controls()
 if args.light:print('PASS_REPAIR_CONTROL_LIGHT',json.dumps(checks));return
 result={'status':'PASS_COMPLETE_CRT_REPAIR_CONTROL','source_hashes':sources,'controls':checks,'actual':actual(),
         'code_hashes':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ('compiler.py','machine.py')}}
 a=result['actual'];bound=(a['factor']+1)*(1000*4096*13**2+2944*3287110+1)
 need(a['steps']<=bound,'complete conservative instruction bound');result['instruction_bound']=bound
 if args.write_result:(p/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 else:need(json.loads((p/'RESULT.json').read_text())==result,'frozen full receipt')
 print(result['status'],a['steps'],a['cells'],a['key_calls'])

if __name__=='__main__':main()
