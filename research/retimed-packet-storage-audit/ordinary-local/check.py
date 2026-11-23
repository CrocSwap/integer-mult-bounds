"""Source-executed byte bounds; not a fixed-tape or production-rank replay."""
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from fractions import Fraction as F
from functools import partial
from hashlib import sha256
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
import ast, inspect, json, sys
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'sources'
def need(ok,message):
    if not ok:raise ValueError(message)
SELECTED={
 'ordinary_carrier.py':['ordinary_swap'],'triangular_ordinary.py':['root_body'],
 'receiver.py':['OwnerBanks.route'],'direct_body.py':['scale_atom'],
 'module_atoms.py':['lower_tape','negate_tape','weighted_pair'],
 'quotient_route.py':['affine_packet','high_packet','quotient_right_route'],
 'limb_scale.py':['unit_scale'],'raw_binary.py':['Banks.clone','Banks.swap','Banks.xor'],
 'streaming_routes.py':['cold_swap_tape','type_route'],'compact_crt.py':['binary_swap']}
def node_at(filename,path):
    body=ast.parse((SOURCE/filename).read_text(),filename=filename).body
    for part in path.split('.'):
        node=next(x for x in body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part)
        body=node.body
    return node
def load_nodes(filename,names,env,mutator=None):
    tree=ast.Module(body=[deepcopy(node_at(filename,n)) for n in names],type_ignores=[])
    if mutator:tree=mutator.visit(tree);ast.fix_missing_locations(tree)
    exec(compile(tree,str(SOURCE/filename),'exec'),env)
def source_and_inventory():
    bindings=json.loads((HERE/'SOURCE-BINDINGS.json').read_text())
    need(bindings['commit']=='dfd25d553a843a946ca0b94130a5ff8943e98fdd','Wrong source head')
    for name,pin in bindings['files'].items():
        data=(SOURCE/name).read_bytes()
        need(len(data)==pin['size'] and sha256(data).hexdigest()==pin['sha256'],'Changed source '+name)
    actual=[]
    for file,names in SELECTED.items():
        for name in names:
            parent=node_at(file,name)
            for n in ast.walk(parent):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='work_tapes':
                    actual.append((file[:-3],name,n.lineno-parent.lineno+1,ast.literal_eval(n.args[0])))
    registered=json.loads((HERE/'ROLE-INVENTORY.json').read_text())
    expected=[(r['module'],r['body'],r['local_line'],r['slots']) for r in registered['work_sites']]
    need(sorted(actual)==sorted(expected),'Selected allocation-site coverage changed')
    need(sum(r[3] for r in actual)==91 and len(actual)==19,'Retained inventory')
    native=sum(r[3] for r in actual if r[0] not in {'ordinary_carrier','triangular_ordinary','compact_crt'} and r[1]!='cold_swap_tape')
    need(native==67,'Public cold binary entered weighted native A')
    return len(bindings['files'])
ACTIVE=None
class Tracked:
    def __init__(self,meter,key,limit):
        self.raw=BytesIO();self.meter=meter;self.key=key;self.limit=limit;self.peak=0
    def endpoint(self):
        self.peak=max(self.peak,self.raw.tell(),len(self.raw.getbuffer()))
        if self.peak>self.limit and not self.meter.failed:
            self.meter.failed=True;raise ValueError('BYTE_CAP '+self.key)
    def tell(self):return self.raw.tell()
    def seek(self,*args):
        n=self.raw.seek(*args);self.endpoint();return n
    def read(self,*args):
        data=self.raw.read(*args);self.endpoint();return data
    def write(self,data):
        n=self.raw.write(data);self.endpoint();return n
    def truncate(self,size=None):
        size=self.tell() if size is None else size
        need(not any(self.raw.getvalue()[size:]),'DIRTY_TRUNCATION '+self.key)
        return self.raw.truncate(size)
    def __enter__(self):return self
    def __exit__(self,*args):
        need(self.raw.getvalue()==b'' and self.tell()==0,'Unreturned work file '+self.key)
        self.meter.peaks[self.key]=max(self.meter.peaks.get(self.key,0),self.peak)
        self.meter.opened-=1;self.raw.close()
