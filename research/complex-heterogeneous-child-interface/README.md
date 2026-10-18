# Heterogeneous native children: exact reciprocal-encoding classification

**Scoped interface theorem and source-bound obstruction; no new kappa.**

PR1836 proposes combining two simultaneous complex frame climbs of ranks
`r,s` into one hypothetical rank-`r+s` child. Its product-space codimension
calculation is correct, but it is not a native operator or operand-volume
invoice. This package resolves one precise implementation route for the
**215 unequal-rank pairs** in its pinned 359-pair census: a single inherited
Clifford child surrounded by an arbitrary invertible encoding and its inverse.
The 144 equal-rank pairs are explicitly credited to PR1920, not claimed again.

There is also a genuine positive result. Unequal, oppositely directed lanes
sometimes *can* be encoded into one native child. For example,

```
(C_1 tensor I_4) direct-sum (C_2^-1 tensor I_2)  ~  -C_4.
```

Both sides have 16 coordinates. `RESULT.json` supplies the complete rational
encoding and inverse, and the verifier checks every coefficient. The child
acts on **both** eight-coordinate lane volumes, not one. These exceptional
identities do not improve the inherited volume-linear cost expression.

## Exact contract and new result

Use the inherited Gaussian-dyadic kernel

```
C = ((1+i)I + (1-i)X)/2,   C_n = C tensor ... tensor C,   C_0 = I.
```

Let two independent lanes each have volume `N`, with `2^q` dividing `N`, and
let `1 <= p < q`. After the fixed per-lane native normal-form charts, their
required operation is

```
T = (C_p tensor I_(N/2^p)) direct-sum
    (C_q^epsilon tensor I_(N/2^q)),   epsilon in {+1,-1}.
```

Tensor factor order is immaterial. We ask for any invertible complex linear
encoding `E`, one child `lambda C_d tensor I_t` with positive integers
**`d>=1` and `t>=1`**, and any number of arbitrary dirty coordinates restored
identically. The decoder is **exactly `E^-1`**. A scalar width-zero child is
outside this declared contract.
The child is identity on coordinates outside its active operand. Padding may
be mixed into the encoding; it is not required to stay in its original slots.
Any nonidentity operation on the child's complement is an additional operation,
not an identity spectator. The original scalar ADD may remain outside this
wrapper and is granted free in the optimistic comparison.

The result permits more than an ordinary single-lane call: the child's operand
may include both lane volumes. A fortiori it tests the smaller ordinary call.
It does **not** permit independent entry/exit transformations whose discrepancy
itself performs part of the desired computation. Nor does it permit a clean
invariant-subspace encoding or a new joint primitive with a different tariff.

### Complete unequal-width classification

A solution requires active child volume `t 2^d = 2N`. The narrower lane is
forward in this table; reversing both lanes is complex conjugation.

| Wider-lane direction | Width condition | Child width d | Phase lambda |
|---|---|---:|---|
| Forward | Any `p<q` | — | No solution |
| Inverse | `q=p+1`, `p=1 mod 4` | `q+2` | `-1` |
| Inverse | `q=p+1`, `p=2 mod 4` | `q+2` | `-i` |
| Inverse | `q=p+2`, `p=1 mod 4` | `q+2` | `-1` |
| Inverse | Every other unequal pair | — | No solution |

Every positive row also requires `2^d` to divide `2N`. If the available
volume is smaller, restored dirty padding cannot supply the missing active
volume. Both signs reversed change a phase exponent `u` to `-u-d mod 4`.
Allowing an inverse child adds no cases: its phase exponent is `u+d mod 4`.
The statement is over characteristic zero containing `i`, with ordinary
linear maps, not Hermitian maps. Equal-width pairs are outside this new theorem.

### Proof for all positive unequal widths

Write `a=(1+i)/2` and `bar(a)=(1-i)/2`. The normalized first traces of a
forward and inverse width-n child are `a^n` and `bar(a)^n`; their square traces
are zero for every positive n. Their fourth powers are identity.

1. **Full volume and restored padding.** Suppose the target has D identity
   coordinates and the candidate has H identity coordinates. Fourth powers
   force `lambda^4=1`. Square traces give `D=H`, even if E mixes every dirty
   coordinate. Dimensions then give `t 2^d=2N`. Consequently a native child
   on only one N-coordinate lane, with the other lane untouched, cannot work.
   This is a full-space statement; clean padding is a different contract.
