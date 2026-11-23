#!/usr/bin/env python3
"""Independent interval and source-caller review; no author checker imported."""
from contextlib import contextmanager, nullcontext
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache, partial
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
from types import SimpleNamespace
import argparse
import ast
import inspect
import json

PROOF_PIN = "b1582d78063be51e057f3d6bcf5819134f4b1a3a62fed1bf90d2411dc67684ca"
AUTHOR_PIN = "e902547ef24bd236818c332b71cdc8bb17b1dc70113535a7377a68a4d422c0c3"


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def load(source, filename, names, env):
    tree = ast.parse((source/filename).read_text())
    nodes = []
    for name in names.split():
        body = tree.body
        for part in name.split('.'):
            node = next(x for x in body if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name == part)
            body = node.body
        nodes.append(deepcopy(node))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source/filename), 'exec'), env)


class BudgetViolation(AssertionError):
    pass


class Interval:
    """No payload array: exact cursor, logical interval and historical endpoint."""
    def __init__(self, length=0, cap=None, role='external'):
        self.length = self.peak = length
        self.cursor = 0
        self.cap, self.role = cap, role

    def tell(self):
        return self.cursor

    def seek(self, offset, whence=0):
        position = (0, self.cursor, self.length)[whence]+offset
        need(0 <= position <= self.length, 'seek outside complete interval')
        self.cursor = position
        return position


def grow(target, amount):
    end = target.cursor+amount
    need(amount >= 0, 'negative copy')
    if target.cap is not None and end > target.cap:
        raise BudgetViolation('pre-write endpoint: '+target.role)
    target.cursor = end
    target.length = max(target.length, end)
    target.peak = max(target.peak, end)


def copy(source, target, amount):
    need(0 <= amount <= source.length-source.cursor, 'short source interval')
    source.cursor += amount
    if target is not None:
        grow(target, amount)


def erase(tape):
    # Contract of the retained erase primitive; historical allocation survives.
    tape.cursor = tape.length = 0


class Model:
    def __init__(self, source):
        self.bound, self.small_helpers = 0, False
        self.peaks = {}

        @contextmanager
        def work_tapes(count):
            caller = inspect.currentframe().f_back.f_back
            name, site = caller.f_code.co_name, caller.f_code.co_qualname
            caps = [self.bound]*count
            if name == 'type_route':
                caps = [3*self.bound, 3*self.bound, self.bound, self.bound, self.bound]
            if self.small_helpers and name in {'lower_tape', 'negate_tape', 'weighted_pair'}:
                caps = [F(self.bound,17)]*count
            tapes = [Interval(cap=cap, role=site+':'+str(i)) for i,cap in enumerate(caps)]
            try:
                yield tapes
            finally:
                for tape in tapes:
                    self.peaks[tape.role] = max(self.peaks.get(tape.role, F(0)), F(tape.peak,self.bound))
                    erase(tape)

        self.env = dict(work_tapes=work_tapes, copy_bytes=copy, write_zeros=grow,
                        erase=erase, Fraction=F, prod=prod)
        load(source,'streaming_routes.py','ternary_extent join_buckets integer_scale negate_field shift_field type_route',self.env)
        load(source,'module_atoms.py','component_widths total_width chart_width lower_tape negate_tape weighted_pair',self.env)
        load(source,'direct_body.py','scale_atom',self.env)
        load(source,'limb_scale.py','unit_scale',self.env)

    def previous(self, source, target, width, prefix, gap, suffix):
        size = prefix*3**(2*width)*gap*suffix
        need(size <= self.bound, 'preceding argument expanded')
        copy(source,target,size)

    def run(self, name, size, args, kwargs=None, ambient_factor=1):
        self.bound = size*ambient_factor
        target = Interval()
        self.env[name](Interval(size),target,*args,**(kwargs or {}))
        need(target.length == size, 'not one complete output: '+name)


