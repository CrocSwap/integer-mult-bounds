# Adapted from Nick Petalas PR2835/PR2781 credited fixtures, Apache-2.0.
# Only fixture root changes to final64; scientific runtime stays unchanged.
"""Small exact fixtures adapted from credited PR2781/2796 constructions.

The unchanged PR2781 integer oracle supplies adapter plans and expectations.
These neutral metadata fixtures do not certify selected catalogue membership.
"""
from types import SimpleNamespace
from binding import need as require


def fixture(m, branch='adapter-good', rank=42, depth=0, modulus=3, borrowed=3, warm=(0, 0)):
    good = branch in ('adapter-good', 'child-good')
    rank = rank if good else 1
    low, plan, ref, scalar, _ = m.oracle2781.reference('good' if good else 'fallback', rank, modulus,
                                                    'head' if good else 'shear')
    root_size = 64 * 64**depth
    r = m.words.Arena(modulus.bit_length()+1, max(65536, warm[0]+1))
    ix = m.words.Arena(root_size.bit_length()+1, max(128, warm[1]+1))
    for a, count in zip((r, ix), warm):
        tmp = [a.zero() for _ in range(count)]
        a.free_many(*tmp)
    mod = r.literal(modulus)
    ring = m.words.Ring(mod)
    ident = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    fallback_low = m.oracle2781.headers('fallback', 1, modulus)[0]
    specs = {0: SimpleNamespace(code=0, good=False, low=fallback_low,
                               template=SimpleNamespace(q=3, rank=1, preparation=ident))}
    code = int(good)
    if good:
        specs[code] = SimpleNamespace(code=code, good=True, low=low,
                                     template=SimpleNamespace(q=3, rank=rank, preparation=ident))
    program = m.records.Program.fixture(ix, r, root_size, 2, [(2, 0, 1, 0, 0, 0)]*depth)
    high = [[0]*64 for _ in range(64)]
    fields = m.records.Fields.fixture(ix, r, [(0, high)]*depth+[(code, high)])
    for j in range(borrowed):
        r.literal(j % modulus)
        ix.literal(j+2)
    coordinate = ix.zero()
    weight = 1 if depth else 2
    if branch.startswith('adapter'):
        request = SimpleNamespace(kind='adapter', reference=ref, coordinate=coordinate, reverse_adapter=False)
        if good:
            expected = scalar
        else:
            num = weight if ref.permutation[ref.first] < 64 else 1
            den = weight if ref.permutation[ref.second] < 64 else 1
            expected = scalar*num*pow(den, -1, modulus) % modulus
    else:
        kind = {'child-good':'good', 'child-pair':'pair', 'child-unit':'unit'}[branch]
        request = SimpleNamespace(kind='child', child_kind=kind, field=0, reverse=False,
                                  half=kind == 'unit', coordinate=coordinate, negative_inverse=False)
        # The good block projector has p00=2. For this pair's field zero,
        # elimination leaves diagonal0=2 and permutation0=0, so parent weights cancel.
        expected = 2*weight % modulus if good else 2 if kind == 'pair' else 1
    limits = (37672 if branch.startswith('adapter') else 20494, 22)
    return SimpleNamespace(**locals())


def saved(case):
    arenas = (case.r, case.ix)
    return {'residents': tuple({s:(bytes(a.words[s].cells), a.words[s].head) for s in a.live} for a in arenas),
            'tapes': tuple((bytes(t.cells), t.head) for t in (case.program.tape, case.fields.tape))}


def preserved(case, before):
    require(saved(case) == before, 'entry ownership, bytes, heads and program/fields restored')
    for a in (case.r, case.ix):
        require(a.template.head == 1, 'template head restored')
        require(set(a.available).isdisjoint(a.live) and len(set(a.available)) == len(a.available), 'free partition')
        require(set(a.available) | a.live == set(range(len(a.words))), 'all slots accounted')
        require(all(a.words[s].head == 1 and list(a.words[s].cells) == [2]+[4]*(a.bits+1)
                    for s in a.available), 'freed slots erased')


def call(m, case):
    return m.numeric.selected_coefficient(case.plan, case.ring, case.ix, case.program,
                                        case.fields, case.specs, case.code, case.request)