2. **The child width is forced.** Divide the first-trace identity by N:
   `a^p + a^q = 2 lambda a^d` for equal directions, or
   `a^p + bar(a)^q = 2 lambda a^d` for opposite directions. In Q(i), use the
   valuation at the Gaussian prime `1+i`, normalized to value one.
   Both a and bar(a) have value -1. Since p<q, the two summands have distinct
   valuations, so their sum has value -q. A fourth root of unity has value
   zero, while 2 has value two. Thus **d=q+2**. No bounded-width search is
   needed for this step.
3. **Classify the possible cancellations.** Set k=q-p. Taking the rational
   Gaussian norm of the trace identity gives

   ```
   cos(k pi/4)     = -2^(k/2-1)       (equal directions),
   cos((p+q)pi/4)  = -2^(k/2-1)       (opposite directions).
   ```

   This is an exact identity among fourth/eighth-root values, not a numerical
   acceptance test. Its right side has magnitude greater than one for k>=3.
   For k=1 the required value is `-1/sqrt(2)`; for k=2 it is `-1`.
   Equal directions give respectively `+1/sqrt(2)` and zero, so neither works.
   Opposite directions give exactly the three congruence rows in the table.
   Substitution into the **first trace**, not the norm alone, gives the stated
   phases. Shifting p and q by four multiplies both sides by `-1/4`, so those
   phases repeat with period four.
4. **Sufficiency.** In each table row the traces of powers zero, one, two and
   three agree. The third traces are the Gaussian conjugates of the first;
   the other two have already been checked. All operators have fourth power
   identity, hence are diagonalizable with eigenvalues in `{1,i,-1,-i}`.
   The invertible four-point Fourier matrix recovers the four multiplicities
   from these four traces. Equal multiplicities give an invertible matching
   basis. Integer Walsh eigenvectors explicitly construct E over Q, with
   a dyadic rational inverse. Thus the table is necessary **and sufficient**.

This uses elementary valuation and trace arguments. PR1920 supplies the
reciprocal-contract idea and equal-width classification; the unequal-width
Gaussian valuation, three nonuniform exception families, and their source
application are the new result here. Finite checks corroborate the argument;
there is no proof-assistant or independent human proof verification claim.

## What the selected source actually supplies

The checker independently scans both 24,767-event emitted orientations of the
pinned selected local word. It checks every climb's old/current frame, binary
inclusion and exact quotient rank; every A/B/tail gate's rational coefficient
and common frame; inverse-transpose scalar orientation; final frames; and the
complete local profile `{1:2412,2:418,3:432,4:142,5:82,8:8}`.

| Unequal shape (r,s) | Source gates |
|---|---:|
| (1,2) | 72 |
| (1,3) | 52 |
| (1,4) | 35 |
| (1,5) | 26 |
| (2,3) | 5 |
| (2,4) | 19 |
| (3,4) | 6 |
| **Total** | **215** |

The remaining 144 comprise `(2,2):14`, `(3,3):122`, `(4,4):8`.
The receipt contains all 215 source gate addresses and endpoint frame IDs,
not only the histogram. This independently corroborates that subset of
PR1836; its original discovery and conditional profile remain credited.

For the canonical ordinary-child implementation of each source pair, the
literal widths are `p=r f`, `q=s f`, with positive column multiplicity f.
Both children have the same direction in either orientation. None is a table
exception. Thus **none of these 215 substitutions is furnished by the declared
reciprocal one-child route**, for any f. This is not an impossibility theorem
for the original physical gate with arbitrary changed charts. The pinned
frame note guarantees separate monomial normal-form charts; it does not
assert those charts are reciprocal, nor does this package silently do so.
We fix those endpoint normalizations and audit packing of the resulting
canonical children. New nonreciprocal adapters need their own implementation.

Even if one hypothetically reverses just one lane, only the `(1,2)`, `(1,3)`
and `(2,3)` shapes can qualify at f=1. For f>=2, the width gap is either at
least three, or equals two with even p, which fails the table. This observation
is not a modification of the source program or a new all-size compiler.

## Fully charged optimistic budget and stopping decision

The card's prescribed ceiling working example and lever table were executed.
`RESULT.json` separately reconstructs the selected profile and the
**counterfactual** profile obtained by replacing just the 215 unequal pairs
with rank sums. The exact brackets are `[0.001690054109,0.001690054110]`
for the baseline and `[0.001733875133,0.001733875134]` for that counterfactual.
The latter does not itself reach the card's 5% gate, and is not an admitted
replacement profile: the changed operation is precisely what the theorem
tests, not an already priced supplier.

For each genuinely positive opposite-direction identity, retain PR679's
inherited available cost expression `A V n^sigma`, `0<sigma<1`, where V is
one lane's *entire* physical volume, including spectators. Original children
cost

