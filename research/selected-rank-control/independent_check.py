"""Independent dense CPU and materialized address-tree oracle for selected control.

No author Machine, Tape, input constructor or verifier is called. Compile-time
Builder output is the program under test. Prepared for CubeJerry with substantial
OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import json
import sys

PKG = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
BLANK, ONE, MARK = '_', '1', '|'


def need(test, message):
    if not test:
        raise AssertionError(message)


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reference = load('controller_reference', PKG/'controller_reference.py')


def forbidden(*args, **kwargs):
    raise AssertionError('author runtime/helper invoked')


reference.Machine = reference.Tape = reference.initial_tapes = forbidden
subject = load('selected_control', PKG/'selected_control.py')


def materialized_tree(width, cutoff, base, sites):
    """Breadth-first materialization, then independently sorted contour events."""
    nodes = [((), width, (), ())]
    cursor = 0
    while cursor < len(nodes):
        path, size, sort_prefix, ancestors = nodes[cursor]
        cursor += 1
        if size >= max(base, cutoff):
            for site in range(sites):
                nodes.append((path+(site,), size//base, sort_prefix+(3+3*site,),
                              ancestors+((size,site),)))
    events = []
    for path, size, prefix, ancestors in nodes:
        if size < max(base,cutoff):
            events.extend([(prefix+(0,), 'L',size,path,ancestors),
                           (prefix+(1,), 'X',size,path,ancestors)])
        else:
            events.extend([(prefix+(0,), 'E',size,path,ancestors),
                           (prefix+(1,), 'B'+str(size%base),size,path,ancestors)])
            for site in range(sites):
                events.extend([
                    (prefix+(2+3*site,), 'D'+str(site),size//base,path+(site,),
                     ancestors+((size,site),)),
                    (prefix+(4+3*site,), 'U'+str(site),size,path,ancestors)])
            events.extend([(prefix+(2+3*sites,), 'A'+str(size%base),size,path,ancestors),
                           (prefix+(3+3*sites,), 'X',size,path,ancestors)])
    events.sort(key=lambda event:event[0])
    return nodes,events


def dense_program(code, alphabet):
    symbols = {symbol:i for i,symbol in enumerate(alphabet)}
    result = []
    for instruction in code:
        op,*args = instruction
        if op=='read':
            tape,arms = args
            result.append((0,tape,tuple(arms.get(symbol,-1) for symbol in alphabet)))
        elif op=='write':
            result.append((1,args[0],symbols[args[1]]))
        elif op=='move':
            need(args[1] in (-1,1),'literal unit move')
            result.append((2,args[0],args[1]))
        elif op=='goto': result.append((3,args[0]))
        elif op=='emit': result.append((4,args[0]))
        elif op=='halt': result.append((5,))
        else: raise AssertionError('unknown instruction')
    return tuple(result),symbols


class DenseCPU:
    """Independently decoded six-opcode CPU over four dense symbol arrays."""
    def __init__(self, code, alphabet, width, cutoff, origins, stack_extent):
        self.program,self.symbols = dense_program(code,alphabet)
        self.alphabet,self.origins = alphabet,origins
        self.heads = list(origins)
        self.lows,self.highs = list(origins),list(origins)
        self.pc,self.steps = 0,0
        self.visited_writes = [0,0,0,0]
        self.mem,self.left,self.protected = [],[],[]
        active = (width,width,stack_extent,cutoff)
        for tape,(origin,extent) in enumerate(zip(origins,active)):
            left,right = origin-8,origin+extent+9
            cells = [self.symbols[BLANK]]*(right-left+1)
            protected = []
            for delta,symbol in ((-7,'t0'),(-6,'0'),(-4,ONE),(-3,MARK),(-2,'0')):
                pos = origin+delta
                cells[pos-left] = self.symbols[symbol]
                protected.append(pos)
            cells[origin-1-left] = self.symbols[MARK]
            protected.append(origin-1)
            # Input words are constructed here, without author helper code.
            length = width if tape==0 else cutoff if tape==3 else 0
            for offset in range(length): cells[origin+offset-left] = self.symbols[ONE]
            # Hostile cells sit beyond the active window and its terminal blank.
            for delta,symbol in ((extent+2,'0'),(extent+3,MARK),(extent+5,'t0')):
                pos = origin+delta
                cells[pos-left] = self.symbols[symbol]
                protected.append(pos)
            self.mem.append(cells)
            self.left.append(left)
            self.protected.append(tuple(protected))
        self.initial = tuple(tuple(cells) for cells in self.mem)

    def get(self,tape,position):
        return self.mem[tape][position-self.left[tape]]

    def unary_width(self):
        origin = self.origins[0]
        size = 0
        while self.get(0,origin+size)==self.symbols[ONE]: size+=1
        need(self.get(0,origin+size)==self.symbols[BLANK], 'unary terminator')
        return size

    def transition(self):
        need(0<=self.pc<len(self.program),'program-counter range')
        instruction = self.program[self.pc]
        self.pc += 1
        self.steps += 1
        opcode = instruction[0]
        if opcode==0:
            tape,arms = instruction[1:]
            target = arms[self.get(tape,self.heads[tape])]
            need(target>=0,'unhandled scanned symbol')
            self.pc = target
        elif opcode==1:
            tape,value = instruction[1:]
            need(tape!=3,'cutoff write')
            need(self.heads[tape] not in self.protected[tape],'protected-cell write')
            self.mem[tape][self.heads[tape]-self.left[tape]] = value
            self.visited_writes[tape] += 1
        elif opcode==2:
            tape,direction = instruction[1:]
            self.heads[tape] += direction
            need(self.origins[tape]-1<=self.heads[tape], 'read below entry marker')
            need(self.left[tape]<=self.heads[tape]<self.left[tape]+len(self.mem[tape]),
                 'dense window exceeded')
            self.lows[tape] = min(self.lows[tape],self.heads[tape])
            self.highs[tape] = max(self.highs[tape],self.heads[tape])
        elif opcode==3: self.pc=instruction[1]
        elif opcode==4: return instruction[1]
        elif opcode==5: return False
        return None


def run_case(base,sites,width,cutoff,origins,compiler=subject.compile_selected,
             mutate=None):
    nodes,expected = materialized_tree(width,cutoff,base,sites)
    code,alphabet = compiler(base,sites)
    if mutate: code=mutate(code)
    if compiler is subject.compile_selected and mutate is None:
        need(len(code)==30*base+42+sites*(69+3*base),'exact transition census')
        need(len(alphabet)==sites+4,'fixed alphabet census')
    stack_extent=max(sum(size+1 for size,_ in ancestor) for *_,ancestor in nodes)
    cpu = DenseCPU(code,alphabet,width,cutoff,origins,stack_extent)
    budget=200*(sites+1)*sum(node[1] for node in nodes)
    compare_pc=next(i for i,op in enumerate(code) if op[0]=='read' and op[1]==3)
    next_event,last_event,compare = 0,None,None
    remainder_scans,comparisons = 0,0
    while True:
        need(cpu.steps<budget,'transition envelope exceeded before halt')
        if cpu.pc==compare_pc and cpu.heads[0]==origins[0] and cpu.heads[3]==origins[3]:
            need(compare is None,'overlapping comparison')
            compare=(cpu.steps,cpu.unary_width())
        event=cpu.transition()
        if event is False: break
        if event is None: continue
        need(next_event<len(expected),'extra event')
        _,label,size,path,ancestors=expected[next_event]
        next_event+=1
        need(event==label,'event oracle mismatch')
        need(cpu.unary_width()==size,'actual emitted WIDTH mismatch')
        need(cpu.heads[0]==origins[0] and cpu.heads[1]==origins[1] and
             cpu.heads[3]==origins[3], 'descriptor head not restored at emit')
        need(all(cpu.get(0,origins[0]+j)==cpu.symbols[BLANK] for j in range(size,width+1)),
             'stale width history at emit')
        need(all(cpu.get(1,origins[1]+j)==cpu.symbols[BLANK] for j in range(width+1)),
             'child history not retired at emit')
        stack=[]
        for ancestor,site in ancestors: stack.extend([ONE]*ancestor+['t'+str(site)])
        need(cpu.heads[2]==origins[2]+len(stack),'stack cursor mismatch')
        need(all(cpu.get(2,origins[2]+j)==cpu.symbols[symbol]
                 for j,symbol in enumerate(stack)), 'materialized ancestor stack mismatch')
        need(all(cpu.get(2,origins[2]+j)==cpu.symbols[BLANK]
                 for j in range(len(stack),stack_extent+1)), 'retired stack history mismatch')
        need(tuple(cpu.mem[3])==cpu.initial[3],'cutoff changed')
        for tape in range(4):
            need(all(cpu.get(tape,pos)==cpu.initial[tape][pos-cpu.left[tape]]
                     for pos in cpu.protected[tape]), 'hostile exterior changed')
        if label in ('E','L') and compare is not None:
            begun,compared_width=compare
            need(cpu.steps-begun<=11*min(compared_width,cutoff)+10,
                 'comparison transition envelope')
            comparisons+=1
            compare=None
        if label.startswith('B') or label.startswith('A'):
            prior='E' if label.startswith('B') else 'U'+str(sites-1)
            need(last_event is not None and last_event[0]==prior,'remainder predecessor')
            need(cpu.steps-last_event[1]==6*size+7,'exact remainder transition charge')
            remainder_scans+=1
        last_event=(label,cpu.steps)
    need(next_event==len(expected),'missing event')
    need(cpu.steps<=budget,'complete transition envelope')
    need(tuple(cpu.heads)==origins,'final head restoration')
    need(tuple(tuple(cells) for cells in cpu.mem)==cpu.initial,'full final cell restoration')
    visited=sum(high-low+1 for low,high in zip(cpu.lows,cpu.highs))
    depth=max(len(node[0]) for node in nodes)
    bound=2*(width+2)+Fraction(width*base,base-1)+depth+2+min(width,cutoff)+2
    linear=(4+Fraction(base,base-1))*width+8
    need(visited<=bound<=linear,'historical visited-interval envelope')
    need(cpu.highs[3]-cpu.lows[3]+1<=min(width,cutoff)+2,'large cutoff visited prefix')
    need(all(low>=origin-1 for low,origin in zip(cpu.lows,origins)),
         'ancestor-prefix locality')
    return dict(base=base,sites=sites,width=width,cutoff=cutoff,origins=origins,
                nodes=len(nodes),events=len(expected),steps=cpu.steps,budget=budget,
                width_volume=sum(node[1] for node in nodes),depth=depth,
                visited_cells=visited,visited_bound=str(bound),
                cutoff_visited=cpu.highs[3]-cpu.lows[3]+1,
                cutoff_input_cells=cutoff+2,comparisons=comparisons,
                exact_remainder_scans=remainder_scans)


def negative_controls():
    out=[]

    def rejects(label,operation,wanted):
        try: operation()
        except AssertionError as error:
            need(str(error)==wanted,'unexpected rejection for '+label+': '+str(error))
            out.append(label)
        else: raise AssertionError('negative control survived: '+label)

    def wrong_remainder(code):
        return tuple(('emit','A0') if op==('emit','A1') else op for op in code)
    rejects('post remainder label changed',
            lambda:run_case(3,2,10,3,(-9,7,21,-4),mutate=wrong_remainder),
            'event oracle mismatch')

    text=(PKG/'selected_control.py').read_text()
    old="if r==m-1:a.op('write',CHILD,ONE);a.op('move',CHILD,1)"
    need(text.count(old)==1,'unique quotient mutation site')
    new=old+";a.op('write',CHILD,ONE);a.op('move',CHILD,1)"
    mutant=ModuleType('wrong_quotient')
    exec(compile(text.replace(old,new),'wrong-quotient-control','exec'),mutant.__dict__)
    rejects('doubled quotient output',
            lambda:run_case(3,1,3,3,(4,-8,13,27),compiler=mutant.compile_selected),
            'actual emitted WIDTH mismatch')

    def wrong_stop(code):
        result=list(code)
        at=next(i for i,op in enumerate(code) if op[0]=='read' and op[1]==3)
        width_probe=code[at][2][ONE]
        wrong=code[width_probe][2][BLANK]
        result[at]=('read',3,{**code[at][2],BLANK:wrong})
        return tuple(result)
    rejects('cutoff equality treated as leaf',
            lambda:run_case(3,2,9,9,(-17,20,4,-30),mutate=wrong_stop),
            'event oracle mismatch')
    return out


def main():
    pins={name:sha256((PKG/name).read_bytes()).hexdigest()
          for name in ('selected_control.py','controller_reference.py','SOURCE-BINDING.md')}
    need(pins['selected_control.py']=='1c977e9f4864d338f874aa4943d9f3422d964c3ab0cc2f877d9bc4c2d9e20237',
         'selected source pin')
    need(pins['controller_reference.py']=='e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73',
         'controller source pin')
    cases=[]
    origins=((-17,4,29,-9),(8,-25,-3,42),(0,0,0,0))
    for base in (2,3,5,7):
        for sites in (1,2,3):
            for width,cutoff in ((1,1),(base-1,base),(base,base),
                                 (base+1,base+1),(base+1,base+2),
                                 (base*base-1,base),(base*base,base),
                                 (base*base+1,base+1),(5*base-1,100003),
                                 (4*base,base+1)):
                cases.append(run_case(base,sites,width,cutoff,origins[len(cases)%3]))
    for base,sites,width,cutoff in ((2,3,63,2),(3,2,257,3),(7,1,4097,100001),
                                   (5,3,500,17),(7,4,301,7)):
        cases.append(run_case(base,sites,width,cutoff,origins[len(cases)%3]))
    result=dict(status='PASS',method='separate dense CPU and materialized address-tree contour',
                cases=len(cases),nodes=sum(row['nodes'] for row in cases),
                events=sum(row['events'] for row in cases),
                transitions=sum(row['steps'] for row in cases),
                exact_remainder_scans=sum(row['exact_remainder_scans'] for row in cases),
                negative_controls=negative_controls(),pins=pins,rows=cases)
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
