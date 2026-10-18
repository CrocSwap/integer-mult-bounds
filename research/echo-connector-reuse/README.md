# Recursive interface: borrow restored sibling connectors

**Research construction / scoped interface refinement; no new kappa.**

A dirty-echo child can borrow sibling connector arrays when it restores them
before return. This removes PR730's blanket reservation during descendant
calls. Source/target ports stay excluded, factor order is preserved, and all
inverse and restoration calls are paid.

| Factors | Cap | PR730 reserved calls | Reuse calls | Actual reuse scratch |
|---|---:|---:|---:|---:|
| 5 | 2 | infeasible | 20 | 2 |
| 15 | 4 | 224 | 144 | 4 |
| 27 | 5 | 704 | 416 | 4 |
| 59 | 5 | infeasible | 1,712 | 5 |
| 59 | 6 | 3,456 | 1,712 | 5 |

The 59-factor comparison reduces the complete leaf bill by **1,744 calls
(50.46%)** at the same cap; the new witness needs one fewer borrowed array.
This is an abstract local operation count, not measured runtime or a supplier
saving. The factors are interface fixtures, not asserted cyclic-inverse kernels.

From the repository root, Python 3.9+ with the standard library:

```sh
python3 -I -O -B research/echo-connector-reuse/verify.py
```

Expected:

```text
PASS_ECHO_CONNECTOR_REUSE: 861 trees; 642 exhaustive price/budget cases; n=59: 3456 -> 1712 calls, 6 -> 5 borrowed arrays
```

Run `python3 -I -O -B research/echo-connector-reuse/test_package.py` for
standalone relocation and four package/implementation corruption controls.
The package also runs when copied outside the repository. It imports only
local files through resolved paths, checks immutable source pins, and compares
the complete deterministic certificate. `--write` deliberately regenerates
that certificate and is not the verification command.

- [PROOF.md](PROOF.md): identity, nonlinear restoration, exact storage/weighted
  optimization recurrence, complete cost/precision bill and inherited limits.
- [CERTIFICATE.json](CERTIFICATE.json): exact trees, counts, word hashes and
  completed coverage. No floating objective or solver is used.
- [SOURCES.json](SOURCES.json): base and byte-exact source/notice pins.
- [CLAIM.md](CLAIM.md): OS seed, selection, sprint coordination and final result.
- [NOTICE.md](NOTICE.md): contributor credit and substantial AI disclosure.
- [VALIDATION.md](VALIDATION.md): performed checks and explicit omissions.

The exact DP optimum is restricted to ordered binary/ternary echo trees with
this allocator and positive fixed integer prices. The written proof also gives
capacity `M_b=2M_(b-1)+M_(b-2)`, starting 1,2: five arrays admit 70 factors,
where PR730's reserved class admits 32. No general reversible-space bound is
claimed. Target-dependent increments, hidden state, aliases and uncontrolled
floating-point target addition do not satisfy the leaf contract.

PR673 (androolloyd) supplies the echo identity. PR730 (Sagar Thakrar) supplies
the fixed-budget interval optimization and the executed reserved comparator.
PR689, PR663, PR628 and their predecessors retain credit. Concurrent #744
audits disjoint-pool ternary schedules; #758 admits higher arities while
retaining the reserved allocation. Their distinct broader/numerical evidence
is acknowledged; no code or unverified count from them is used in this table.
PR714's clean root uses a different storage contract. This package requires
no clean borrowed array.

Publication refresh: Alexander Schwartzman's #784 proves a sharp call bound
for all-arity trees with reserved parent scratch; this allocator changes that
hypothesis. nightangelflowerwin-ops's #788 reuses an initially clean checkpoint
within reserved binary trees. Both are distinct concurrent results, not source
dependencies. Their proof heads are recorded in [VALIDATION.md](VALIDATION.md).

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Selected #626/#543 remains
`51110230636731/31250000000000000`. PR730 is pinned to
`d222e348179cc02a54d6d26dbd2838944f62c6e5`; PR673 to
`156f259b99723468cfdd2b5d47d0ba894f09bea7`.

PR673's direct all-role integration still fails its favorable complete-cost
screen. No supplier integration, all-size/tape/physical realization, analytic
transfer, numerical rounded-leaf audit, full repository replay, full Lean
multiplication proof or new exponent is supplied by this local result.
`upstream/`, existing generators, review ledger and selected frontier are unchanged.
