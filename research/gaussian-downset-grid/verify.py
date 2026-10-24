"""Execute actual normalized/raw callers under one reduced common grid."""
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import json
from types import FunctionType
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    raw = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            data = (ROOT/row['path']).read_bytes()
            need(sha256(data).hexdigest() == row['sha256'], 'source bytes: '+row['path'])
            raw[row['path']] = data
    return raw


def inverse(a, C):
    n = len(a)
    rows = [list(row)+[C(int(i == j)) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        k = next((i for i in range(j, n) if rows[i][j] != 0), None)
        need(k is not None, 'independent inverse pivot')
        rows[j], rows[k] = rows[k], rows[j]
        pivot = rows[j][j]
        rows[j] = [x/pivot for x in rows[j]]
        for i in range(n):
            if i != j:
                c = rows[i][j]
                rows[i] = [x-c*y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def mv(a, v):
    return [sum((x*y for x, y in zip(row, v)), row[0]*0) for row in a]


def squared(v):
    return sum((z.norm2() for z in v), Q(0))


def reject(call, text):
    try:
        call()
    except (ValueError, AssertionError) as exc:
        need(text in str(exc), 'wrong rejection: '+str(exc))
    else:
        raise ValueError('missing rejection: '+text)


def main():
    raw = authenticate()
    sys.path[:0] = [str(HERE), str(ROOT/'research/full-downset-allocation'),
                    str(ROOT/'research/rational-unitary-fft')]
    from allocation import adapted
    from bridge import bind
    from exact import C, Vec, apply, ceil_log2, vector_hash
    import full, gaussian, raw_gaussian
    from gaussian_reference import Entry, Reference
    reduced, binding = adapted(raw['research/rational-unitary-fft/full.py'], need, ceil_log2)
    Gaussian, RawGaussian = bind(gaussian, raw_gaussian, reduced)
    old_normalized, old_raw = gaussian.Gaussian, raw_gaussian.RawGaussian
    need(Gaussian.compile_root.__code__ is old_normalized.compile_root.__code__
         and RawGaussian.__init__.__code__ is old_raw.__init__.__code__, 'same actual caller code')
    need(gaussian.allocation is full.allocation and raw_gaussian.allocation is full.allocation,
         'frozen caller modules unchanged')

    def trajectories(caller, programs, intended, bits, radius):
        n = len(intended[0])
        vectors = [[C(Q((-1)**i, 2), Q(i, 8)) for i in range(n)],
                   [C(Q(1, 1 << bits))]+[C()]*(n-1)]
        rows = []
        for label, program, matrix in zip(('forward', 'inverse'), programs, intended):
            for v in vectors:
                need(squared(v) <= radius**2, 'invocation radius')
                out, stats = apply(program, Vec(v), bits)
                error = squared([x-y for x,y in zip(out, mv(matrix, v))])
                allowance = getattr(caller, label+'_error')
                target = caller.target if hasattr(caller, 'target') else caller.spec.target
                need(error <= allowance**2 and allowance < Q(1, 1 << target),
                     'actual rounded endpoint allowance')
                b = caller.bound if hasattr(caller, 'bound') else caller.builder.bound
                need(stats['max_observed_height'] <= b['temporary_bits']
                     and stats['max_grid_numerator_bits']+1 <= bits+b['integer_bits'],
                     'actual intermediate word widths')
                rows.append(dict(direction=label, error_squared=str(error),
                                 output_sha256=vector_hash(out), statistics=stats))
        return rows

    records = []
    for label, n, c, shift, incoming in (
            ('normalized-shift', 2, Q(1,2), Q(1,3), 4),
            ('normalized-fine', 2, Q(2), Q(-3,8), 512)):
        new = Gaussian(raw, n, c, shift, 4, 10, incoming)
        old = old_normalized(raw, n, c, shift, 4, 10, incoming)
        plan, oldplan = new.compile(), old.compile()
        b, ob = new.builder.bound, old.builder.bound
        need(new.root == old.root and new.offsets == old.offsets
             and new.record()['root_sha256'] == old.record()['root_sha256'], 'same normalized kernel')
        need(b['child_target_bits'] < ob['child_target_bits']
             and b['data_bits'] <= ob['data_bits'], 'reduced actual normalized allocation')
        rows = trajectories(new, (plan, new.builder.inverse(plan)),
                            (new.root, inverse(new.root, C)), b['data_bits'], Q(4))
        if incoming == 512:
            need(b['data_bits'] == 512, 'incoming precision preserved')
        records.append(dict(label=label, old_child_bits=ob['child_target_bits'],
                            child_bits=b['child_target_bits'], old_data_bits=ob['data_bits'],
                            data_bits=b['data_bits'], trajectories=rows))

    ref = Reference(raw, 128, 1, 3, 3, 20, 160)
    final = None
    for kind, start, n, incoming in (
            ('narrow', 2, 2, 4), ('broad', 2, 2, 4), ('narrow', 2, 4, 512)):
        old = old_raw(raw, ref, kind, start, n, 4, 10, incoming)
        new = RawGaussian(raw, ref, kind, start, n, 4, 10, incoming)
        plan, oldplan = new.compile(), old.compile()
        cb, ocb = new.child.builder.bound, old.child.builder.bound
        need(new.reference_hash == old.reference_hash and new.reference_description == old.reference_description
             and new.reference_matrix == old.reference_matrix, 'same immutable raw reference')
        need(new.a_values == old.a_values and new.b_values == old.b_values
             and new.diagonal_records == old.diagonal_records, 'same raw gauges and setup')
        need(new.data_bits == cb['data_bits'] >= incoming, 'raw normalized common-grid fixed point')
        need(cb['child_target_bits'] < ocb['child_target_bits']
             and new.data_bits <= old.data_bits, 'reduced actual raw allocation')
        rows = trajectories(new, (plan,new.inverse_plan),
                            (new.reference_matrix,inverse(new.reference_matrix,C)),new.data_bits,Q(4))
        records.append(dict(label=kind+str(n), old_child_bits=ocb['child_target_bits'],
                            child_bits=cb['child_target_bits'], old_data_bits=old.data_bits,
                            data_bits=new.data_bits, incoming_bits=incoming,
                            reference_sha256=new.reference_hash, trajectories=rows))
        final = new

    need(any(r['data_bits'] < r['old_data_bits'] for r in records), 'actual data-width improvement witness')
    allocation_identity = (gaussian.allocation is full.allocation
                           and raw_gaussian.allocation is full.allocation)
    need(allocation_identity, 'no global mutation')
    reject(lambda: adapted(raw['research/rational-unitary-fft/full.py'].replace(
        b'256 * n ** 3 * chi ** 12', b'128 * n ** 3 * chi ** 12'), need, ceil_log2), 'exact original')
    wrong = RawGaussian(raw, ref, 'narrow', 2, 2, 4, 10, 4)
    key = 'narrow', ref.selected[2], ref.selected[2]
    entry = ref.entries[key]
    ref.entries[key] = Entry(Q(2), 'unit-diagonal', 0, Q(0))
    reject(wrong.compile, 'same common reference')
    ref.entries[key] = entry
    reject(lambda: RawGaussian(raw, ref, 'broad', 63, 4, 4, 10), 'cell')
    reject(lambda: apply(final.plan, Vec([C(Q(1,1<<512))]+[C()]*(final.n-1)), 4), 'input already on data grid')
    globals_without_child = dict(RawGaussian.__init__.__globals__, Gaussian=old_normalized)
    wrong_init = FunctionType(RawGaussian.__init__.__code__, globals_without_child,
                              argdefs=RawGaussian.__init__.__defaults__)
    MissingChild = type('MissingChildBinding', (old_raw,), {'__init__': wrong_init})
    reject(lambda: MissingChild(raw, ref, 'broad', 2, 2, 4, 10, 4).compile(),
           'one raw and normalized data grid')
    result = dict(binding=binding, cases=records, controls=5,
                  actual_callers=True, no_global_module_mutation=allocation_identity,
                  physical_tape_execution=False, new_kappa=False)
    encoded = json.dumps(result,sort_keys=True,separators=(',', ':'))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path)
    args = parser.parse_args()
    if args.emit:
        with args.emit.open('x') as out:
            json.dump(result,out,indent=2,sort_keys=True)
            out.write('\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(encoded == json.dumps(expected,sort_keys=True,separators=(',', ':')),
             'complete typed receipt')
    print(json.dumps(dict(cases=len(records), trajectories=sum(len(r['trajectories']) for r in records),
                          controls=5, result_sha256=sha256(encoded.encode()).hexdigest()),sort_keys=True))
    print('PASS_GAUSSIAN_DOWNSET_GRID same_reference_same_grid no_new_kappa')


if __name__ == '__main__':
    main()
