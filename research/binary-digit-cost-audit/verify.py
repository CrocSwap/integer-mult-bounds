"""Independent exact billing of pinned binary digit primitives.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
PR2501 supplies the executed primitives; PR2473 supplies the credited Counter
lifecycle formula. Integer formulas below are audit code, never runtime words.
"""
import argparse
import builtins
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
KEYS = ('reads', 'writes', 'moves')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read_json(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'duplicate JSON key: '+key)
            result[key]=value
        return result
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)


def plus(*items):
    return tuple(sum(item[j] for item in items) for j in range(3))


def times(n, item):
    return tuple(n*x for x in item)


def delta(after, before):
    return tuple(x-y for x,y in zip(after,before))


def count(n, width=None):
    """Full positive countdown, including its input-word traffic (PR2473)."""
    require(n > 0, 'positive billing domain')
    b = n.bit_length() if width is None else width
    require(b >= n.bit_length(), 'counter encoding fits')
    s = n.bit_count()
    return (7*n-2*s+5*b+14, 2*n-s+3*b+4, 6*n-2*s+6*b+18)


def one_test(n, margin=False):
    if n % 2 == 0:
        return (2, 0, 2)
    return (7, 0, 8) if n % 4 == 1 and (n > 1 or margin) else (6, 0, 6)


def copy_suffix(n):
    return plus(one_test(n), count(n) if n > 1 else (0,0,0))


def digit_bill(q, u, g, s, complement=False):
    """Independent closed formula, no retained function or meter consulted."""
    buckets = q if complement else q*q
    v = u*buckets*g*s
    payload = (10*v+5*buckets+3, 3*v, 10*v+6*buckets+4)
    counters = plus(times(2,count(u)),
                    (0,0,0) if complement else times(2*u*q,count(g)),
                    times(2*u*buckets*g,copy_suffix(s)))
    return plus(payload,counters)


def clear_bill(v):
    return (2*v+3,v,2*v+4)


def load(mutation=None):
    manifest = read_json(HERE/'PREDECESSORS.json')
    for item in manifest['files']:
        raw = (HERE/item['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256: '+item['path'])
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == item['git_blob'], 'source blob: '+item['path'])
    modules = {}
    original_import = builtins.__import__
    def scoped_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in modules:
            return modules[name]
        return original_import(name,globals,locals,fromlist,level)
    for name in ['words','records','stream','cardinality','bitstream']:
        module = types.ModuleType('retained_'+name)
        module.__dict__['__builtins__'] = dict(vars(builtins), __import__=scoped_import)
        path = HERE/'vendor/pr2501'/(name+'.py')
        raw=path.read_bytes()
        if mutation is not None and name=='bitstream':
            edits={
                'untransposed_buckets':(b'copy_bits(buckets[b][a], out, suffix)',b'copy_bits(buckets[a][b], out, suffix)'),
                'omit_bucket_erasure':(b'tape.clear()',b'tape.rewind()'),
                'omit_source_return':(b'source.rewind()',b'pass # deliberately omitted borrowed head return'),
                'omit_sign_rotation':(b'copy_blocks(right, output, ring.one, suffix, unobserved)\n        copy_blocks(left, output, leading, suffix, unobserved)',
                                      b'copy_blocks(left, output, leading, suffix, unobserved)\n        copy_blocks(right, output, ring.one, suffix, unobserved)')}
            before,after=edits[mutation]
            require(before in raw,'control edits an existing source operation')
            raw=raw.replace(before,after)
        exec(compile(raw,str(path),'exec'),module.__dict__)
        modules[name] = module
    modules['original_tape'] = modules['records'].Tape
    modules['original_counter'] = modules['stream'].Counter
    return modules


