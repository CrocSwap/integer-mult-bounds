# Rounded native children for the retimed P104 dual

The two new native transports in Vasek / flyingviper's
[PR2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725), exact head
`71d24b655c2fdddc063b9aaf285e8425ce197499`, have an executable rounded
reference implementation satisfying

```
||computed - U input||_2 <= 2^-b ||input||_2,       b >= 0.
```

This includes both exact Gaussian monomial wrappers and rounding after every
binary C stage. It applies to arbitrary Gaussian-dyadic entrance arrays,
including zero and cancellation inputs. The reference output retains its
chosen working grid. **A final downcast to the entrance grid is excluded and
has an explicit failing fixture.**

This answers part of [PR2878's rounded-child handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2878).
That package assumes completed relative defects to prove conditional recovery;
this package constructs one finite numerical realization for two actual calls.
It pays a scalar butterfly expansion and does not implement an admitted fast
recursive child, the other 1,938 transports, scalar ADDs, or full-word recovery.
No supplier, improved paid profile, new kappa or runtime speedup is claimed.

Nick Petalas's [PR2771 QQ16 rounded-line package](../qq16-rounded-native-line/README.md)
already proves the unitary perturbation sum, the common-grid counterexample
and the sufficient maximum-component block scale used below. Those methods
are credited, not claimed as new lemmas. The delta is their source-bound
application to PR2725's two rank-seven/eight P104 recipes, including all four
actual quadratic-phase/affine wrappers, an integer execution retaining an
exactly embedded entrance, an independent all-column replay, the failed final
downcast and an explicit integer-width/work envelope. The QQ16 executable and
receipt do not bind these P104 recipes. No priority claim for block scaling is made.

## Literal binding and evidence

Only the X90 rank-seven transport at zero-based event **4642** and N90 rank-eight
transport at event **4643** of the 5,268-event PR2725 word are bound. WORD and
NATIVE bytes are live SHA256/Git-blob inputs, authenticated before parsing;
their original attribution-bearing README is also pinned. No predecessor
executable, compiler or native interpreter is imported. The association of
these recipes with their canonical chart transports remains inherited from
PR2725; this checks execution of those recipes, not their entire native ancestry.

The independent closed tensor-convolution oracle checks **all 1,024 basis
columns**, including wrapper direction and global phase. It uses a separate
wrapper evaluator and imports no butterfly arithmetic. This corroborates the
exact recipe implementation; a column test is not a proof about nonlinear
rounding. The written estimate below supplies the arbitrary-input bound.

[RESULT.json](RESULT.json) additionally checks 120 rounded executions: zero,
unit basis, dense, wide dense and near-cancellation arrays; entrance fractional widths
0, 19, 300; requested relative bits 0, 1, 8, 64. Wide dense inputs exercise
nonzero rounding even at b=64. All local and completed squared-error comparisons
use integers.
Controls reject same-grid relative claims, an unpriced final downcast, wrong
phase, invalid address maps, source drift and receipt drift. Tests also mutate
the precision policy and an actual butterfly sign. Separate algorithms by
the same assistant are not independent human review.

## Working-grid lemma

Let `N=2^n`, `K>=1` be the number of binary C stages, and

```
C = ((1+i)I + (1-i)X)/2.
```

C and both Gaussian monomial wrappers are unitary. Each disjoint pair uses
four sums of four signed integer components, divided by two and rounded to
nearest even on the grid of spacing `eps=2^-F`. Each real-component error is
at most eps/2. Therefore the Hilbert defect of one completed stage is at most
`sqrt(N/2)*eps`. Subsequent exact unitary stages preserve that norm. Expanding
the rounded recurrence and applying the triangle inequality gives

```
||computed - U input||_2 <= K sqrt(N/2) 2^-F.
```

No probabilistic independence, cancellation-free output, or componentwise
relative bound is assumed. Exact wrappers add zero defect. Their phases and
permutations cannot amplify an existing Hilbert defect.

Represent the entrance as Gaussian integers times `2^-f`, `f>=0`. If it is
zero, execute exactly at F=f. Otherwise let M be the largest absolute real or
imaginary integer numerator and set

```
h = bit_length(M)-1-f,
g = ceil(log2 K) + ceil((n-1)/2),
F = max(f, b+g-h).
```

The entrance embeds exactly since F>=f. Also `2^h <= ||input||_2` and
`K sqrt(N/2) <= 2^g`, so the stage bound is at most
`2^(h-b) <= 2^-b ||input||_2`. This is a sufficient policy, not an optimal
precision theorem. For the actual n=9, K=7 or 8 calls, **g=7**.
The maximum-component scan and integer bit length suffice; no square root
or floating-point norm estimate is executed.

The same written estimate applies to a tensor lift with n=9*lambda and
K=r*lambda if its literal implementation has the stated unitary binary stages
and exact tensor monomials. The executable here is only the finite lambda=1
case; it does not establish an all-size native compiler or recursive cost.

### Why a common fixed grid fails

For either actual recipe pull a single child-coordinate basis vector back
through its entrance monomial. Give it physical amplitude `2^-f`. At the first
C stage, all four nonzero real/imaginary components are signed half-quanta.
Same-grid nearest-even rounding maps them all to zero; every later stage stays
zero. Unitarity gives exact output norm `2^-f`. The completed relative error
is **one for every f>=0**, violating u=1/2. Increasing the common grid's
fractional width only rescales this counterexample. This differs from
PR2665's nonzero private cleanup residual despite locally allowed defects:
here the proposed uniform local relative premise itself fails.

## Finite arithmetic and representation bill

The returned array has grid F, with no uncharged conversion to f. Integer
addition, shifts, permutation and sign/quarter-turn phases are exact. Each
binary butterfly uses 12 signed integer additions/subtractions and four
nearest-even halvings. The primary implementation also counts local squared
defects as certificate instrumentation; those diagnostic multiplications are
outside the following execution-kernel counts and may be omitted.

| Rank | Disjoint butterflies | Signed additions | Rounded halvings | Wrapper moves |
|---|---:|---:|---:|---:|
| 7 | 1,792 | 21,504 | 7,168 | 1,024 |
| 8 | 2,048 | 24,576 | 8,192 | 1,024 |

In addition, scan 1,024 entrance components for M, embed 1,024 components
by exact shifts, and construct/cache two 512-entry address/phase plans. Plan
construction costs O(N*n^2) elementary bit operations with fixed n=9; its
bijectivity validation also sorts N addresses. Plans are recipe-specific,
not state-specific. The caller's borrowed input is retained. The logical
kernel needs at most two owned N-element Gaussian arrays during a wrapper,
constant pair scratch, two mapping tables, and O(K) diagnostic scores.
These are mathematical slots, not a measurement of Python object memory.

If entrance numerators have magnitude bit length at most w, put
`L=max(w,b+g+1)+ceil((n+1)/2)+2`. All stored component magnitudes fit in L bits
and four-term scratch in L+2 bits, plus signs. Indeed embedding needs at most
max(w,b+g+1) bits; any completed prefix norm is at most the entrance norm plus
`K sqrt(N/2)2^-F`, at most `sqrt(2N) M 2^-f + 2^h` when nonzero. This also
bounds each component; the stated L is a conservative integer envelope.
With linear-time fixed-width integer arithmetic, the kernel takes
O(N*(K+1)*L) bit work after its address plans are available. Arbitrary accesses,
plan sorting, and Python allocation are not constant-cost Turing tape steps.
No paid recursive or tape/movement/owner invoice follows from this count.

## Reproduce

Python 3.12 or later, standard library, from the repository root:

```sh
python3 -I -B research/p104-rounded-native-child/verify.py
python3 -I -B research/p104-rounded-native-child/test_verify.py
python3 scripts/research_package.py --package research/p104-rounded-native-child
```

Default replay is read-only. `verify.py --write-result NEW_PATH` exclusively
creates a receipt. Direct replay needs this package plus the three declared
live files under `research/p104-dual-add-retiming/`; it needs neither Git nor
network. The registered metadata check also resolves historical provenance.

Validation: Windows AMD64, CPython 3.12.10, standard library. Registered replay
and all five behavioral groups pass, including an optimized Git-free child
replay. The primary certificate also passes on CPython 3.14.6. A workspace
temporary directory was selected because the host sandbox's default temp
location was unwritable. No Linux or hosted-CI execution is claimed.

Submission checkpoint: main `38746ad3f6ffebcc0275e286b1dbb733d7c696dd`;
the isolated branch was fast-forwarded and guidance, selected record and
consumed inputs were unchanged. Live overlap at 2026-10-16 07:37--07:38 UTC
covered 486 open PRs and 1,543 Discussion records with complete pagination.
PR2771's method overlap is explicitly credited above. Arbitrary diffs,
unpublished work and complete closed-PR bodies remain outside that coverage.

## Open next questions

Can an admitted fast recursive child implement this relative contract at an
actual viable consumer's entrance? First bind its magnitude scan, numerical
representation, retained output grid, restoration, accesses and movement to
the recursive bill. The scalar expansion here is a numerical reference, not
that implementation. ADD error and the rest of the transport inventory also
remain unbound, so this package alone cannot instantiate PR2878 on the full word.
The current fixed-profile consumer obstructions remain applicable. Stop this
local investigation rather than infer a justification for further construction.
Structured scope and next-step details are in [TASK.json](TASK.json).

## Sources and credit

Base main `ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8`, priority 5; chooser nonce
`e99f40ffa10cfbc1b874e47b8b6f5001`, complex mechanisms. The physical-correction
card is explicitly **changed** to the numerical side result after live overlap.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18966620).
Exact source bindings are in [SOURCES.json](SOURCES.json).

Credit Vasek / flyingviper / PR2725 for the two literal recipes and word;
commdata2338 / PR2662, ywz65 / PR2586/2497, Ross Richardson and Nick Petalas
for the endpoint/native/grid lineage; PR2878 for the conditional recovery
contract and handoff; PR2665 for the distinct rounded-cleanup counterexample;
PR2754/2772/2813 for exact-grid implementations. Retain Chafik Boukhalfa,
Rohan Arun, Adam Gall, Josie Elliston, Ali Romman, icekylinx and the full
geometry/native/compiler ancestry credited in the pinned PR2725 README.
Credit Nick Petalas / PR2771 for the prior explicit perturbation/block-scale
lemma and common-grid relative counterexample. Nearest-even rounding and
unitary perturbation sums are standard mathematics. The contribution is this
changed-source implementation and its literal binding, not a new general bound.

Prepared for Arham Tahir with substantial OpenAI Codex assistance in mathematics,
code, checking and writing. No independent human, formal-kernel, selected cold
replay, all-size implementation or hosted-CI success is claimed. New work is
Apache-2.0; no frozen predecessor file is changed.