def intervals(source):
    model = Model(source)
    counts = dict(scale=0,lower=0,negate=0,pair=0,type=0,unit=0)
    factors = (F(1),F(-1),F(2),F(5),F(7),F(19),F(20),F(2,5),F(-20,19),F(19,20))
    for layout,prefix,piece in product(((1,1,0,0),(1,3,0,0),(2,1,1,2),(1,2,2,1)),(1,3),(1,2)):
        width = model.env['total_width'](layout)
        for factor in factors:
            model.run('scale_atom',prefix*3**width*piece,(layout,prefix,piece,factor))
            counts['scale'] += 1
        for gap in (1,2):
            size = prefix*3**(2*width)*gap*piece
            runs = lambda p=prefix: iter(((1,2),(p-1,5))) if p>1 else iter(((1,2),))
            model.run('lower_tape',size,(layout,prefix,gap,piece),{'runs':runs})
            model.run('weighted_pair',size,(layout,prefix,gap,piece,None,model.previous),{'runs':runs})
            counts['lower'] += 1
            counts['pair'] += 1
        model.run('negate_tape',prefix*3**width*piece,(layout,prefix,piece))
        counts['negate'] += 1
    # Whole compiler and smaller line uses share the same fixed type roles.
    for rows,types,piece,ambient,inverse in product((1,3),(2,4,8,16,17,26,28),(1,2),(1,17),(False,True)):
        model.run('type_route',rows*types*piece,(rows,types,piece),{'inverse':inverse},ambient)
        counts['type'] += 1
    for digits,unit in product(range(1,9),(2,5,8,17)):
        model.run('unit_scale',6*3**digits,(digits,2,3,unit,model.previous))
        counts['unit'] += 1
    bad = Model(source)
    bad.small_helpers = True
    rejected = False
    try:
        bad.run('weighted_pair',9,((1,1,0,0),1,1,1,lambda _:2,bad.previous))
    except BudgetViolation:
        rejected = True
    need(rejected, 'V-only stopped-helper control did not reject')
    scales = {r:p for r,p in model.peaks.items() if r.startswith('scale_atom:')}
    need(len(scales)==22 and all(0<p<=1 for p in scales.values()), 'twenty nonempty buckets and main pair')
    for role,peak in model.peaks.items():
        need(peak <= (3 if role in {'type_route:0','type_route:1'} else 1), 'cross-shape role envelope')
    return dict(cases=counts, ratios={r:str(p) for r,p in sorted(model.peaks.items())},
                V_only_stopped_helpers_rejected=rejected,
                method='independent exact interval contracts; no payload arrays or author meter')


def callers(source):
    schedules = []
    def pipe(arena,kind,source,target,size,schedule): schedules.append((size,list(schedule)))
    def lower(*args,**kwargs): pass
    def pair(*args,**kwargs): pass
    def scale(*args,**kwargs): pass
    def compiled(*args,**kwargs): pass
    def child(*args,**kwargs): pass
    env = dict(partial=partial,prod=prod,lru_cache=lru_cache,Fraction=F,pipe=pipe,
               lower_tape=lower,weighted_pair=pair,scale_atom=scale,one_weight=lambda *_:1,
               residue=lambda x,m:F(x).numerator*pow(F(x).denominator,-1,m)%m)
    load(source,'module_atoms.py','component_widths total_width chart_width pair_shape',env)
    load(source,'direct_body.py','direct_actions direct_route',env)
    load(source,'receiver.py','Receiver.compensate',env)
    load(source,'five_exchange.py','corner_exchanges same_order_line',env)
    load(source,'same_order_body.py','SameOrderBody.weighted',env)
    counts = dict(direct=0,compensation=0,covered=0,stopped=0)
    rejected = False
    def inspect_gates(kind,alpha):
        nonlocal rejected
        for size,gates in schedules:
            for gate in gates:
                if not isinstance(gate,partial): continue
                kw = gate.keywords
                if gate.func in {lower,pair}:
                    runs = list(kw['runs']())
                    need(sum(length for length,_ in runs)==kw['prefix'],'caller run-length prefix')
                    need(kw['prefix']*alpha**2*kw['gap']*kw['suffix_bytes']==size,'complete helper shape')
                    rejected |= len(runs) != kw['prefix']
                    counts[kind] += 1
                elif gate.func is scale:
                    need(kw['prefix']*alpha*kw['suffix']==size,'scale owner shape')
        schedules.clear()
    for n,width,f,unused,older,gap,suffix in product((2,3),(1,2),(1,2),(1,2),(1,2),(1,2),(1,3)):
        alpha=3**width
        core=SimpleNamespace(n=n,layout=(1,width,0,0),atom=alpha,modulus=alpha,
             previous=lambda *_:None,storage=lambda:nullcontext(None),arena=None,
             stock=2,compiled=compiled,weighted=child)
        word=(('add',0,1,2),('add',1,0,1),('swap',0,n-1),('scale',1,F(2)))
        env['direct_route'](core,None,None,word,f,unused,older,gap,suffix,lambda *_:1)
        inspect_gates('direct',alpha)
        matrix=tuple(tuple(1 if j<=i else 0 for j in range(n)) for i in range(n))
        env['compensate'](core,None,None,matrix,f,older,gap,suffix,lambda *_:1)
        inspect_gates('compensation',alpha)
        u=tuple([1]+[0]*(n-1));v=tuple([1]+[0]*(n-2)+[1])
        env['same_order_line'](core,None,None,pivot=0,factors=lambda _,u=u,v=v:(u,v),f=f,
             unused=unused,heights=3,older=older,gap=gap,suffix=suffix,weight=lambda *_:1)
        inspect_gates('covered',alpha)
        env['weighted'](core,None,None,atoms=n*f+1,available=2*unused,older=older,gap=gap,suffix=suffix)
        inspect_gates('stopped',alpha)
    need(rejected,'visible-run-length omission control was vacuous')
    return dict(descriptors=counts,dropping_visible_run_lengths_rejected=rejected)


