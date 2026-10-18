# An exact-producer entry contract for the QQ16 numerical decoder

The numerical chain for PR2707 leaves its post-B1 input norm and grid as
premises. This package supplies sufficient values from the actual **exact
F0 followed by B_1_2** producer, rather than assuming unrelated current inputs.
It closes one conditional entry implication, not a complete physical caller.

Suppose all 224 physical data arrays before F0 have maximum-per-owner payload
Hilbert norm at most H>0, component grid `2^-f Z`, and H<=2^e, for nonnegative
integers f,e.
Use the source's initial X frame C_q and Y frame I, 73 address axes per tensor
factor, and positive tensor depth lambda. Assume the producer's native children,
scalar arithmetic and cover maps are exact, with its inherited helper contract.
Then all 224 physical post-B1 arrays satisfy

```text
norm <= B = 17628*H,
component grid 2^-Q0 Z,  Q0 = f + ceil(lambda/2) + 6 + 9*lambda,
B < 2^(e+15).
```

These are conservative upper bounds, not attained maxima or necessary precision.
For original-input error target `H*2^-beta`, with nonnegative integer beta,
choose the existing decoder's relative target `b=beta+15`. Its inherited finite-format theorem gives

```text
k = beta+37 + ceil_log2(lambda) + floor(73*lambda/2),
Qmax = Q0 + 3*k + 6,
W = Qmax + e + 35 signed bits per real component.
```

For `lambda=1`, `f=64`, `e=0`, `beta=64`, this yields **W=532**, with Q0=80,
b=79, k=137 and Qmax=497. The earlier W=456 example supplied post-B1 grid 64
and exponent bound zero directly, and measured error relative to that supplied
post-B1 bound. These are different premises and error targets; no earlier
format claim is contradicted. W here bounds the added decoder, not the producer.

## Proof and exact boundary

