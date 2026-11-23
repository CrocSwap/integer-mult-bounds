#!/usr/bin/env python3
"""Independent rational audit of exact stored compiler cuts.

Actual source factories build the words. Matrix arithmetic, inverses, PSD
certificates, ownership/cut reconstruction and failure controls below are
independent of their exact.py matrix helpers and predecessor verifiers.
"""

from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import json
import sys
import types

HERE = Path(__file__).resolve().parent
RET = HERE/'retained'


def need(ok, why):
    if not ok:
        raise ValueError(why)


@dataclass(frozen=True)
class Z:
    re: Q = Q(0)
    im: Q = Q(0)

    @staticmethod
    def get(x):
        if isinstance(x, Z):
            return x
        if hasattr(x, 're') and hasattr(x, 'im'):
            return Z(Q(x.re), Q(x.im))
        return Z(Q(x))

    def __add__(self, other):
        other = Z.get(other)
        return Z(self.re+other.re, self.im+other.im)

    __radd__ = __add__

    def __neg__(self):
        return Z(-self.re, -self.im)

    def __sub__(self, other):
        return self+-Z.get(other)

    def __rsub__(self, other):
        return Z.get(other)+-self

    def __mul__(self, other):
        other = Z.get(other)
        return Z(self.re*other.re-self.im*other.im,
                 self.re*other.im+self.im*other.re)

    __rmul__ = __mul__

    def bar(self):
        return Z(self.re, -self.im)

    def norm2(self):
        return self.re*self.re+self.im*self.im

    def __truediv__(self, other):
        other = Z.get(other)
        norm = other.norm2()
        need(norm > 0, 'Independent zero divisor')
        numerator = self*other.bar()
        return Z(numerator.re/norm, numerator.im/norm)

    def __bool__(self):
        return bool(self.re or self.im)


def matrix(a):
    return [[Z.get(x) for x in row] for row in a]


def ident(n):
    return [[Z(Q(i == j)) for j in range(n)] for i in range(n)]


def adjoint(a):
    return [[a[j][i].bar() for j in range(len(a))] for i in range(len(a[0]))]


