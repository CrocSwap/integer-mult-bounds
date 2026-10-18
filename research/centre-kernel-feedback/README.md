# Transporting the terminal-Y kernel through centre feedback

**Research interface and exact finite certificate; no new κ or native supplier.**
PR2799's 149-dimensional terminal-Y kernel survives changes to the centre
operators, but its basis must change. Exactly **128** of its directions stay
valid without any operator-dependent correction. The other **21** require
feedback corrections at **546** chronological centre sites in the selected
144-call schedule.

This package supplies the exact correction matrix, a causal transport proof,
and a source-preserving repair program with a complete bill in an explicit
rational field-bank model. It addresses the operator-sensitivity obligation
behind the proposed quotient; it does not establish a consumer accepting that
quotient. The accepted κ remains `0.001672660197076918`.

## Model and result

The source is the selected PR1094 480-helper word, with 14,336 ordinary owners,
144 calls, 1,152 rank-eight centre events, 144 bridges and 16 signed terminal
exchanges. Keep every scalar instruction, shared owner, private clear, bridge
and continuation. As in PR2622/2799, frame, idle and address actions are
**projected to identity**. Retain arbitrary equal ordinary input dirt in the
compared executions; their initial difference is zero.

In this projection, replace the identity action at centre site `j` by any linear
operator `H_j` on a common vector space `V`. Add an error `e_j` immediately
**after** that action, following PR2799's insertion convention. Compare two
executions with the same `H_j` and initial data. This defines an error-response
map; the modified no-error program is not asserted to implement the selected
supplier.

Let `R` be the original final ordinary response, `R_Y` its final-Y restriction,
and `K` the strictly lower triangular map from identity-centre insertion errors
to the values immediately **before** later centre events. All 1,152 rows of `K`
are independently reconstructed here. The fixed scalar readout is
`Y = {i : i mod 224 >= 112}`.

Write `Δ = diag(H_j-I)` and understand scalar matrices as acting on copies of
`V`. Then the complete deformed response is

```text
R_H = R (I - Δ K)^(-1),
ker(P_Y R_H) = (I - Δ K) ker(R_Y).
```

These identities hold even when the `H_j` do not commute or are singular.
For finite-dimensional `V`, the kernel dimension is always `149 dim(V)`.
This is an application of the standard causal feedback identity, not a claim
that the abstract identity itself is new.

Let `B` be PR2799's retained 149-column kernel basis: 128 coordinate directions
and 21 other directions. The exact new computation gives:

| Object | Rank / coverage |
|---|---:|
| `K B` on the 128 coordinate directions | zero |
| `K B` on the 21 other directions, forward-site rows | 21; 394 nonzero rows; 1,461 terms |
| `K B` on the 21 other directions, backward-site rows | 21; 152 nonzero rows; 452 terms |
| Total correction matrix | 546 nonzero rows; 1,913 rational coefficients |
| Final-Y derivative on the 21 other directions, forward `t`, backward `t^-1`, at `t=1` | rank 21 |

Thus **the parameter-independent kernel is exactly the 128 coordinate
directions**, already present in PR2799 and all lying in the final forward
stage. The additional 21 directions are valid with the transported errors
`e = Bz - ΔKBz`. A nonzero derivative of a fixed basis vector does **not** imply
that the deformed kernel loses dimension. The distinction is central here.

[CORRECTION.json](CORRECTION.json) gives every nonzero row of `KB` for the
21 noncoordinate parameters. A key is chronological error index `8*c+k`, not
the call's time field; parameter columns are numbered 0 through 20 in PR2799's
basis order. [RESULT.json](RESULT.json) records exact minors, coefficient
digests, the witness and both invoices.

## Proof of transport and of the fixed-kernel statement

At site `j`, let `f_j` denote its effective insertion into the original
identity-centre program. All earlier effective errors determine its input
difference `(Kf)_j`. Applying the changed centre and then adding `e_j` gives

```text
f_j = e_j + (H_j-I)(Kf)_j.
```

