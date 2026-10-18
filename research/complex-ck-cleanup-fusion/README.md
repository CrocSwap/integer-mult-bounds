# Rank-two obstruction to CK cleanup pair fusion

**Status: scoped negative result. No new supplier or kappa.**

The selected #626 CK provider has 8,309 full-frame cleanup operations,
including 8,186 additions and 123 nonzero scalings. Exactly 78 pairs of additions
have the same ordered target and source registers. For every such pair, removing
the two endpoints while retaining the intervening word creates a defect of rank
two. Consequently, **no single addition, scaling, or other rank-one update can
replace the pair at any position among the unchanged intervening gates**.

This is a statement about the complete rational map on arbitrary register inputs.
It allows any coefficient and any target/source for the proposed replacement.
It does not rule out changing intermediate gates, using multiple replacement
gates, exploiting restricted inputs, or resynthesizing a larger circuit.

## Reproduce

From the repository root, with Python 3.11 or later:

```sh
python3 -B research/complex-ck-cleanup-fusion/verify.py
```

Expected:

```text
PASS_CK_CLEANUP_RANK_TWO pairs=78 rank=2 columns=312 controls=8
```

The command needs only the standard library and committed files. It performs
no network access or file writes. It checks source pins, the binding to the
selected CK specification, every cleanup register's full-frame boundary,
complete pair coverage, all 156 forward/dual witnesses, and the committed
certificate. Checks stay enabled with `python3 -O`.

`verify.py` is the authoritative entry point for source pins and all certificate
metadata. `check_columns.py` also runs separately, without checking those pins.
It checks all 624 minor entries by
replaying 312 basis columns. This is an independent arithmetic implementation,
not an independent human review. It uses dense vectors and literal inverse
and forward scalar operations; it imports no code from the sparse conjugation
checker. The main command additionally checks the recorded support sizes and
conjugation factors. Neither implementation replays all 716 columns of the
complete supplier. Two columns suffice for each nonzero minor.

## Exact finite statement

Use column vectors and let an addition be
`A(t,s,a) = I + a e_t e_s^T`, with `t != s` and `a != 0`.
For a repeated pair at cleanup indices `i < j`, put

```text
E = e_t e_s^T
M = the product of cleanup gates strictly between i and j
P = (I + b E) M (I + a E)
u = M e_t
v^T = e_s^T M^-1
D = P M^-1 - I
  = a (u + b e_t u_s) v^T + b e_t e_s^T.
```

Every middle gate is invertible. All additions have distinct registers, and all
scalings have a nonzero coefficient. Thus the inverse used here exists.

Choose `r != t` with `u_r != 0` and `c != s` with `v_c != 0`. The determinant
of the minor of `D` on ordered rows `[t,r]` and columns `[s,c]` is

```text
det D[[t,r],[s,c]] = a b u_r v_c != 0.
```

The expression for `D` is a sum of two rank-one matrices, so its rank is
exactly two. Such `r,c` exist for every one of the 78 pairs. The certificate
records the four minor entries, their determinant, the two exterior factors,
and the support sizes. These are rational identities and remain nonzero over
the complex numbers.

For a proposed insertion position, split the unchanged middle word as `M=Y X`.
A replacement `R` would have to satisfy `P=Y R X`, hence

```text
R - I = Y^-1 (P - M) X^-1.
```

Multiplying by invertible matrices preserves rank. Therefore `rank(R-I)=2` at
every insertion position. A single addition or scaling has `rank(R-I) <= 1`,
so it cannot work. This also excludes arbitrary rank-one updates, which are
more permissive than the supplier's actual scalar gate set.

The backward orientation replaces each chronological gate by its inverse
transpose, keeping the gate order. The checker recomputes the witnesses in that
orientation rather than assuming the forward minors also work. Independently,
`P^-T - M^-T = P^-T (M-P)^T M^-T` shows that the defect rank is preserved.

For example, pair `[17,24]` consists of additions from register 236 to register
230 with coefficients `-2` and `1`. The forward minor on rows `[230,231]` and
columns `[236,230]` is

```text
[-1   1]
[ 2  -1]
```

Its determinant is `-1`. The corresponding dual minor also has determinant
`-1`. All indices are zero-based within the pinned cleanup list.

## Experiment and coverage

OS randomness produced assignment seed **20**, selecting the complex-supplier
track and, by parity, CK rather than JP8. The three candidate tasks were factory
resynthesis, B-frame reassignment, and cleanup pair fusion. Concurrent #681 and
#698 already cover the first two, so this experiment uses the cleanup circuit.

