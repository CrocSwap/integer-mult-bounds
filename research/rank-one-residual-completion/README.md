# Exact all-rank completion for a rank-one residual form

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. For an
injective binary symplectic partial map h:U -> V, let D=(h+I)U, r=dim D,
and let b((h+I)u,(h+I)v)=omega(u,(h+I)v). If rank b=1, then

    minimum transvection length = 2r-1.

The new cases have r at least three. Krzysztof Wojt's
[PR5097](https://github.com/CrocSwap/integer-mult-bounds/pull/5097) proves
the lower bound r+nullity(b), the zero-form optimum 2r, and the rank-two
rank-one case. Its Open next question 1 asks about higher-rank nonzero forms.
This contribution supplies the attaining word for the rank-one slice at
every r. At r=3 it closes the interval [5,6] at five. It does not classify
other residual ranks or improve kappa.

[PROOF.md](PROOF.md) shows that one anisotropic pivot leaves a zero residual
form on r-1 displacement dimensions. The predecessor's two-turn reduction
then finishes the word. [completion.py](completion.py) implements that
construction locally. It validates independence, injectivity and preservation
of pairings, and rejects residual forms whose rank differs from one.

All axes lie in the original V. The action outside U is free. Required fixed
spectators must be prescribed in U, and the implementation preserves them.
Under the cited signed-Pauli contract, compatible sign corrections are free
in this formal tariff. Absolute phase and physical costs are separate.

## Exact evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rank-one-residual-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rank-one-residual-completion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank-one-residual-completion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rank-one-residual-completion --check-source-history
```

Other machines may substitute their CPython 3.12 path. The standalone marker
is `PASS_RANK_ONE_RESIDUAL_COMPLETION`; the launcher must also print
`PASS_REGISTERED_RESEARCH_PACKAGE`. Receipts are generated on stdout and bind
every regular package file by SHA256. No receipt is hand-written or stored in
the checkout. The standalone commands are read-only and require no Git or
external source inputs.

The finite checks cover exactly:

- Every nonzero rank-one binary form in dimensions 3, 4 and 5, represented
  uniquely as p q-transpose for nonzero p,q. There are 1,235 forms. Each has
  a literal symplectic realization and two prescribed fixed spectators.
- All 242 of those forms with zero diagonal, where a sum of basis vectors
  rather than a basis vector must supply the anisotropic pivot.
- 52 larger or conjugated fixtures, through displacement rank 12, including
  a rank-three contract in the original six-dimensional ambient space.
- Independent dense-coordinate evaluation of every emitted full matrix,
  every prescribed image, all symplectic pairings and full displacement rank
  exactly 2r-1. The checker uses dense row elimination rather than the
  constructor's packed binary elimination.
- 182 rejecting one-turn omissions, plus malformed/out-of-scope contracts
  and an inconsistent pairing system. The generated receipt gives the
  control count.

These are finite corroborations of the written dimension-uniform proof.
They do not enumerate all partial maps in the tested dimensions. No
predecessor scientific executable, receipt, census or compiler is replayed.

## Scope and provenance

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. [TASK.json](TASK.json) records the explicit change
from the formal-interface-lemma card to this written interface side result.
[SOURCES.json](SOURCES.json) pins the problem statements as provenance only.
The selected source-binding orientation command passed. The advance
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363481)
and scoped overlap checks precede the construction.

The turn count is an abstract tariff. It is not native Gaussian rank, paid
recursive rank, a favorable supplier invoice, physical tape cost or a new
multiplication theorem. A compatible signed lift with charged monomial
passes, phase anchor, actual caller, dirty-owner restoration, precision,
stock and compiler/outer admission remains to be supplied. The selected
frontier and five retained assumptions are unchanged. Selected cold replay,
Lean and Docker were not run. Independent human and formal proof-kernel
review are unclaimed. CI results belong in the PR body.

## Implementation bounds

The public `complete` entry point accepts at most 16 qubits, hence at most
32 basis vectors and 32-bit ambient vectors. Every elimination loop is bounded
by these dimensions. A correction has at most 2r-1 turns and each step
strictly decreases displacement rank. Helpers operate on validated internal
data. The mathematical theorem has no dimension cap.

Power of Ten rule 3 has a managed-runtime deviation in `completion.py` and
`verify.py`. Python allocates integers and collections during execution.
The API cap above bounds the live algebraic data; the verifier has fixed
finite census bounds and does not accumulate per-case matrices. Verification
checks the accepted cap and rejects a dimension above it. A fixed-capacity
native implementation would be needed before a steady-allocation claim.
Rule 10 uses warning-strict normal/optimized replay and source compilation;
availability of additional static diagnostics is recorded in the PR body.
No function exceeds 60 physical lines. There is no recursion, dynamic code
generation, network access or subprocess execution in either scientific file.
The verifier loads the named local completion module through the standard
import loader; that is its sole dynamic dispatch boundary.

## Open next questions

- Determine an attaining formula for residual rank two at displacement rank
  at least three. First examine the residual form after an anisotropic pivot;
  a nonzero alternating remainder is an unresolved obstruction here.
- Price one actual signed native contact satisfying this partial contract.
  Include fixed spectators and an absolute phase anchor, then charge every
  turn, Pauli correction, monomial pass and owner/restoration operation.
  A shorter formal word alone gives no recursive saving.

## Credit

Krzysztof Wojt / krzysztofwojt / PR5097 supplies the explicit higher-rank
question, displacement-plus-nullity lower bound, zero-form construction and
rank-two pivot proof. Nick Petalas / PR5085 supplies the residual form and
low-length cutoff. Brian / JoyboyBrian / PR5051 supplies signed compatibility;
David Ganz / Dugongue / PR4841 supplies native compiler context. Cao Yifan /
intqwq, Cinna Davis, zxv, Jacob Alan Sussman and the retained native/compiler
lineage retain their predecessor credit. Symplectic transvections, residual
forms and binary elimination are classical. No literature-priority claim is
made. The new step is the all-rank rank-one attainment proof and its local
constructor; predecessor files and credit lines are unchanged.
