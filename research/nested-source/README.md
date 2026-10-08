# Nested controlled bases and full residual batching: a conditional 2^-20 improvement

The exact conditional witness is

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{9799}{10^{10}}=9.799\times10^{-7}>2^{-20}.}
\]

The saving is about **7.92% larger than the subsequently inspected PR #14** (`90799/10^11`) and **27.28% larger than PR #13** (`7699/10^10`) and **2.75% above 2^-20**. This is an asymptotic exponent comparison, not a practical runtime claim or linear-time multiplication.

This branch is based on main `6e564879f51ae16f23d392e9e196c605f36d90df`. It retains PR #13 at `3ef246fa4f69c87ebfed78376418afa9ffcad145`, including PR #10 and its dependencies. The complete `research/` sources from PR #12 at `35d31e30f28bc5da0ae6a88e7b03d75ebc855534` supply the credited dimension checker and star rules. The new contribution is this directory, `notes/nested-bit.tex`, `notes/nested-complex.tex`, and the independent complete `patches/nested-source.patch`.

## Construction and proof

Use the ternary five-subset network of Zhihao Chen's PR #7 at **h=32**, with the fully rebuilt producer from Rohan Arun's PRs #9/#11/#12. Its exact auxiliary count is **25,224,960**, comprising 23,210,704 additions and 2,014,256 output uses. All 201,376 neighbor images are checked. The source-span argument gives center dimension 30 and deficit fraction `113/203`.

Apply eumemic's PR #13 auxiliary source-frame translation: a stage-two auxiliary starts at `P_D0` and ends at `I+P_D0`. The entrance disappears while the exit has rank `m-h`. The endpoint difference remains the identity, and arbitrary dirty logical auxiliaries are restored by the same scalar circuit.

Our **nested controlled basis** restricts PR #10's common basis one more level. It keeps the required nonzero corners of every relevant projector while making the new auxiliary-exit corner diagonal. Separate rational witnesses show that every required determinant polynomial is nonzero within this restricted parameter family. Their finite product supplies one simultaneous rational basis, including dual orientations. The proof provides terminating fixed-parameter enumeration; finite-field samples do not substitute for this existence argument.

The new bit pivot profiles at `m=32768`, `H=1024` are:

| Edge class | Singleton children | Contiguous child widths |
|---|---:|---|
| Shared stage-one/three auxiliary join | 64 | 32640 |
| Reframed stage-two auxiliary exit | 0 | 32, 32704 |
| Stage-two data entrance | 63 | 898 |
| Stage-three data entrance | 93 | 962, 30658 |

Every unspecified rank unit retains the singleton compiler. The exact moment certifies

\[
a_b=49/25000000=1.96\times10^{-6}>2^{-19}
\]

with strict gap greater than `3e-10`.

The complex network remains the **h=28** PR #7 producer. We enumerate its full physical edge-rank histogram in both orientations and batch **every nonzero residual** using PR #10's signed whole-residual identity. All residuals are proper; the maximum rank is 21896 below `m_c=21952`. The exact moment certifies `a_c=4e-6`, with gap greater than `1.83e-8`.

A new guard covers the whole child list: every arithmetic dependency path has total rank at most `m_c+6h=22120`, and every child rank is at most 21896. Convexity at `rho=3/2` gives a path moment below `0.99731 < 999/1000`. This yields `C1=3749/2500` at beta=1/1000 and zeta=1/10000. It does not assume the old two-class guard applies unchanged.

The complete proofs are [nested-bit.tex](../../notes/nested-bit.tex) and [nested-complex.tex](../../notes/nested-complex.tex). The manuscript patch preserves the prior results, adds named interfaces for this construction, and redirects all current transform, resampling and assembly consumers to them. Bit arity 32768 and complex arity 21952 remain distinct.

## Exact assembly

| Parameter | Rational value |
|---|---:|
| tau | 1 − 49/25000000 |
| sigma | 1 − 1/250000 |
| epsilon | 499999/1000000 |
| c | 1 |
| beta | 1/1000 |
| delta | 1/10^10 |
| C1 | 3749/2500 |
| lambda | tau + 1/10^16 |
| lambda-prime | tau + 2/10^16 |
| kappa | 9799/10^10 |

All **29 strict constraints and seven final margins** pass exact rational arithmetic. The minimum margin is `4899990199500001/5000000000000000000000`, with strict absorption gap `490199500001/5000000000000000000000` above kappa. The corrected Gaussian enclosure of PR #10 is unchanged.

## Reproduction and validation

From the repository root, using Python 3.11+, C++17, Git and Make:

