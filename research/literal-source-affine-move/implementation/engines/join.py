"""Fixed-rank literal positive central join in unchanged nine-slot geometry.

Apache-2.0; prepared with substantial OpenAI assistance. All constructors
run offline. Encoded parameters never select/expand the runtime table.
"""
from pathlib import Path
from hashlib import sha256
import atexit
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_cache = tempfile.TemporaryDirectory(prefix='positive-join-source-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode = True
sys.pycache_prefix = str(Path(_cache.name) / 'required-absent')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    raw = (HERE / pin['local']).read_bytes()
    if len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('frozen source drift: ' + pin['local'])
P = load('positive_join_parent', HERE / 'reference/rank2/rank2.py')
Builder, LEAF = P.Builder, P.LEAF
BLANK, ONE, MARK, BITS = P.BLANK, P.ONE, P.MARK, P.BITS
HEADER, DATA, WORK, TRACE, TAPES = P.HEADER, P.DATA, P.WORK, P.TRACE, P.TAPES


def fixed_rank(rank):
    if type(rank) is not int or not 1 <= rank <= 9:
        raise ValueError('fixed construction-time native rank 1..9')
    return rank


def multiply_capture(a, rank):
    """Multiply captured positive MSB binary f in-place using fixed carries.

    FBIN was prefixed with ceil(log2(rank)) zero digits before Gamma capture.
    This guarantees zero carry at the left marker. PREFIX receives the
    canonical result, FLEN is rebuilt, then PREFIX is moved back and erased.
    The original unary F and HEADER are unchanged.
    """
    h = LEAF
    k = 'mul_'
    h.clear(a, h.FLEN, (ONE,))
    a.mark(k+'end')
    a.op('read', h.FBIN, {'0': k+'step', ONE: k+'step', BLANK: k+'lsb'})
    a.mark(k+'step'); a.op('move', h.FBIN, 1); a.op('goto', k+'end')
    a.mark(k+'lsb'); a.op('move', h.FBIN, -1); a.op('goto', k+'carry0')
    for carry in range(rank):
        label = k+'carry'+str(carry)
        a.mark(label)
        a.op('read', h.FBIN, {'0': label+'b0', ONE: label+'b1',
                              MARK: k+'product' if carry == 0 else 'reject'})
        for digit in (0, 1):
            value = rank*digit+carry
            a.mark(label+'b'+str(digit))
            a.op('write', h.FBIN, str(value % 2)); a.op('move', h.FBIN, -1)
            a.op('goto', k+'carry'+str(value//2))
    a.mark(k+'product'); a.op('move', h.FBIN, 1)
    a.mark(k+'skip')
    a.op('read', h.FBIN, {'0': k+'zero', ONE: k+'copy'})
    a.mark(k+'zero'); a.op('write', h.FBIN, BLANK); a.op('move', h.FBIN, 1)
    a.op('goto', k+'skip')
    a.mark(k+'copy')
    a.op('read', h.FBIN, {s: k+'copy'+s for s in BITS} | {BLANK: k+'copied'})
    for bit in BITS:
        a.mark(k+'copy'+bit)
        a.op('write', h.PREFIX, bit); a.op('move', h.PREFIX, 1)
        a.op('write', h.FLEN, ONE); a.op('move', h.FLEN, 1)
        a.op('write', h.FBIN, BLANK); a.op('move', h.FBIN, 1); a.op('goto', k+'copy')
    a.mark(k+'copied')
    a.rewind(h.FBIN, (BLANK,)); a.rewind(h.PREFIX, BITS); a.rewind(h.FLEN, (ONE,))
    a.mark(k+'back')
    a.op('read', h.PREFIX, {s: k+'back'+s for s in BITS} | {BLANK: k+'done'})
    for bit in BITS:
        a.mark(k+'back'+bit)
        a.op('write', h.FBIN, bit); a.op('move', h.FBIN, 1)
        a.op('write', h.PREFIX, BLANK); a.op('move', h.PREFIX, 1); a.op('goto', k+'back')
    a.mark(k+'done'); a.rewind(h.FBIN, BITS); a.rewind(h.PREFIX, (BLANK,))


def compile_guard(rank, *, weak=False):
    """Check rank*f <= actual binary cutoff without changing nine-slot f."""
    rank = fixed_rank(rank)
    multiplier = 1 if weak else rank
    h, a = LEAF, Builder()
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, MARK); a.op('move', tape, 1)
    for _ in range((multiplier - 1).bit_length()):
        a.op('write', h.FBIN, '0'); a.op('move', h.FBIN, 1)
    h.gamma(a, h.F, capture=(h.FBIN, h.FLEN))
    multiply_capture(a, multiplier)
    for tape in (h.R, h.P, h.S, h.WIDTH):
        h.gamma(a, tape)
    h.gamma_binary(a); h.cutoff_guard(a)
    h.trace_return(a, h.HEADER, h.HTRACE)
    for tape in h.PRIVATE:
        a.rewind(tape, BITS); h.clear(a, tape, BITS)
    for tape in h.PRIVATE:
        a.op('move', tape, -1); a.op('write', tape, BLANK); a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject'); a.op('read', h.HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))


def components(rank, mutation=None):
    rank = fixed_rank(rank)
    result = [('rank_guard_', compile_guard(rank, weak=mutation == 'weak_cutoff')),
              ('C0_', LEAF.compile_leaf())]
    for slot in range(1, rank):
        word = ((0, slot), (slot, 0), (0, slot))
        result.append(('swap_in'+str(slot)+'_', P.compile_word(word)))
        if not (mutation == 'omit_last_C' and slot == rank-1):
            result.append(('C'+str(slot)+'_', LEAF.compile_leaf()))
        result.append(('swap_out'+str(slot)+'_', P.compile_word(word)))
    return result


def compile_join(rank, mutation=None):
    """One public-owner transaction for positive C on first rank slots."""
    factors, a = components(rank, mutation), Builder()
    for tape in (WORK, TRACE):
        a.op('move', tape, -1); a.op('write', tape, MARK); a.op('move', tape, 1)
    a.mark('clone')
    a.op('read', DATA, {'0': 'clone0', ONE: 'clone1', BLANK: 'cloned'})
    for bit in BITS:
        a.mark('clone'+bit)
        a.op('write', WORK, bit); a.op('move', WORK, 1); a.op('move', DATA, 1)
        a.op('write', TRACE, ONE); a.op('move', TRACE, 1); a.op('goto', 'clone')
    a.mark('cloned'); P.return_source(a); a.rewind(WORK, BITS)
    entries = {}
    for index, (name, (code, alphabet)) in enumerate(factors):
        entries[name] = len(a.code)
        after = factors[index+1][0]+'0' if index+1 < len(factors) else 'commit'
        P.insert(a, name, code, alphabet, after)
    a.mark('commit'); entries['commit'] = len(a.code)
    a.op('read', WORK, {'0': 'commit0', ONE: 'commit1', BLANK: 'committed'})
    for bit in BITS:
        a.mark('commit'+bit)
        a.op('write', DATA, bit); a.op('write', WORK, BLANK)
        a.op('move', WORK, 1); a.op('move', DATA, 1)
        a.op('write', TRACE, ONE); a.op('move', TRACE, 1); a.op('goto', 'commit')
    a.mark('committed'); P.return_source(a); a.rewind(WORK, (BLANK,))
    for tape in (WORK, TRACE):
        a.op('move', tape, -1); a.op('write', tape, BLANK); a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((BLANK, '0', ONE, MARK))
    return code, alphabet, entries