def arithmetic(source):
    sites={'direct_body.py':{'scale_atom':22},'module_atoms.py':{'lower_tape':3,'negate_tape':3,'weighted_pair':2},
      'quotient_route.py':{'affine_packet':3,'high_packet':2,'quotient_right_route':10},'limb_scale.py':{'unit_scale':11},
      'raw_binary.py':{'Banks.clone':1,'Banks.swap':2,'Banks.xor':2},'receiver.py':{'OwnerBanks.route':1},
      'streaming_routes.py':{'type_route':5}}
    total=0
    for filename,functions in sites.items():
        root=ast.parse((source/filename).read_text())
        for name,expected in functions.items():
            body=root.body
            for part in name.split('.'):
                node=next(x for x in body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==part)
                body=node.body
            count=sum(ast.literal_eval(x.args[0]) for x in ast.walk(node) if isinstance(x,ast.Call)
                      and isinstance(x.func,ast.Name) and x.func.id=='work_tapes')
            need(count==expected,'source work-site partition')
            total+=count
    need(total==67 and total+6+2+5+11==91,'complete inventory partition')
    need(22+3+2+10+11+1+2+2+1==54 and 3+3+2+9==17,'coefficient sum')
    need(17+F(54,17)<21 and 4196+254*21==9530 and 9530*9==85770,'composition coefficient')
    for n in range(2,128):
        need((n+1)**2 <= 4*n*n <= 9*n*n,'tag induction step')
    need(4<=9**2 and F(16*4,16)==4,'tag base and generic API boundary')
    return dict(native_positions=67,owner_positions=54,full_W_positions=8,type_positions=5,
                A='17+54/B',native_bound='9530T < 85770X',generic_tag_ratio='4')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();package=args.package.resolve();source=package/'sources'
    need(sha256((package/'PROOF.md').read_bytes()).hexdigest()==PROOF_PIN,'reviewed proof changed')
    need(sha256((package/'check.py').read_bytes()).hexdigest()==AUTHOR_PIN,'reviewed author checker changed')
    pins=json.loads((package/'SOURCE-BINDINGS.json').read_text())
    need(pins['commit']=='dfd25d553a843a946ca0b94130a5ff8943e98fdd','source head changed')
    for name,pin in pins['files'].items():
        data=(source/name).read_bytes()
        need(len(data)==pin['size'] and sha256(data).hexdigest()==pin['sha256'],'changed source '+name)
    result=dict(status='PASS_INDEPENDENT_ORDINARY_BYTE_ENVELOPES',proof_sha256=PROOF_PIN,
      author_checker_sha256=AUTHOR_PIN,source_files=len(pins['files']),table=arithmetic(source),
      callers=callers(source),intervals=intervals(source),scope='Symbolic/extent method and source review; no production replay')
    result['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
