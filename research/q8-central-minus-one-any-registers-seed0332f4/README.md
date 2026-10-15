# The Q8 central-minus-one mixed triples need four calls at every finite width

**Uniform group-algebra lower bound; no new kappa.** In the formal algebra
`F2[Q8]`, let the first three diagonal targets contain exactly one `[-1]`
entry and two entries independently chosen from `{[i],[j]}`. At every total
register width `r >= 3`, all remaining `r-3` arbitrary dirty scalar roles must
return to identity.
With paid labels `{i,j}` and every binary rank-one idempotent on all `r` roles,
the exact minimum is **four** calls.

The direct construction costs `2 + 1 + 1`: two `i` calls implement `-1=i^2`,
and one call implements each generator target. The new result is a uniform
lower bound for the twelve central-`-1` target tuples, independent of how many
dirty identity-target roles are appended. It extends the `r=3,4` exact-search
coverage in [Q8 PR #1925](https://github.com/CrocSwap/integer-mult-bounds/pull/1925);
it is an algebraic proof, not a larger finite search.
The other 24 `k/-k` tuples were already handled for every finite `r>=3` by
that predecessor's first-order quotient bound and are outside this note's new
claim.

## Exact model

Write

```text
Q8 = {±1, ±i, ±j, ±k},    i^2 = j^2 = -1,    ij = k,    ji = -k.
```

The coefficient ring is the full formal group algebra `R=F2[Q8]`. A paid
factor is

```text
D_N(g) = I + ([g] + [1]) N,    g in {i,j},
```

where `N=uv^T`, `u,v in F2^r`, and `v^T u=1`. Thus `N` has rank one,
`N^2=N`, and `tr(N)=1` in `F2`. Free scalar basis changes do not enlarge the
factor alphabet because conjugation preserves the set of all rank-one
idempotents. Every input coordinate is arbitrary; the extra identity-target
roles are restored, not initialized clean.

## Uniform lower bound

Let `J` be the augmentation ideal of `R`, and set

```text
x = [i]+[1],    y = [j]+[1],    z = [-1]+[1].
```

The abelianization of `Q8` is `C2 x C2`, so `J/J^2` has basis `x,y`; the
central element is zero in this first-order quotient. In the full group
algebra the exact identities are

```text
x^2 = y^2 = z,    z^2 = 0.
```

Suppose a word has `q_i` factors labelled `i`, `q_j` labelled `j`, and
`k=q_i+q_j` total calls. Its two coefficient matrices in `J/J^2` are

```text
A = sum of N over the i-labelled calls,
B = sum of N over the j-labelled calls.
```

Products of two augmentation terms vanish modulo `J^2`, so these are exactly
the linear coefficients of the word. For the target, `A` is the diagonal
projection onto the `i` target slots and `B` onto the `j` target slots. Let
their counts be `n_i,n_j`, with `n_i+n_j=2`. Taking traces gives

```text
tr(A)+tr(B) = n_i+n_j = 0 in F2,
tr(A)+tr(B) = q_i+q_j = k in F2.
```

Therefore every realizing word has even length. A word of length at most
three could only have length zero or two. Length zero has the wrong nonzero
linear coefficients, so consider two calls.

* If both calls are labelled `i`, the target's `j` coefficient is zero, so
  `n_j=0` and `n_i=2`. The first-order equation is
  `N1+N2=P`, where `P` is the rank-two coordinate projection onto the two
  `i` target slots. Since `P^2=P`, `P=N1+N2`, and `N1^2=N1`, `N2^2=N2`,
  expanding gives `N1N2=N2N1`. Also `rank(P)=rank(N1)+rank(N2)=2`, so their one-dimensional
  images are distinct and have zero intersection. The common product has
  image in that intersection, hence `N1N2=N2N1=0`. The exact two-factor word
  is then `I+xP`; it has no `z` coefficient at the third, central-`-1` slot.
* If both calls are labelled `j`, the same argument gives `I+yP` and again
  no central coefficient.
* If one call has each label, the first-order equations force the two
  idempotents to equal the coordinate projections `E_p` and `E_q` for the
  distinct `i` and `j` target slots. Hence both ordered products are zero.
  The exact word is `I+xE_p+yE_q`, with no central coefficient.

In each two-call case the target needs the nonzero term `zE_c` at its central
slot `c`; the candidate has none. Thus length two is impossible. This uses
the exact second-order central term and the rank-one idempotent constraint,
not just a first-order rank count. Together with parity, no word of at most
three calls exists. The direct four-call word proves the exact minimum for
every finite `r>=3`.

The proof is uniform in `r`: it uses only ranks of the two coefficient
matrices, the identity `P=E_p+E_q`, and intersections of two one-dimensional
images. Extra dirty roles may appear in `N1,N2`; the rank and image argument
still applies on the full `r`-space.

## Exact controls

The package verifier uses an eight-element formal Q8 table, not a finite
address representation. It checks `J/J^2` has dimension two, `J^2` has
dimension five, `x,y` give the stated basis, and `z` lies in `J^2`. It
enumerates all 28 rank-one idempotents at `r=3` and all 120 at `r=4`.
For every pair of these idempotents whose sum is any rank-two coordinate
projection, it confirms both ordered products vanish. It replays all twelve
four-call targets at both widths (24 exact full group-algebra products) and
checks omitted-call, wrong-target and non-idempotent controls.

These bounded controls support the proof but do not replace the all-`r`
argument. The lower bound itself covers arbitrary finite `r>=3`; it does not
claim a physical bit-supplier implementation.

## Complete cost and frontier relevance

| Item | Cost in this formal model |
|---|---:|
| Direct `-1` target | 2 paid calls |
| Other two generator targets | 1 call each |
| Direct complete word | **4 calls** |
| Hypothetical three-call target | 3 calls (25% saving) |
| Extra identity-target roles | arbitrary finite `r-3`; arbitrary dirt is included in all allowed idempotents |
| Frames / copies / helpers / restoration / hosting / precision | outside the formal model; all zero here |

This is a structural lower bound on a finite group-algebra relaxation, not a
construction for the selected integer-multiplication supplier. The selected
record remains conditional and the complex-side moment remains binding; no
selected profile or `kappa` changes.

## Reproduce

From the repository root, with standard-library Python 3.10 or later:

```sh
python3 -I -B research/q8-central-minus-one-any-registers-seed0332f4/verify.py
python3 -I -O -B research/q8-central-minus-one-any-registers-seed0332f4/test_package.py
python3 scripts/research_package.py --package research/q8-central-minus-one-any-registers-seed0332f4 --check-only
```

Expected verifier marker:

```text
PASS_Q8_CENTRAL_MINUS_ONE_ANY_R q8=8 dim_J_over_J2=2 idempotents=28,120 pair_checks=54 direct=24 controls=3 exact_min=4 no_new_kappa
```

`SOURCES.json` pins the selected record/review/assembly and the exact Q8
predecessor files at base `c676548106012571fefa1dce0ec16f1bcfe11dce`. The
selected cold replay was not repeated because this work changes no selected
source or assembly input.

## Overlap and attribution

The pre-claim scan at 2026-10-14 17:42 UTC covered 359 open PRs and 670
Discussion records with complete pagination and no warnings; it is retained
as `OVERLAP-CLAIM.json`. The final pre-submission refresh at 18:02 UTC covered
367 open PRs and 682 Discussion records, also with complete pagination and no
warnings. Its body search returned 207 possible matches and saved the top 100.
The exact Q8 predecessor is PR #1925; [Q8 PR #1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822)
studies a different two-role repeated central-commutator target. Recent S3,
order-21 and binary-tetrahedral claims use different groups or target tuples.
The refreshed discussion snapshot includes this cycle's claim and finding;
no competing claim on these twelve central-`-1` tuples was found. See
`OVERLAP.json` for the refresh and `OVERLAP-CLAIM.json` for the claim-time
snapshot. The claim is Discussion #2034.

Upstream `main` at submission was `fcea6916f3af98346ff13581ac7626718b7e55a2`.
Its selected-record SHA-256 and task-catalogue SHA-256 are unchanged from this
cycle's pinned base `c676548106012571fefa1dce0ec16f1bcfe11dce`; the recorded
research base remains the exact commit above.

The exact predecessor heads are PR #1925 `009ed860f34ed5d7b0d626098ce93c4c2a7eb4df`
(merged as `1ff5f7bc448445516944f10c8e7834db371103aa`) and PR #1822
`ee736b4b11bbd63b04d94c8edafb3790161ebdea` (merged as
`cad44bb9eb8f71edf3a0421f169ef168eb1a1ccd`). Their source files are also
blob-pinned in `SOURCES.json` at this cycle's base.

Credit Cinna Davis / Q8 PR #1925 for the finite-width target family and
uniform treatment of its other 24 tuples; credit Navinor / PR #1822 for the
Q8 group-algebra lineage and the distinct two-role target. Prepared for
@ToikY with substantial OpenAI Codex assistance in proof derivation,
implementation, controls and writing. No independent human review or
proof-assistant formalization is claimed. Apache-2.0.

## Open next questions

Does the trace-plus-central-coefficient mechanism extend to a different
finite 2-group and a target tuple whose central correction also first appears
at augmentation degree two? Any follow-up needs a fresh group alphabet,
optimistic call bill, and live overlap check; this result alone supplies no
physical supplier transfer.