```sh
python3 research/nested-source/producer.py
python3 research/nested-source/verify.py --full
python3 research/nested-source/make_patch.py --materialize build/nested-manuscript
make verify
```

The h32 support rebuild uses several GB of memory and exact support keys, never fingerprints. `producer.py --reuse-screen` reuses a previously regenerated `build/geometric-dimensions/32/result.json` and independently rechecks all selected templates. The complete source rebuild is required when those inputs have not just been regenerated.

Checks completed for this contribution:

- Two complete h32 support passes, all **35,960** star boundaries and **561** selected templates, exact output maps and disjoint additions.
- **220,673 basis directions per orientation** through the selected reversible templates, including arbitrary dirty scratch and actual compiled support-frame paths.
- Every one of **201,376** neighbor images, all 496 central spaces, and **446,400** exact central Gram entries.
- Four joint nested bases over a finite field, covering **32 complete physical pivot profiles** across A1/A3/A4/data and their duals; two deliberately degenerate basis choices correctly rejected.
- The h28 complex map, binary labels, local physical-role schedules in both directions, all tensor boundary classes, 16 dirty-scratch controls at h8/h10, and **1,087,080** mixed-sign matrix entries.
- Exact positive-series logarithm enclosures, both mixed-width moments, the new path guard and final assembly; exaggerated savings, inflated role counts and the unsupported 2^-19 headline are rejected.
- The retained PR #13 suite: **172 tests and 19 patch checks**, with exact regeneration. Five new integration tests also pass, including duplicate-label and stale-consumer negative controls. The combined suite passes all 177 tests. The complete 126-page manuscript compiles with pdfLaTeX/BibTeX without undefined or duplicate references; see [the PDF](../../artifacts/nested-source-20-manuscript.pdf).

These checks support the written result. The pinned upstream multiplication theorem, its finite-tape primitives and analytic interfaces, and the written predecessor proofs remain conditional dependencies. This is not formal verification or external mathematical review. Claims about all physical interfaces use the general proofs together with the explicitly described finite controls; no enumeration of every address of the enormous tensor network is claimed.

## Attribution

**Zhihao Chen (jacklightChen)** contributed the new nested simultaneous basis, contiguous data/corner refinements, full complex residual accounting and guard, and their assembled witness, with substantial **OpenAI Codex assistance**. The earlier PR #7 GPT-6 Astra assistance attribution is retained as recorded; this does not assert this continuation's runtime model identity.

This result builds on Zhihao Chen's ternary network and paired producers (PR #7); icekylinx's controlled batching, arbitrary-width rows, path framework and Gaussian correction (PR #10); eumemic's auxiliary source-frame translation (PR #13, with Claude assistance); and Rohan Arun's dimension checker and star refinements (PRs #9/#11/#12, with OpenAI Codex assistance). Douglas Colkitt, Bortlesboat, dleen, eumemic, the original OpenAI manuscript, and all existing notices remain credited.

Future research using this construction or the ternary network should explicitly acknowledge **Zhihao Chen (jacklightChen)** and cite the relevant contribution, while also crediting the other dependencies used. This acknowledgment request adds no license restriction. No worldwide priority is asserted; the specific new contribution is identified relative to the pinned repository and PR state.

### Concurrent data-corner work

Before publication we inspected Rohan Arun's [PR #14](https://github.com/CrocSwap/integer-mult-bounds/pull/14), commit `1fa5b9a9aaccbebb3eb29ac7ea55811f46464eee`. It independently combines the same two types of data-corner improvement with h30 and source frames, reaching `90799/10^11`, below 2^-20. We do not claim exclusive priority for those overlapping lemmas. This submission's distinguishing additions are the **nested** common basis batching the translated auxiliary exit's h-wide corner, the complete complex residual list with its new guard, and the fully checked h32 composition exceeding 2^-20. PR #14 was inspected after these local proofs had been written; none of its source files are imported.

### Final publication check: PR #15

The final upstream check found eumemic's [PR #15](https://github.com/CrocSwap/integer-mult-bounds/pull/15), commit `a17cab396ce1c79c288bde9d06002cefdc0af8e6`, with the higher stated saving `1076678/10^12`. It independently uses full complex residual batching and rho=3/2 together with a smaller h30 producer. Consequently this PR claims neither the repository's best numerical saving nor the first publication exceeding 2^-20, and no exclusive priority for full complex batching. The distinct nested simultaneous basis can be reviewed and potentially combined with that producer; such a combination has not been verified here. The author requested publication of this already verified result before continuing toward 2^-19. No PR #15 source files are imported.
