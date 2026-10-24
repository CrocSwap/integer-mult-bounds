"""Independent standard-library scalar/frame/ownership audit of PR4703.

No imported upstream evaluator, Clifford implementation, or solver is used here.
The exact Clifford decoder remains a separately credited upstream replay.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
UP = HERE / 'upstream'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def read(name):
    b = (UP/name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)

def span(basis):
    out = {0}
    for v in basis:
        need(v not in out, 'Dependent frame basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)

def linear(columns, x):
    result = 0
    for i, v in enumerate(columns):
        if x >> i & 1:
            result ^= v
    return result

def replay(z, direction):
    c, p = z['canonical'], z['programs'][direction]
    spaces = [span(b) for b in c['frames']]
    need(len(c['start']) == len(c['final']) == 632, 'All arbitrary persistent inputs')
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(632)}
    rows['C', 0] = {(('C', 0), ()): Q(1)}
    current = {('L', i): f for i, f in enumerate(c['start'])}
    current['C', 0] = None
    paid, counts = Counter(), Counter()
    maps = {r['op']: r['G_columns'] for r in c['warps']}
    inverse = {}
    for op, cols in maps.items():
        need(len(cols) == 9, 'Nine-dimensional shared map')
        image = [linear(cols, x) for x in range(512)]
        need(len(set(image)) == 512, 'Shared native map invertible')
        inverse[op] = {v: x for x, v in enumerate(image)}
    max_coefficient = 0
    for index, e in enumerate(p):
        kind = e[0]
        counts[kind] += 1
        if kind == 'scalar':
            g, f = e[1:]
            action, target = g[0], tuple(g[1])
            if action == 'clear':
                need(target == ('C', 0), 'Only owned cell may be erased')
                rows[target], current[target] = {}, f
                continue
            need(current[target] == f, 'Scalar target chart')
            if action in ('add', 'copy'):
                source = tuple(g[2])
                need(current[source] == f, 'Scalar source chart')
                if action == 'copy':
                    need(target == ('C', 0), 'Only owned cell may be overwritten')
                    rows[target] = rows[source].copy()
                else:
                    need(source != target, 'Distinct reversible ADD arguments')
                    coefficient = Q(g[3], g[4])
                    max_coefficient = max(max_coefficient, abs(g[3]), abs(g[4]))
                    result = rows[target]
                    for monomial, value in rows[source].items():
                        result[monomial] = result.get(monomial, Q(0)) + coefficient * value
                        if not result[monomial]:
                            del result[monomial]
            else:
                need(action == 'scale', 'Known scalar opcode')
                coefficient = Q(g[2], g[3])
                max_coefficient = max(max_coefficient, abs(g[2]), abs(g[3]))
                need(coefficient != 0, 'Persistent nonzero scale')
                rows[target] = {m: coefficient*v for m, v in rows[target].items()}
        elif kind == 'warp':
            _, r, operator, a, b = e
            target = tuple(r)
            need(current[target] == a, 'Warp chronological source')
            op = abs(operator)
            moved = frozenset(linear(maps[op], x) if operator > 0 else inverse[op][x] for x in spaces[a])
            need(moved == spaces[b], 'Shared native map matches every frame occurrence')
            # Free generators may be renamed in either orientation. This injective
            # signed renaming does not affect a universal word identity.
            changed = {}
            for (variable, word), coefficient in rows[target].items():
                newword = word[1:] if word and word[0] == -operator else (operator,) + word
                key = variable, newword
                changed[key] = changed.get(key, Q(0)) + coefficient
            rows[target] = {k: v for k, v in changed.items() if v}
            current[target] = b
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, role, a, b, rank = e
                target = ('L', role)
                need(spaces[a] < spaces[b], 'Ascending persistent paid job')
            else:
                _, role, a, b, rank = e
                target = ('C', role)
                need(spaces[a] < spaces[b] or spaces[b] < spaces[a], 'Nested owned paid job')
            need(current[target] == a, 'Paid chronological source')
            need(rank == abs(len(c['frames'][b])-len(c['frames'][a])) > 0, 'Exact positive paid width')
            current[target] = b
            paid[rank] += 1
        else:
            need(kind in ('adapter', 'residual_adapter', 'phase'), 'Known inert metadata')
    need([current['L', i] for i in range(632)] == c['final'], 'Final persistent charts')
    need(rows['C', 0] == {}, 'Arbitrary owned entry erased at return')
    for role in range(632):
        expected = {(('L', role), ()): Q(1)}
        if (direction == 'forward' and 112 <= role < 224) or (direction == 'backward' and role < 112):
            source = role-112 if direction == 'forward' else role+112
            expected[(('L', source), ())] = Q(1 if direction == 'forward' else -1)
        need(rows['L', role] == expected, 'Exact arbitrary-input diagonal/shear endpoint, role ' + str(role))
    helpers = Counter()
    for a, b in zip(c['start'][224:], c['final'][224:]):
        need(spaces[a] < spaces[b], 'Strict independent helper productive endpoint')
        helpers[len(c['frames'][b])-len(c['frames'][a])] += 1
    return dict(paid=dict(sorted(paid.items())), helpers=dict(sorted(helpers.items())), events=dict(sorted(counts.items())), shared_maps=len(maps), final_rows=632, final_terms=sum(len(rows['L', i]) for i in range(632)), final_nonempty_words=sum(bool(w) for i in range(632) for v,w in rows['L',i]), max_scalar_numerator_denominator=max_coefficient, owned_entry_columns=1)

def audit():
    base = read('BASE-ROUND3-WORD.json.gz')
    reports, words = {}, {}
    for label, prefix in [('B','QUOTIENT153-ROUND3'), ('C','INTERSECTION153-ROUND3')]:
        z = read(prefix+'-ACTUAL-WORD.json.gz')
        words[label] = z
        report = {d: replay(z,d) for d in ('forward','backward')}
        profile = read(prefix+'-ACTUAL-PROFILE.json')
        for d, r in report.items():
            need(r['paid'] == {int(k):v for k,v in profile['paid'].items()}, 'Complete paid profile')
            need(r['helpers'] == {int(k):v for k,v in profile['helpers'].items()}, 'Complete helper profile')
            need([e[1] for e in z['programs'][d] if e[0]=='scalar'] == [e[1] for e in base['programs'][d] if e[0]=='scalar'], 'Exact retained scalar word and coefficients')
        need(report['forward']['paid'] == report['backward']['paid'], 'Orientation invoice agreement')
        normalizers = read(prefix+'-MAIN-NORMALIZERS.json.gz')
        kinds = {r['port']: r['kind'] for r in normalizers}
        need(len(kinds)==112 and Counter(kinds.values())==Counter({'A':56,label:56}), 'Typed main partition')
        special = [i for i in range(112) if kinds[i] != 'A']
        for i in range(112):
            original = base['canonical']['frames'][base['canonical']['start'][i]]
            need(len(original)==1 and bool((original[0]&153).bit_count()%2)==(i in special), 'Exact complementary incidence')
        paid_count = sum(report['forward']['paid'].values())
        # Two child normalizers; all warp/main/backward-convention/helper wrappers.
        monomial_bound = 2*paid_count + report['forward']['events']['warp'] + 448 + 448 + 2*408
        need(monomial_bound < 9000, 'Conservative lifted monomial count')
        report['special_ports'] = special
        report['monomial_operations_upper_bound'] = monomial_bound
        report['native_local_allowance_status'] = 'Written constructive eventual O(V) model bound; no compiler/native outer theorem supplied'
        reports[label] = report
    need(reports['B']['special_ports']==reports['C']['special_ports'], 'Both suppliers have the same exceptional port set')
    controls = {}
    # These controls change actual program mathematics, rather than just a manifest.
    bad = deepcopy(words['C'])
    edge = next(e for e in bad['programs']['forward'] if e[0]=='climb')
    edge[5] += 1
    try:
        replay(bad,'forward')
    except ValueError as e:
        need(str(e)=='Exact positive paid width', 'Unexpected paid control rejection')
        controls['paid_rank_corruption'] = str(e)
    else:
        raise ValueError('Paid rank corruption accepted')
    bad = deepcopy(words['B'])
    position = next(i for i,e in enumerate(bad['programs']['forward']) if e[0]=='scalar' and e[1][0]=='add')
    bad['programs']['forward'][position][1][3] *= -1
    try:
        replay(bad,'forward')
    except ValueError as e:
        need(str(e).startswith('Exact arbitrary-input'), 'Unexpected scalar control rejection')
        controls['scalar_sign_corruption'] = str(e)
    else:
        raise ValueError('Changed scalar sign accepted')
    return dict(status='PASS_INDEPENDENT_SCALAR_FRAME_HELPER_ADMISSION', providers=reports, controls=controls, scope='Exact finite free-group identities, whole paid ownership and typed incidence. Clifford/absolute phase correctness is credited to the separate upstream exact replay. No profitable consumer or compiler/outer claim.')

if __name__ == '__main__':
    result = audit()
    result['script_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    result['sources_sha256'] = sha256((HERE/'SOURCES.json').read_bytes()).hexdigest()
    (HERE/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'])
