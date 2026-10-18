# Native rank lift for the first two selected centre cuts

**Scoped proof with an exact finite certificate; no new κ or supplier.**
The sixteen centre-source rows in the selected time-0/time-1 forward calls
have joint complex rank **8,192 = 16 × 512** in the local native address model.
Their two scatter increments have the same rank. This closes the *local
native-frame lift* left open by [Adam Gall's PR1918](https://github.com/CrocSwap/integer-mult-bounds/pull/1918)
for this pair, using the repository's existing common-frame conjugation lemma.
It does not prove a lower bound of 128 on recursive rank mass.

In particular, a replacement whose **entire source-dependent transcript** is
eight 512-dimensional complex rows cannot reconstruct both scatter increments
when it has no other source-dependent input. This is an information bound on
that specified linear interface. Eight reusable storage slots, additional
reads, larger rows, altered output obligations and arbitrary recursive calls
are different interfaces and are not excluded.

## Exact object and new evidence

Base: `c676548106012571fefa1dce0ec16f1bcfe11dce`. The selected PR1094 source is
`0fc329d0bec93ca7cd288eaea1295172e8789810`. The claim is in
[discussion #1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884#discussioncomment-18930557).
The two complete calls have time/stage/replica `(0,0,0)` and `(1,0,8)`, both
forward and using the exact same selected `gauge44` emitted program. There
are 704 ordinary roles per call and 30 common physical owners; every common
owner is a helper in both calls. Neither call uses any of the other's active
source or target families. The union has 1,378 owners.

PR1918 already supplies a rank-16 **scalar** minor and explicitly declines to
infer native rank. This package adds the missing factorization and checks its
hypotheses against the exact selected word:

| Check | Result |
|---|---:|
| Complete forward events with extended labels | 24,767; zero violations |
| Ordinary scalar input columns, complete continuation | 704 |
| Used native child recipes, phase included | 2,888, each on all 512 columns |
| Source/target adapter identities | 224, each on all 512 columns |
| Invertible residual-wrapper records and their role bindings | 36 records; 480 events |
| Source-to-helper block at the complete endpoint | zero |
| Pivot-input block in targets before the centre phase | zero |
| Native source/scatter rank at both cuts | 8,192 |
| Literal native replay of one encoded input | all 24,767 events; 360,448 endpoint amplitudes |

The scalar stream audit and rank application are implemented here. Exact
Clifford evaluation reuses the pinned independent kernel from
[Sagar Thakrar's selected-recipe audit](../frontier1094-recipes-exact-seed76/README.md).
Its recipe theorem is credited prior work; repeating those identities supplies
fresh evidence for this application's premise. The proof below, rather than
an 8,192-square Gaussian elimination, establishes the native rank.

## 1. Common-frame factorization, including the continuation

Write `T_f` for the invertible canonical operator of frame `f` on
`M = C^512`. Formulas use each call's admitted local chart; external row-wise
admission maps contribute additional invertible factors. An actual child from frame `a` to `b` applies
`T_b T_a^-1`. The checker decodes its serialized `L F_r R` and verifies

```
L F_r R T_a = T_b
```

on every basis column, including global phase. Every ADD combines rows at
the same frame. A relabel, scalar ADD/SCALE, private COPY or CLEAR consequently
preserves the invariant `physical_row = T_label × normalized_row`, where
the normalized rows follow the scalar word. This is
[`Stream.conj_matrix`](../e8-lemma-g-lean/LemmaG/Stream.lean), not a new general lemma.

The invariant also covers the conversion boundaries. If the source-entry
monomial is `M_i`, the initial label operator is `M_i^-1 T_start(i)`.
For a helper with start/end `(a,b)` and serialized wrappers `R,L`, use initial
operator `R T_a` and final operator `L^-1 T_b`; its actual pre/post operations
are `R^-1` and `L^-1`. For a target whose exit operation is `N_i^-1`, its
post-label operator is `N_i^-1 T_final(i)`. Other identity adapters preserve
the canonical label. These definitions make each conversion a conjugation
between the stated label operators. The code checks every conversion's role,
phase, direction, frame and multiplicity, and rejects an ADD through a
noncanonical boundary label. All serialized monomials used here are invertible.
Early helper endpoints are included: this does not assume every helper ends
at the full frame.

Hence the complete physical word has block form

```
D_final (S ⊗ I_M) D_initial^-1,
```

where both `D` matrices are invertible and block diagonal by role. Fresh
exact scalar replay gives `S: (x,y,h) -> (x,y+x,h)` on all 704 ordinary
columns, and every private centre is cleared. In particular, **the native
source-to-helper block is zero**, even though a helper's own state can advance
by a nonidentity operator. This distinction matters: helper restoration to
its original bits is not assumed. Initial helper and target dirt is arbitrary;
take differences between executions holding that dirt fixed.

## 2. An explicit invertible native minor

For each call, vary only source roles `J = (0,1,2,3,4,5,6,12)`. All other
initial rows are fixed. Let `u_j` be these eight physical source variations.
The source-adapter identities verified above give normalized initial values

```
x_j = C_qj^-1 u_j,
C_q = ((1+i)I + (1-i)X_q)/2.
```

Here the actual port masks are `(11,19,35,67,131,259,13,41)`.
Each `C_q` is invertible (`C_q^2 = X_q`); its forward/inverse product is also
checked on all 512 columns. The eight normalized carrier values at the centre
cut are `z = (P ⊗ I_M)x`, with

```
P = [ 1  0  1  0  0  0  0  1
      1  1  1  1  1  1  1  0
      1  1  0  0  0  0  1  1
      1  0  0  1  1  1  0  0
      0 -1  0 -1  0  0  1  1
      0  0  0  0 -1  1  0  0
      0  0  1  1  0  0  0  1
      0 -1 -1  0 -1 -1  1  0 ],    det(P) = 32.
```

Thus the actual eight carrier rows are
`diag(T_415,...,T_422) (P ⊗ I_M) diag(C_qj^-1) u`, an invertible
4,096-square map. The native centre descents remove the `T_415,...,T_422`
factors before the scatter, whose target frame is zero.

Let `B` be the scalar scatter matrix restricted to target roles
`(112,113,115,116,117,118,120,131)`. The checker extracts it from the literal
centre events and finds

```
det(B) = -1/16384,        det(BP) = -1/512.
```

The same eight target increments therefore have native matrix
`(BP ⊗ I_M) diag(C_qj^-1)`, also invertible. Exact matrices, both-sided
inverses and determinant witnesses are in [RESULT.json](RESULT.json).
Every target's variation is zero before the centre phase on this input
slice, so these increments are not supplied by pre-existing target data.

## 3. Why the two noncoincident cuts still add

The first complete call finishes before the second begins. Their only shared
owners are helpers. Section 1 proves that no variation of the first call's
source data survives in any helper at its endpoint. The second call therefore
has no dependence on those first eight pivot inputs. Conversely, the first
call never touches the second call's pivot source families. The sixteen
physical pivot owner IDs are precisely PR1918's

```
0,1,2,3,4,5,6,12, 7168,7169,7170,7171,7172,7173,7174,7180.
```

The two-cut minor is block diagonal with two invertible blocks from section 2,
giving rank `2 × 4096 = 8192`. This also is the maximum possible rank of sixteen
carrier rows. The full 176-row scatter history factors through those sixteen
rows and contains the displayed invertible output minor, so its rank is
exactly 8,192 as well. This is a pair of chronological observations, not a
claim that the sixteen carrier rows exist simultaneously.

The local native statement retains all 512 addresses. For its interpretation
in the selected hosted model, we use the **inherited injective chart/cover
contract**: the template identifies both windows as the first nine axes with
empty prefix, all data routes have stage zero, and `rho_0,q = I`. Distinct
data owner families give independent row variables. Complete call sweeps and
block-diagonal helper endpoints allow arbitrary shared helper dirt. Row-wise
invertible chart changes and a common spectator tensor factor preserve the
factorization and its zero cross blocks. No equality between the two calls'
helper charts or offsets is assumed. We check the selected owner/window/route
records, but do **not** independently reprove or replay the global 73-axis
hosting compiler. The global interpretation remains conditional on that
existing contract; the local operator calculation does not.

## Transcript consequence and its limits

Suppose a linear replacement receives the two scatter outputs' source
information solely through a transcript `E u` consisting of `d` complex
scalars; it has no other source-dependent state or observations on the above
input slice. Correctness would imply `F = R E`, where `F` is the demanded
scatter-history map. Therefore `d >= rank(F) = 8192`. Eight rows of dimension
512 have only 4,096 dimensions and cannot suffice. This also excludes nonlinear
decoding of a *linear* transcript, since any kernel collision of `E` must be a
kernel collision of `F`. No nonlinear-encoding claim is made.
The observation contract must retain both scatter increments. A replacement
that only preserves the final call endpoints may change these internal
observations and is outside this exclusion.

A concrete native collision for naive pooling is obtained by choosing any
nonzero `v in M`, setting normalized centre values to `e_0 v` in the first
call and `-e_0 v` in the second, and choosing physical pivot inputs
`u_j = C_qj (P^-1)_(j,0) v` with opposite signs between calls. Corresponding
native carriers have the same frame in their respective local charts, so
their pairwise sums in those coordinates vanish. Their
separate scatter increments are nonzero. This is PR1918's scalar collision
with the previously missing native input twists supplied.

The source-only condition is essential. Other helpers can contain source
information *at the centre cut*, even though the complete endpoint removes it.
A replacement that reads them has an additional transcript. Sequential reuse
of eight registers can convey sixteen rows and is not excluded either. No
conversion from complex information dimension to a minimum number/rank of
recursive calls is established. The unchanged two-phase bill is 16 rank-eight
transports, 16 COPYs, 32 CLEARs and 352 ADDs, with transport rank mass 128.
This proof does not certify that bill optimal. There is no changed profile to
screen with `ceiling.ceiling`; the card's ideal 1.90× shared-centre relaxation
was only the entry planning control.

## Reproduce and verification scope

Python 3.12, standard library only:

```sh
python3 -I -B research/selected-centre-native-lift/verify.py
python3 scripts/research_package.py --package research/selected-centre-native-lift
```

Expected:

```text
PASS_SELECTED_CENTRE_NATIVE_LIFT source_rank=8192 scatter_rank=8192 children=2888 columns=512 controls=11 no_new_kappa
```

Normal replay is read-only; `--write-result NEW_PATH` creates an absent receipt
exclusively. Source hashes are checked before importing the Clifford kernel.
Archive members are named by full path, not basename. The eleven semantic
controls cover an omitted climb, wrong common frame, omitted cleanup gate,
omitted private clear, shared source owner, intervening bridge, repeated pivot column, wrong child
phase, wrong source port, loss under pooling and a wrong descent phase in the
literal native executor. Checks remain active under
`-O`. The exact packed evaluator's radix is chosen from its proved bound on
the number of Fourier gates; it uses integers, not floating-point arithmetic.

[native_probe.py](native_probe.py) separately interprets every emitted event
on unpacked Gaussian-dyadic vectors for the explicit encoded input
`u_j = C_qj (P^-1)_(j,0) e_0`. It uses a new evaluator for the serialized
monomials, their inverses and the square-root translations. It compares all
4,096 carrier amplitudes, 57,344 target amplitudes at the scatter cut, and
360,448 ordinary amplitudes at the complete endpoint, including zero helper
response and private erasure. A corrupted descent phase fails at the scatter
cut even though the scalar shadow is unchanged. This is one engineered
input and a semantic integration control, not a substitute for the all-input
conjugation proof. The three unit-test groups additionally use an independent
permutation-sum determinant oracle and check relocated inputs, corrupted
archives and rejection of a changed kernel before it can execute.

The existing conjugation lemma is read and pinned; Lean was not run. No full
supplier cold replay, compiler/tape integration, precision proof, all-size
theorem, independent human review or outer-transfer proof is claimed. The
36 residual-wrapper coordinate-factor/tariff identities are not reverified:
their invertibility and role-local action suffice for this rank application.
The selected record and frozen source packages are unchanged.

## Open next questions

1. **A priced interface with additional reads or sequential reuse.** Such an
   interface could evade this transcript bound and still reduce recursive
   centre work. Start with one explicit two-call word and enumerate every
   source-dependent read, frame change, restoration and hosting charge. The
   blocker is the absent implementation and invoice, not the rank lemma.
2. **A pair with dependent chronological sources.** A different pair with
   intersecting active data could permit a smaller joint rank. First identify
   that pair and compose every intervening call in normalized coordinates.
   The present disjoint-data proof does not apply automatically. Full chart
   and chronological binding is the blocker. Structured questions are in
   [TASK.json](TASK.json).

## Credit and provenance

Adam Gall's PR1918 (`cc43a233ad989e717c8d46c6398ee50f97f5c0b9`) supplies the
specific pair, scalar minor and open question. DreamingOfClouds and the
PR484/509 Lemma G lineage supply the common-frame theorem, with their original
Claude assistance notices retained. Sagar Thakrar supplies the independent
Clifford kernel and selected recipe audit; this account's PR1415 and
BigCactusLabs' PR702 are among that kernel's calibrations. The construction
and source retain Rohan Arun, Jeremy Kothe, Hao Yan, icekylinx, Zhihao Chen,
Chafik Boukhalfa, DreamingOfClouds and the earlier credited lineage.

Related work: PR1829/Discussion1963 concern owner identity; PR1664/1684 give
conditional transport-height arguments; PR1708/1748 assume shared post-A
values; PR1969/1981 concern joint-query coding and source restoration. None of
those results is claimed anew. Exact live inputs, Git blobs and source hashes
are in [SOURCES.json](SOURCES.json); no pending implementation is imported.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0; predecessor sources and notices remain unchanged.