No insertion affects an earlier centre input. Therefore `ΔK` is strictly lower
triangular, `(ΔK)^1152=0`, and `I-ΔK` has the finite inverse
`I+ΔK+...+(ΔK)^1151`. Substituting `f=(I-ΔK)^(-1)e` into the original final
response proves both identities. The argument uses only linearity and
chronology, so it applies to noncommuting vector operators and singular
assignments elsewhere in the program. It also proves equality of the whole
ordinary difference trajectory after each corrected centre with the original
trajectory for `f=Bz`.

For the fixed-kernel claim, specialize to forward centres `tI` and backward
centres `t^-1 I`. If `e` is valid for every such nonzero `t`, at `t=1` it belongs
to the already certified 149-dimensional kernel. Its derivative must vanish.
The replay computes that derivative exactly in `Q[ε]/(ε²)`, with forward
`1+ε` and backward `1-ε`, and a nonzero 21-by-21 prime-field minor proves
injectivity on the 21 noncoordinate directions. Hence their coefficients must
vanish. Conversely, `KB=0` on the 128 coordinate directions, so transport leaves
them unchanged for **every** collection of `H_j`. The same necessity holds if
`t` is restricted to the complex unit circle: set `t=exp(iθ)` and the derivative
at zero is `i` times the checked derivative. This is not a native frame/cover
rank theorem.

For example, PR2799's `-4 e8 + e40` cancels at `t=1`. Its reciprocal derivative
changes **903** final Y owners, including owner 560 by `-1` and owner 561 by
`-1/2`. The literal verifier checks every derivative coefficient. The transported
combination cancels again; the 903 values do not contradict PR2799.

## One explicit repair, with source access and cleanup

Assume the 21 arbitrary vector parameters `Z_k` are available at entry and stay
read-only. Assume a single invertible operator `H`, using `H` at forward sites
and `H^-1` at backward sites. These are interface assumptions, not facts about
the actual caller. Allocate 42 initially zero work fields:

```text
U+_k = (H-I) Z_k,     U-_k = (H^-1-I) Z_k.
```

For each field, the literal preparation is `W += Z; W = H^(±1) W; W -= Z`.
At site `j`, add its original kernel row in `Z`, then subtract its correction
row in `U+` or `U-`. Reverse the preparations after the last injection. All 42
fields return to zero and every `Z` is unchanged at every prefix.

There are 50 original kernel terms and 1,913 correction terms. To avoid treating
a weighted addition as a unit native operation, `repair.py` expands each
nonunit coefficient `q` using one additional zero scratch field:

```text
S += source; S *= q; destination += S; S *= 1/q; S -= source.
```

The scratch returns to zero after every such term and at every centre boundary.
All denominators are nonzero exact rationals. These scales are not claimed to
be a paid BIT or physical stream implementation.

| Complete generated repair | Count |
|---|---:|
| Calls to `H` | 42 |
| Calls to `H^-1` | 42 |
| Signed unit additions, including source loads and cleanup | 4,969 |
| Rational scalings | 2,838 |
| Total operations | 7,891 |
| Initially zero work fields, restored to zero | 43 |
| Read-only parameter fields | 21 |

The 1,152 injection targets in the formal replay represent successive arbitrary
dirty centre slots; they are not 1,152 extra retained work fields. The word
adds the required error to each slot. Its operations are checked over the free
Laurent module `Q[H,H^-1]`, so the check covers every invertible linear `H`, not
just numerical samples.

The abstract cost recurrence for this module is

```text
C_repair = 42 C(H) + 42 C(H^-1) + 4969 C(signed ADD) + 2838 C(rational SCALE).
```

This includes all accesses in the displayed bank program and its restoration.
Availability of the 21 parameters and 43 clean fields, physical retention,
movement, frames, hosting, precision, and the eventual complementary X output
are **additional unresolved caller obligations**. Clean fields are a stated
input contract; their creation from arbitrary dirty workspace is not free.
No unchanged supplier tariff is applied to this new interface.

