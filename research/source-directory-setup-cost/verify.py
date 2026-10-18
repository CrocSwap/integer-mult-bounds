"""Source-exact cubic radix setup and volume-linear directory audit."""
import argparse
import builtins
import hashlib
import itertools
import json
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def load():
    manifest = read_json(HERE/'SOURCES.json')
    raw = {}
    for row in manifest['retained_sources']:
        data = (HERE/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 '+row['path'])
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(blob == row['git_blob'], 'source Git blob '+row['path'])
        raw[row['path']] = data
    modules = {}
    def scoped_import(name, *args, **kwargs):
        return modules[name] if name in modules else builtins.__import__(name, *args, **kwargs)
    for name in ('words', 'records', 'stream', 'cardinality', 'counts', 'low_codes', 'directory'):
        module = types.ModuleType(name)
        path = 'source/pr2569/'+name+'.py'
        module.__file__ = str(HERE/path)
        module.__dict__['__builtins__'] = {**vars(builtins), '__import__': scoped_import}
        exec(compile(raw[path], module.__file__, 'exec'), module.__dict__)
        modules[name] = module
    return modules


class Run:
    def __init__(self):
        self.modules = load()
        self.tapes, self.arenas = [], []
        original = self.modules['records'].Tape
        audit = self
        class Tracked(original):
            def __init__(self):
                super().__init__()
                audit.tapes.append(self)
        for module in self.modules.values():
            if hasattr(module, 'Tape'):
                module.Tape = Tracked
        def reject_decode(_word):
            raise ValueError('retained execution may not decode numerical words')
        self.modules['words'].Word.inspect = reject_decode

    def ring(self, q, w):
        words = self.modules['words']
        arena = words.Arena((q**w).bit_length()+1)
        self.arenas.append(arena)
        modulus = arena.input(q**w)
        return words.Ring(modulus)

    def total(self):
        meters = [x.meter for x in self.tapes] + [x.meter for x in self.arenas]
        return tuple(sum(getattr(meter, key) for meter in meters) for key in ('reads','writes','moves'))

    def clean(self, protected):
        keep = {id(x) for x in protected}
        blank = self.modules['words'].BLANK
        need(all(t.head == 1 and all(x == blank for x in t.cells[1:])
                 for t in self.tapes if id(t) not in keep), 'all other count/control tapes erased')


def delta(after, before):
    return tuple(a-b for a,b in zip(after,before))


def numeral(word):
    """Unmetered external observer; never used to control retained code."""
    cells = word.cells if hasattr(word, 'cells') else word.tape.cells
    return sum(bit << i for i,bit in enumerate(cells[1:cells.index(3)]))


def division_writes(length, quotient_ones):
    return 3*length*length+8*length+4 + quotient_ones*(3*length+2)


def setup_bound(q, w, dimension, c):
    length = (q**w).bit_length()+1
    square, bq, bits = dimension*dimension, q.bit_length(), c.bit_length()
    multiplications = square*(w-1)
    return (2000*square*(w+1)*(length+1)**2 +
            100*multiplications*(bits+multiplications*bq+bq+1))


def setup_case(q, w, dimension, c):
    run = Run()
    modules = run.modules
    ring = run.ring(q,w)
    value = modules['counts'].Count.literal(c)
    length = ring.arena.bits
    expected_live = set(ring.arena.live)
    calls, shifts = [], [0]
    original_div, original_shift = ring.raw.divmod, ring.raw.shift_add_bit
    def shift(*args):
        shifts[0] += 1
        return original_shift(*args)
    def divide(numerator, denominator):
        before = ring.arena.meter.writes
        first = shifts[0]
        answer = original_div(numerator,denominator)
        ones = numeral(answer[0]).bit_count()
        observed = ring.arena.meter.writes-before
        need(observed == division_writes(length,ones), 'exact full-width division write bill')
        need(shifts[0]-first == length, 'every division scans all L bits')
        calls.append((ones,observed))
        return answer
    ring.raw.divmod, ring.raw.shift_add_bit = divide, shift
    before = run.total()
    before_natural = tuple(getattr(value.tape.meter,k) for k in ('reads','writes','moves'))
    before_arena = tuple(getattr(ring.arena.meter,k) for k in ('reads','writes','moves'))
    modules['counts'].high_power(value,ring,q,dimension)
    observed = delta(run.total(),before)
    natural = delta(tuple(getattr(value.tape.meter,k) for k in ('reads','writes','moves')),before_natural)
    arena = delta(tuple(getattr(ring.arena.meter,k) for k in ('reads','writes','moves')),before_arena)
    need(len(calls) == dimension*dimension*w, 'm-squared w exponent divisions')
    need(numeral(value) == c*q**(dimension*dimension*(w-1)), 'exact CH cardinality')
    need(observed == tuple(a+b for a,b in zip(natural,arena)), 'all tapes and word arenas included')
    lower = dimension*dimension*w*division_writes(length,0)
    upper = setup_bound(q,w,dimension,c)
    need(observed[1] >= lower and all(x <= upper for x in observed), 'source-loop setup lower and upper bounds')
    need(ring.arena.live == expected_live and value.tape.head == 1, 'setup numeric ownership')
    need(all(x.head == 1 for x in ring.arena.words) and ring.arena.template.head == 1, 'setup word heads')
    run.clean([value.tape])
    result = {'q':q,'w':w,'dimension':dimension,'C_bits':c.bit_length(), 'C':str(c), 'L':length,
        'divisions':len(calls),'shifts':shifts[0], 'meter':observed,'natural_meter':natural,
        'radix_word_meter':arena, 'division_writes':sum(x[1] for x in calls),
        'division_quotient_ones':sum(x[0] for x in calls), 'write_lower_bound':lower,
        'per_operation_upper_bound':upper}
    value.close();ring.close();ring.arena.free(ring.modulus)
    run.clean([])
    need(not ring.arena.live, 'setup final arena cleanup')
    return result


def serialize_field(code, high, code_bits, length):
    return bytes([(code>>i)&1 for i in range(code_bits)]+[5]+
        [x for value in high for x in ([(value>>i)&1 for i in range(length)]+[5])]+[6])


def directory_case(q,w,dimension,c,h):
    run = Run()
    modules = run.modules
    ring = run.ring(q,w)
    codes = modules['low_codes'].LowCodes(q,dimension,2)
    old_count = modules['counts'].Count.literal(c)
    old_fields = modules['counts'].Count.literal(h)
    old = modules['records'].Tape()
    square, cap = dimension*dimension,q**(w-1)
    prefixes = [b''.join(serialize_field(0,tuple((j+p%2)%cap for j in range(square)),codes.bits,ring.arena.bits)
                         for _ in range(h)) for p in range(c)]
    for prefix in prefixes:
        for bit in prefix:
            old.append(bit)
    old.rewind()
    original = bytes(old.cells)
    division_calls = [0]
    original_div = ring.raw.divmod
    def counted_div(*args):
        division_calls[0] += 1
        return original_div(*args)
    ring.raw.divmod = counted_div
    before = run.total()
    context = modules['directory'].Context(ring,codes)
    output, count = modules['directory'].produce(old,old_fields,old_count,1,context)
    context.close()
    observed = delta(run.total(),before)
    expected = b''.join(prefix+serialize_field(1,high,codes.bits,ring.arena.bits)
        for prefix in prefixes for high in itertools.product(range(cap), repeat=square))
    actual = bytes(output.cells[1:])
    need(actual == expected, 'complete directory order and old-prefix multiplicity')
    volume = c*cap**square*(h+1)*(codes.bits+2+square*(ring.arena.bits+1))
    need(len(actual) == volume and numeral(count) == c*cap**square, 'exact D and CH')
    need(division_calls[0] == (2*square+1)*w+1, 'complete context and producer division count')
    need(bytes(old.cells) == original and old.head == output.head == 1, 'old directory source and output heads')
    need(ring.arena.live == {ring.modulus.slot,ring.one.slot}, 'directory numeric work restored')
    run.clean([old,old_count.tape,old_fields.tape,output,count.tape])
    result = {'q':q,'w':w,'dimension':dimension,'C':c,'h':h,'D':volume,'meter':observed,
              'sha256':hashlib.sha256(actual).hexdigest(),'prefixes':c*cap**square,
              'code_bits':codes.bits,'L':ring.arena.bits,'divisions':division_calls[0]}
    for tape in (old,output):
        tape.clear()
    for tape in (old_count,old_fields,count):
        tape.close()
    ring.close();ring.arena.free(ring.modulus)
    run.clean([])
    need(not ring.arena.live, 'directory final arena cleanup')
    return result


def calculate():
    cases = [setup_case(q,w,1,1) for q in (3,5) for w in (1,2,4,8,16,32)]
    cases += [setup_case(3,w,m,c) for w,m,c in ((3,2,7),(4,3,9),(2,1,2**128+1),(1,64,1))]
    directories = [directory_case(3,w,1,c,h) for w in (1,2,4) for c,h in ((1,0),(3,0),(3,2))]
    directories += [directory_case(3,2,2,2,1)]
    directories += [directory_case(3,1,64,1,0)]
    absorption = []
    for q in (3,5,7):
        for w in range(1,129):
            for dimension in (1,2,64):
                # Compare bit lengths before constructing an enormous H.
                need(w*w <= q**w, 'elementary exponential absorption')
                need(w-1 <= dimension*dimension*(w-1), 'high-cube absorption exponent')
                absorption.append((q,w,dimension))
    witness = next(x for x in cases if x['q']==3 and x['w']==8)
    need(witness['natural_meter'][1] < witness['write_lower_bound'], 'multiplication-only invoice control')
    length = witness['L']
    short = (3).bit_length()+1
    need(division_writes(length,1) != division_writes(short,1), 'significant-width substitution control')
    need(witness['divisions'] != 1, 'one exponent reconstruction control')
    empty = next(x for x in directories if x['C']==3 and x['h']==0 and x['w']==2)
    need(empty['prefixes'] == 9 and empty['prefixes'] != 3, 'empty-prefix deduplication control')
    return {'status':'PASS_SOURCE_DIRECTORY_SETUP_COST', 'setup_cases':cases,
        'directory_cases':directories, 'absorption_cases':len(absorption),
        'controls':{
          'charge_only_cardinality_multiplications':'omits word-arena writes below the proven setup lower bound',
          'scan_only_significant_dividend_bits':{'actual_L':length,'incorrect_L':short,
             'last_division_writes':division_writes(length,1),'incorrect_writes':division_writes(short,1)},
          'count_one_radix_division':'source performs m²w full-width divisions',
          'deduplicate_empty_old_prefixes':'three distinct physical positions must remain three positions'},
        'scope':'Cubic retained cardinality setup and O_q(D) metered directory production; no full driver, reserve constant, fixed-tape machine or new supplier/exponent.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result',action='store_true')
    args = parser.parse_args()
    path = HERE/'RESULT.json'
    if args.write_result:
        need(not path.exists(), 'refusing to overwrite receipt')
        expected = None
    else:
        expected = read_json(path)
    result = calculate()
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write_result:
        with path.open('x',encoding='utf-8',newline='\n') as target:
            target.write(text)
    else:
        need(json.dumps(result,sort_keys=True) == json.dumps(expected,sort_keys=True), 'complete typed receipt mismatch')
    print('PASS_SOURCE_DIRECTORY_SETUP_COST setup=16 directories=11 controls=4')


if __name__ == '__main__':
    main()
