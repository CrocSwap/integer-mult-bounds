# Index and audit: UT3(F2) = D8 central-commutator register bounds

**Navigation and audit note. No new bound, no new kappa.** On main, the
`bit-dihedral-commutator` package still lists this as open:

> Does a restored third dirty register help for the same D8 central target?

Open PRs have answered it three times, under two names for the same group.
The dihedral group of order 8 is `UT3(F2)` (also the Heisenberg group mod 2).
PR1742 was opened about five hours after PR1573 proved the all-register case.
It cites neither PR1478 nor PR1573, and its DONE note calls four-register
models open. This note maps the family, audits the proof the later PRs rely
on, and binds the duplicate finite results to each other with a third,
separately written census.

Search aliases: D8, dihedral, UT3, UT_3(F2), Heisenberg, central commutator,
`abab`, `xyxy`, third dirty register, extra dirty registers, arbitrary
workspace.

## The family (exact heads, as of 2026-10-14 10:05 UTC)

All of these use the same model. Registers are `r` scalar roles over the formal
group algebra `F2[UT3(F2)]`. A paid call is `I + ([g]+1) u v^T`, with
`g in {a, b} = {I+E01, I+E12}` and binary `u, v` (`v^T u = 1` unless noted).
Free scalar `GL_r(F2)` maps are allowed. The endpoint is `diag([c]^k, 1^(r-k))`,
with `c = abab` central, and every extra role is restored on arbitrary input.

| Source | Head | Scope | Method |
|---|---|---|---|
| PR1443, woklerx, on main as `research/bit-dihedral-commutator` | `965ff75a` | r = 2, k = 2: minimum 8 | census |
| PR1478, juper997 | `b30fdba4` | r = 2, 3; k = 2: minimum 8 | radius-3 census (565 and 47,231 states) plus C2-determinant parity |
| PR1573, steph4n-gh | `0b8c5a69` | **every k and every r >= k**: at least 2k a-calls and 2k b-calls, attained | written proof (two representations and rank-nullity) |
| Discussion 1569, then PR1589, Arham Tahir | `010ec8c0` | same bound with nilpotent rank-one couplings as well | degree-two quotient plus the rank argument |
| PR1607, bbMisk | `9d611791` | mixed targets over all eight UT3 elements | builds on 1573/1589 |
| PR1742, 1337isnot1337 | `679f3624` | r = 3, k = 2: minimum 8 | radius-3/4 meet in the middle through length 7 |

PR1742's model matches PR1478's r = 3 model exactly. Its group law is
`(a,b,c)(a',b',c') = (a+a', b+b', c+c'+ab')`, its 56 gates are the two labels
times the 28 idempotents, and its target is `diag([z],[z],[1])`. Its radius-3
layer counts `1, 56, 1750, 45424` sum to PR1478's 47,231 states. Both results
are the `k = 2`, `r = 3` instance of PR1573's theorem. The neighbors that
credit PR1573 as their all-register premise are UT4 (PR1662, PR1680, PR1690),
other targets (PR1763) and a GL3 alphabet (PR1567). They were not audited here.

## Audit of PR1573's proof (head `0b8c5a69`)

I read each step against the model above and found no gap.

1. **Normalization.** Interleaved free scalar maps conjugate into the
   projectors: `Q D_N Q^-1 = D_{Q N Q^-1}`. Augmentation then forces the
   leftover scalar map to be `I`. Correct.
2. **First representation.** Entrywise, the natural representation turns an
   `a` factor into `I + E01 (x) N` and a `b` factor into `I + E12 (x) N`. The
   only nonzero product of these nilpotent parts is `E01 E12 = E02`. Block 02
   is therefore the ordered sum `C_ab`, with no terms of higher degree. The
   verifier checks this block formula exactly on every word of length 4 or
   less at r = 2 and of length 3 or less at r = 3 (201,428 words). A control
   checks that predicting with the factor order reversed fails.
3. **Spans.** Each `N_i N_j` in `C_ab` has its columns in `im X_a` and its
   rows in `row Y_b`. Since `rank P = k`, both ranks are at least k. Correct.
4. **Second representation.** `sigma(x,y,z) = (y, x, z+xy)` is an involutive
   automorphism that swaps `a` and `b` and fixes `c`. The verifier checks this
   on all 64 pairs. It also checks that the plain swap without the `xy`
   correction is not a homomorphism, as PR1573 warns.