The inherited [ordered producer](../joint-query/evidence/CONSERVED-QQ16.md)
uses R with 56 signed unit entries per row, K=R^T/4 with absolute row sum one,
and disjoint eight-port minors A,T with `R_A R_A^T=R_T R_T^T=4I`.
There are 96 ordinary ports U. The initial and completed physical frames come
from the [bridge review](../joint-query/evidence/BRIDGE-REVIEW.md) and
[PR2707's proof](../qq16-line-normalized-decoder/PROOF.md).
Their ideal native semantics are inherited, not independently certified here.
All source bytes and the actual R/K certificate are pinned in SOURCES.json.

Use `R_s=R D_s`, `K_s=D_s^-1 K`, with restrictions to named ports. Each D_s
permutes cover owners. Its physical realization also applies exact payload
translations. Each summand therefore preserves the component grid and the
maximum-per-owner payload Hilbert norm. Different chart maps need not commute.
Port sums still need the triangle inequality; they are not unitary operations.

Write original logical inputs as x,y. First form `f0=R_0 x` and `c=R_(0,T)x`.
The exact F0 outputs are

```text
x1_U=x_U-K_(0,U)f0,  x1_A=K_(0,A)c,  x1_T=K_(0,T)f0,
y1_U=y_U+x1_U,       y1_S=x_S+y_S-x1_S,  S=A union T.
```

For B_1_2 set `u=y1+K_(2,A)R_(2,U union T)y1`,
`a=R_(1,T)x1`, `bq=R_1 u`. Then

```text
y2_U=y1_U+K_(1,U)a,  y2_A=u_A,
y2_T=u_T-K_(1,T)bq-11*K_(1,T)a,
x2_U=x1_U-y1_U=-y_U,
x2_S=x_S+y_S-y2_S.
```

The last equality uses the exact conserved selected sums across both calls.
It does not identify current and future queries. These are the conserved-sum
producer equations, not the earlier clean-query variant.

Starting from logical entry norm H and a common logical grid, propagate
absolute coefficient sums and add two fractional bits for each K injection.
R queries add no fractional bits. The complete per-port receipt gives:

| Logical field | Norm bounds on A / T / U, in units H | Fractional debts on A / T / U |
| --- | --- | --- |
| x1 | 4 / 56 / 57 | 2 / 2 / 2 |
| y1 | 6 / 58 / 58 | 2 / 2 / 2 |
| u | 3022 / 58 / 58 | 4 / 2 / 2 |
| x2 | 3024 / 17628 / 1 | 4 / 6 / 0 |
| y2 | 3022 / 17626 / 282 | 4 / 6 / 4 |

Every a coordinate is bounded by 224H with debt two, and every bq coordinate
by 15104H with debt four. For example `u_A` costs at most
`6+52*58=3022`, and `bq` at most `4*3022+52*58=15104`.
The checker uses each actual signed R/K row to derive all bounds rather than
assuming uniform sparsity. The norm/grid propagation does not claim that every
triangle inequality can be saturated simultaneously.

To pass from physical entry to logical entry, apply C_q^-1 to each X field.
Across lambda factors this is a product of lambda signed Gaussian lines,
so it preserves the norm and adds at most `ceil(lambda/2)` fractional bits.
Y needs no unframing. This step is a mathematical change of representation,
not a new uncharged producer instruction.

For completeness, any product of n signed Gaussian lines has component
coefficients on grid `2^-ceil(n/2) Z[i]`. Expand each factor as its two
translation terms. Each term has numerator a product of n factors `1+i`
or `1-i`, divided by `2^n`. Both factors are associates of `1+i`, and
`(1+i)^2=2i`, so every term has the stated denominator. Colliding translations
only add such coefficients. This proof does not assume independent directions.
It also covers identity projected directions and tensor products.

At the completed B1 cut, X is in F17 and Y in F17 C_q^-1. These are products
of respectively 17*lambda and 18*lambda lines, with exact coordinate
translations. Thus both need at most `9*lambda` additional fractional bits.
They are unitary on each owner's payload and preserve the logical norm bound.
Combining unframing, six logical fractional bits and physical reframing proves
Q0 and B above. No producer-interior range or precision bound follows.

Finally PR2807's theorem, inheriting PR2771/2736, gives strict all-cut decoder
error `<B*2^-b`. Since `17628<2^15`, setting b=beta+15 gives strict error
`<H*2^-beta`. Outputs recover the original logical arrays **in F17**, not their
original physical C_q/I frames. Unitarity permits comparison in that logical
norm; a physical endpoint adapter or consumer still needs its own invoice.

## Reproduce and evidence

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-producer-entry-contract
```

Normal and optimized replay authenticate the inputs and compare the complete
per-port RESULT.json. Five test groups independently evaluate all 224 scalar
basis inputs, sixteen four-owner fixtures with noncommuting replacement chart
permutations, all Gaussian coefficient products through 72 factors, the format
example and boundary failures. They also exercise a Git-free export, corrupted
source and receipt, duplicate keys, an oversized receipt, invalid arguments,
non-dyadic coefficients, changed geometry and exclusive deterministic receipt
creation. The replacement-chart fixtures test the stated isometry hypotheses;
they do not replay the actual native cover action or prove its source theorem.

Local Linux x86_64 verification used CPython 3.12.15 for the registered replay
and CPython 3.13.5 for the optimized test suite. All five groups passed on both;
the eight repository package-diagnostic tests, Ruff and warning-as-error
compilation also passed. Separately, the unchanged producer replay passed all
37 native cases, 712 common-chart columns per orientation and 16,384 new native
columns with this command:

```sh
python3.12 -Werror -I -O -B research/joint-query/replay.py \
  --repo . --out /tmp/qq16-entry-producer-replay
```

That is a historical validation run, not an extra registered input or a replay
of the original recursive child interiors. The new verifier imports no
predecessor executable. Its default is read-only;
`--write` only creates an absent receipt. The per-port table is an exact
certificate of this conservative recurrence, not a finite search extrapolated
to larger lambda. The written Gaussian argument supplies the all-depth step.

## Remaining obligations and expansion decision

The producer is assumed exact. Its actual finite arithmetic, intermediate
range, recursive-child accuracy, helper placement and full-cover movement are
not implemented or priced here. Approximate producer errors are not absorbed
into H without an additional stability argument. The decoder's norm/rounding
and finite-format theorems are inherited. No full native, selected cold-replay,
formal-kernel, independent human review or supplier-admission claim is made.

Owned outputs and private scratch have the predecessor's exclusive ownership
and destructive CLEAR contracts; borrowed post-B1 arrays remain read-only.
This lemma neither grants writable slices nor changes those contracts. The
existing 336-child decoder, map/wrapper counts, data lifetimes and physical
consumer costs are unchanged. No Boolean count is assigned a recursive tariff.
Unknown movement, storage, control, cleanup and consumption costs remain unknown.

Family decision: **narrow and stop** at the exact-producer entry implication.
This is not evidence to expand the family into another implementation round or
to change the selected frontier. The task and overlap coverage are in TASK.json.
The scientific base is main `9d76996a4cb4f558481067d10fd994f4f6c6d88a`, priority
revision 5. Submission refresh saw main `afc158a25ef3e0bd80de81d1eb5339f0dace118e`
at 2026-10-16 14:19 UTC; guidance, selected result and all live inputs were
unchanged. No main update is silently applied to these source pins.

## Open next questions

1. Can one actual finite F0/B1 implementation supply this exact grid, or a
   quantified entry error compatible with the decoder? Begin with its completed
   native-child error and common-cut range ledger. The present exact-producer
   hypothesis, not another root calculation, is the blocker.
2. Can a complete caller afford the decoder and consume F17 outputs? Pin owners,
   writable slices and the consumer, then charge all arithmetic, maps, wrappers,
   movement, storage and cleanup together. No favorable full bill is supplied.

## Credit and engineering scope

New entry-envelope composition and checker by Nick Petalas, Apache-2.0.
Credit Ali Romman and the joint-query team for the ordered F0/B1 maps and
bridge/native contracts; ywz65 for PR2707/2540; Arham Tahir for PR2681;
Nick Petalas for PR2736/2771/2807; and starship-s, Sagar Thakrar, Ross Richardson
and the retained QQ16/native/geometry lineage. Predecessor files are unchanged.
Substantial automated assistance was used; no independent human review is claimed.

Build the Lever led to the replayable per-port certificate. Prove It Works led
to authenticating actual R/K and checking the public command. Test Behavior,
Not Implementation led to the independent integer-grid producer and CLI failures.

Power-of-Ten scope: no new recursion or unbounded queue; traversals have fixed
112-port/eight-query bounds and fixtures have at most four owners and 72 line
factors. Source files are capped at 1 MiB, decompressed certificate at 12 MiB,
metadata at 64 KiB and receipt at 128 KiB. The parameter calculator caps each
input at 4096; the written theorem is not restricted by that test-tool limit.
Rule 3 deviation: managed Python integers and collections allocate during
verification, bounded by those inputs. Python/JSON library allocations are not
independently profiled. Rule 9 deviations: JSON's duplicate-key hook and one
test-only import of the explicit local verifier. Warning-as-error execution,
compilation and Ruff diagnostics cover changed code; no static type checker
or fixed-allocation machine implementation is claimed. A variable-size service
or physical implementation requires a separate capacity review.
