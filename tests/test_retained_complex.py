"""Exact dirty-scratch, binary phase and rejected-parameter controls."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from retained_complex import RetainedComplexCircuit as Retained, binary_rank, dot, counts, check, parameters

def add_row(target, source, scale=1):
    for key, value in source.items():
        value = target.get(key, 0) + scale * value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def projector(h, basis):
    return [sum((sum((b >> i & 1)*dot(b,1 << j) for b in basis)&1) << j
                for j in range(h)) for i in range(h)]


def apply(matrix, vector):
    return sum(dot(row,vector) << i for i,row in enumerate(matrix))


def matrix_product(a, b):
    columns = [sum((row >> j & 1) << i for i,row in enumerate(b)) for j in range(len(b))]
    return [sum(dot(row,column) << j for j,column in enumerate(columns)) for row in a]


def scatter_row(circuit, mask, rows):
    """The retained dyadic scatter row in terms of D_0,...,D_{h-2},C_*.

    The source contribution is the scalar central coefficient.  Keeping this
    as a row operation also checks arbitrary initial retained scratch values.
    """
    row = {}
    last = circuit.h - 1
    if mask & (1 << last):
        add_row(row, rows[-1], 1)
        for i in range(last):
            if not mask & (1 << i):
                add_row(row, rows[i], Q(-1, 4))
    else:
        add_row(row, rows[-1], Q(-1, 2))
        for i in range(last):
            if mask & (1 << i):
                add_row(row, rows[i], Q(1, 4))
    return row


def scalar_control(h=8):
    """Check forward/inverse/shear with every dirty role as a basis input."""
    circuit = Retained(h)
    code = circuit.compile()
    v, roles = len(circuit.inputs), circuit.roles
    rows = [{i: Q(1)} for i in range(2 * v + roles)]
    x, y, scratch = rows[:v], rows[v:2 * v], rows[2 * v:]
    original = [[dict(r) for r in bank] for bank in (x, y, scratch)]

    def mix(sign):
        gates = code["gates"] if sign > 0 else reversed(code["gates"])
        for _, ins, outs in gates:
            if sign > 0:
                for slot in ins[1:]:
                    add_row(scratch[ins[0]], scratch[slot])
                for slot in outs[1:]:
                    add_row(scratch[slot], scratch[ins[0]])
            else:
                for slot in outs[1:]:
                    add_row(scratch[slot], scratch[ins[0]], -1)
                for slot in ins[1:]:
                    add_row(scratch[ins[0]], scratch[slot], -1)

    def copy(sign, bank):
        for triple, slot in code["sources"].items():
            add_row(scratch[slot], bank[circuit.inputs.index(triple)], sign)

    def side_inject(sign, bank):
        for index, (target, coefficient) in enumerate(circuit.targets):
            row = scratch[code["outputs"][index]]
            add_row(bank[circuit.masks.index(target)], row, sign * Q(coefficient, 2))

    total_rows = [scratch[code["outputs"][i]] for i in circuit.total_outputs]

    def total_scatter(sign, bank):
        for j, mask in enumerate(circuit.masks):
            add_row(bank[j], scatter_row(circuit, mask, total_rows), sign)

    def invoke(inverse=False, source=None, target=None):
        source = x if source is None else source
        target = y if target is None else target
        operations = [
            (mix, 1),
            (total_scatter, -1), (side_inject, -1),
            (mix, -1), (copy, 1),
            (mix, 1),
            (total_scatter, 1), (side_inject, 1),
            (mix, -1), (copy, -1),
        ]
        if inverse:
            operations = [(op, -sign) for op, sign in reversed(operations)]
        for operation, sign in operations:
            if operation is copy:
                operation(sign, source)
            elif operation in (total_scatter, side_inject):
                operation(sign, target)
            else:
                operation(sign)

    invoke()
    expected = [dict(r) for r in original[1]]
    for target, source in zip(expected, original[0]):
        add_row(target, source)
    assert [x, y, scratch] == [original[0], expected, original[2]]
    invoke(True)
    assert [x, y, scratch] == original

    invoke()
    invoke(True, source=y, target=x)
    invoke()
    if x != [{key: -value for key, value in row.items()}
             for row in original[1]]:
        raise AssertionError(("exchange x", x[:2], original[1][:2]))
    if y != original[0]:
        raise AssertionError(("exchange y", y[:2], original[0][:2]))
    assert scratch == original[2]
    return dict(h=h, basis_variables=2 * v + roles,
                retained_roles=roles, forward_inverse_dirty_scratch=True,
                forward_shear=True, signed_exchange_controlled=True,
                exchange_snapshot=(len(x), len(y)))


def frame_control(h=8, reverse=False):
    """Enumerate all physical edges with grouped retained-total scatter."""
    circuit = Retained(h)
    code = circuit.compile()
    v, roles = len(circuit.inputs), circuit.roles
    zero, identity = [0] * h, [1 << i for i in range(h)]
    lines = [projector(h, [mask]) for mask in circuit.masks]
    node_projection = {
        node: projector(h, circuit.basis(circuit.labels[node]))
        for node in circuit.active
    }
    frames = lines[:] + [zero] * (v + roles)
    x, y = list(range(v)), list(range(v, 2 * v))
    slots = [2 * v + i for i in range(roles)]
    totals = [slots[code["outputs"][i]] for i in circuit.total_outputs]
    cache, total, loss, edges = {}, 0, 0, 0

    def transition(old, new):
        key = (tuple(old), tuple(new))
        if key in cache:
            return cache[key]
        delta = [a ^ b for a, b in zip(old, new)]
        rank = binary_rank(delta)
        increasing = matrix_product(old, new) == old and matrix_product(new, old) == old
        decreasing = matrix_product(old, new) == new and matrix_product(new, old) == new
        assert increasing or decreasing, "non-nested physical frame edge"
        residual = [w for w in range(1 << h) if apply(delta, w) == w]
        assert binary_rank(residual) == rank
        if rank:
            assert any(dot(w, w) for w in residual), "alternating residual"
            basis, remaining = [], residual
            while len(basis) < rank:
                characteristic = apply(delta, circuit.full)
                for b in basis:
                    characteristic ^= b
                choices = [w for w in remaining if dot(w, w) and
                           (rank - len(basis) == 1 or w != characteristic)]
                assert choices, "no orthonormal residual basis"
                b = choices[0]
                basis.append(b)
                remaining = [w for w in remaining if not dot(w, b)]
            for address in range(1 << h):
                phase = (apply(new, address).bit_count() -
                         apply(old, address).bit_count()) % 4
                expected = sum(b.bit_count() * dot(b, address) for b in basis) % 4
                if not increasing:
                    expected = -expected % 4
                assert phase == expected, "weight-mod-four phase identity"
        answer = rank, binary_rank(old) - binary_rank(new) if decreasing else 0
        cache[key] = answer
        return answer

    def gate(wires, frame):
        nonlocal total, loss, edges
        for wire in set(wires):
            rank, decrease = transition(frames[wire], frame)
            total += rank
            loss += decrease
            edges += 1
            frames[wire] = frame

    def frame_for(mode, line):
        if mode == "low":
            return zero
        if mode == "high":
            return identity
        if mode == "line":
            return line
        complement = [a ^ b for a, b in zip(identity, line)]
        return complement if mode == "complement" else line

    def mix(mode, inverse=False):
        gates = reversed(code["gates"]) if inverse else code["gates"]
        for node, ins, outs in gates:
            frame = frame_for(mode, node_projection[node])
            gate([slots[s] for s in ins + outs], frame)

    def copy(bank, mode):
        for triple, slot in code["sources"].items():
            j = circuit.inputs.index(triple)
            frame = frame_for(mode, lines[j])
            gate([bank[j], slots[slot]], frame)

    def inject(bank, mode):
        by_target = {mask: [] for mask in circuit.masks}
        for index, (mask, _) in enumerate(circuit.targets):
            by_target[mask].append(slots[code["outputs"][index]])
        for j, mask in enumerate(circuit.masks):
            frame = frame_for(mode, lines[j])
            gate([bank[j]] + by_target[mask], frame)

    def totals_gate(bank, frame):
        gate(bank + totals, frame)

    if not reverse:
        mix("low"); totals_gate(y, zero); inject(y, "low"); mix("low", True)
        copy(x, "line"); mix("node"); totals_gate(y, zero)
        inject(y, "complement"); mix("high", True); copy(x, "high")
    else:
        copy(y, "low"); mix("low"); inject(x, "line"); totals_gate(x, identity)
        mix("complement", True); copy(y, "complement"); mix("high")
        inject(x, "high"); totals_gate(x, identity); mix("high", True)

    for j in range(v):
        gate([x[j]], identity)
        gate([y[j]], [a ^ b for a, b in zip(identity, lines[j])])
    gate(slots, identity)
    expected = (2 * v + roles) * h - 2 * v + 2 * ((h - 1) ** 2 + h)
    assert total == expected
    assert loss == (h - 1) ** 2 + h
    return dict(h=h, reverse=reverse, roles=2 * v + roles, edges=edges,
                rank_sum=total, decreasing_dimension=loss,
                distinct_projector_edges=len(cache), all_phase_identities=True)



class RetainedComplexTests(unittest.TestCase):
    def test_complete_dirty_basis_and_both_phase_paths(self):
        self.assertTrue(scalar_control()['forward_inverse_dirty_scratch'])
        for reverse in (False,True):
            r=frame_control(reverse=reverse)
            self.assertEqual((r['roles'],r['rank_sum'],r['decreasing_dimension']),(1279,10234,57))

    def test_patch_keeps_max_when_complex_saving_exceeds_bit_saving(self):
        patch=(Path(__file__).resolve().parents[1]/'patches/retained-complex-31.patch').read_text()
        added='\n'.join(line[1:] for line in patch.splitlines()
                        if line.startswith('+') and not line.startswith('+++'))
        self.assertIn(r'\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}',added)
        self.assertNotIn(r'\chi=\tau+(1-\beta)(\sigma-\tau)',added)

    def test_supported_domain_and_retained_multiplicities(self):
        with self.assertRaises(ValueError): Retained(6)
        c=Retained(8)
        self.assertTrue(c.verify()['exact_total_multiplicities'])
        node=c.outputs[c.total_outputs[0]]
        left,_=c.args[node];c.args[node]=(left,left)
        with self.assertRaisesRegex(ValueError,'multiplicity'):c.verify()

    def test_consumer_rejects_stale_spacing_saving_and_guard(self):
        n=counts(Retained(24))
        for p in (replace(parameters(),c=Q(1,5)),
                  replace(parameters(),sigma=1-Q(8,10**9)),
                  replace(parameters(),kappa=Q(830,10**12)),
                  replace(parameters(),C1=Q(2))):
            with self.assertRaises(ValueError):check(p,n)
        self.assertGreater(check(parameters(),n)['absorption_gap'],0)

if __name__=='__main__':unittest.main()