class Run:
    def __init__(self, modules):
        self.modules = modules
        self.tapes, self.arenas = [], []
        self.live_counters = self.peak_counters = 0
        original = modules['original_tape']
        owner = self
        class TrackedTape(original):
            def __init__(self):
                super().__init__()
                owner.tapes.append(self)
        self.Tape = TrackedTape
        counter=modules['original_counter']
        class TrackedCounter(counter):
            def __init__(self,word):
                super().__init__(word)
                owner.live_counters += 1
                owner.peak_counters=max(owner.peak_counters,owner.live_counters)
            def close(self):
                super().close()
                owner.live_counters -= 1
        for name in ['records','stream','cardinality','bitstream']:
            modules[name].Tape = TrackedTape
        for name in ['stream','cardinality','bitstream']:
            modules[name].Counter = TrackedCounter

    def total(self):
        meters = [t.meter for t in self.tapes] + [a.meter for a in self.arenas]
        return tuple(sum(getattr(m,k) for m in meters) for k in KEYS)

    def natural(self, n):
        tape = self.Tape()
        for bit in range(n.bit_length()):
            tape.append((n >> bit)&1)
        tape.append(self.modules['words'].RIGHT)
        tape.rewind()
        # Natural's constructor normalizes; fixture work precedes the baseline.
        return self.modules['cardinality'].Natural(tape), tape

    def word(self, n):
        arena = self.modules['words'].Arena(max(2,n.bit_length()+1))
        self.arenas.append(arena)
        return arena.input(n)

    def payload(self, v, plane):
        source = self.Tape()
        for i in range(v):
            source.append(((i+1) >> plane)&1)
        source.rewind()
        return source

    def unchanged(self, inputs, snapshots):
        for obj, raw in zip(inputs,snapshots):
            tape = getattr(obj,'tape',obj)
            require(bytes(tape.cells) == raw and tape.head == 1, 'borrowed input/head changed')

    def scratch_clean(self, protected):
        require(self.live_counters==0 and self.peak_counters<=3,'counter role lifetime')
        blank = self.modules['words'].BLANK
        for tape in self.tapes:
            if id(tape) not in protected:
                require(all(value == blank for value in tape.cells[1:]) and tape.head == 1,
                        'private tape not erased/restored')


def permutation(q, w, u, g, s, sign=False):
    m=q**w
    if sign:
        return [((outer*m+(-x)%m)*s+tail)
                for outer in range(u) for x in range(m) for tail in range(s)]
    return [((((outer*m+y)*g+gap)*m+x)*s+tail)
            for outer in range(u) for x in range(m) for gap in range(g)
            for y in range(m) for tail in range(s)]


def check_bits(output, order, plane):
    expected = bytes(((i+1)>>plane)&1 for i in order)
    require(bytes(output.cells[1:]) == expected and output.head == 1, 'independent source-bit permutation')


def digit_case(modules,q,u,g,s,complement=False,plane=0,check_cost=True):
    run=Run(modules)
    uword, ufixture=run.natural(u)
    gword, gfixture=run.natural(g)
    sword, sfixture=run.natural(s)
    v=u*(q if complement else q*q)*g*s
    source=run.payload(v,plane)
    inputs=[source,uword,gword,sword]
    snapshots=[bytes(getattr(t,'tape',t).cells) for t in inputs]
    before=run.total()
    if complement:
        output=modules['bitstream'].digit_complement(source,q,uword,sword)
        order=[((outer*q+q-1-x)*s+tail) for outer in range(u) for x in range(q) for tail in range(s)]
    else:
        output=modules['bitstream'].digit_swap(source,q,uword,gword,sword)
        order=permutation(q,1,u,g,s)
    observed=delta(run.total(),before)
    if check_cost:
        require(observed == digit_bill(q,u,g,s,complement),'exact digit movement formula')
    require(all(a <= b*v for a,b in zip(observed,(93,27,106))),'uniform digit bound')
    check_bits(output,order,plane)
    run.unchanged(inputs,snapshots)
    protected={id(t) for t in [source,output,ufixture,gfixture,sfixture,uword.tape,gword.tape,sword.tape]}
    run.scratch_clean(protected)
    return {'q':q,'u':u,'g':g,'s':s,'kind':'complement' if complement else 'swap',
            'volume':v,'meter':observed,'counter_peak':run.peak_counters}


