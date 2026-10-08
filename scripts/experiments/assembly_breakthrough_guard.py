#!/usr/bin/env python3
"""Audit a dependency-path guard for the existing compressed complex network.

This does not change a published multiplier witness.  It uses conservative
all-to-all dependencies within each fixed scalar gate, and the compiled side
roles of complex_circuit.py, to check every frame descent in one invocation.
The written argument composes the three disjoint-invocation stages without
materializing their trillions of roles.

Prepared with assistance from OpenAI Codex.  Not formal verification.
"""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from complex_circuit import ComplexSideCircuit, Checks, compile_roles
from complex_network import counts as complex_counts
from certify import require
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from prepare_layers import serializable

RHO = Q(1001, 1000)
ZETA = Q(1, 10000)


class PathAudit:
    """Maximum path weight in a DAG; every gate joins all its incidences."""

    def __init__(self, dimensions):
        self.dim = list(dimensions)
        self.loss = [0] * len(dimensions)
        self.rank = [0] * len(dimensions)
        self.descents = []
        self.gates = 0

    def gate(self, name, roles, dimension):
        roles = tuple(set(roles))
        for role in roles:
            old = self.dim[role]
            self.rank[role] += abs(dimension - old)
            descent = max(0, old - dimension)
            self.loss[role] += descent
            if descent:
                self.descents.append((name, role, descent))
            self.dim[role] = dimension
        loss = max(self.loss[role] for role in roles)
        rank = max(self.rank[role] for role in roles)
        for role in roles:
            self.loss[role] = loss
            self.rank[role] = rank
        self.gates += 1

    def terminal(self, role, dimension):
        self.gate("terminal", (role,), dimension)


def invocation(c, code, dimensions, stage, inverse):
    """Check full early/middle/late schedules including data and centers."""
    h, m = c.h, c.h ** 3
    v, r = len(c.triples), code["roles"]
    # Physical banks X,Y; side roles; central roles.  Scratch starts at 0.
    x = {t: i for i, t in enumerate(c.triples)}
    y = {t: v + i for i, t in enumerate(c.triples)}
    side = lambda slot: 2 * v + slot
    center = tuple(range(2 * v + r, 2 * v + r + h + 1))
    a = h ** (stage - 1)
    low, high = h ** stage - h, h ** stage
    audit = PathAudit([a] * v + [a - 1] * v + [0] * (r + h + 1))
    pieces = {t: [] for t in c.triples}
    for i, slot in code["outputs"].items():
        pieces[c.pieces[i][0]].append(side(slot))

    def mix(mode, reverse=False):
        gates = reversed(code["gates"]) if reverse else code["gates"]
        for node, ins, outs in gates:
            if mode == "low":
                frame = low
            elif mode == "high":
                frame = high
            elif mode == "label":
                frame = low + dimensions[node]
            else:
                assert mode == "complement"
                frame = low + h - dimensions[node]
            audit.gate("mix-" + mode, (side(s) for s in ins + outs), frame)

    def inject(bank, frame):
        for t in c.triples:
            audit.gate("inject", [bank[t]] + pieces[t], frame)

    def copy(bank, frame):
        for t, slot in code["sources"].items():
            audit.gate("copy", (bank[t], side(slot)), frame)

    def central(bank, frame, name):
        audit.gate(name, tuple(bank.values()) + center, frame)

    if not inverse:
        mix("low")
        inject(y, low)
        mix("low", True)
        central(y, low, "old-scatter")
        copy(x, low + 1)
        central(x, high, "gather")
        central(y, low, "central-return")
        mix("label")
        inject(y, high - 1)
        mix("high", True)
        central(x, high, "undo-gather")
        copy(x, high)
    else:
        copy(y, a - 1)
        central(y, low, "gather")
        mix("low")
        inject(x, low + 1)
        mix("complement", True)
        central(x, high, "scatter")
        central(y, low, "central-return")
        copy(y, high - 1)
        central(x, high, "undo-scatter")
        mix("high")
        inject(x, high)
        mix("high", True)

    for role in x.values():
        audit.terminal(role, high)
    for role in y.values():
        audit.terminal(role, high - 1)
    for role in range(2 * v, len(audit.dim)):
        audit.terminal(role, m)

    assert len(audit.descents) == h + 1, audit.descents[:10]
    assert all(name == "central-return" and d == h
               for name, role, d in audit.descents)
    assert max(audit.loss) == h
    assert max(audit.rank) <= m + 2 * h
    return dict(stage=stage, inverse=inverse, roles=len(audit.dim),
                conservative_gate_count=audit.gates,
                decreasing_edges=len(audit.descents),
                decreasing_edge_rank=h,
                maximum_path_descent=max(audit.loss),
                maximum_path_rank=max(audit.rank),
                upper_path_rank=m + 2 * h)


def audit_h(h):
    c = ComplexSideCircuit(h)
    checks = Checks(c)
    code = compile_roles(c)
    dimensions = {node: checks.label(node).dim for node in c.active}
    controls = [invocation(c, code, dimensions, stage, inverse)
                for stage, inverse in [(1, False), (2, True), (3, False)]]
    return dict(h=h, ambient_dimension=h ** 3,
                maximum_three_stage_path_descent=3 * h,
                three_stage_path_rank_upper=h ** 3 + 6 * h,
                invocations=controls)