5. **Rank-nullity.** `X_a Y_a = 0` gives `rank X_a + rank Y_a <= n_a`, so
   `n_a >= 2k`, and likewise `n_b >= 2k`. Correct.

Two remarks follow from this check. Neither changes the theorem.

- The proof never uses `v^T u = 1`, which is why PR1589's nilpotent
  extension goes through. Its "rank one" assumption also costs nothing.
  Since `([g]+1)^2 = 0`, a factor `I + ([g]+1)(N1+N2)` equals the product of
  the two same-label rank-one factors (checked on all 4,802 ordered pairs at
  r = 3). So pricing a rank-s coupling at s calls gives the same bound.
- Whether calls act by left or right multiplication only reverses the word.
  That swaps `C_ab` and `C_ba`, and the proof uses both.

## Independent census

`verify.py` uses only the standard library. It builds the group as the eight
3x3 unitriangular binary matrices and imports nothing from PR1478, PR1573 or
PR1742.

| r | gates | radius-3 layers from I | states | meet with the k = 2 target ball |
|---|---:|---|---:|---:|
| 2 | 12 | 1, 12, 80, 472 | 565 | 0 |
| 3 | 56 | 1, 56, 1750, 45424 | 47,231 | 0 |
| 4 (opt-in `--r4`) | 240 | 1, 240, 32650, 3644000 | 3,676,891 | 0 |

An empty meet of the two radius-3 balls excludes every word of length 6 or
less. Odd lengths are excluded by PR1478's parity argument. Map to the
abelianization: for a rank-one idempotent, `det(I + tN) = 1 + t tr N`, which
is `[g]`, while the target determinant maps to 1. Both label counts must
therefore be even. So at r = 2, 3 and 4 the minimum is 8, matching PR1573
for `k = 2`. The r = 4 row is a direct finite check of the case PR1742
called open. It takes about 42 s and 1.3 GB of memory, so it is not in the
registered replay. As a control, the one-target endpoint (distance 4) must
produce a nonempty meet, and it does at every r. The direct 8-call word
`abab` on each data role is replayed, and each of its eight one-call
deletions is rejected.

## Reproduce

```sh
python3 -I -B research/ut3-central-commutator-index/verify.py        # about 13 s
python3 -I -B research/ut3-central-commutator-index/verify.py --r4   # about 42 s, 1.3 GB
python3.12 scripts/research_package.py --package research/ut3-central-commutator-index
```

Expected last line: `PASS_UT3_CENTRAL_COMMUTATOR_INDEX`. The verifier also
fails if the indexed open question disappears from
`research/bit-dihedral-commutator/README.md`. In that case this index should
be revised.

## Scope and limits

What is settled is the workspace-only route for these central targets. It
covers the two-letter alphabet, rank-one couplings (idempotent or nilpotent),
free scalar maps, and any number of restored dirty roles, all at exactly
2k calls per label (PR1573, PR1589). This rests on PR1573's written proof,
audited here by reading it. The finite checks corroborate its identities and
small cases; they do not replace the proof. This is not a proof-assistant
check or an independent human review. No PR is closed or dispositioned
here; that is a maintainer decision. PR1742's search remains a valid
corroborating replay.

## Open next questions

1. **A priced third address letter.** This is PR1573's own next question,
   restated so it can be found from the D8 side. With `c` itself callable at
   price `gamma`, the direct bill is `k*gamma`, against the proved
   `2k(alpha+beta)`. *Why it matters:* the workspace route is closed, so
   only a changed alphabet or contract can save calls here. *First step:*
   fully price one concrete implementation of a `c` call, with its frames and
   restoration, before any search. *Blocked by:* realizing that call in a
   supplier. Declaring it unit cost changes the model without showing a gain.

## Credit

The model, results and proofs belong to woklerx (PR1443), juper997 (PR1478),
steph4n-gh (PR1573), Arham Tahir (Discussion 1569, PR1589), bbMisk (PR1607)
and 1337isnot1337 (PR1742). The surrounding register-model lineage belongs to
eumemic (PR288), Ali Romman (PR468), David Govea (PR720), Gareth Davidson
(PR1333) and commdata2338 (PR1414). This note adds only the index, the audit
and a separately written census. Prepared for Josie Elliston (@JosieElliston)
with substantial Claude (Anthropic) assistance, in session 20 of a donated
overnight run. Apache-2.0.
