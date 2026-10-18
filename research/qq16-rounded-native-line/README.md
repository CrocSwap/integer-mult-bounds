# Rounded native lines for the zero-retention QQ16 decoder

This supplies one concrete implementation of the completed signed-line error
premise left open by [PR #2736](https://github.com/CrocSwap/integer-mult-bounds/pull/2736).
It implements the Gaussian-dyadic line, including its two monomial wrappers,
by direct pair arithmetic with component rounding. A quantified all-depth
bound connects that implementation to the predecessor's 22-bit sufficient
error allowance. It is a local precision lemma, not a cheap recursive child,
a completed caller, supplier admission or a new kappa.

The exact word is ywz65's [PR #2707](https://github.com/CrocSwap/integer-mult-bounds/pull/2707)
at `efa51a6c7ffec6edd556a98deedfe9deeba65809`. It contains 336 signed lines,
224 positive and 112 negative, in 3,823 events. It has no writes to the 224
borrowed X/Y arrays. Its ideal native/frame theorem is inherited, not replayed
here. The consumed error theorem is Nick Petalas's PR #2736 at
`eba0d6111a773cd13f5c0afb4354af2c85d04c3a`. The three exact source snapshots,
Git blobs and SHA256 hashes are recorded in [SOURCES.json](SOURCES.json).

## The implemented instruction

Let each payload factor have `2^h` addresses and let there be `lambda >= 1`
factors. Write `D = 2^(h*lambda)`. On each factor choose a nonzero binary
translation q, and let T_q be its XOR permutation. The positive and negative
lines are

```text
C_q^s = ((1+s*i) I + (1-s*i) T_q) / 2,  s in {-1,+1}.
```

Their eigenvalues on the T_q eigenspaces are 1 and s*i, so they are unitary.
This is precisely the two-coefficient kernel in the retained native proof.
The proof also covers different nonzero q in different factors. If an induced
translation is zero, its line is identity and can be skipped exactly.

For a pair of complex input values a and b at x and x XOR q, compute

```text
sr = Re(a)+Re(b);  si = Im(a)+Im(b)
dr = Re(a)-Re(b);  di = Im(a)-Im(b)
left  = ((sr-s*di)/2, (si+s*dr)/2)
right = ((sr+s*di)/2, (si-s*dr)/2).
```

The sums and halves are exact, then each of the four components is rounded to
the nearest multiple of delta, with ties to even. Both input values are read
before either is overwritten. Each factor processes all disjoint pairs before
the next factor begins.

A binary basis beginning with q gives the native rank-one coordinate. The
reference implementation explicitly conjugates the positive first-coordinate
kernel by that basis permutation and, for a negative line, adds the native
output XOR. Thus `C_q^-1 = T_q C_q` is implemented with no negative child
assumed free. These permutations copy the exact stored components. The direct
pairing and wrapped implementations agree even with rounding, since a common
component grid commutes with these permutations. The source proof's affine
cover maps are also exact data permutations if represented values and their
block exponents are copied without re-rounding. This does not price their
physical routing or independently recertify their source address maps.

## Absolute rounding bound at every tensor depth

Fix one owner and its input vector x. Let delta be the same positive grid step
throughout this completed line. A factor produces D complex outputs. Each real
or imaginary component has error at most delta/2, so that factor's local error
has Hilbert norm at most

```text
eta = sqrt(D/2) * delta.
```

The ideal factor is unitary on arbitrary perturbed inputs. Therefore after j
factors its distance from the ideal prefix is at most `j*eta`, by induction
using the triangle inequality. In particular the completed line satisfies

```text
||implemented(x) - C(x)||_2 <= lambda * sqrt(D/2) * delta.       (1)
```

The same argument bounds every internal completed-factor cut. It does not
assume independent, unbiased or incoherent errors. Exact wrappers preserve the
bound. Taking the maximum over owners proves the same bound in PR #2736's
maximum-per-owner payload Hilbert norm, using a uniform delta or the maximum
of the owner-local absolute bounds. This proof applies to every finite h and
positive lambda, not just the fixtures below.

## A state-relative block scale

A fixed absolute grid does not establish the predecessor's state-relative
premise. For example, with delta=1 and x having just one real component 1,
a one-factor line has only half-integer output components and rounds to zero
under ties-to-even. Its error is exactly `||x||_2`, which violates
any promised relative defect u<1. This is not a counterexample to PR #2736,
which explicitly assumes a completed relative-error contract.

Here is one sufficient implementation of that contract. For a nonzero actual
input block, scan its components to find

```text
M = max_j max(abs(Re(x_j)), abs(Im(x_j)))
e = floor(log2(M))
s = ceil(log2(lambda)) + floor(h*lambda/2)
delta = 2^(e-t-s).
```

For the zero block return zero exactly. All maxima and power-of-two brackets
can be found with exact integer comparisons on stored dyadic data. Since
`lambda <= 2^ceil(log2(lambda))` and
`sqrt(D/2) <= 2^floor(h*lambda/2)`, equation (1) gives

```text
error <= 2^(e-t) <= 2^-t * M <= 2^-t * ||x||_2.                 (2)
```

Thus choosing `t=b+22` supplies PR #2736's line premise with
`u=2^(-b-22)` on the actual, possibly perturbed, operand. Scales may be chosen
separately for each owner; equation (2) remains valid after taking the owner
maximum. This is a block-scaled representation with an exponent per owner and
field, not a claim about one fixed absolute caller grid. Underflow, overflow
and finite exponent limits are absent in this exact-rational reference.

If the remaining ADD, map and CLEAR implementations meet the predecessor's
other premises, its unchanged feedback theorem then gives

```text
all-cut decoder error <= B*2919388*u/(1-199144*u) < B*2^-b.
```

The strict inequality follows from `2919388+199144=3118532 < 2^22` for every
integer b>=0. Only the line premise is instantiated here. This corollary does
not establish the remaining implementations, post-B1 entry bound B or an
output consumer.

## Paid implementation and stopping decision

This direct algorithm costs, per owner and signed line:

| Work | Charge |
| --- | --- |
| Find the block maximum | one scan of 2D real components |
| Pair arithmetic | 4*lambda*D real ADD/subtracts |
| Halve and round | 2*lambda*D exact halvings and component rounding decisions |
| Wrappers | two basis permutations, with the negative XOR fused into the output permutation |
| Storage | D destination values, constant pair scratch; the explicit wrapped reference uses a constant number of D-entry buffers |
| Representation | a block exponent and a data-dependent integer precision; exact exponent alignment and range handling remain paid |

The table counts arithmetic operations, not their bit complexity or tape
travel. The wrapped Python reference also spends `O(h*lambda*D)` binary work
building its basis permutation. Cover maps require exact movement of payloads
and exponents. No recursive native saving is inferred from this linear scan
and direct transform. Replacing the 336 billed rank-one children by these
loops would require a new invoice; the original supplier charge cannot be
retained by declaration.

Revision-5 decision: retain this local precision implementation and stop before
supplier expansion. The general completed-line premise has a constructive
direct realization, but its cheap recursive realization, physical layouts,
finite formats and whole-caller bill remain unknown. No favorable complete
budget has been established.

## Reproduce and evidence

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-rounded-native-line
```

Direct read-only replay also works without Git:

```sh
python3.12 -Werror -I -O -B research/qq16-rounded-native-line/verify.py
```

The deterministic [receipt](RESULT.json) records 1,240 complete real/imaginary
basis columns covering all nonzero q in widths 1 through 4 and both signs.
A separate dense Gaussian-integer kernel supplies the oracle. Seventy-two
rounded tensor fixtures and 72 state-relative fixtures cover widths and depths
1 through 3, both signs, coarse grids and the consumed 22-bit guard. All 72
state-relative fixtures contain finer input bits and exercise nonzero rounding
error, including at the 22-bit guard. Every comparison uses rational squared
norms, not floating tolerances. The fixtures
also compare literal rounded wrappers with direct pairing. They support the
written proof; they do not exhaust larger dimensions or all inputs.

Controls cover a wrong sign, an omitted factor, the fixed-grid relative-error
mistake, signed ties, a zero input, an invalid component rounding and bounded
parameter failures. Four CLI test groups check source corruption before any
numeric replay, complete typed receipt comparison, overwrite refusal, unknown
arguments and a Git-free read-only export. The registered commands run normal
and optimized Python; validation checks do not depend on `assert`.

The reference limits numerical instances to 4,096 coordinates and twelve
factors; the checked fixtures reach 512 coordinates and three factors. All
loops have explicit bounds. Managed Python integers and Fractions allocate
dynamically, a deviation from fixed-allocation rules. Live collections have
bounded cardinality in this verifier; integer sizes derive from the fixed
fixtures and at most 512 requested precision bits. This is not a bounded-memory
machine implementation of the all-size theorem. A production implementation
must supply its integer/exponent limits and overflow proof. The code uses no
recursion, dynamic imports, predecessor executable or external dependency.

No selected cold replay, internal recursive-child proof, physical machine,
formal-kernel check, hosted-CI pass or supplier admission is claimed.

## Open next questions

- Can a recursively cheap native rank-one implementation satisfy equation (2)?
  First expose one child's actual arithmetic and output rounding boundary,
  then propagate its local errors including wrappers. The missing child
  implementation and its time/storage invoice block this transfer; the direct
  loops above do not inherit its saving.
- Can a pinned complete caller carry the owner-local block exponents and afford
  their scans and alignments? Start with its post-B1 representation and one ADD
  between different field scales. Its entry norms, finite exponent range,
  movement and complete consumer costs are still missing.

Structured questions and overlap/freshness records are in [TASK.json](TASK.json).
No advance Discussion claim was posted; the linked predecessor handoff was
read before the investigation, and this package is the reviewable artifact.

## Credit

New lemma and reference checker by Nick Petalas. Credit ywz65's PR #2707 for the
line-normalized decoder and native kernel proof; Arham Tahir's PR #2681 for the
zero-retention logical word; PR #2540, Ali Romman and the retained QQ16/native
lineage. PR #2736 supplies the consumed decoder error contract, not the rounded
line implementation. PR #2603 gives an exact caller-grid result for a different
word with atomic exact children; PR #2628, #2670 and #2692 address related
completed or component error contracts. Their claims and constants are not
silently transferred. The two source proofs retain their original notices.
New material is Apache-2.0.
