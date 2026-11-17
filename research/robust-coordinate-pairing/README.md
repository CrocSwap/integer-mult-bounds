# Exact helper-pairing capacity under coordinate uncertainty

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written algebraic proof with exact finite corroboration.
No new kappa is claimed.

For any field, nominal matrix B and set E of independently uncertain entries,
the largest identity block recoverable by one fixed left/right pairing is

```text
max { r : X (B + sum_E t_ij E_ij) Y = I_r for every t }
  = max { rank B[A,C] : the rectangle A times C contains no entry of E }.
```

The theorem grants arbitrary dense field-valued X,Y. It supplies attaining
maps from a clean nonsingular minor. Testing just the nominal map and each
single-entry alternative gives the same capacity as the entire uncertainty
family. The proof works over small fields as well as R or C.

For B=I, the capacity is exactly the independence number of the directed
error-support graph; loops forbid their vertices. Dense mixing gives no gain
over selecting independent coordinates. A directed n-cycle has sharp capacity
floor(n/2), even though the nominal and every single-entry alternative are
invertible. Five such uncertain entries therefore reduce five pointwise
recoverable channels to exactly two common channels. [PROOF.md](PROOF.md)
gives the quantified statements, proof and explicit boundary witnesses.

This is an original contract obstruction for the optimistic identity-pairing
relaxation. It can reject a common helper contract when its uncertain pairing
has too little capacity. No selected supplier is asserted to have that
uncertainty model, and passing this test supplies no physical implementation.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/robust-coordinate-pairing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/robust-coordinate-pairing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/robust-coordinate-pairing
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/robust-coordinate-pairing --check-source-history
```

Substitute another absolute CPython 3.12 path elsewhere. Direct replay prints
`PASS_ROBUST_COORDINATE_PAIRING` in a generated JSON receipt bound to the six
package files by SHA256. It writes nothing and needs no Git, network, solver
or predecessor executable. Normal and optimized modes enforce the same checks.

The exhaustive oracle considers every left/right matrix, not just coordinate
selectors. It compares the exact maximum against the clean-rectangle formula
on 10,266 support cases from 231 nominal matrices, examining 943,861 sandwiches
and finding 7,869 nominal identity sandwiches. The nominal domains are all
1-by-1 and 2-by-2 matrices over F2 and F3, all 2-by-3 and 3-by-2 matrices over
F2, and I3 over F2. Every possible uncertainty support is included in each
case. All 8,400 positive-capacity cases also receive a constructed attaining
pairing, checked against the nominal and every permitted single-entry change.

Additional checks cover all 530 directed graphs with loops on one through
three vertices; fifteen cycle instances of lengths three through five over
Q, F2, F3, F5 and F7; and 112 rational nominal/support cases. Eight boundary
equalities and four rejecting omitted-error controls distinguish independent
uncertainty, correlated uncertainty, the identity nominal assumption, empty
and full uncertainty, singular nominal matrices and exact recovery.

These are finite corroborations of the written theorem. They do not exhaust
all fields or dimensions and are not a proof-kernel certificate.

## Scope, provenance and credit

The complex-new-helper-inventory card changes scope to a common-pairing
interface lemma. This settles an explicitly changed algebraic premise rather
than delivering the card's physical supplier or complete signed moment. Work
stopped at the first proved result. The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19571898)
records the question before the proof and exhaustive computation.

The base is canonical main e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8. The selected record gives conditional kappa 0.00363005817 and
`make frontier7000-verify`; the older priority prose describes an earlier
checkpoint. The selected binding-only orientation passed. The selected
scientific construction was not replayed. SOURCES pins the selected record
and original card as historical provenance; there are no live source inputs.

The proof builds on classical rank inequalities, nonsingular minors and the
zero-outer-product property over fields. No contributor construction, word,
identity, invoice or numerical result is used as a premise. Ali Romman's
[#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615) supplies the
surrounding dyadic helper-pairing context. Nick Petalas's
[#7269](https://github.com/CrocSwap/integer-mult-bounds/pull/7269) concerns odd
denominator budgets for a fixed pairing; his
[#6585](https://github.com/CrocSwap/integer-mult-bounds/pull/6585) requires
common-chart isolation with both cross blocks zero. Those results are
background and are neither extended nor audited here. No general literature
priority is claimed for elementary rank-factorization methods.

Live open/account PR lists, recent handoff comments, active Discussions,
local reservations, the cached card search, targeted merged/open PR searches
and direct main-tree formula/object searches were inspected. Their text
coverage does not prove novelty or cover all diffs and unpublished work.

## Limitations

Only the retained identity block is constrained. Both spectator cross blocks,
arbitrary dirty restoration, chronology, extra workspace, adaptive charts,
correlated errors, approximation and coefficients in rings with zero divisors
require different arguments. Field-valued attaining maps need not be dyadic.
No actual cut, producer, consumer, scalar schedule, native realization,
precision/storage policy, physical hosting, paid/target invoice or complete
multiplication theorem is supplied. All five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.
Lean, Docker and the selected scientific cold replay are unrun.

## Open next questions

- Does one actual helper cut require common pairings across a specified
  independently varying coordinate family? Bind the producer's alternatives
  and permitted charts first. Without that contract, this theorem does not
  exclude the cut or imply a new supplier cost.
- What is the capacity for a supplied correlated error space? Begin with two
  specified error generators. The skew-symmetric boundary witness shows why
  replacing the space by the union of its entry supports can lose channels.
  Physical delivery and complete invoices remain separate obligations.

## Implementation bounds

Build the Lever led to the rerunnable verifier. Prove It Works led to the
complete small-field sandwich oracle and explicit attaining maps. The
engineering playbook is autonomous local run, with a stop at the first proved
result. No shared code or frozen predecessor package is changed.

All functions are below 60 physical lines. There is no recursion, subprocess,
network or dynamic code execution. The verifier has no external mathematical
input. Matrix dimensions are at most five; field enumerations store at most
512 matrices with nine entries each, and support tables have at most 512
entries. Each exhaustive loop is bounded by these fixed finite domains.
The five-dimensional cycle check considers at most 1,024 rectangles. Explicit
exceptions retain mathematical checks under optimized execution.

Power of Ten rule 3 has a managed-runtime deviation in verify.py: CPython
allocates bounded tuples, lists, integers and Fractions during this offline
calculation. The finite domains above bound live state; no fixed-pool or
steady-service claim is made. A fixed-storage implementation would need a
separate port. Rule 9 uses one fixed local sorting key for a finite rectangle
list and ordinary standard-library iterators; there is no user-supplied call
target. Warning-strict normal/optimized replay and in-memory compilation are
the available interpreter diagnostics. No separate static type analysis is
claimed. No production implementation is admitted by these checks.