The initial test allowed moving an addition across individually commuting gates
to merge it with another addition on the same ordered registers. All 78 pairs
have blockers. That failed search alone says nothing about collective
cancellation within the middle word. The one refinement was to compute the
complete conjugated shear and an exact rank minor. It proves the stronger
fixed-middle obstruction above, including middle words whose individual gates
do not commute with the endpoint.

The completed domain consists of **every pair of distinct additions with the
same ordered target and source in this one cleanup word**, with both
orientations checked. Pair generation stops after exhausting the list. There
is no sampling, timeout, or random search beyond the assignment choice. No
fixed-point fusion pass is needed because no first fusion in this class exists.
Pairs with different endpoint registers are outside this domain.

Even granting a replacement arbitrary coefficients, an arbitrary rank-one map,
and free placement/source access does not overcome the rank defect. No proposed
circuit reaches the cost-accounting stage. Frame changes, wrappers, restoration,
recursive children, ownership, and the selected bit supplier therefore retain
their original costs. Cleanup arithmetic simplification alone would not change
the recursive rank histogram in any case.

## Controls

Five semantic controls check the distinction between a blocker and a proof:

- A commuting middle addition permits a rank-one combined update.
- A noncommuting source scaling by two still permits a combined coefficient
  `3/2`; it must not be classified as a rank-two obstruction.
- A reverse-direction middle addition has the exact minor determinant `-1`.
- Opposite endpoint coefficients around that middle addition do not cancel.
- Two inverse middle additions cancel collectively and permit fusion, despite
  each being an individual commutation blocker.

The direct-column checker also rejects three altered certificates: a changed
minor entry, a flipped dual endpoint coefficient, and an omitted pair. A
recomputed certificate must match every field of the committed evidence.

## Provenance, relation to other work, and limits

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The accepted result at this base is conditional
`kappa=51110230636731/31250000000000000`, from #626 with #543.
The actual construction and scope are identified by
[the selected record](../../certificates/selected-result.json) and
[the maintainer review](../../docs/research/community-k492-review.md).
[SOURCES.json](SOURCES.json) records exact dependency heads and file hashes.
The compressed word is bound by its decompressed-payload hash, so gzip metadata
and compression versions do not affect equality.

Credit belongs to Jeremy Kothe's #622 K-triangle construction, Chafik Boukhalfa's
#626 selected owner package, DreamingOfClouds' cold-helper and native-verifier
work, icekylinx's scalar factory/direct-delivery lineage, Dugongue's coordinate
and rank-sector work, eumemic's retained #543 bit supplier, and the predecessors
credited in the selected review. The original source files and notices remain
unchanged.

Related pending work is credited without treating its titles as accepted results:

- Evan McKinney's [#271](https://github.com/CrocSwap/integer-mult-bounds/pull/271)
  simplifies bit cleanup sandwiches and changes helper endpoints. Its field,
  circuit, and allowed rewrite differ from this fixed complex cleanup test.
- eumemic's [#411](https://github.com/CrocSwap/integer-mult-bounds/pull/411)
  resynthesizes complex target prefixes and recomputes dirty responses.
- [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) resynthesizes an
  eight-register raw factory window. This does not contradict the narrower
  two-endpoint, unchanged-middle obstruction.
- [#687](https://github.com/CrocSwap/integer-mult-bounds/pull/687) examines raw
  K-triangle read relocation; [#698](https://github.com/CrocSwap/integer-mult-bounds/pull/698)
  optimizes B frames at fixed gate order; [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)
  lowers the primitives implementing unchanged complex macros.
- Concurrent [#710](https://github.com/CrocSwap/integer-mult-bounds/pull/710),
  prepared for Sagar Thakrar with Codex assistance, uses exact conjugation to
  shorten the bit supplier's R420 cleanup. It was discovered during the final
  overlap refresh. Its joint two-sandwich rewrite over F2 changes five gates
  to three; this rational CK census excludes only two endpoints becoming one
  update with their middle fixed. The two results are compatible.

None of those pending packages is imported or needed to reproduce this result.
The accepted providers, `upstream/`, selected frontier, and global accounting
are unchanged. No optimality claim is made for CK, JP8, the whole cleanup word,
or broader circuit synthesis. All-size compilation, common-label and
mutable-basis realization, hosting, residual, precision/tape, recovery, and
analytic-transfer assumptions of the selected construction remain inherited.
This finite certificate and written rank argument are not a Lean proof or a
verification of the complete multiplication theorem.

Prepared for **@thakrarsagar**, with substantial **OpenAI Codex assistance** in
research, code, mathematical analysis, verification, and writing. A second Codex
agent supplied the independent column implementation and reviewed the rank
argument. New material is under the repository's [Apache-2.0 license](../../LICENSE).