```
B_original = A V (p^sigma + q^sigma).
B_child    = 2 A V (q+2)^sigma + E_cost.
```

`E_cost>=0` includes the encoding and inverse, gathering/scattering, copied
information, input/output access, all fixed and new frame/phase charts,
restoration, coefficient preparation, hosting, precision and descriptors.
Granting every term in E_cost free still gives `B_child > B_original`, because
`q+2>q>p`. Restored dirty coordinates cannot count as productive extra volume.
Thus no positive exception improves this inherited **upper-bound-expression
comparison**, and synthesis under this contract stops. This is not a lower
bound on optimal runtime, not a scalar-to-recursive cost conversion, and not
an exclusion of a genuinely different joint-child algorithm. No cheaper
available profile, 5% construction-gate success or kappa improvement follows.

## Reproduce and exact evidence

From the repository root, standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -B research/complex-heterogeneous-child-interface/verify.py
uv run --python 3.12 --no-project python -I -O -B research/complex-heterogeneous-child-interface/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/complex-heterogeneous-child-interface
```

The ordinary checker is read-only and compares every field with `RESULT.json`.
To regenerate explicitly, pass `--write /new/path.json`; existing destinations
are rejected. The registered replay checks the optimized execution and source
pins. `VALIDATION.json` records the commands actually exercised and environment.

Evidence includes the complete unequal-width spectrum classification through
64 (candidate widths through q+3, both lane directions and four phases), an
independent cyclic recurrence versus binomial counts through 67, inverse-child
and both-lane-sign reductions, and full rational 16/32/32-dimensional encoding
witnesses for `(p,q)=(1,2),(2,3),(1,3)`. Controls reject wrong phase/direction,
source rank/frame/coefficient mutations, domain weakening, missing active
volume, and nonqualifying signed width pairs. No native solver, full selected
cold replay, hosting change or remote CI success is claimed.

## Provenance, overlap and credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; independently sampled chooser
seed `c2889b6f0505155ec921e731269f82bf`, track `complex-mechanisms`.
`SELECTION.json` preserves the complete once-drawn selection. `TASK.json`
records the explicit changed scope from physical synthesis to this missing
interface implication. [Public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18926013).

* Cinna Davis / 1337isnot1337, PR1836 at
  `0a62e3f1c0ea493ddb83f25b91c5548c87978bcc`: higher-rank same-gate census,
  hypothetical J_(r,s) profile and explicit unadmitted interface.
* Arham Tahir, PR1920 at `057b214aea45c65926b93ad8b95693c80f0f79c9`:
  arbitrary reciprocal basis, uniform-direction equal-width obstruction,
  equal-width opposite-direction exceptions, and volume accounting.
* ToikY, PR1924 at `0a7c54dd94bce3784b61c4203adfdda98d13d53d`:
  clean invariant encodings, a different contract not excluded here.
* Cinna Davis / PR1866 at `7d22d1d51eb6c0bc040f8181b6c5f83e051fb234`:
  a heterogeneous bilinear rank-six tensor, not a Clifford reciprocal
  encoding; no claim that this theorem excludes its different primitive.
* Greer Guthrie / PR679: selector batching and the inherited linear-volume
  tariff. Douglas Colkitt / PR1240: exact fixed-word ceiling engine.
* icekylinx and the retained Rohan Arun / Jeremy Kothe / Hao Yan selected
  lineage: source frame construction and physical local word. Original
  notices and all frozen predecessor files remain untouched.

The final parent refresh covered 584 open PRs and 565 discussion records,
with complete pagination at 14:27–14:29 UTC. Targeted live reads checked the
named heads and scopes at 14:32 UTC, including PR1924's changed head.
Local READMEs/TASKs and the ledger also cover merged predecessors. These
metadata searches do not prove novelty. No priority is claimed for Walsh
basis diagonalization, Gaussian valuations or elementary spectral identities.

Prepared for Adam Gall (@adamgall) with substantial OpenAI Codex assistance in
research, proof, implementation, exact checking and writing. New material is
Apache-2.0. The selected frontier and all inherited multiplication theorem,
all-size/compiler, source/phase/hosting and precision/tape obligations remain
unchanged.

## Open next questions

Can a fully priced **nonreciprocal** adapter realize one of the selected
heterogeneous pairings with a better complete bill? Start with one pinned
(1,2) gate and explicit source/output charts; provide matrices, actual copied
volume, phase/source access and dirty-restoration costs before a profile.
The blocker is an inexpensive physical adapter or a new child tariff, not
more reciprocal basis searches. Structured details are in `TASK.json`.
