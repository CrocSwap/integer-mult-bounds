# P104 private-macro dual: exact local precision interface

The finite private-macro dual in [PR2479](https://github.com/CrocSwap/integer-mult-bounds/pull/2479)
has **absolute-defect coefficient 2393/2** and **native-only coefficient 861/2**.
These are attained, and exceed the original forward word's 450 and 356 in
[PR2096](https://github.com/CrocSwap/integer-mult-bounds/pull/2096).
The native rank profile is unchanged, but the signed propagation of errors is
different. PR2096 does not claim its constants for this dual word; this result
prevents that unsupported transfer and supplies the separate local implication.

The norm is the maximum of the individual register Hilbert norms. It is neither
an addresswise maximum nor the Hilbert norm of the concatenated register bank.
The exact domain is PR2479's 4,058-event original G/2 dual, with 280 arbitrary
public inputs, eight known-zero owned accumulator lifetimes and 4,042 defect
sites. A corrected P104 identity word is not covered.

| Quantity | Exact coefficient | First attaining boundary |
| --- | ---: | --- |
| Ideal input to any prefix, P | 64 | after event 1125, X88 |
| Unit absolute defects at every update, A | 2393/2 | after event 4009, X3 |
| Independent defects weighted by local input count, K | 3025/2 | after event 4009, X3 |
| Native-child-only unit defects | 861/2 | after event 4009, X3 |

Cuts are one-based completed-event boundaries. The ideal endpoint maximum is
only 26. Final absolute-defect maxima are `2393/2, 7, 10, 723/4, 211/2` for
`X, Y, G, Q, D` respectively. Exact symbolic restoration of the 72 dirty helpers
does not imply restoration of perturbations injected along their computation.

## Local contract and exact scalar reduction

Let H be a complex Hilbert space. Each initial register is an arbitrary vector
of norm at most B; different registers may have correlated values. Every
canonical chart and ideal native transport is unitary. A completed ADD
`dst += a*src` or native transport is followed by an arbitrary additive defect
in its destination. There are 2,632 ADDs and 1,410 native transports. A native
defect bounds the completed child output, not any unspecified internal step.
Endpoint monomials, known-zero allocation and discard are exact in this model.

For a register at frame V, conjugate its physical value and each newly injected
defect by its actual unitary dual chart. Norms are unchanged. A transport then
preserves the logical value and adds its transformed defect; an ADD is the
literal rational scalar recurrence. This is PR2096's credited Hilbert-defect
method applied to the changed word. It applies conditionally in any Hilbert
dimension with these unitary charts. Only the retained 512-address realization
is source-checked here.

The retained PR2479 replay checks the complete word, all native phases and
positive child ranks, including ordinary transpose of private transports and
complex conjugation of public transports. Transpose and conjugation of a
unitary matrix remain unitary. Its canonical native child has eigenvalues
1 and i on the two eigenspaces of an involutive permutation; all other factors
are address permutations and unit-modulus Gaussian phases. Thus the norm
premise is tied to the actual finite native recipes. We do not assume a rounded
recursive implementation is contractive or that a norm check authenticates phase.

Write the exact logical value at cut t in register r as

    sum_i p[t,r,i] * initial_i + sum_s e[t,r,s] * defect_s.

Signed rational propagation follows every event. At zero allocation the new C
row is empty; at discard only its own row is deleted. Errors already exported
from C remain in other rows. Each lifetime starts separately. Row absolute
sums give the constants in the table. Unchanged registers retain their prior
rows, so examining the changed register after every event and all initial
states covers every live register at every boundary.

The first three defect quantities use weights 1, `1+abs(a)` at ADDs / 1 at
transports, and 1 only at transports respectively. The initial-input bound and
each independent-defect bound are sharp: choose a common unit vector and align
the independent inputs or defects with the signs of the attaining row. The
verifier executes those rational assignments literally and attains all four
reported coefficients. In particular zero inputs and unit independent
all-update defects attain 2393/2 at X3; restricting injections to native sites
attains 861/2. Those are explicit failures of transferring the forward bounds,
not failures of the correctly scoped forward result.

## State-relative feedback implication

Now suppose a native completed-output defect has norm at most `u*||input||`,
and an ADD defect has norm at most `u*(||dst||+abs(a)*||src||)`, using the actual
preinstruction values. The factors making up the ideal native call and endpoint
adapters are exact; any implementation errors must be included in this stated
completed-output allowance. Let M be the maximum actual register norm at any
boundary, including private accumulators. Each defect is bounded by u times
its weight times M. Hence, when `(3025/2)*u < 1`,

    M <= 64*B / (1 - (3025/2)*u)
    max_boundary_error <= 96800*u*B / (1 - (3025/2)*u).

For every integer b >= 0, **u <= 2^(-b-17)** therefore suffices for all-role
error at most `B*2^-b`: `K*(P+1) = 196625/2 < 2^17`. The same sufficient bit
margin happens to hold for the forward word, but its coefficients do not
transfer. The 16-bit version of this sufficient formula fails; that is not a
lower bound on actual rounding precision. Weighted independent-defect
sharpness does not claim the feedback bound is attained under state-relative
arithmetic errors.

## Private lifetime and supplier boundary

The eight private values are owned known-zero accumulators, not arbitrary
dirty borrowed storage. Each gathers independent D values, travels from its
line to its cap, updates Q and is discarded while generally nonzero. This is
PR2479's explicit changed contract. The exact allocation/discard premise is
retained here, and local stability does not admit it to the old pure-copy bill.
The receipt records every discarded input/error row and a concrete private
defect that survives after C has been erased.

No rounded-child implementation, internal recursive-kernel stability,
owner/storage admission, physical scalar/tape bill, corrected side word,
global hosted precision reserve, all-size supplier, reduced precision charge
or new kappa is claimed. In particular the original native mass 2,368 is not
a completed supplier invoice.

## Reproduction and independent checks

Python 3.12, standard library only:

```sh
python3 -I -B research/p104-dual-precision/verify.py
python3 scripts/research_package.py --package research/p104-dual-precision
```

Author runs use native CPython 3.12.14 on Windows. The registered replay uses
`-I -O -B`. All source SHA256 and Git blob pins are checked before imports;
the retained native compiler/interpreter and complete-word checks are replayed.
New independent reverse adjoints agree with every nonzero endpoint input/error
coefficient and every attaining row. Literal collinear executions attain the
four peaks; a separate execution injects nonzero rational defects at all 4,042
sites and agrees with the full endpoint response maps.

The controls also expose invalid forward-constant transfer, a surviving
discarded-private error and the sufficient feedback margin. Export tests check
read-only Git-free execution, complete signed receipt mutation and retained/live
executable mutation before import. Default replay writes nothing. Author-only
`--write-result` creates a new receipt and refuses to overwrite one. No selected
supplier cold replay, hosted CI, proof assistant or human review is claimed.

## Sources and credit

Scientific base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4. [SOURCES.json](SOURCES.json) pins five retained-main inputs;
[PREDECESSORS.json](PREDECESSORS.json) pins every copied document/program/data
file from PR2479 `65e58f85d98b4a6344c6221623df1d4caa519604` and PR2096
`f22626f334a06f6e842766e4a6647419e6821d2d`. [TASK.json](TASK.json) records
selection, scope change, overlap and freshness. Frozen predecessors and the
selected result are unchanged.

Credit Adam Gall / PR2096 for the Hilbert-defect and feedback method; ywz65 /
PR2479 for the whole changed word and finite native binding; Rohan Arun /
PR1972, Chafik Boukhalfa / PR1991, Adam Gall / PR1940, Josie Elliston / PR1071,
Ali Romman and the retained geometry/Clifford contributors for its lineage.
PR2166 gives precision for a different corrected forward word and is not
consumed. New work is Apache-2.0, prepared for ywz65 with substantial OpenAI
Codex assistance in proof, implementation, verification and writing.

## Open next questions

The next obligations are concrete: bind an actual rounded child to the
completed-output Hilbert contract; admit the owned nonzero-discard lifetimes
with their full owner/storage charge; then propagate actual family magnitudes
and incoming helper residuals through both orientations of a corrected hosted
word. This local result discharges none of those implementation premises.
