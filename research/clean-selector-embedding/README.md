# Sharp clean encoding width for independent tensor lanes

**Scoped algebraic interface and unfavorable inherited-budget result; no new κ.**

For `q=2^s` independent same-direction `C_n` lanes, an exact injective encoding
into one `i^u C_d` child exists precisely when its four eigenspace multiplicities
dominate the lane multiplicities. For every `n,s>=1` and each allowed phase, the
least native width is **`n+s+1` or `n+s+2`**, decided by four integer inequalities.
[PROOF.md](PROOF.md) gives the all-size argument and an explicit dyadic Walsh
encoding; the finite checker is separate evidence.

This minimum is for the literal host `C_d` with no extra variable spectator
factor. Common spectator fibers extend the result only by `E tensor I`, with
the same fibers separate from the encoding. Reassigning them changes the
contract; neither the minimum width nor the budget formula below covers that
model. PROOF.md gives an unchanged-volume width-one example and a distinct
twofold-volume width-two example. This is not a minimum supplier recursive-rank
theorem.

The sharp closed formula, with `N=n+s`, is:

| Convention | Least d |
| --- | --- |
| Exact phase, `n>=3` | `N+1` |
| Exact phase, `n=2` and `s mod 8` in `{0,1,5,6,7}` | `N+1` |
| Exact phase, `n=1` and `s mod 8` in `{0,6,7}` | `N+1` |
| Other exact-phase cases | `N+2` |
| Any fourth-root global phase allowed | `N+1` |

Pascal averaging and the eight-residue character signs prove this for every
positive `n,s`; finite enumeration corroborates the formula separately.

The motivating 16-lane, width-one target has multiplicities `(16,16,0,0)`:

| Native width | Multiplicities of C_d | Exact phase | Optional phase |
| --- | --- | --- | --- |
| 5 | `(6,6,10,10)` | fails | every phase fails |
| 6 | `(16,12,16,20)` | fails | `-C_6` passes |
| 7 | `(36,28,28,36)` | passes | passes |

Thus the exact-phase encoding uses 128 ambient coordinates for 32 active
coordinates; allowing a global minus sign reduces it to 64. A phase is an
explicit interface choice, not an ignored equality up to phase.

The input may be arbitrary and correlated within the encoded subspace. Its
complement must be zero. An invertible extension of the encoder returns that
zero complement to zero, but generally rotates **dirty** complement coordinates
by fourth-root phases. This does not provide an arbitrary-dirty workspace
replacement for a selected child.

Under the predecessor's full-array cost expression `A V d^sigma`, `0<sigma<1`,
one encoded child alone costs relative to the `q` lanes

```text
2^(d-n-s) * (d/n)^sigma > 2.
```

This waives encoding, decoding, initialization, routing, phase application,
restoration and precision costs. Nonnegative extra charges cannot rescue this
particular comparison. These are available upper-bound expressions; this is
not a lower bound on optimal runtime or a universal obstruction to other
algorithms. Scaling a data width to `n*f` requires recomputing the literal
dimension; the finite `C_7` example is not automatically a `C_(7f)` interface.

## Reproduction and evidence

```sh
python3.12 -I -B research/clean-selector-embedding/verify.py
python3.12 -B scripts/research_package.py --package research/clean-selector-embedding
```

Expected `PASS_CLEAN_SELECTOR_EMBEDDING`, followed by the registered-package
marker. Standard library only. The verifier reads its committed certificate;
`--output /new/path.json` creates an exclusively new receipt.

- Independent integer binomial and roots-of-unity character counts agree at
  all 131 widths `0..130`.
- All 4,096 `(n,s)` pairs in `1..64` check fixed and optional phase boundaries,
  exclusion at equal volume, and the uniform two-extra-bit upper endpoint.
- Twelve complete fixtures, including both 16-lane phase conventions, compare
  every entry of `i^u C_d E` and `E (I_q tensor C_n)` by literal Gaussian-dyadic
  butterflies. Exact Gram identities give a left inverse of each encoding.
- Seven controls reject insufficient eigenspace capacity, duplicate labels,
  an unbilled phase, zero payload width, absence of batching, unrestored dirty
  complement, and admission from a constant-vector smoke test.

These linear identities cover arbitrary complex coefficients on the declared
subspace. No existing supplier word, physical route or production precision
schedule is executed by these fixtures. Local replay details and external
source-byte pins are recorded in `VALIDATION.json` and `PREDECESSORS.json`.

## Task and overlap

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; fresh OS nonce
`9a396c07a6d107acdb9a76567c1010d0`; revision 3 complex-mechanisms /
complex-rank-shape-decoder. Selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Baseline bindings, assigned ceiling positive control and lever table were
replayed before the detour.

The initial full-space reciprocal-basis idea overlapped Arham Tahir's fresh
[Discussion1901](https://github.com/CrocSwap/integer-mult-bounds/discussions/1901).
Before implementation, one pivot changed the premise to a clean invariant
subspace. The exact claim and completed handoff are in that Discussion. The
card's physical construction and 5% gain acceptance gate is **not met**.

PR665 already states the generic multiplicity criterion and builds a spectral
encoder for a different two-host split. This contribution specializes that
credited method to one `C_d` host for repeated equal-width lanes and supplies
the sharp native width, explicit phase distinction and full-volume screen.
It does not claim priority for spectral encoding or for Arham's full-space
trace obstruction. PR679 and Ross Richardson's subsequent audit concern the
monomial arbitrary-dirty contract; their conclusions remain credited.

Initial overlap covered 554 open PR titles/bodies, local notes and relevant
live Discussions. Numbered REST pages are non-atomic; no complete Discussion
census or novelty certificate is claimed. The pre-submission refresh at
13:54–13:55 UTC covered 573 open PR bodies and 873 local notes. Arham's newly
published [PR1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920),
head `057b214aea45c65926b93ad8b95693c80f0f79c9`, explicitly excludes the
parallel clean-injective premise. Frozen sources and the selected frontier
remain unchanged.

## Open next questions

- Can a different recursion algorithm price an encoded host by its reachable
  subspace? First give a uniform implementation and complete volume/workspace
  invoice; the current full-array bound does not permit that discount.
- Can a selected caller supply the clean invariant space and a legal encoder?
  First identify one exact source-bound call and prove its entry state belongs
  to the subspace; no selected occurrence or compiler is provided here.
- Can nonreciprocal adapters or a different child alphabet change the budget?
  First name the changed endpoint and charge both adapters and dirty restoration.
  The current statement covers an injective invariant encoding only.

## Credit and limits

Douglas R. Colkitt's PR665 supplies the spectral-capacity/Walsh method. Greer
Guthrie's PR679 supplies the kernel, monomial support obstruction, dirty padding
and volume warning. Arham Tahir's Discussion1901 supplies the parallel
full-space trace obstruction; his PR1605 supplies the rank-shape budget context.
Ross Richardson's `8a3900c84213fd7603b99beaceaff48f501b4232` audit identifies
the direct-sum/tensor gap and clean-encoding next question. Credit Jose Manuel
(jmbarrancoml), publishing account Cinna Davis (1337isnot1337)/PR1779, Josie
Elliston/PR1817, icekylinx's exact kernel and the Rohan Arun, Jeremy Kothe,
Hao Yan and retained selected construction lineage.

New specialization/checker by ToikY with substantial OpenAI Codex assistance
and bounded proof/review agents. Apache-2.0. No full selected cold replay,
physical/native admission, all-size tape compiler, production precision,
analytic transfer, Lean multiplication theorem, hosted CI pass or independent
human approval is claimed.
