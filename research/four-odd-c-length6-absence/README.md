# Integral four-odd-c labels miss length-6 support

**Proof for integral labels. No new κ and no word.**

In the PR2085/2112 register model, no six nonzero integral rank-one labels
sum to `4I`, meet target support, and have at least four labels of odd `c`.
For every pair of distinct old projectors, the length-6 equation

```
R + S + T + U = 4I - E - F
```

therefore has no integral solution that meets support and has at least four
odd-`c` labels. The argument is written in [PROOF.md](PROOF.md).

The PR #7100 witness `A, B, P, Q, 2A, 2B` still meets support, with odd-`c`
count exactly two. Count four is the next even value. This package does not
classify the count-two solutions. Odd `c` means the integer coordinate of
`P` is odd. A rational label with a non-integral coordinate is outside the
theorem.

Selected κ stays `363005817/100000000000`.

## Scope and evidence

Original card: `bit-new-register-model`, with `scope_status: changed`. The
card asks for a larger or nonabelian native alphabet. This package stays in
the abelian symmetric 2-by-2 model and answers the integral half of open
question 1 in PR #7100. It does not redo the #7100 witness, the length-5
one-old proof, or the zero-old four-call proof.

Evidence classes, kept apart:

1. **Proof, by a finite pair census plus a case split.** Lemmas 1–4 and
   Section 5 of [PROOF.md](PROOF.md) cover every integral six-label multiset
   with odd-`c` count 4 or 6. The pair step enumerates `b ∈ {-4,...,4}` for
   nine goals. For `|b| ≥ 5` the discriminant is negative because
   `f(n) = |A2|n^2 - |A1|n - |A0|` satisfies `f(5) > 0` and
   `f(n+1)-f(n) = |A2|(2n+1)-|A1| ≥ 11|A2|-|A1| > 0`. That bound is the
   completeness argument for the census. The case split then uses only the
   parity of `a+b` and `c`.
2. **Boundary witness, not a new construction.** The six #7100 labels meet
   support and have odd-`c` count 2. Shifting `2A` by `A` breaks the sum.
   The checker does not repeat that package's six old-pair scans.
3. **Bounded control.** Every sum-correct quadruple of max norm 4, over
   every old pair, was scanned. More than 200 quadruples occur. Support
   occurs at odd-`c` count 2 and does not occur at count 4 or 6. This box
   is not a census of larger frames.

The determinant identity, the subset-sum necessity, and the
call-versus-target inequality are inherited from
`research/bit-two-signed-frame-floor` and are not reproved. Predecessor
replays, Lean, Docker, and the selected-result cold replay were not run.
No rational search is claimed, successful or otherwise.

Source commits, Git blobs, and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance. Full Git history
is needed to resolve those pins.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 scripts/research_package.py --package research/four-odd-c-length6-absence --check-only
python3.12 scripts/research_package.py --package research/four-odd-c-length6-absence
```

The direct check is `python3 -I -W error -B research/four-odd-c-length6-absence/verify.py`.

## Open next questions

Does any pair of nonzero rational rank-one frames, not both integral, sum to
`4I-H` for a target `H`? The pair census is integral. A rational complement
pair would allow a size-4 carrier. The first step is one rational solution
of `X+Y = 4I-(A+P)`, or a discriminant obstruction over `Q`.

Does `R+S+T+U = 4I-E-F` have a non-integral rational support solution on
which the inherited lattice character detects at least four calls? The
integral odd-`c` count is empty, so a length-6 word would have to leave
`Z^3`. The first step is one rational support solution with a denominator
greater than 1, then the subset scan and the character on its lattice.

## Credit

The register model is Cinna Davis's PR2085/2112 formal model. The determinant,
the subset-sum necessity, and the call-versus-target inequality are the
PR2910 package as recorded in apoursh's two-signed-frame floor, PR #6190.
The four-call support proof is PR #6952. The one-old length-5 proof is
PR #7083. The length-6 support witness with odd-`c` count two, whose open
question this note answers for integral labels, is PR #7100. None of those
arguments is redone here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review. New work is Apache-2.0.
