# k-dimensional port groups: the published decoders of PR2297 and PR2041 are not scalar decoders

**Scoped negative result (audit); no new κ.** It applies to two open coverage-law PRs, both by Cinna Davis
(`1337isnot1337`):
- [PR2297](https://github.com/CrocSwap/integer-mult-bounds/pull/2297): five-dimensional port groups, u=5.
- [PR2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041): three-dimensional port groups, u=3.

Each proves an exact F2 factorisation of the label-pairing matrix `B0_ij = q_i·q_j` and uses it as the decoder of
the k-unpaid endpoint:
- PR2297's PROOF.md calls the 112×112 identity exact "including every forbidden zero entry".
- PR2041's `verify.py` checks `q_i·q_j` as the "full 112x112 decoder identity".

Merged [PR1889](../paired-plane-scalar-mask-obstruction/README.md) (adamgall) showed this step invalid for PR1825's
paired planes. philippeVV then ruled that the masked identity, not `B0`, is the decoder target, for arbitrary label
subspaces (Discussion 1587,
[18927507](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18927507)).

What is new here is applying these k=2 results to the two later k-group PRs, with an exact source-pinned replay. The
results come from:
- PR1889's mask;
- ctoth's naive per-port decoder and masked-set term count;
- philippeVV's 2-integral floor.

## Result

**The required mask.** The contract is source `E_j → FULL`, target `0 → E_i^⊥`, where `E_i` is the span of the labels
in port `i`'s group. A cross-addition from source `j` into target `i` is rank-zero only when `E_j ≤ E_i^⊥`, that is,
the port spaces are orthogonal. A scalar decoder `K` (target ← source) therefore needs a common nonzero diagonal and
`K_ij = 0` on every other pair. Only orthogonal-group pairs may carry free entries.

| | PR2297 (k=5) | PR2041 (k=3) |
|---|---:|---:|
| cover | 22 five-frames + 1 pair | 37 three-frames + 1 line |
| published terms; charge in the PR's label-support pricing | 16; 118 | 11; 85 |
| same terms in port-space pricing | 144 | 99 |
| F2 identity Σ terms = B0 (positive control) | reproduced | reproduced |
| free ordered pairs under the group mask | **0** | 102 (72 between four three-frame pairs, 30 between the line and five three-frames) |
| literal lift: forbidden nonzero entries | 12,281 | 11,755 |
| of which parity-forced (B0 = 1) | 6,608 | 6,608 |
| literal lift diagonal values | {1,3,5,7,9} | {1,3,5,7} |
| dirty source columns failing (of 112) | 112 | 112 |
| rank of any valid scalar decoder | **≥ 112** (K diagonal) | ≥ 99 |
| 2-integral floor `rank_F2 blockdiag_i Gram(E_i) = Σ_i dim E_i` | **554** | **334** |
| zero-saving threshold: uniform u·w (the PRs' model) / exact (8/9)Σ dim E_i | 497.8 / 492.4 | 298.7 / 296.9 |
| incumbent-tie threshold (ceiling.py, children of rank 1–9) | 455–460 | 256–261 |

**Counterexample.** Take target port 0 (q=11) and source port 7 (q=21), with `q_0·q_7 = 1`.
- The literal coefficient is 1 in PR2297 and 3 in PR2041, using `K = Hᵀ` with the left factor as the source, as in
  PR2297's PROOF.md.
- The reverse orientation, which PR2297's own dirty test uses, gives 5 and 1.
- With source 7 equal to 1, every other source zero, and target 0 dirty at 11, the literal map returns 12 or 14.
  Every valid endpoint must return 11.
- The forbidden counts do not depend on the orientation.

PR2297's own dirty test passes only because it compares against `dirty ⊕ q_i·q_source`, which is the F2 `B0`, not
the masked scalar map.

### What the table means

1. **The published factorisations are correct over F2 but are not scalar decoders.** `B0` is 1 exactly on the 6,608
   label-incompatible ordered pairs, which a decoder must make zero. Every integral lift that reduces to the published
   factors leaves those entries odd, hence nonzero. Signs, even corrections and a common rescaling cannot fix them.
   The literal diagonal is also unequal.
2. **For k=5 there are no free entries at all.**
   - On F2^9, `dim E^⊥ = 9 − dim E`, so a five-dimensional `E_j` cannot lie in the four-dimensional `E_i^⊥`, in the
     same group or another. The residual pair's plane is not orthogonal to any group, including itself.
   - So K must be `c·I` on all 112 ports, which has rank 112. Any sum of rank-one scalar terms realising it has at
     least 112 terms, against the published 16. This is ctoth's masked-set count
     ([18916040](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18916040)).
   - For k=3, an exact maximum-weight clique of 33 pairwise non-orthogonal three-frames forces rank ≥ 99.
3. **No 2-integral decoder saves anything, in port-space pricing.** philippeVV's Theorem 1
   ([18927273](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18927273); a plane
   statement whose proof uses only the mask) carries over to k-groups:
   - Assume a decoder's terms have no even denominators and its normalisation `c` is odd.
   - Expand `K` by port spaces: `M_(i,α),(j,β) = K_ij · (e_iα·e_jβ)` over bases `e_iα` of `E_i`. Free blocks vanish
     because they are orthogonal, so for a valid decoder `M = c·blockdiag_i Gram(E_i)`. Each group is orthonormal, so
     `Gram = I` and `M mod 2` has F2 rank `Σ_i dim E_i`.
   - A rank-one term `c_t a_t b_tᵀ` contributes `c_t D_a G D_b`, where `G` is the full pairing matrix of the stacked
     bases. Mod 2 its rank is at most the pairing rank between the port spaces of its supports, which is its
     port-space charge.
   - By subadditivity, total charge ≥ 554 (k=5) or 334 (k=3), which is above both zero-saving thresholds.
   - The direct decoder attains this floor. It makes one per-port transfer `target_i += source_i`, whose frame
     distance is `dim T + dim S − 2 dim(T∩S) = k` for `T = E_i^⊥`, `S = FULL`. The lemma is icekylinx's,
     `notes/general-clifford-frames.tex`; see also `complex-frame-distance-seed80`.
   - Its exact deficit is `(8/9 − 1)·Σ_i dim E_i = −Σ_i dim E_i / 9`, whatever the cover. Every port carries 8/9 live
     families per call.

   So any saving needs a decoder with even-denominator (2-adic) gain above about 56–62 (k=5) or 35–37 (k=3). Tying the
   incumbent needs about 94 (k=5) or 73 (k=3). For comparison, the rebuilt line incumbent's gain is 48 (philippeVV).

**Why the incumbent line decoder is cheap.** Its centre (C=64) needs both of the following. A k=5 group mask removes
the first; the second is untested here.
- free entries on orthogonal-label pairs, which let it have low rank;
- the even normalisation `K_ii = 4`, which gives 2-adic cancellation
  (`complex-rank8-decoder-rigidity/PROOF.md`).

**Pricing conventions.** The published charges 118 and 85 use the PRs' label-support pricing, where a single-port
transfer is billed `q_i·q_i = 1`. In that pricing a per-port identity would cost 112 and would appear to save. For
k-dimensional ports that pricing undercharges, because the frame distance from FULL to `E_i^⊥` is `k`. ctoth priced
the naive plane decoder at 224 = 2 per port
([18914510](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510)), and open
[PR2203](https://github.com/CrocSwap/integer-mult-bounds/pull/2203) (jeremydiviney) prices native paired-plane
identity blocks at `Σ dim E_i`. All floors and thresholds above use port-space pricing; in it, the published terms
would cost 144 and 99.

**Consequence for the screens.** No k-port decoder is certified by:
- PR2297's charge 118, its "157 additional rank-one-equivalent units" and its favourable `a=1/99` screen. Its
  threshold of 275 was computed for its own rank shape.
- PR2041's charge 85. PR2041 already reports that its screen misses `a=1/99` and disclaims a physical realisation; the
  audit concerns only the validity of its charge-85 decoder.

## Scope

**Not disputed:** the binary linear algebra, the cover searches, and the local correction identities `C_E² = X_(⊕q)`.

**Not ruled out:**
- decoders with even-denominator (2-adic) gain; philippeVV's Smith lemma,
  [18932906](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18932906), is the
  framework for them;
- an operator- or block-valued interpretation with its own complete endpoint identity and charges, including a
  PR2126-style block identity priced by label support;
- another call contract.

**Caveats.**
- The term-count floor uses rank-one scalar terms.
- The 2-integral floor is the port-space-pricing statement above.
- The uniform-u thresholds follow the PRs' `ceiling.py` usage; they overstate the residual groups' unpaid
  coordinates, which favours the PRs. The exact figures are also given.
- The dirty test is of the finite scalar map, not of a native, hosted invocation.

## Reproduce

From the repository root, standard library only, about 7 s:

```sh
python3 -I -B research/kport-group-scalar-endpoint-audit/verify.py
```

Expected final line:
`PASS_KPORT_GROUP_SCALAR_ENDPOINT_AUDIT PR2297:forbidden=12281,parity=6608,rank>=112,floor=554 PR2041:forbidden=11755,parity=6608,rank>=99,floor=334`

**What the script checks.** The computed receipt must equal the committed `RESULT.json`; `--out` regenerates it. In
addition:
- the selected labels and `terminal_Y_translation == q`, from the archive member and payload hash used by PR1889;
- both vendored CANDIDATE.json files, by commit, git blob and sha256;
- every published term's support and label charge, recomputed;
- the `ceiling.py` pin and its "no positive saving" error, which must be exactly that error, plus a positive control
  just below `u·w`.

**Controls.**
- A positive fixture (identity diagonal, arbitrary entries on free pairs) is accepted with 0 failing dirty columns.
- Five negative controls are rejected:
  - the literal lift (112 failing columns);
  - `B0`;
  - a line-mask decoder;
  - a single forbidden entry (exactly 1 failing column);
  - an unequal diagonal.
- For PR2297 the positive fixture is the plain identity, because there are no free pairs.

All results were run on CPython 3.14.4. The registered Python 3.12 replay was not run locally.

## Coordination and overlap

- **Concurrent [PR2528](https://github.com/CrocSwap/integer-mult-bounds/pull/2528) (ywz65, 13:40Z)** audits a different
  PR2297 premise: the uniform five unpaid coordinates against the literal mixed cover (weighted unpaid dimension
  277/56), and lowers the overhead allowance from 157 to 152. It retains PR2297's binary factorisation as the decoder.
  This audit shows that factorisation is not a scalar decoder, so the corrected allowance also has no valid decoder
  behind it. Its weighted dimension agrees with the exact accounting here: `(8/9)·554 = 492.4`, and
  `554/112 = 277/56`.
- Neither PR had comments or reviews at the time of this audit.
- `find_overlap.py --task coverage-law-change` (refreshed cache: 720 open PRs, 1,208 discussion records, about 13:34Z
  on 2026-10-15) and reviews of Discussions 1587, 2024, 2278 and 2292 found no earlier audit of PR2297 or PR2041.

## Open next questions

- **Even-denominator gain for k=5.** Can a decoder with even-denominator gain above about 56 realise the diagonal
  rank-112 map under the k=5 mask? It needs about 94 to tie the incumbent. First step: apply philippeVV's 2-adic Smith
  lemma to a mask with no free entries. The top-layer lemma may force the gain to zero there.
- **Even-denominator gain for k=3.** Can even-denominator terms exploit PR2041's 102 free pairs for gain above about
  35, or about 73 to tie? Sharing on free pairs alone cannot help any 2-integral decoder.

## Credits and licence

- Cinna Davis (`1337isnot1337`): PR2297 and PR2041, the audited constructions, vendored unmodified; and PR1825, the
  predecessor construction that PR1889 audited.
- Adam Gall (`adamgall`): PR1889, the paired-plane scalar-mask argument.
- ctoth and collaborators (Discussion 1587): the plane-port endpoint, the naive per-port decoder and the masked-set
  term count.
- philippeVV: the masked-identity ruling, Theorem 1 (the 2-integral floor) and the Smith lemma (Discussion 1587), and
  the lever map (Discussion 2278).
- icekylinx: the frame-distance lemma (`notes/general-clifford-frames.tex`); woklerx: its independent check.
- jeremydiviney: PR2203's native block price.

Prepared by Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). Three adversarial
AI reviewers recomputed every count independently and found the attribution and pricing issues fixed in this
version. No independent human review is claimed. Apache-2.0.