def multiply(a, b):
    need(len(a[0]) == len(b), 'Independent matrix dimensions')
    out = [[Z() for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = out[i][j]+x*y
    return out


def subtract(a, b):
    return [[x-y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def inverse(a):
    n = len(a)
    rows = [list(row)+unit for row, unit in zip(a, ident(n))]
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j]), None)
        need(pivot is not None, 'Independent singular matrix')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        v = rows[j][j]
        rows[j] = [x/v for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                v = rows[i][j]
                rows[i] = [x-v*y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def psd(a):
    need(a == adjoint(a), 'Hermitian PSD input')
    a = [list(row) for row in a]
    for k in range(len(a)):
        diagonal = a[k][k]
        if diagonal.im or diagonal.re < 0:
            return False
        if not diagonal:
            if any(a[k][j] for j in range(k+1, len(a))):
                return False
            continue
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                a[i][j] = a[i][j]-a[i][k]*a[k][j]/diagonal
    return True


def norm_at_most(a, cap):
    gram = multiply(adjoint(a), a)
    margin = [[Z(cap*cap if i == j else 0)-x for j, x in enumerate(row)]
              for i, row in enumerate(gram)]
    return psd(margin)


def frobenius2(a):
    return sum((x.norm2() for row in a for x in row), Q(0))


def embed(a, ids, n):
    out = ident(n)
    for i, old_i in enumerate(ids):
        for j, old_j in enumerate(ids):
            out[old_i][old_j] = a[i][j]
    return out


def convert_plan(plan, n):
    out = []
    for layer in plan:
        used, row = set(), []
        for ids, gate in layer:
            ids = tuple(ids)
            need(len(set(ids)) == len(ids) and not used.intersection(ids), 'Actual matching supports')
            need(all(0 <= i < n for i in ids), 'Actual gate wires')
            used.update(ids)
            row.append((ids, matrix(gate)))
        out.append(row)
    return out


def product(plan, n):
    out = ident(n)
    for layer in plan:
        for ids, gate in layer:
            out = multiply(embed(gate, ids, n), out)
    return out


def boundaries(plan, n):
    prefixes, prefix_inverses = [ident(n)], [ident(n)]
    for layer in plan:
        p, pi = prefixes[-1], prefix_inverses[-1]
        for ids, gate in layer:
            p = multiply(embed(gate, ids, n), p)
            pi = multiply(pi, embed(inverse(gate), ids, n))
        prefixes.append(p)
        prefix_inverses.append(pi)
    suffixes, suffix_inverses = [None]*(len(plan)+1), [None]*(len(plan)+1)
    suffixes[-1], suffix_inverses[-1] = ident(n), ident(n)
    for k in range(len(plan)-1, -1, -1):
        g = product([plan[k]], n)
        gi = inverse(g)
        suffixes[k] = multiply(suffixes[k+1], g)
        suffix_inverses[k] = multiply(gi, suffix_inverses[k+1])
    return prefixes, prefix_inverses, suffixes, suffix_inverses


def cuts(plan, n):
    pre, pri, suf, sui = boundaries(plan, n)
    for k, layer in enumerate(plan):
        for mask in range(1 << len(layer)):
            yes = [gate for j, gate in enumerate(layer) if mask >> j & 1]
            no = [gate for j, gate in enumerate(layer) if not mask >> j & 1]
            h, rest = product([yes], n), product([no], n)
            yield (k, mask, multiply(h, pre[k]), multiply(pri[k], inverse(h)),
                   multiply(suf[k+1], rest), multiply(inverse(rest), sui[k+1]))
    yield len(plan), 0, pre[-1], pri[-1], ident(n), ident(n)


def load_source():
    origins = json.loads((HERE/'ORIGINS.json').read_text())
    for row in origins['files']:
        data = (HERE/row['local']).read_bytes()
        need(sha256(data).hexdigest() == row['sha256'],
             'Pinned source SHA-256: '+row['local'])
        need(len(data) == row['bytes'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
             'Pinned source Git blob and byte count: '+row['local'])
    modules = {}
    for name in ('exact', 'engine', 'triangular', 'generator', 'full'):
        m = types.ModuleType(name)
        m.__file__ = str(RET/(name+'.py'))
        sys.modules[name] = m
        exec(compile((RET/(name+'.py')).read_bytes(), m.__file__, 'exec', optimize=0), m.__dict__)
        modules[name] = m
    gen = modules['generator']
    raw = {gen.SOURCE+'check_circuits.py': (RET/'check_circuits.py').read_bytes(),
           gen.ORACLE: (RET/'interval_kernel.py').read_bytes(),
           gen.PRODUCER: (RET/'stein_rational.py').read_bytes(),
           gen.PROVENANCE: (RET/'STEIN-PROVENANCE.json').read_bytes()}
    return modules, raw, len(origins['files'])


def source_value(z, source):
    z = Z.get(z)
    return source.C(z.re, z.im)


def primitive_fixture(values, modules, raw, label):
    exact, engine, gen = (modules[n] for n in ('exact', 'engine', 'generator'))
    values = matrix(values)
    n = len(values)
    source_matrix = exact.Mat([[source_value(x, exact) for x in row] for row in values])
    # These are actual certified source words at a bounded declared precision.
    phases = engine.Phases(12, raw[gen.ORACLE])
    builder = engine.Builder(phases, 12, raw[gen.SOURCE+'check_circuits.py'])
    plan = convert_plan(builder.plan(source_matrix), 2*n)
    # Exercise the nonreal butterfly twiddle site directly, even when this
    # bounded whole fixture only needs smaller FFTs.
    w=phases.phase(8,1)
    butterfly=matrix(builder.butterfly(w))
    wrong_inverse=matrix(builder.butterfly(w.conjugate()))
    need(multiply(adjoint(butterfly),butterfly)==ident(2), 'Nonreal rational butterfly is unitary')
    need(multiply(wrong_inverse,butterfly)!=ident(2), 'Conjugating only the twiddle is not inversion')
    mg, mh = builder.bounds
    cap = 1+mg+mh+Q(2, 1 << 12)
    spectral_layers, unitary_gates = [], 0
    for k, layer in enumerate(plan):
        crossings = []
        for ids, gate in layer:
            crossing = len(ids) == 2 and ids[0] < n <= ids[1]
            if crossing:
                need(gate[0][0] == Z(Q(1)) and gate[1][1] == Z(Q(1)) and not gate[0][1],
                     'Actual crossing is one oriented shear')
                crossings.append((ids, gate))
            else:
                need(all(i < n for i in ids) or all(i >= n for i in ids), 'Actual bank-local support')
                need(multiply(adjoint(gate), gate) == ident(len(gate)), 'Exact unitary bank gate')
                unitary_gates += 1
        if crossings:
            need(len(crossings) == n and len(crossings) == len(layer), 'Complete one-to-one spectral matching')
            spectral_layers.append(k)
    need(len(spectral_layers) == 2, 'Exactly two spectral sweeps')
    count, partial, norm_checks, invariant_checks = 0, 0, 0, 0
    endpoint = product(plan,2*n)
    for k, mask, p, pi, s, si in cuts(plan, 2*n):
        count += 1
        partial += k < len(plan) and mask not in (0, (1 << len(plan[k]))-1)
        for a in (p, pi, s, si):
            need(norm_at_most(a, cap), 'Actual primitive four-way cut bound')
            norm_checks += 1
            upper = [row[:n] for row in a[:n]]
            lower = [row[n:] for row in a[n:]]
            cross = [row[:n] for row in a[n:]]
            need(not any(x for row in a[:n] for x in row[n:]),
                 'Source cut keeps the bank-triangular orientation')
            need(multiply(adjoint(upper), upper) == ident(n)
                 and multiply(adjoint(lower), lower) == ident(n),
                 'Source cut has unitary diagonal bank factors')
            need(norm_at_most(cross, cap-1), 'Additive source spectral off-diagonal bound')
            invariant_checks += 1
        need(multiply(pi, p) == ident(2*n) and multiply(s, p) == endpoint,
             'Independent primitive inverse and concatenation')
    return dict(label=label,side=n,layers=len(plan),gates=sum(map(len,plan)),cuts=count,
                proper_partial_cuts=partial,psd_certificates=norm_checks,
                unitary_gates=unitary_gates,cap=str(cap),bank_invariant_certificates=invariant_checks,
                nonreal_twiddle_inverse_control='wrong conjugated-twiddle replacement rejected')


def atom_ideal(atom, n):
    ids = atom['indices']
    a = matrix(atom['ideal'])
    if atom['kind'] == 'leaf':
        return embed(a, ids, n)
    m = len(a)
    local = ident(2*m)
    for i in range(m):
        for j in range(m):
            local[m+i][j] = a[i][j]
    return embed(local, ids, n)


def atom_prefix(atom, k, selected, n):
    local = atom['converted']
    j = k-atom['start']
    out = atom['prefixes'][j]
    for ids, gate in selected:
        if set(ids).issubset(atom['indices']):
            # Global coordinates are retained in every atom's converted plan.
            out = multiply(embed(gate, ids, n), out)
    return out


def timing_predecessors(atoms,depth):
    predecessors=[set() for _ in atoms]
    for i,a in enumerate(atoms):
        need(0<=a['start']<=a['stop']<=depth, 'Source timestamp domain')
        lo,hi=a['interval']
        descendants=[j for j,b in enumerate(atoms)
                     if (lo,hi)!=tuple(b['interval']) and lo<=b['interval'][0]<b['interval'][1]<=hi]
        if a['kind']=='upper':
            lower=[j for j,b in enumerate(atoms) if b['kind']=='lower' and tuple(b['interval'])==(lo,hi)]
            need(len(lower)==1, 'Unique matching lower atom')
            for j in descendants+lower:
                need(a['stop']<=atoms[j]['start'], 'Upper atom precedes every descendant, including zero-duration atoms')
                predecessors[j].add(i)
        if a['kind']=='lower':
            for j in descendants:
                need(atoms[j]['stop']<=a['start'], 'Every descendant completes before lower atom')
                predecessors[i].add(j)
    return predecessors


def full_fixture(values, modules, raw, label, reverse=False):
    exact, full = modules['exact'], modules['full']
    values = matrix(values)
    n = len(values)
    source_matrix = exact.Mat([[source_value(x, exact) for x in row] for row in values])
    lam, q, _ = full.admission(source_matrix)
    # Independently check the leading solves and component envelopes used by
    # the source allocation. No computed whole-inverse bound is substituted.
    for size in range(1,n+1):
        a = [row[:size] for row in values[:size]]
        ai = inverse(a)
        need(multiply(a, ai) == ident(size), 'Independent leading-section inverse')
        component = max(max(sum(abs(x.re)+abs(x.im) for x in row) for row in ai),
                        max(sum(abs(x.re)+abs(x.im) for x in col) for col in zip(*ai)))
        need(component <= q, 'Admitted component inverse envelope')
    bound = full.allocation(n, lam, q, 1, 1, 0)
    compiler = full.Full(bound, raw)
    ids = list(reversed(range(n))) if reverse else list(range(n))
    source_plan = compiler.plan(source_matrix, ids)
    plan = convert_plan(source_plan, n)
    target = embed(values, ids, n)
    atoms = [dict(a) for a in source_plan.atoms]
    predecessors=timing_predecessors(atoms,len(plan))
    for a in atoms:
        mapping = a['indices']
        local = [[(tuple(mapping[i] for i in js), matrix(g)) for js,g in layer]
                 for layer in a['local_plan']]
        need(len(local) == a['stop']-a['start'], 'Source atom duration')
        a['converted'] = local
        a['prefixes'] = boundaries(local,n)[0]
        a['stored'] = a['prefixes'][-1]
        a['ideal_global'] = atom_ideal(a,n)
        need(norm_at_most(subtract(a['stored'], a['ideal_global']), bound['eta']),
             'Actual atom coefficient defect including same stored inverse')
    # Literal ownership binds timestamps to every lowered source instruction.
    for k, layer in enumerate(plan):
        for ids0, gate in layer:
            owners = [a for a in atoms if a['start'] <= k < a['stop'] and set(ids0).issubset(a['indices'])]
            need(len(owners) == 1, 'Exactly one active source atom owns each gate')
            a = owners[0]
            need((ids0,gate) in a['converted'][k-a['start']], 'Exact source-owned gate and local timestamp')
    ideal_endpoint = ident(n)
    stored_endpoint = ident(n)
    for a in atoms:
        ideal_endpoint = multiply(a['ideal_global'],ideal_endpoint)
        stored_endpoint = multiply(a['stored'],stored_endpoint)
    need(ideal_endpoint == target, 'Independent complete ideal atomic product')
    need(stored_endpoint == product(plan,n), 'Source linearization equals lowered stored endpoint')
    stored_inverse = product(convert_plan(compiler.inverse(source_plan),n),n)
    need(stored_inverse == inverse(stored_endpoint), 'Literal same-stored inverse word')

    # Independent noncommutative normalized-defect recurrence and suffix
    # cancellation; no product of separately bounded approximate prefixes.
    ideal_prefix,stored_prefix,z=ident(n),ident(n),ident(n)
    normalized=[z]
    for a in atoms:
        previous=ideal_prefix
        ideal_prefix=multiply(a['ideal_global'],ideal_prefix)
        stored_prefix=multiply(a['stored'],stored_prefix)
        g=multiply(multiply(inverse(ideal_prefix),subtract(a['stored'],a['ideal_global'])),previous)
        factor=[[g[i][j]+int(i==j) for j in range(n)] for i in range(n)]
        z=multiply(factor,z)
        need(z==multiply(inverse(ideal_prefix),stored_prefix), 'Normalized perturbation recurrence')
        normalized.append(z)
    normalized_suffix_checks=0
    for j in range(len(atoms)+1):
        qj=ident(n);hatqj=ident(n);rest=ident(n)
        for a in atoms[:j]:
            qj=multiply(a['ideal_global'],qj);hatqj=multiply(a['stored'],hatqj)
        for a in atoms[j:]:
            rest=multiply(a['stored'],rest)
        interaction_tail=multiply(normalized[-1],inverse(normalized[j]))
        need(multiply(multiply(target,interaction_tail),inverse(qj))==rest,
             'Consecutive normalized suffix identity')
        need(multiply(stored_endpoint,inverse(hatqj))==rest, 'Stored suffix cancellation')
        normalized_suffix_checks+=1

    b,h,kphys,l0 = (bound['completed_prefix_bound'],bound['fragment_bound'],
                    bound['execution_bound'],max(Q(1),lam,q))
    need(kphys == 2*l0*b*h, 'Literal physical-cut constant')
    counts = dict(cuts=0,proper_partial_cuts=0,simultaneous_nonempty_fragments=0,
                  trace_equalities=0,global_frobenius_certificates=0,noncommuting_prefix_controls=0)
    for k, mask, p, pi, s, si in cuts(plan,n):
        selected = [g for j,g in enumerate(plan[k]) if mask >> j & 1] if k < len(plan) else []
        completed = [a for a in atoms if a['stop'] <= k]
        active = [a for a in atoms if a['start'] <= k < a['stop']]
        remaining = [a for a in atoms if a not in completed and a not in active]
        completed_ids={j for j,a in enumerate(atoms) if a['stop']<=k}
        for j,a in enumerate(atoms):
            if a in completed or a in active:
                need(predecessors[j].issubset(completed_ids), 'Completed/active source downset')
        used = [i for a in active for i in a['indices']]
        need(len(used)==len(set(used)), 'Active source atom supports are disjoint')
        qhat, rem, fragments, tails = ident(n),ident(n),ident(n),ident(n)
        for a in completed:
            qhat = multiply(a['stored'],qhat)
        for a in remaining:
            rem = multiply(a['stored'],rem)
        nonempty=0
        for a in active:
            f = atom_prefix(a,k,selected,n)
            t = multiply(a['stored'],inverse(f))
            fragments=multiply(f,fragments); tails=multiply(t,tails)
            nonempty += f!=ident(n) and t!=ident(n)
        need(multiply(fragments,qhat)==p, 'Exact active-prefix trace identity')
        need(multiply(rem,tails)==s, 'Exact active-suffix trace identity')
        need(multiply(inverse(qhat),inverse(fragments))==pi, 'Prefix inverse order')
        need(multiply(inverse(tails),inverse(rem))==si, 'Suffix inverse order')
        if multiply(qhat,fragments)!=p:
            counts['noncommuting_prefix_controls']+=1
        for a in (p,pi,s,si):
            need(frobenius2(a)<=kphys*kphys, 'Independent conservative Full spectral consequence')
            counts['global_frobenius_certificates']+=1
        counts['cuts']+=1
        counts['proper_partial_cuts']+=k<len(plan) and mask not in (0,(1<<len(plan[k]))-1)
        counts['simultaneous_nonempty_fragments']+=nonempty>=2
        counts['trace_equalities']+=4
    need(norm_at_most(subtract(stored_endpoint,target),bound['coefficient_error']), 'Accumulated forward atom error')
    need(norm_at_most(subtract(stored_inverse,inverse(target)),bound['coefficient_error']), 'Accumulated inverse atom error')
    zero_controls=0
    for j,a in enumerate(atoms):
        if a['start']!=a['stop']:
            continue
        mutated=[dict(row) for row in atoms]
        mutated[j]['start']+=1;mutated[j]['stop']+=1
        try:
            timing_predecessors(mutated,len(plan))
        except ValueError:
            zero_controls+=1
    if any(a['start']==a['stop'] for a in atoms):
        need(zero_controls>0, 'Delayed zero-duration source predecessor must reject')
    return dict(label=label,n=n,layers=len(plan),gates=sum(map(len,plan)),atoms=len(atoms),
                zero_duration_atoms=sum(a['start']==a['stop'] for a in atoms),
                source_atom_timestamps=[(a['id'],a['start'],a['stop']) for a in atoms],
                child_target_bits=bound['child_target_bits'],theta=str(bound['theta']),
                coefficient_error=str(bound['coefficient_error']),execution_bound=str(kphys),
                normalized_suffix_identities=normalized_suffix_checks,
                rejected_delayed_zero_atoms=zero_controls,**counts)


def controls():
    out=[]
    # A whole unitary gate can have a singular intermediate coordinate write.
    swap=matrix([[0,1],[1,0]])
    partial=matrix([[0,1],[0,1]])
    need(norm_at_most(swap,1) and not norm_at_most(partial,1), 'Split-write norm control')
    try:
        inverse(partial)
    except ValueError:
        out.append('coordinate-write splice is singular; no inverse-cut contract')
    else:
        raise ValueError('Singular intermediate write accepted')
    # Endpoint restoration alone cannot bound fragments.
    shrink=matrix([[Q(1,2),0],[0,1]])
    need(multiply(inverse(shrink),shrink)==ident(2) and not norm_at_most(inverse(shrink),Q(3,2)),
         'Missing exact-unitarity control')
    out.append('nonunitary compensated bank gates violate a near-one fragment cap')
    # Reusing an adjoint instead of the stored inverse breaks a nonunit pivot.
    scalar=matrix([[Q(3,2)]])
    need(multiply(inverse(scalar),scalar)==ident(1) and multiply(adjoint(scalar),scalar)!=ident(1),
         'Stored inverse versus adjoint')
    out.append('nonunitary scalar adjoint is not its stored inverse')
    # The generic zero-loss adjacent-boundary interpolation rule is false.
    p0=matrix([[6,0],[1,Q(1,6)]])
    p1=multiply(matrix([[Q(1,6),0],[0,6]]),p0)
    cut=multiply(matrix([[1,0],[0,6]]),p0)
    need(norm_at_most(p0,8) and norm_at_most(p1,8) and not norm_at_most(cut,8),
         'Generic matching interpolation still needs a loss')
    out.append('generic no-loss interpolation rejected; source structure is necessary')
    opposite = multiply(matrix([[1,2],[0,1]]), matrix([[1,0],[2,1]]))
    need(opposite == matrix([[5,2],[2,1]]) and not norm_at_most(opposite,5),
         'Opposite-direction spectral sweeps violate the additive bound')
    out.append('opposite-direction sweeps violate the additive bank-triangular bound')
    return out


def main():
    modules,raw,authenticated=load_source()
    primitives=[primitive_fixture([[0]],modules,raw,'zero_side1'),
                primitive_fixture([[1,Q(1,3)],[Q(-1,4),1]],modules,raw,'dirty_side2'),
                primitive_fixture([[Z(Q(1),Q(1,4)),Z(Q(1,3),Q(-1,5))],
                                   [Z(Q(-1,4),Q(1,7)),Z(Q(1),Q(1,4))]],modules,raw,'complex_side2')]
    fulls=[full_fixture([[3,1],[1,3]],modules,raw,'n2_nonzero_approximation'),
           full_fixture([[2,1,1,2],[1,2,1,1],[1,1,2,1],[0,1,1,2]],modules,raw,
                        'n4_asymmetric_zero_atom',True),
           full_fixture([[Z(Q(3,2),Q(1,2))]],modules,raw,'n1_complex_scalar')]
    need(fulls[1]['zero_duration_atoms']>0 and fulls[1]['simultaneous_nonempty_fragments']>0,
         'Actual asymmetric fixture exercises the intended source risk')
    need(sum(x['noncommuting_prefix_controls'] for x in fulls)>0,
         'Actual source distinguishes illegal factor order')
    report=dict(status='PASS_SOURCE_ORDERED_FOUR_WAY_CUT_AUDIT',authenticated_origins=authenticated,
                primitive_words=primitives,full_words=fulls,negative_controls=controls(),
                proof_sha256=sha256((HERE/'PROOF.md').read_bytes()).hexdigest(),
                checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                python_version=sys.version.split()[0],
                boundary='Exact stored one/two-wire gate cuts, including arbitrary matching subsets; no split-output inverse claim',
                scope='Finite evidence corroborates PROOF.md; phase, rank and conditioning premises remain explicit')
    (HERE/'EVIDENCE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=report['status'],primitive_cuts=sum(x['cuts'] for x in primitives),
                         primitive_psd=sum(x['psd_certificates'] for x in primitives),
                         full_cuts=sum(x['cuts'] for x in fulls),
                         full_trace_equalities=sum(x['trace_equalities'] for x in fulls)),sort_keys=True))


if __name__=='__main__':
    main()
