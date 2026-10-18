# Four roles do not share two noncommuting S4 three-cycles in three calls

## Result

For every ordered noncommuting pair \((a,b)\) from
\(\{s_1s_2,s_2s_1,s_2s_3,s_3s_2\}\), the target
\(T_{a,b}=\operatorname{diag}([a],[b],[e],[e])\) has minimum paid length
**four**. There are eight such ordered pairs. Each has the direct four-call
construction below. The exact radius-three search excludes every word of
length at most three for all eight targets, even with the additional dirty
scalar role and free scalar \(\mathrm{GL}_4(\mathbb F_2)\) mixing included
in the alphabet. This is a scoped negative result: that extra role does not
produce the proposed one-call sharing for these targets and this operation
alphabet.

With right-to-left permutation composition, \(s_1=(12)\), \(s_2=(23)\),
and \(s_3=(34)\), so \(s_1s_2=(123)\) and \(s_2s_3=(234)\); the set also
contains their inverses.

## Exact model

Work over the noncommutative group algebra \(\mathbb F_2[S_4]\). Its 24
basis elements are the permutations of four points, and matrix entries are
24-bit coefficient masks. A paid call is

\[
F_{s,N}=I+([s]+[e])N,
\]

where the paid address label \(s\) is one of the adjacent transpositions
\((12),(23),(34)\), and \(N=xy^T\in M_4(\mathbb F_2)\) ranges over all
rank-one idempotents, with \(x,y\ne0\) and \(y^Tx=1\). There are 120 such
idempotents and hence 360 paid factors. Each factor is an involution. The
complete idempotent inventory includes the normalized free scalar
\(\mathrm{GL}_4(\mathbb F_2)\) mixing allowed by this formal model.

The equality to \(T\) restores roles three and four exactly and applies the
two stated transformations to arbitrary values in roles one and two. All
four roles may start dirty. Each adjacent-transposition call costs one; scalar
mixing, hosting the fourth role, and interface transitions are optimistically
priced at zero.

## Exact lower bound and upper bound

The verifier enumerates every one of the \(360^2=129{,}600\) ordered products
\(F_iF_j\), including repeated factors. This gives 87,016 distinct pair
product matrices, including the identity. For each of the eight ordered
noncommuting target pairs, it checks all 360 target-side meets, for 2,880
complete misses. The canonical row-major encoding uses a three-byte
big-endian coefficient mask for each of the 16 entries; the sorted
complete-state stream has SHA-256

`cc18ab4f9e58731f43f42ed0fd791531696836385f9435c6328cbbe36651f2f7`.

No target-side meet hits this set. For each target \(T_{a,b}\) and each of
the 360 possible final factors \(F_k\), the verifier checks
\(T_{a,b}F_k\notin\{F_iF_j\}\). Since every factor is an involution, any
three-call identity \(T_{a,b}=F_iF_jF_k\) would imply
\(T_{a,b}F_k=F_iF_j\). This complete meet excludes length three; direct
membership checks also exclude lengths zero, one, and two for all targets.

Every target pair has a two-letter factorization for each cycle. If
\(a=u_1u_2\) and \(b=v_1v_2\), its four-call word uses the diagonal
idempotents \(E_{00}\) and \(E_{11}\):

\[
F_{u_1,E_{00}}F_{u_2,E_{00}}F_{v_1,E_{11}}F_{v_2,E_{11}}=T_{a,b}.
\]

The verifier also checks a one-call positive control, all 32 one-call
deletions across the direct words, a changed-target control, all 360 factor
involutions, and noncommutativity of every target pair. Arithmetic is exact
in \(\mathbb F_2[S_4]\); no sampled columns or floating-point checks are used.

## Cost and limits

The favorable comparison is four paid calls versus a sought three-call word,
so the proposed saving would have been one call (25%) before any other charge.
This experiment found no such call reduction for any of the eight declared
targets. The fourth role and free scalar mixing were not charged, which makes
the failed three-call search a useful obstruction inside this abstract model.

The result does not cover other address groups, other paid labels, more than
four roles, different register dimensions, or richer call types. It does not
map these formal calls to the selected bit supplier, prove a native circuit
cost, change the selected recursive moment, or improve \(\kappa\).

## Provenance, overlap, and reproduction

The cycle used seed `a27baaa734817e395db88b840bf4a089`, track
`bit-mechanisms`, task `bit-new-register-model`, priority revision 3, base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, and selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
`SOURCES.json` pins the task catalogue, selected record, selected review,
source manifest, assembly certificate, and the abelian three-register
predecessor. Current related work at the final overlap refresh included PR
#1720 (two identical 4-cycle targets at three roles) and PR #1734 (two
identical double-transposition targets at three roles); this package changes
both the target pair and register count. PR #1705 uses a different
`F2[GL2(F2)]` address alphabet. The live pre-submit refresh also found
[PR #1742](https://github.com/CrocSwap/integer-mult-bounds/pull/1742), which
settles a three-role \(UT_3(\mathbb F_2)\) D8 central-commutator target with
labels \(x,y\) and a seven-call lower-bound search. That result has a
different address group, alphabet, target pair, register count, and baseline;
this package searches four roles over \(S_4\), with three adjacent
transpositions and distinct noncommuting 3-cycle targets. The scoped
coordination claim is
[Discussion #1740](https://github.com/CrocSwap/integer-mult-bounds/discussions/1740).

Run the exact finite search directly:

```sh
python3.12 -I -B research/s4-noncommuting-threecycle-r4-seeda27b/verify.py
```

Expected marker:

```text
PASS_S4_NONCOMMUTING_R4 rank_one_idempotents=120 factors=360 ordered_pairs=129600 pair_states=87016 target_pairs=8 radius3_misses=2880 pair_sha256=cc18ab4f9e58731f43f42ed0fd791531696836385f9435c6328cbbe36651f2f7 direct_calls=4
```

The registered repository package gate is:

```sh
python3.12 scripts/research_package.py --package research/s4-noncommuting-threecycle-r4-seeda27b
```

Prepared with substantial OpenAI Codex assistance. No subagents or
independent human review are claimed.

## Open next questions

- **Question:** Does a fifth restored dirty role or another explicitly priced
  paid-label set permit a sub-four-call identity for this family of
  noncommuting targets?
  **Why it matters:** That would separate a four-role obstruction from a
  limitation caused by the three adjacent-transposition labels, and could
  expose an actual sharing mechanism in a larger address model.
  **First step:** Fix five roles and the same target
  `diag([s1*s2],[s2*s3],[e],[e],[e])`, enumerate its complete rank-one
  idempotent alphabet through radius three for the eight target pairs, and
  test the exact four-call baseline.
  **Blocked by:** A new bounded scope and source/base refresh; this package
  deliberately stops at four roles. Any abstract saving would still need a
  separate implementation and full register/interface cost.
