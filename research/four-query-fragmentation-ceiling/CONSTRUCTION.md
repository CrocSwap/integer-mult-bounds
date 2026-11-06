# Four-query attainment for two equal-orientation fragments

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
This is a new module construction, following the native suppliers of
Cinna Davis and Ali Romman (#6348, #6398), the root of thu-nmrc (#6716),
zxv's source #6726, and the three-query obstruction #6764.

## 1. Exact contract

Work over the commutative ring
`Z[S,L,R]/(S^2-1)` and six arbitrary independent inputs `X,Y,A,B,E,F`.
The symbols `L,R` are algebraically independent commuting body operators.
No inverse body, division, zero-initialized coordinate, erasure, or relation
between different body symbols is used. The construction also specializes
over any field, including characteristic two. For the query lower bound,
retain the characteristic-zero hypotheses of #6764.

An ordinary operation is an invertible integer row addition or multiplication
by -1. A thin query `Q(d,s)` means `d <- d + S s`. A native child supplier
`N_D(d,s)` is the **atomic** supported operation

`(d,s) <- (D(d+S s), D s)`.

The query and its two-coordinate body act consecutively. An idle `I_D(d)`
means `d <- D d`. A compound child body can replace `D` only under precisely
this inherited arbitrary-input supplier interface, with its other target
outputs retained in their independent internal bank.

The endpoint we construct is

`(LR(X+S Y), LR Y, SL A, SL B, R E, R F)`.

Thus the two old auxiliary inputs retire after the L child, while two fresh
independent inputs supply the R child idles. The word uses exactly two native
child calls, two thin central queries, two L idles, and two R idles. Counting
the central query inside each native call gives four central queries.

## 2. Literal ordinary word

Rows are numbered `X=0,Y=1,A=2,B=3,E=4,F=5`; updates are sequential.

| Step | Operation |
|---:|---|
| 1 | `X <- L X` (idle) |
| 2 | `Y <- L Y` (idle) |
| 3 | `N_L(B,A)` |
| 4 | `A <- -A` |
| 5 | `A <- A + S B` (thin query) |
| 6 | `A <- A - B` |
| 7 | `B <- B + A` |
| 8 | `A <- A + S B` (thin query) |
| 9 | `A <- -A` |
| 10 | `A <- A + B` |
| 11 | `N_R(X,Y)` |
| 12 | `E <- R E` (idle) |
| 13 | `F <- R F` (idle) |

All four query coefficients are +1. The five ordinary operations use only
integer coefficients +1 and -1. The L native supplier now acts on the old
auxiliary pair; the main pair acquires its L body through the two paid idles.
This change of complete history is essential: it is not a basis change at
the fixed completed-left cut of #6764.

For a direct proof of the auxiliary endpoint, let `A0,B0` be the original
inputs. After step 3 the pair is `(L A0, L(B0+S A0))`. After steps 4 and 5,
`A=SL B0`. Step 6 gives `A=L((S-1)B0-S A0)`. Step 7 gives `B=SL B0`.
Step 8 gives `A=SL(B0-A0)`, using `S^2=1`. Steps 9 and 10 give `A=SL A0`.
No later operation touches either retired coordinate. Independently,
steps 1,2,11 give the declared main endpoint; steps 12,13 give the fresh
endpoints. Every cross coefficient is zero. The verifier checks all 36
entries over the formal ring rather than checking only sample inputs.

Within the positive-body scalar contract and atomic native support of
#6764, its equal-orientation three-query theorem excludes this endpoint
with three central queries. This construction therefore attains the
four-query lower bound. The lower bound is inherited from that proof;
the present replay verifies attainment and does not re-prove that theorem.

## 3. Exact #6726 source interface

The retained source is #6726 head
`435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`, path
`research/p104-paid-idle-fragmentation/frozen/two-fragment/caller.py`,
SHA256 `e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c`.
Its exact bytes are retained as `frozen/caller6726.py` and hash checked.
They are not imported by the new checker. They define the source opcodes
and the wrappers used here, rather than serving as a second proof oracle.

In the source complex normalization, `q^4=1` and

`lambda=(1+i)/2 + ((1-i)/2) q^2`, `S=lambda q^-1`.

Then `S^2=1` and `lambda^-1=(1-i)/2+((1+i)/2)q^2`.
The native operation is exactly the consecutive source word

`LAMBDA(d,-1); LOCAL(stage,s,d); LAMBDA(d,+1)`.

The thin operation is

`LAMBDA(d,-1); QUERY(d,s,-1); LAMBDA(d,+1)`.

Here `LOCAL` first adds `q^-1 s` to `d`, then applies the corresponding
body to both coordinates. The four normalized central operations expand
to twelve source events; the complete literal word has 21 events. It has
8 ordinary LAMBDA operations, 3 integer ADD operations, 2 sign SCALE
operations, 2 LOCAL operations, 2 QUERY operations, and 4 IDLE_ONE
operations. The complete expanded list is emitted in `CONSTRUCTION-REPLAY.txt`.

The checker independently represents Gaussian rational coefficients and
formal `q^4,L,R` monomials. It checks every coefficient of the expanded
6-by-6 matrix against the substitution of S into the formal endpoint.
It additionally checks final `LAMBDA(A,-1)` and `LAMBDA(B,-1)`, which convert
the two `SL` targets to `q^-1 L`. The fresh `R E,R F` targets require no
central-phase normalizer. A caller integration must therefore select
normalizers by the declared endpoint; a blanket old caller normalization
on every newly introduced role is not automatically appropriate.

This is an exact atomic-supplier interface identity. It supplies no new
native physical circuit, no independent physical Fourier-bank admission,
and no complete compiler or precision-tape estimate. The five inherited
conditional obligations remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. All inputs in this
module are arbitrary independent inputs; E,F are fresh in identity and
allocation, not initially zero. No old arbitrary information is erased.
A concrete complete caller would also have to admit the changed target
phase masks and maintain auxiliary ownership through its bank schedule.

## 4. Full local signed invoice

Write `H(d)=d^(1-kappa)` for scalar normalized dimensions and
`i(d)=H(d+1)-H(d)`. Let `a,b>0` be the L and R body dimensions. Relative to
the old binary node, the native child calls and every inherited native
helper target are unchanged in number and contract. The changed auxiliary
entries are exactly:

| Item | Original | New |
|---|---:|---:|
| Productive targets | `2 H(a+b+1)` | `2 H(a+1)+2 H(b)` |
| Paid whole idles | `2 H(a+b)` | `2 H(a)+2 H(b)` |
| Paid thin queries | `H(1)` | `2 H(1)` |

The new signed moment minus the old is therefore

`Delta = 2[H(a+1)+H(b)-H(a+b+1)]`
`        - 2[H(a)+H(b)-H(a+b)] - H(1)`
`      = 2[i(a)-i(a+b)] - 1`.

The two fresh R targets and their paid R idles cancel in this difference;
they must both be included before cancelling. The extra thin query costs
one complete scalar unit. This is a two-fragment price, not twice a
one-fragment price plus a free query.

For `0<kappa<1`, the old binary-node excess is `2 i(a+b)-1`; after replacement
it is `2 i(a)-2<0`. A local improvement can occur for sufficiently large b
when `i(a)>1/2`, because `i(a+b)` tends to zero. That fact does not imply a
paying whole construction. The independent complete six-child-root grammar
bound in [ECONOMICS.md](ECONOMICS.md) shows the fixed #6726 source cannot improve its retained raw ceiling
using any number or placement of these replacements in the audited ranges
(complex kappa in [0.0033,0.004], BIT in [0.0037,0.004]): ordinary trees
dominate below its finite-tail cutoff, and its inherited positive
per-node envelope bounds every larger mixed tree. The present package
proves the local construction and exact invoice; the companion ceiling
certificate is required for the all-size global statement.

## 5. Verification and limits

`python3 -I -B construct.py` uses only the Python standard library and runs
without imports from the retained source. It checks the formal endpoint,
source-phase endpoint, retirement prefix, fresh-input independence,
exact signed-multiplicity cancellation, and 21 mutations: omission of
each of the 13 literal gates and reversal of each of the 8 absolute LAMBDA
signs. Every mutation is required to fail. Running with `-O` has the same
output because proof checks do not rely on `assert`.

The exact polynomial identity proves all formal coefficients. The four
invoice fixtures verify transcription/cancellation, not numerical values
of real powers. There was no exhaustive finite construction search; this
is a direct construction. No new kappa, selected-frontier edit, or
complete multiplication theorem is claimed.