A narrower optimality fact explains why this direct repair is not a free
21-call saving. In a one-pass linear batch that queries only `H(sum a_k Z_k)`
or `H^-1(sum a_k Z_k)` with fixed rational coefficients and combines their
outputs linearly, the coefficients of `H` and `H^-1` have ranks 21 and 21.
Each query contributes a rank-at-most-one coefficient matrix. Comparing the
independent Laurent powers forces at least **42 queries before cleanup**.
Preparation attains that count. This excludes only that direct batch model;
it is not a lower bound for adaptive queries, reuse of existing caller outputs,
a known special operator, or recursive children. The 84-call restored program
is not claimed optimal. It supplies no changed paid profile or κ.

## Reproduce and verification scope

Scientific base: `28f54620ff770dd051d5df35882bd84303d13c6f`, priority revision 5.
Rebased onto refreshed main `d9b24831174325cad2e04e34da2068d7acb02938`;
guidance, selected inputs and the replay runner are unchanged.
Dependencies and source Git blobs/SHA256 values are in [SOURCES.json](SOURCES.json).
Only the selected replay archive is an external execution input. Compressed
predecessor receipts decompress to their byte-exact original JSON and are never
executed. No predecessor code is imported.

With standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/centre-kernel-feedback
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/centre-kernel-feedback outcome=completed
```

The primary forward replay reproduces **every** original local and global
response coefficient, checks strict causality and all kernel vectors, and
certifies both correction ranks and the derivative rank. Rational elimination
and separate modular minors supply matching exact evidence. The separately
written literal interpreter executes all **2,835,792** scalar instructions,
checks every chronological correction coefficient and private exit, and tests
1,152 repairs using noncommuting invertible 2-by-2 operators; wrong signs fail
at 435 sites. A complete rational literal derivative witness is also retained.
The general operator statement is the proof above, not a finite-test inference.

Controls include primitive assignment oracles, permutation-sum determinant
oracles, omitted cleanup, a wrong oracle direction, optimized Git-free replay,
source/reference corruption, a changed correction coefficient, bool/integer
receipt substitution and occupied-output refusal. Normal replay is read-only;
`verify.py --out ABSENT_DIRECTORY` writes fresh receipts. No whole-repository
replay, native cover/compiler replay, full supplier admission, all-size theorem,
formal proof-assistant run or independent human review is claimed.

## Credit

Credit **Arham Tahir / PR2799** at
`3401bcfce70ad5b692cd4d89e92955229f56c819` for the terminal kernels and reverse
response, and **ywz65 / PR2622** at
`4ffb893a08e8868057a30a065642d0b5f647f742` for the complete response and quotient
handoff. PR2763's independently checked source histories are a different
obligation. Retain **Sagar Thakrar / PR2199**, **Adam Gall / PR1918**,
**commdata2338 / PR2048**, **Aaron Wang / PR2391**, and the Rohan Arun,
Jeremy Kothe, Hao Yan, icekylinx, DreamingOfClouds and Douglas Colkitt selected
construction/compiler lineage. PR2391's native counterexample is a reason to
keep this projection boundary explicit.

New proof instantiation, code and checking by **Tekalign (@tekuuu), with
substantial OpenAI Codex assistance**. The two checking implementations have
the same AI-assisted author; no independent human/subagent review is claimed.
Apache-2.0. [TASK.json](TASK.json) records the seed, three candidates, scope
refinement, bounded coverage and coordination.

## Open next questions

The next useful tasks are concrete caller obligations, not another subset
census. Can a caller accept the 128 terminal directions while consuming or
restoring X within budget? Can it supply existing `HZ`/`H^-1 Z` values that
avoid this direct repair's additional calls? Can one compensated direction be
lifted through the actual native cover and bridge actions? For each question,
TASK.json records a feasible first step and the missing contract. This round
stops at the verified interface and does not launch supplier expansion.
