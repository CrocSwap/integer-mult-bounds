# Compact universal certificates for dirty linear circuits

**A reusable algebraic bridge and exact checker; no new κ.** A linear register
program with r arbitrary inputs and q noncommuting unary calls compiles into
r+q coefficient states. Exact subspace closure certifies its complete endpoint
for **every operator substitution and payload dimension**, without expanding
its noncommutative words. Failure returns a distinguishing word, its dirty
input/output roles, and explicit finite matrix counterexamples. An optional
change of variables makes every counterexample generator invertible.

This addresses the gap between small matrix experiments and universal recursive
substitution. The weighted-automata and noncommutative PIT algorithms are
classical and credited in [PROOF.md](PROOF.md). The contribution is the compact
register compiler, complete-boundary certificate contract, separate checker,
constructive diagnostics and source-bound application. No new general PIT
algorithm or first universal algebra check in this project is claimed.

## Result and use

The [bridge theorem](PROOF.md) gives a polynomial exact-field procedure and a
finite certificate of initial-span coverage, operator closure and zero final
projections. The checker performs no search or Gaussian elimination and imports
no producer code. A shortest nonzero coefficient word of length k produces an
explicit (k+1)-dimensional counterexample. With `--invertible`, all generators
are simultaneously triangular unipotent matrices. The checker validates the
discrepancy; shortestness follows from the search proof.

The [one-page guide](../../docs/research/universal-dirty-circuit-guide.md) gives
the grammar and acceptance boundary. The tools use only the standard library:

```sh
python3 -I -B research/universal-dirty-certificates/linear_words.py \
  research/universal-dirty-certificates/examples/dirty-echo3.json \
  --output /tmp/my-new-dirty-certificate.json
python3 -I -B research/universal-dirty-certificates/check_certificate.py \
  research/universal-dirty-certificates/examples/dirty-echo3.json \
  /tmp/my-new-dirty-certificate.json
```

Output paths must be new. Add `--matrices` to the checker to print sparse
concrete matrices for a negative certificate. API users can call
`linear_words.decide(problem, shifted=False)` and
`check_certificate.check(problem, certificate)`.

The committed wrong-order fixture is rejected using `A0=I+E01`, `A1=I+E12`,
`A2=I` in dimension three. Source payload e2 and zero other inputs produce
target discrepancy −1 in coordinate zero. Every generator is invertible.
Scalar substitutions miss the analogous commutator failure.

## Source-bound evidence

The adapter translates the actual emitted instructions of the authenticated
`research/cyclic-dirty-commutator-audit/echo.py`. The reference is identity on
every role plus `y += sign A_(n-1)...A_0 x`. The echo construction, schedule and
arbitrary-n/rounded proofs are predecessor work. New certificates cover the
tested emitted schedules for arbitrary substituted linear maps; the rounded
backend and its cost theorem are not replayed.

- 210 complete source-echo identities: 1,2,3,5,8,12,16 factors; fanouts 2,3,8;
  both signs; Q, Q(i), F2, F3, F5. At most 284 states and 38 invariant rows.
- 120 differential circuits against separately implemented explicit-word
  expansion, including self reads, rational coefficients, swaps and zero maps.
  Each planted discrepancy has a literal full-column matrix replay.
- Cleanup, source, coefficient and order mutations; malformed certificates;
  finite-field controls; scalar commutator blindness; the tensor-of-sum trap;
  and the sharp unipotent-degree witness family.
- **2^64 distinct endpoint words** in one stress circuit: 130 states and 65
  certificate rows. Initial production/check took about 1.3 seconds on the
  Python 3.14 host. This measurement does not predict arbitrary supplier replay.

Committed examples contain problems and inspectable certificates. Default
verification is read-only and checks exact certificate reproduction. Environment
and measured replays appear in [VALIDATION.json](VALIDATION.json).

```sh
python3 -B scripts/research_package.py --package research/universal-dirty-certificates --check-only
python3 -B scripts/research_package.py --package research/universal-dirty-certificates
```

Direct verification also supports `-I -O -B`. Generic CI targets Python 3.12;
local interpreter versions are recorded separately. No historical heavy suite,
native supplier replay or Lean build is required.

## Limits and trust

Supported fields are Q, Q(i), and F_p, prime p<=2^31-1; fractions need invertible
denominators. Every input/returned role is retained. Equal payload dimensions
and **independent** operator symbols are required. A negative verdict need not
survive additional inverse, commutation, Clifford or reachable-state constraints.
The existing relation-aware free-group tensor audit remains appropriate there.

The proof is written mathematics with exact executable certificates, not a
proof-assistant formalization or independent human review. The checker has a
separately transcribed compiler and shares `fields.py` with the producer. These,
Python and source transcription are trusted; differential expansion and literal
matrix execution are additional checks, not independent reviewers.

Universal acceptance permits termwise tensor substitution with scalar
coefficients fixed. It does not tensorize a sum. Affine constants, rectangular
types, nonlinear leaves, physical aliasing, native implementation, precision,
rounded restoration, stock, hosting, tapes and the complete paid/outer invoice
remain separate. No supplier admission or selected-frontier change is claimed.

## Open next questions

- Bind another contributor's independent-symbol program with a literal source
  adapter and complete endpoint. Compare its certificate against an existing
  symbolic replay. Types and generator relations must match first.
- Add a relation-aware frontend for one named inverse/commutation model, starting
  with a sound normalization theorem and boundary controls. Independent symbols
  are only a conservative test of a relation-constrained implementation.
- Profile rational coefficient growth and repeated path traversal on a larger
  real adapter, preserving exactly the same closure equations. The arithmetic
  bound does not guarantee scalable replay of every 632-role supplier.

## Credit and coordination

Prepared for **zxv** with substantial **OpenAI Codex assistance**; Apache-2.0.
Classical weighted-automata/PIT credit belongs to the cited authors. The echo
package is prepared for **androolloyd**, following **Chafik Boukhalfa / chafreaky
PR628**, **Ali Romman PR621** and the retained inverse/precision lineage.
**Cinna Davis PR4100/4088**, **ToikY's free-word tensor-lift audit**, **Sagar
Thakrar PR3687**, **roger-sato PR3693**, and the universal dirty-phase audit
following **Charles Bethin PR1278** retain their prior results and credit.
Ross Richardson's cut58 and the two-register short-mixing work retain their
distinct tensor-separation arguments. Only the small echo scheduler is imported.

[SOURCES.json](SOURCES.json) pins the base, catalogue, selected record, live
scheduler and relevant provenance. [TASK.json](TASK.json) records the explicit
scope change and bounded obligations. The canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145795)
records overlap and publication status. Cache misses do not establish novelty;
unpublished work and arbitrary historical diffs remain outside the checked scope.