class Meter:
    def __init__(self,volume,type_factor=3,route_factor=1):
        self.volume=volume;self.type_factor=type_factor;self.route_factor=route_factor
        self.peaks={};self.opened=0;self.max_open=0;self.failed=False;self.calls=0
    def factory(self):
        frame=inspect.currentframe().f_back
        # The exact source TemporaryFile factory is invoked inside its list comprehension.
        while frame and not(frame.f_code.co_name in ('<listcomp>','work_tapes') and '_' in frame.f_locals):frame=frame.f_back
        need(frame is not None,'Missing source tuple allocation');index=frame.f_locals['_']
        while frame:
            if Path(frame.f_code.co_filename).parent==SOURCE and frame.f_code.co_name not in ('work_tapes','<listcomp>'):break
            frame=frame.f_back
        need(frame is not None,'Unidentified source allocation')
        name=frame.f_code.co_name;file=Path(frame.f_code.co_filename).stem;limit=self.volume
        if name=='type_route' and index<2:limit*=self.type_factor
        if name=='quotient_right_route':limit*=self.route_factor
        if name=='cold_swap_tape' and index>=2:limit=F(limit,9)
        if name=='binary_swap' and index>=2:limit=F(limit,4)
        self.opened+=1;self.calls+=1;self.max_open=max(self.max_open,self.opened)
        return Tracked(self,f'{file}.{name}:{index}',limit)
    def __enter__(self):
        global ACTIVE
        need(ACTIVE is None,'Nested test meter');ACTIVE=self;return self
    def __exit__(self,*args):
        global ACTIVE
        ACTIVE=None;need(self.opened==0,'Open work-file scope survived return')
def environment():
    env={'ExitStack':ExitStack,'contextmanager':contextmanager,'Fraction':F,'prod':prod,
         'partial':partial,'CHUNK':65536,'ZEROS':bytes(65536),'TemporaryFile':lambda:ACTIVE.factory(),
         'residue':lambda x,m:F(x).numerator*pow(F(x).denominator,-1,m)%m}
    load_nodes('streaming_routes.py',['read_exact','copy_bytes','write_zeros','erase','work_tapes','ternary_extent','join_buckets','trit_swap','cold_swap_tape','integer_scale','negate_field','shift_field','type_route'],env)
    load_nodes('module_atoms.py',['component_widths','total_width','chart_width','pair_shape','lower_tape','negate_tape','weighted_pair'],env)
    load_nodes('direct_body.py',['scale_atom'],env);load_nodes('limb_scale.py',['unit_scale'],env)
    names=[n.name for n in ast.parse((SOURCE/'quotient_route.py').read_text()).body if isinstance(n,ast.FunctionDef)]
    load_nodes('quotient_route.py',names,env);load_nodes('raw_binary.py',['Banks'],env)
    load_nodes('receiver.py',['OwnerBanks'],env);load_nodes('compact_crt.py',['binary_swap'],env)
    return env