def macro_case(modules,q,w,u,g,s,sign=False,all_planes=True):
    order=permutation(q,w,u,g,s,sign)
    v=len(order)
    planes=max(1,v.bit_length()) if all_planes else 1
    result=None
    for plane in range(planes):
        run=Run(modules)
        extent=[run.word(n) for n in (u,g,s)]
        modulus=run.word(q**w)
        ring=modules['words'].Ring(modulus)
        source=run.payload(v,plane)
        inputs=[source,*extent,modulus,ring.one]
        snapshots=[bytes(t.cells) for t in inputs]
        live=[set(a.live) for a in run.arenas]
        before=run.total()
        if sign:
            output=modules['bitstream'].sign_address(source,ring,q,extent[0],extent[2])
        else:
            output=modules['bitstream'].atom_swap(source,ring,q,*extent)
        observed=delta(run.total(),before)
        check_bits(output,order,plane)
        run.unchanged(inputs,snapshots)
        require([a.live for a in run.arenas] == live,'numeric workspace not restored')
        extra=max(a.meter.peak_live-len(old) for a,old in zip(run.arenas,live))
        require(extra<=6,'numeric workspace capacity')
        for arena in run.arenas:
            for word in arena.words:
                if word.slot not in arena.live:
                    require(all(x==modules['words'].BLANK for x in word.cells[1:]),'erased numerical slot')
        run.scratch_clean({id(source),id(output)})
        b=q.bit_length()+1
        require(all(n <= 1000000*(b+3)**2*w*v for n in observed),'complete primitive cost bound')
        record={'q':q,'w':w,'u':u,'g':g,'s':s,'kind':'sign' if sign else 'atom_swap',
                'volume':v,'meter':observed,'origin_planes':planes,
                'counter_peak':run.peak_counters,'extra_numeric_words':extra}
        require(result is None or record==result,'payload-dependent billing')
        result=record
    return result


def controls():
    rejected={}
    for fault,expected in [('untransposed_buckets','independent source-bit permutation'),
                           ('omit_bucket_erasure','private tape not erased/restored'),
                           ('omit_source_return','borrowed input/head changed')]:
        try:
            digit_case(load(fault),3,2,2,3,plane=2,check_cost=False)
        except ValueError as error:
            require(str(error)==expected,'control failed for wrong reason: '+fault)
            rejected[fault]=str(error)
        else:
            raise ValueError('ineffective control: '+fault)
    try:
        macro_case(load('omit_sign_rotation'),3,2,2,1,3,True)
    except ValueError as error:
        require(str(error)=='independent source-bit permutation','sign fault reason')
        rejected['omit_sign_rotation']=str(error)
    else:
        raise ValueError('ineffective sign fault')
    modules=load()
    original=modules['bitstream'].radix_power
    def truncated(*args):
        completed=list(original(*args))
        yield from completed[:-1]
    modules['bitstream'].radix_power=truncated
    try:
        macro_case(modules,3,2,2,1,3)
    except ValueError as error:
        require(str(error)=='independent source-bit permutation','missing digit fault reason')
        rejected['omit_last_atom_digit']=str(error)
    else:
        raise ValueError('ineffective last digit fault')
    for n in (1,2,3,8,17):
        run=Run(load())
        word,fixture=run.natural(n)
        before=run.total()
        counter=run.modules['stream'].Counter(word)
        while not counter.finished:
            counter.decrement()
        counter.close()
        actual=delta(run.total(),before)
        b=n.bit_length()
        own=delta(count(n),(3*b+3,0,2*b+4))
        require(actual==count(n) and actual!=own,'omitted input-word traffic accepted')
    rejected['omit_counter_input_traffic']='five actual lifetimes disagree with own-tape-only bill'
    case=digit_case(load(),3,2,2,1)
    false=plus(digit_bill(3,2,2,1),times(2*2*9*2,count(1)))
    require(tuple(case['meter'])!=false,'one-bit shortcut billing control')
    rejected['charge_nonexistent_suffix_counter']='actual S=1 source does not construct it'
    # The public macro requires each spectator's own one-zero margin.
    modules=load();run=Run(modules)
    arena=modules['words'].Arena(5);run.arenas.append(arena)
    padded=arena.input(2)
    try:
        modules['stream'].positive_extent(padded)
    except ValueError as error:
        require('separately canonical' in str(error),'padded extent fault reason')
        rejected['borrow_larger_extent_width']=str(error)
    else:
        raise ValueError('ineffective extent fault')
    return rejected


