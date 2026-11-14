"""Read-only exact source coverage and all fixed dispatch/relocation checks."""
from pathlib import Path
from hashlib import sha256,sha1
import ast,json,types,sys
HERE=Path(__file__).resolve().parent
def need(x,s):
 if not x:raise ValueError(s)
def load(path,name):
 m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def scope_check(raw):
 tree=ast.parse(raw);calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
 need(sum(isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='owner' and n.func.attr=='simple' for n in calls)==1,'one literal simple dispatch')
 need(not any(isinstance(n.func,ast.Subscript) and isinstance(n.func.value,ast.Name) and n.func.value.id=='original' for n in calls),'no saved-provider fallback call')

def dispatch_check(code,start,row,slot,symbol,target,override=None):
 pc=start;head=0;steps=0;read_positions=[];physical=None;selector=64+row[1]
 frame=['L']+[str((slot>>i)&1) for i in range(6)]+['R']
 while True:
  instruction=(override or {}).get(pc,code[pc]);op=instruction[0];steps+=1;need(steps<=31,'finite dispatch path')
  if op in('R','W','M') and instruction[1]<64:
   need(physical is None and head==0 and instruction[1]==slot and op==row[0],'exact physical slot/op and returned selector')
   physical=pc
   if op=='R':pc=instruction[2][symbol]
   else:need(instruction[2]==row[2],'exact literal operation');pc+=1
  elif op=='R':
   need(instruction[1]==selector and 0<=head<8,'only correct descriptor read');read_positions.append(head);pc=instruction[2][frame[head]]
  elif op=='M':
   need(instruction[1]==selector and 0<=head+instruction[2]<8,'bounded selector movement');head+=instruction[2];pc+=1
  elif op=='J':pc=instruction[1]
  else:raise ValueError('unexpected dispatch instruction')
  if physical is not None and pc==target:break
 need(head==0 and read_positions==list(range(8)) and steps==(30 if row[0]=='R' else 31),'complete fixed dispatch cost')
 return physical

def main():
 pins=json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
 for item in pins:
  raw=(HERE/item['local']).read_bytes();need(len(raw)==item['bytes'] and sha256(raw).hexdigest()==item['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'exact retained source object')
 root=HERE/'inputs/all-divisions/inputs/divider/inputs/headers/inputs/keypass/inputs/route/inputs/point/inputs/predecessor/research'
 sites={}
 for rel in('encoded-current-crt/producer.py','encoded-crt-leaf-payload/frozen/inverse_producer.py'):
  tree=ast.parse((root/rel).read_bytes());rows=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Attribute) and n.func.value.attr=='raw':rows.append((n.lineno,n.func.attr))
  need(len(rows)==16 and {name for _,name in rows}=={'add','compare','subtract_exact','divmod'},'exact closed raw method inventory');sites[rel]=sorted(rows)
 word=ast.parse((root/'r437-preparation-composition/predecessor4025/source/words.py').read_bytes());unsigned=next(n for n in word.body if isinstance(n,ast.ClassDef) and n.name=='Unsigned');exact=next(n for n in unsigned.body if isinstance(n,ast.FunctionDef) and n.name=='subtract_exact')
 need([n.func.attr for n in ast.walk(exact) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]==['subtract'],'finite subtract_exact delegates to covered provider')
 raw=(HERE/'binding.py').read_text();scope_check(raw)
 try:scope_check(raw.replace('return owner.simple(raw,a,b,kind)',"return original['add'](raw,a,b)"))
 except ValueError:pass
 else:raise ValueError('provider fallback mutant escaped source check')
 d=load(HERE/'inputs/all-divisions/inputs/divider/divider.py','B12scd');a=load(HERE/'arithmetic.py','B12sca');old,oldlabels,om=d.compile_divider();code,labels,meta=a.compile_arithmetic(d);logical,ll=a.logical_graph(d)
 need(code[:len(old)]==old and len(old)==336150,'entire exact old graph prefix')
 need(all(meta['entries'][k]==v for k,v in om['entries'].items()) and meta['setters']==om['setters'],'all old entry/setter addresses')
 mapping=meta['logical_to_physical'][len(om['logical_to_physical']):];need(len(mapping)==len(logical),'complete new relocation map')
 count=0;witness=None
 for pc,row in enumerate(logical):
  start=mapping[pc];op=row[0]
  if op in('R','W','M') and row[1]<4:
   for slot in range(64):
    for symbol in(d.ALPHABET if op=='R' else('0',)):
     target=mapping[row[2][symbol]] if op=='R' else mapping[pc+1]
     got=dispatch_check(code,start,row,slot,symbol,target);count+=1
     if witness is None and op=='M':witness=(start,row,slot,symbol,target,got)
  elif op=='R':need(code[start]==('R',row[1],{s:mapping[t] for s,t in row[2].items()}),'relocated direct read')
  elif op=='J':need(code[start]==('J',mapping[row[1]]),'relocated jump')
  else:need(code[start]==row,'unchanged direct logical operation')
 for name in('COMPARE','ADD','SUBTRACT'):need(meta['entries'][name]==mapping[ll[name]],'new fixed entry address')
 start,row,slot,symbol,target,physical=witness;bad={physical:(row[0],(slot+1)%64,row[2])}
 try:dispatch_check(code,start,row,slot,symbol,target,bad)
 except ValueError:pass
 else:raise ValueError('wrong physical port mutant escaped')
 print(json.dumps({'status':'PASS','source_objects':len(pins),'source_sites':sites,'graph':d.digest(code),'locations':len(code),'unchanged_old_locations':len(old),'new_logical_locations':len(logical),'dispatch_paths':count,'fallback_mutant_rejected':True,'wrong_port_mutant_rejected':True},indent=2,sort_keys=True))
if __name__=='__main__':main()
