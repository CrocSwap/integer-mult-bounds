# Exactly four optimal punctures in the 240-port global star code

**Scoped negative result / exact finite classification; no new κ.** For the
240 paired ports with four coordinates chosen from six pairs, arbitrary
off-target proper stars do not reduce the five deletions needed to decode one
retained target. There are exactly four optimal deletion sets per target. Each
isolates one of its three-coordinate stars; no additional optimal support is
made possible by off-target stars.

The same certificate gives the exact **algebraic all-target threshold: 85
deletions**. The proper-star code has dimension 155. An explicit set of 155
retained ports admits decoders for every target, while no larger surviving
family does. This is a statement about scalar identities, not their physical
implementation or cost.

The original question came from Theorem 2 of
[Sam Sung's PR #669](https://github.com/CrocSwap/integer-mult-bounds/pull/669),
which leaves punctured global stars outside its scope. Two contributions
arrived during this experiment: [Luke Mansoor's #732](https://github.com/CrocSwap/integer-mult-bounds/pull/732)
proves the general minimum threshold and independently checks the same
240-port rank and distance; [Sagar Thakrar's #725](https://github.com/CrocSwap/integer-mult-bounds/pull/725)
classifies 67 optimal patterns in the smaller 80-port (5,4) case, only four of
which are target-local. Those threshold/rank results are credited, not claimed
as new here.

This contribution adds the **complete equality classification for (6,4)**:
all four optimal patterns are target-local, and there are no off-target-only
optima. It also supplies the **sharp algebraic all-target threshold and an
explicit information set**, outside the one-target scope of both concurrent
notes. The overlapping minimum-distance calculation is separately implemented
corroboration. No code or proof from either concurrent package is imported.
The finite classification does not claim a general equality theorem for other
p or k.

## Model

There are six pairs `{2i, 2i+1}`, for `0 <= i < 6`. A port S is a four-element
set using four distinct pairs. Let P be all `2^4 * binom(6,4) = 240` ports.
Let D be the deleted ports, F=P\D the surviving ports, and T a retained target.
All input symbols x_S, for S in F, are independent over F₂.

For every nonempty compatible coordinate set L of size less than four, define

```text
star_L(F) = sum_{S in F, L subset S} x_S.
C_j(T,F)  = sum_{S in F, |S intersect T| = j} x_S,  j=1,2,3.
```

The allowed decoder is

```text
x_T = sum_L a_(T,L) star_L(F) + sum_{j=1}^3 b_(T,j) C_j(T,F).
```

The 232 star coefficients may vary arbitrarily with both T and L, including
L outside T. The three correction coefficients may vary with T, but remain
uniform within each overlap class. No degree-four star or correction C_4 is
allowed: either would directly supply x_T. The global sum is optional here;
the certificate proves that it already belongs to the proper-star span for
this instance. Both stars and corrections are recomputed on F after deletion.

## Why the problem reduces to one binary code

Put `A_l(T,F) = sum_{L subset T, |L|=l} star_L(F)`. Coefficient comparison at
every surviving source gives

```text
C_1 = A_1 + A_3,    C_2 = A_2 + A_3,    C_3 = A_3.
```

For a source intersecting T in r coordinates, A_l has coefficient
`binom(r,l) mod 2`. Substitution for r=0,...,4 proves these identities,
including r=4 where each right-hand side is zero. Deleting sources just
restricts these pointwise identities. Thus the correction columns add no
freedom, even after puncturing.

Let C be the span in F₂^240 of all proper-star incidence vectors on P. A
decoder on F exists for T exactly when some c in C has c_T=1 and
`support(c) subset {T} union D`. This equivalence does not assume a symmetric
decoder, a bound on the number of totals, or an efficient implementation.

## Certificate and exhaustive finite argument

[CERTIFICATE.json](CERTIFICATE.json) contains 155 independent proper stars,
85 independent parity checks H, an information set of 155 ports, and the four
optimal puncture witnesses. The builder and verifier are separate programs;
the verifier does not import or execute the builder or a predecessor checker.

The verifier independently constructs the coordinate sets and incidence
supports. It checks that every parity row annihilates **every** proper star
and overlap correction, and checks the two ranks using set elimination.
Since `155 + 85 = 240`, this proves `C = kernel(H)` and `dim(C)=155`.
It also checks H against the global sum. No solver status is trusted.

Let h_i be column i of H. The assignment seed selects target index 42 in the
specified ordering (pair combinations, then sign tuples). Define A to contain
zero, every non-target h_i, and every sum h_i+h_j of distinct non-target
columns. Its **28,681 elements are all distinct**:

```text
1 + 239 + binom(239,2) = 28,681.
```

Every set D of at most four non-target ports splits into two parts of size at
most two. Therefore `h_T = sum_{i in D} h_i` would imply
`A intersect (h_T+A)` is nonempty. The checker exhausts this intersection and
finds it empty. This excludes every allowed decoder with at most four
deletions, across all `2^155` codewords, without enumerating their coefficients.

At the boundary, the checker exhausts all **2,246,839 triples** of non-target
ports and looks up the complementary pair syndrome. Unique pair syndromes
make this lookup lossless. Exactly 40 hits yield four distinct five-element
sets, each appearing `binom(5,2)=10` times. Overlapping pairs and triples are
handled by symmetric difference; they would produce a smaller support and
are rejected. Every five-element support has such a partition, so the census
is complete. Its fixed stopping rule is exhaustion of these lists, not a time
limit or a heuristic search.

For each resulting set D, a three-coordinate J contained in T satisfies
`star_J(F)=x_T`. The verifier checks every surviving source coefficient. These
four J are exactly the four triples in T. Equivalently, D consists of the five
other ports containing J. The fifth deletion is necessary: restoring any one
of them breaks the identity, and the direct equation solver also rejects it.

Permutations of the six coordinate pairs and independent swaps within pairs
act transitively on ports and preserve the full star family and overlap
classes. Hence the result for index 42 applies to **every target** in this
fixed geometry. Every nonzero codeword contains a target, so C has minimum
distance six; its minimum words are precisely the 160 triple-star supports
(`240 * 4 / 6 = 160`, also `2^3 * binom(6,3)`). This is a finite,
computer-assisted classification, not a formalized proof of multiplication.

## All-target corollary

For a surviving family F, the available decoder vectors are the projection
`C|F`, including all the correction classes by the identities above. Decoding
every target requires all unit vectors and thus `C|F = F₂^F`. Its dimension is
at most 155, so `|F| <= 155`: at least 85 ports must be deleted.

The certificate's `information_set` attains this. Restricting its 155
independent star rows to those 155 coordinates has rank 155. The independent
tests additionally solve for all 155 unit vectors and check their literal
incidences. These are algebraic decoders with unrestricted star use. No
favorable copy cost, frame schedule, or restoration circuit is inferred.

## Reproduce

Python 3.9 or newer, standard library only; no downloads or external solvers:

```sh
python3 -I -B research/global-star-punctures/verify.py
```

Expected final line:

```text
PASS_GLOBAL_STAR_PUNCTURES ports=240 rank=155 dual=85 minimum_deletions=5 optimal_sets=4 all_target_deletions=85 triples=2246839 controls=8 restored_ports=20 kappa=unchanged
```

Eight default negative-control categories cover a changed parity bit,
dependent dual rows, duplicate primal rows, omitted minimum supports,
incomplete coverage receipts, deletion of the target, all 20 one-port
restorations, and a wrong coordinate sign. Checks remain active under `-O`.

Additional direct equation checks and certificate regeneration:

```sh
python3 -I -O -B research/global-star-punctures/test_verify.py
python3 -I -B research/global-star-punctures/build_certificate.py --output /tmp/global-star-certificate.json
cmp research/global-star-punctures/CERTIFICATE.json /tmp/global-star-certificate.json
```

The five test groups use an independent ternary-word port enumeration and
solve the actual decoder equations, without parity certificates, for all four
optima, their 20 one-port restorations, and 20 wrong five-port punctures. They
also check all 155 information-set targets, positive controls outside the
obstruction (degree-four stars, k=3, and p=k=4 with one puncture), the vacuity
of dropping the target equation, and optimized subprocess rejection of four
corrupted certificates. See [VALIDATION.md](VALIDATION.md) for actual runs.

## Scope, budget, provenance and credit

The proposed escape was to allow off-target stars to beat the known
target-local puncture threshold. It fails here already at scalar exactness.
Giving helpers, source access, frame changes, copies, restoration and recursive
children zero cost cannot make the excluded identities hold. The attaining
five-deletion witnesses are the predecessor's isolated-star mechanism; their
paid implementation is not supplied. The 85-deletion information set is not
a proposed improved supplier, and no complete-cost or κ improvement is claimed.

Other p or k, higher-degree totals, source-dependent correction coefficients,
other fields/geometries, nonlinear decoders and alternative stage structures
remain outside this result. No global bound on integer multiplication follows.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins the predecessor heads and inspected source
bytes. [CLAIM.json](CLAIM.json) records the OS-random seed **42**, three candidate
tasks, selected object, stopping rule, and overlap checks. No pinned sprint
issue existed. Only this package is added; `upstream/` and the frontier are
unchanged. The accepted conditional κ remains
`51110230636731/31250000000000000 = 0.001635527380375392`, from #626/#622/#623
with #543. Its construction was read for context, not re-certified here.
All inherited compiler, common-label/mutable-basis, hosting, restoration,
precision/tape/recovery and analytic obligations remain.

Credit: Joel Pulikkan / GamingPuzzled's
[#231](https://github.com/CrocSwap/integer-mult-bounds/pull/231) supplied the
symmetric parity obstruction, following icekylinx's #144 and eumemic's paired
cube identity. Sam Sung / @the-missionary-company's
[#669](https://github.com/CrocSwap/integer-mult-bounds/pull/669), pinned at
`308f1e6ec3bb0b6ec0584cf7bfe219addc219b1e`, supplied the global unpunctured
obstruction, target-local puncture theorem, and explicit remaining question.
No predecessor code is copied or executed. E8 puncture and extension work in
#620/#631/#715 has a different geometry and was checked for overlap.

Concurrent credit: **Luke Mansoor (@lukemansoor), #732**, at
`80431a74c31e807581f5c2258c87abe2084caacd`, supplies the general star-code
distance theorem and the same (6,4) rank/distance. **Sagar Thakrar
(@thakrarsagar), #725**, at `6eadc4eb4ebc355b13fa36a3138d97a583ea7f37`,
supplies the (5,4) equality classification. Their source README hashes are
pinned in SOURCES.json. The change in emphasis after their arrival is recorded
in CLAIM.json; the scientific certificate and its enumeration domain did not
change.

Prepared by **Alishan Ladhani (@aladh)** with substantial **OpenAI Codex
assistance** in research, proofs, implementation, verification and writing.
No independent human peer review is claimed. New files are under the
repository's [Apache-2.0 license](../../LICENSE).