def data(size,seed=1):return bytes(((i*73+(i//7)*19+seed)%256) for i in range(size))
def act(env,name,raw,args,kwargs=None,**meter_kwargs):
    target=BytesIO()
    with Meter(len(raw),**meter_kwargs) as meter:env[name](BytesIO(raw),target,*args,**(kwargs or {}))
    need(len(target.getvalue())==len(raw),'Complete output extent '+name)
    return target.getvalue(),meter
def unpack(value,radices):
    out=[]
    for r in reversed(radices):value,c=divmod(value,r);out.append(c)
    need(value==0,'Address exceeds declared field');return list(reversed(out))
def pack(values,radices):
    out=0
    for x,r in zip(values,radices):out=out*r+x
    return out
def scalar_oracle(raw,prefix,radices,piece,c):
    side=prod(radices);out=bytearray(len(raw))
    for p in range(prefix):
        for x in range(side):
            y=pack([(a*F(c).numerator*pow(F(c).denominator,-1,r))%r for a,r in zip(unpack(x,radices),radices)],radices)
            a=(p*side+x)*piece;b=(p*side+y)*piece;out[b:b+piece]=raw[a:a+piece]
    return bytes(out)

def primitive_cases(env):
    cases={};all_peaks={};allocations=0
    def remember(kind,meter):
        nonlocal allocations
        cases[kind]=cases.get(kind,0)+1;allocations+=meter.calls
        for key,p in meter.peaks.items():all_peaks[key]=max(all_peaks.get(key,0),F(p,meter.volume))
    factors=sorted({F(a,b) for a in range(-20,21) if a and a%3 for b in range(1,21) if b%3})
    for layout,prefix,piece in (((1,1,0,1),2,3),((2,1,0,1),3,2),((1,2,1,1),1,2),((1,3,0,1),1,2)):
        radices=[3**w for w in env['component_widths'](layout)];raw=data(prefix*prod(radices)*piece)
        for factor in factors:
            out,m=act(env,'scale_atom',raw,(layout,prefix,piece,factor))
            need(out==scalar_oracle(raw,prefix,radices,piece,factor),'Direct factor address oracle');remember('direct_scale',m)
    for digits,prefix,piece,unit in product(range(1,8),(1,2),(1,3),(2,4,5,8,17)):
        raw=data(prefix*3**digits*piece,digits)
        out,m=act(env,'unit_scale',raw,(digits,prefix,piece,unit,env['cold_swap_tape']))
        need(out==scalar_oracle(raw,prefix,[3**digits],piece,unit),'General unit address oracle');remember('unit_scale',m)
    for layout,prefix,gap,piece in product(((1,1,0,1),(2,1,0,1),(1,2,1,1)),(1,2),(1,2),(1,3)):
        radices=[3**w for w in env['component_widths'](layout)];side=prod(radices)
        raw=data(prefix*side*gap*side*piece,7);coefficient=lambda p:2+3*p
        out,m=act(env,'lower_tape',raw,(layout,prefix,gap,piece,coefficient));expected=bytearray(len(raw))
        for p,x,g,y in product(range(prefix),range(side),range(gap),range(side)):
            xx,yy=unpack(x,radices),unpack(y,radices)
            z=pack([(b+coefficient(p)*a)%r for a,b,r in zip(xx,yy,radices)],radices)
            a=(((p*side+x)*gap+g)*side+y)*piece;b=(((p*side+x)*gap+g)*side+z)*piece
            expected[b:b+piece]=raw[a:a+piece]
        need(out==expected,'Product-module lower address oracle');remember('lower',m)
        small=data(prefix*side*piece);out,m=act(env,'negate_tape',small,(layout,prefix,piece))
        need(out==scalar_oracle(small,prefix,radices,piece,-1),'Module negation oracle');remember('negate',m)
        weight=lambda p:2+3*p
        out,m=act(env,'weighted_pair',raw,(layout,prefix,gap,piece,weight,env['cold_swap_tape']))
        back,m2=act(env,'weighted_pair',out,(layout,prefix,gap,piece,weight,env['cold_swap_tape']))
        need(back==raw,'Stopped weighted-pair opaque-record return');remember('weighted_pair',m);remember('weighted_pair',m2)
    for rows,types,piece in product((1,2,4),(1,2,4,5,8,10),(1,3)):
        raw=data(rows*types*piece,31);out,m=act(env,'type_route',raw,(rows,types,piece))
        expected=b''.join(raw[(r*types+t)*piece:(r*types+t+1)*piece] for t in range(types) for r in range(rows))
        need(out==expected,'Type transpose address oracle');remember('type_forward',m)
        back,m=act(env,'type_route',out,(rows,types,piece),{'inverse':True})
        need(back==raw,'Type inverse complete payload return');remember('type_inverse',m)
    for bits,prefix,gap,piece in product(range(1,4),(1,2),(1,2),(1,3)):
        side=2**bits;raw=data(prefix*side*gap*side*piece,55)
        out,m=act(env,'binary_swap',raw,(bits,prefix,gap,piece));expected=bytearray(len(raw))
        for p,x,g,y in product(range(prefix),range(side),range(gap),range(side)):
            a=(((p*side+x)*gap+g)*side+y)*piece;b=(((p*side+y)*gap+g)*side+x)*piece
            expected[b:b+piece]=raw[a:a+piece]
        need(out==expected,'Public binary cold oracle');remember('binary_cold',m)
    for digits,fields,piece in product((1,2),(2,3),(1,2)):
        side=3**digits;matrix=((2,1),(1,1));shift=(1,side-1);raw=data(side**fields*piece,2)
        out,m=act(env,'affine_packet',raw,(digits,fields,piece,matrix,shift,env['cold_swap_tape']))
        expected=bytearray(len(raw))
        for address in range(side**fields):
            x=unpack(address,[side]*fields)
            y=[(sum(c*z for c,z in zip(row,x))+s)%side for row,s in zip(matrix,shift)]+x[2:]
            dest=pack(y,[side]*fields);expected[dest*piece:(dest+1)*piece]=raw[address*piece:(address+1)*piece]
        need(out==expected,'Affine full spectator address oracle');remember('affine',m)
    word=(('add',0,1,1),('scale',1,2),('swap',0,1))
    inverse=(('swap',0,1),('scale',1,F(1,2)),('add',0,1,-1))
    for n,digits,groups in ((2,1,1),(2,1,2),(3,1,1),(2,2,1)):
        body=3**(2*n*digits);high=3**((digits-1)*env['free_count'](n))
        raw=data(groups*env['low_count'](n)*high*body,9)
        out,m=act(env,'quotient_right_route',raw,(n,digits,groups,body,word),{'previous_swap':env['cold_swap_tape']})
        back,m2=act(env,'quotient_right_route',out,(n,digits,groups,body,inverse),{'previous_swap':env['cold_swap_tape']})
        need(back==raw,'Covered whole-owner return');remember('quotient_forward',m);remember('quotient_inverse',m2)
    raw=data(81,72);backing=BytesIO()
    banks=env['OwnerBanks'](backing,2,len(raw),lambda s,t,w:env['copy_bytes'](s,t,len(raw)))
    with Meter(len(raw)) as meter:
        first=banks.zero();banks.install(first,BytesIO(raw));second=banks.clone(first)
        different=data(len(raw),111);banks.install(second,BytesIO(different))
        banks.swap(first,second);banks.xor(first,second);banks.route(first,())
        actual=BytesIO();banks.read(first,actual)
        need(actual.getvalue()==bytes(a^b for a,b in zip(raw,different)),'Owner clone/swap/XOR/route records')
    remember('owner_operations',meter)
    return cases,all_peaks,allocations

class DropCurrentErase(ast.NodeTransformer):
    def visit_Expr(self,node):
        x=node.value
        if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='erase' and len(x.args)==1 and isinstance(x.args[0],ast.Name) and x.args[0].id=='current':return ast.Pass()
        return self.generic_visit(node)
class InflateOddTail(ast.NodeTransformer):
    def visit_AugAssign(self,node):
        if isinstance(node.target,ast.Name) and node.target.id=='tail' and isinstance(node.op,ast.Mult) and isinstance(node.value,ast.Constant) and node.value.value==3:node.value=ast.Constant(9)
        return self.generic_visit(node)
def rejected(call,phrase=None):
    try:call()
    except (ValueError,EOFError) as e:
        if phrase:need(phrase in str(e),'Wrong control rejection: '+str(e))
        return str(e)
    raise ValueError('Negative control did not fail')
def controls(env):
    tests={};mutant=dict(env);load_nodes('direct_body.py',['scale_atom'],mutant,DropCurrentErase())
    tests['missing_scale_erase']=rejected(lambda:act(mutant,'scale_atom',data(54),((2,1,0,1),2,3,F(-10,7))),'BYTE_CAP')
    tests['one_volume_type_cap']=rejected(lambda:act(env,'type_route',data(40),(2,4,5),type_factor=1),'BYTE_CAP')
    bad=dict(env);load_nodes('limb_scale.py',['unit_scale'],bad,InflateOddTail())
    tests['inflated_saved_tail']=rejected(lambda:act(bad,'unit_scale',data(27),(3,1,1,2,env['cold_swap_tape'])))
    tests['overlong_coefficient_runs']=rejected(lambda:act(env,'lower_tape',data(9),((1,1,0,1),1,1,1),{'runs':lambda:iter(((2,1),))}))
    raw=data(16);args=(2,1,1,1,(('swap',0,1),));_,m=act(env,'quotient_right_route',raw,args,route_factor=4)
    tag=m.peaks['quotient_route.quotient_right_route:1'];need(tag==64,'Exact standalone API tag counterexample')
    tests['uninstalled_small_body']=rejected(lambda:act(env,'quotient_right_route',raw,args,route_factor=3),'BYTE_CAP')
    tests['small_body_tag_ratio']=str(F(tag,len(raw)))
    fake=Meter(1);t=Tracked(fake,'control',1);t.write(b'\x01')
    tests['dirty_truncate']=rejected(lambda:t.truncate(0),'DIRTY_TRUNCATION')
    public=node_at('ordinary_carrier.py','ordinary_swap')
    calls=[n for n in ast.walk(public) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='binary_swap']
    need(len(calls)==1,'Public binary location changed')
    need(not any(isinstance(n,ast.Name) and n.id=='binary_swap' for n in ast.walk(node_at('ordinary_carrier.py','ternary'))),'Binary cold leaked into ternary predecessor')
    return tests

def shape_guards():
    cases=0
    for n,width,f,u,old,gap,suffix,remainder,b in product((2,3,4),(1,2),(1,2),(1,2),(1,2),(1,3),(1,2),(0,1),(1,17)):
        alpha=3**width;q=prod(3**j-1 for j in range(1,n+1));h=3**((width-1)*n*(n+1)//2)
        w=u*b*q*h*old*alpha**(2*(n*f+remainder))*gap*suffix
        body=old*alpha**(2*n*f)*(gap*alpha**remainder)*(suffix*alpha**remainder)
        v=u*q*h*body
        need(b*v==w and body>=n*n,'Full residual owner or tag guard')
        cases+=1
    need(F(17)+F(54,17)<21,'Uniform production A')
    need(4196+254*21==9530 and 37764+2286*21==85770,'Composition substitution')
    return cases

def main():
    source_count=source_and_inventory();env=environment()
    cases,peaks,allocations=primitive_cases(env);negative=controls(env);shapes=shape_guards()
    expected={f'{file[:-3]}.{node_at(file,name).name}:{i}'
              for file,names in SELECTED.items() for name in names
              for node in ast.walk(node_at(file,name))
              if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='work_tapes'
              for i in range(ast.literal_eval(node.args[0]))
              if file not in ('ordinary_carrier.py','triangular_ordinary.py')}
    expected-={f'limb_scale.unit_scale:{i}' for i in range(3,7)}
    expected|={f'limb_scale.odd_step:{i}' for i in range(7)}|{'limb_scale.carry_step:0'}
    need(expected<=set(peaks),'A retained local slot was not exercised: '+repr(sorted(expected-set(peaks))))
    report={'status':'PASS_UNIFORM_ORDINARY_LOCAL_BYTES','source_files':source_count,
      'inventory_slots':91,'native_transient_slots':67,'inactive_public_binary_slots':6,
      'uniform_coefficient':'17+54/B','uniform_B_ge_17':21,'native_seven_stage_T':9530,'native_seven_stage_X':85770,
      'cases':cases,'shape_checks':shapes,'work_file_allocations':allocations,
      'peak_ratios_by_source_position':{k:str(v) for k,v in sorted(peaks.items())},
      'negative_controls':negative,'python':sys.version.split()[0],
      'scope':'historical byte endpoints for installed complete-field calls; no production ranks, headers, machine transitions or owner-capacity proof'}
    (HERE/'EVIDENCE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('status','inventory_slots','native_transient_slots','uniform_coefficient','cases','shape_checks','work_file_allocations')},sort_keys=True))

if __name__=='__main__':main()