def preparation_checks():
    rows=[]
    for q in (3,5,7):
        for bits in (1,2,3,31,127,522):
            n=1 if bits==1 else (1 << (bits-1))+1
            modules=load();run=Run(modules)
            natural,fixture=run.natural(n)
            before=run.total()
            natural.multiply_small(q)
            product=delta(run.total(),before)
            end=natural.tape.cells.index(modules['words'].RIGHT)
            actual=sum(value<<j for j,value in enumerate(natural.tape.cells[1:end]))
            require(actual==q*n and natural.tape.head==1,'binary cardinality multiply')
            before=run.total()
            remainder=natural.divide_small(q)
            division=delta(run.total(),before)
            end=natural.tape.cells.index(modules['words'].RIGHT)
            actual=sum(value<<j for j,value in enumerate(natural.tape.cells[1:end]))
            require(actual==n and remainder==0 and natural.tape.head==1,'binary cardinality division')
            bound=100*(bits+2*q.bit_length()+3)
            require(all(x<=bound for x in (*product,*division)),'Natural source-loop bound')
            rows.append({'q':q,'bits':bits,'multiply':product,'divide':division})
    arithmetic=[]
    for bits in (4,9,31,127,522):
        modules=load();run=Run(modules)
        arena=modules['words'].Arena(bits,capacity=16);run.arenas.append(arena)
        n=(1<<(bits-1))-1
        numerator,denominator=arena.input(n),arena.input(3)
        before=run.total()
        quotient,remainder=modules['words'].Unsigned(arena).divmod(numerator,denominator)
        observed=delta(run.total(),before)
        require((quotient.inspect(),remainder.inspect())==divmod(n,3),'binary division identity')
        require(all(x<=1000*(bits+1)**2 for x in observed),'binary division source-loop bound')
        require(numerator.head==denominator.head==1,'binary division input heads')
        arithmetic.append({'bits':bits,'meter':observed})
    return {'cardinality_cases':rows,'word_division_cases':arithmetic}


def calculate():
    modules=load()
    digits=[]
    for q in (3,5,7):
        for u,g in ((1,1),(2,1),(1,3),(3,2)):
            for s in (1,2,3,4,5,8,9):
                digits.append(digit_case(modules,q,u,g,s))
                if g==1:
                    digits.append(digit_case(modules,q,u,1,s,True))
    macros=[]
    for q,w,u,g,s in [(3,1,1,1,1),(3,1,2,3,5),(3,2,2,1,3),(3,3,1,1,1),
                      (5,1,3,2,1),(5,2,1,1,2),(7,1,1,2,3)]:
        macros.append(macro_case(modules,q,w,u,g,s))
        macros.append(macro_case(modules,q,w,u,1,s,True))
    return {'status':'PASS_BINARY_DIGIT_COST_AUDIT','digit_cases':digits,'macro_cases':macros,
            'controls':controls(),
            'preparation':preparation_checks(),
            'scope':'Exact digit formulas and all-size primitive bound; no complete residual, recursive caller, supplier or kappa admission.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    path=HERE/'RESULT.json'
    if args.write:
        require(not path.exists(),'refusing to overwrite a scientific receipt')
        expected=None
    else:
        expected=read_json(path)
    result=json.loads(json.dumps(calculate()))
    if args.write:
        with path.open('x',encoding='utf-8',newline='\n') as output:
            json.dump(result,output,indent=2,sort_keys=True)
            output.write('\n')
    else:
        require(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),
                'complete typed committed receipt mismatch')
    print('PASS_BINARY_DIGIT_COST_AUDIT digits='+str(len(result['digit_cases']))+' macros='+str(len(result['macro_cases'])))


if __name__=='__main__':
    main()