def exact_recurrence_controls():
    """Integer-power comparison plus independent finite recurrence controls."""
    h = 25
    m, path = h ** 3, h ** 3 + 6 * h
    rho = RHO
    assert path ** rho.denominator < m ** rho.numerator
    # Check the exact closed form for representative positive node charges.
    for node_charge in (1, 97, 10 ** 80):
        for leaf in (1, 17, m - 1):
            depth = 8 * leaf
            for levels in range(9):
                closed = path ** levels * 8 * leaf
                closed += node_charge * (path ** levels - 1) // (path - 1)
                assert depth == closed
                assert depth <= (8 * leaf + node_charge) * path ** levels
                depth = path * depth + node_charge
    beta, zeta, epsilon = Q(1, 1000), Q(1, 10000), Q(49999, 100000)
    c1 = beta + (1 - beta) * rho + zeta
    assert epsilon * c1 < 1
    # Existing complex leaf saving, now with a small stopping exponent.
    ac = Q(14, 10 ** 9)
    return dict(h=h, m=m, path_branching=path, rho=str(rho),
                exact_power_comparison="15775^1000 < 15625^1001",
                beta=str(beta), zeta=str(zeta), epsilon=str(epsilon),
                guard_exponent=str(c1), guard_slack=str(1 - epsilon * c1),
                complex_leaf_saving=str((1 - beta) * ac),
                old_beta_19_over_25_leaf_saving=str(Q(6, 25) * ac),
                finite_recurrence_comparisons=3 * 3 * 9)


def dependency_guard(n, beta, zeta=ZETA, rho=RHO):
    """Same C0 as the published stopped guard; certify its new exponent."""
    require(0 < beta < 1 and zeta > 0 and rho > 1, "Invalid guard parameters")
    h, m, s, W = (n[key] for key in ("h", "m", "s", "W"))
    require(m == h ** 3, "The three-stage frame argument requires m=h^3")
    q = m + 6 * h
    require(q ** rho.denominator < m ** rho.numerator,
            "rho does not dominate the dependency-path branching exponent")
    E = 64 * (W + m + 1) ** 3
    B = s + E
    raw = max(Q(128 * m * B * B), 18 * m * B * B * (1 + 1 / zeta))
    C0 = -(-raw.numerator // raw.denominator)
    C1 = beta + (1 - beta) * rho + zeta
    slacks = dict(total_call_domination=s - q,
                  one_piece_constant=9 * B * B - q * (8 + E),
                  whole_layer_constant=C0 - (9 * m * B * B * (1 + 1 / zeta) + 18),
                  exponent_above_one=C1 - 1)
    for name, slack in slacks.items():
        require(slack > 0, "Guard constant comparison failed: " + name)
    return dict(h=h, m=m, s=s, W=W, path_branching=q, E=E, B=B,
                rho=rho, beta=beta, zeta=zeta, C0=C0, C1=C1,
                constant_slacks=slacks)


def research_witness(n=None, parameters=None):
    """Same aligned-bit kappa, explicitly certified with the smaller beta.

    This deliberately bypasses the historical witness() guard equality;
    the complete new guard argument and all old assembly slacks are checked.
    No existing witness function or published certificate is modified.
    """
    from aligned_bit_network import parameters as aligned_parameters
    n = n or complex_counts(ComplexSideCircuit(25))
    if parameters is None:
        beta = Q(1, 1000)
        parameters = replace(aligned_parameters(), beta=beta,
                             C1=beta + (1 - beta) * RHO + ZETA)
    p = parameters
    g = dependency_guard(n, p.beta)
    require(p.C1 == g["C1"], "Dependency-path guard mismatch")
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    slacks = fast_constraints(p)
    slacks["packed_overhead"] = p.lam - exponents["internal"]
    slacks["reserved_axes"] = p.lamp - exponents["preprocessing"]
    for name, slack in slacks.items():
        require(slack > 0, "Research witness constraint failed: " + name)
    margins = fast_margins(p)
    minimum = min(margins.values())
    require(minimum > p.kappa, "Research witness has no absorption gap")
    return dict(
        status="ALTERNATE BASELINE WITNESS; NO HEADLINE IMPROVEMENT",
        parameters=vars(p), guard=g, recurrence=exponents,
        constraint_slacks=slacks, margins=margins,
        minimum_margin=minimum,
        limiting_margins=[key for key, value in margins.items() if value == minimum],
        absorption_gap=minimum - p.kappa,
        scope="Same aligned-bit kappa, additionally conditional on the written dependency-path guard proof.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h", nargs="+", type=int, default=[8, 10, 12, 25])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = dict(
        status="RESEARCH GUARD REFINEMENT; NO NEW MULTIPLICATION EXPONENT",
        date="2026-10-07",
        assumption="Existing nested residual frames and saved-input scalar gates",
        invocation_controls=[audit_h(h) for h in args.h],
        recurrence=exact_recurrence_controls(),
        alternate_baseline_witness=research_witness(),
        scope="Conservative finite DAG controls support the written proof; not formal verification.")
    result = serializable(result)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        witness = result["alternate_baseline_witness"]
        print("PASS dependency-path guard; h controls", ",".join(map(str, args.h)),
              "; q=15775; C1=1001099/1000000; same kappa", witness["parameters"]["kappa"],
              "; minimum margin", witness["minimum_margin"])
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
