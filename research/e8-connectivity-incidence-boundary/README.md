# Connected frame subfamilies need not saturate diagonal incidence

**Exact finite counterexample to (G) ⇒ (D) for selected genuine E8 frame
subfamilies. No decoder, supplier, cost-floor or new κ claim.**

The [handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18914508)
asks whether two-point connectivity can replace eight diagonal-incidence rank
computations. The criterion in
https://github.com/CrocSwap/integer-mult-bounds/pull/1560 allows a chosen finite
family of live frames. Its application in
https://github.com/CrocSwap/integer-mult-bounds/pull/1616 uses **all** live frames.
These scopes must be distinguished: the general chosen-family implication is
false; the all-live-family implication remains open here.

## Explicit object and result

Generate the doubled E8 roots of squared length eight: vectors with two entries
±2 and the rest zero, or eight entries ±1 with an even number of negatives.
Choose the representative whose first nonzero entry is positive and sort
lexicographically, obtaining 120 root-line IDs. Set `G_ij = v_i·v_j/4`.
A frame is eight mutually orthogonal lines.

```text
FRAME0 = (0,1,6,11,20,29,106,119)
X      = (32,45,73,78,88)
F      = (2,5,8,9,30,41,108,117)
L      = {0,...,119} minus FRAME0 minus X       (107 live lines)
```

There are 2,025 frames in the full geometry and 877 wholly inside L. For each
pivot coordinate k in F, put
`I_k = {i in L minus F : G_ik != 0}`. Define q on the 51 entries of I₂ to be −1
on the following lines and +1 on the others:

```text
7,23,26,33,34,38,44,47,52,60,68,71,72,76,83,87,91,92,95,96,100,103,111
```

Select **every** live frame S for which `Σ_{i in S∩I₂} q_i = 0`. This defines
a family of 347 genuine frames, including F, without any RNG dependency in the
certificate. The bounded proposal search found it on its first vector.

For every unordered pivot pair k,ℓ, form the graph on `I_k∩I_ℓ`, with an edge
between i,j exactly when a selected frame intersects that vertex set in {i,j}.
**All 28 nonempty graphs are connected**, satisfying (G).

Let M[I_k] be the selected-frame incidence matrix. The seven vectors
`h_kℓ(i)=G_ik G_iℓ`, ℓ≠k, are independent and satisfy `M h_kℓ=0` exactly.
At k=2 the additional vector q lies in the kernel and is independent of all
seven. The ranks are:

| k | columns | selected rank | required (D) rank / full-family rank |
|---|---:|---:|---:|
| 2 | 51 | **43** | **44** |
| 5 | 49 | 42 | 42 |
| 8 | 49 | 42 | 42 |
| 9 | 49 | 42 | 42 |
| 30 | 48 | 41 | 41 |
| 41 | 50 | 43 | 43 |
| 108 | 50 | 43 | 43 |
| 117 | 50 | 43 | 43 |

## Why this is an exact counterexample

The direct integer kernel products give rational-rank upper bounds. Gaussian
elimination modulo the verified prime 1,000,003 gives lower bounds: a nonzero
minor modulo a prime is a nonzero integer minor. The bounds meet for every
reported rank. Modular rank is **not** treated as a stand-alone upper bound.
The augmented kernel matrix has modular rank eight, so q cannot be in the
seven-vector rational span. Thus `rank_Q M[I₂] = 43 < 51−7`, violating (D)
while (G) holds. The same bounds hold over any characteristic-zero field.

Selecting rows that annihilate a chosen extra vector is the mechanism; merely
sampling an unconditioned frame family need not expose it. This does not
construct nongauge factors or refute the predecessor's theorem, which assumes
(D) separately. Nonlinear projector equations could impose more constraints
than this incidence system; no claim about their solution set is made.

The complete 877-frame family satisfies all eight (D) identities. The omitted
frame `(3,4,7,10,30,41,108,117)` has q-sum **2**. Adding just this frame to the
347-family restores **all eight** required ranks. Zero added frames cannot
repair its deficit; this single-frame repair is attained, not a universal
repair theorem. Connectivity survives because adding edges cannot disconnect
the unchanged vertex sets. The certificate records this control explicitly.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -I -O -B research/e8-connectivity-incidence-boundary/verify.py
python3 -I -O -B research/e8-connectivity-incidence-boundary/test_verify.py
python3 scripts/research_package.py --package research/e8-connectivity-incidence-boundary --check-only
python3.12 scripts/research_package.py --package research/e8-connectivity-incidence-boundary
```

Expected verifier output:

```text
PASS_E8_CONNECTIVITY_INCIDENCE_BOUNDARY live=877 selected=347 graphs=28 rank=43 required=44 canonical_kernel=7 extra_kernel=1 full_family_control=PASS one_frame_repair=PASS
```

The checker independently regenerates roots, frames, graph edges, all kernel
identities and all reported ranks, then compares its deterministic receipt with
[CERTIFICATE.json](CERTIFICATE.json). It imports no predecessor checker and uses
no floating point. `--write` explicitly regenerates the result after the
mathematical checks. Replays otherwise do not change evidence files.
Two unittest groups exercise a positive optimized CLI and five rejection
controls: deleted pivot, invalid negative support, disconnected signs, false
rank and an omitted graph receipt. A pivot-only graph is also rejected inside
the verifier. Local replay takes about two seconds including these controls.

## Task, budget and provenance

Base `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920`; complex-mechanisms assignment;
OS nonce `0d6468a107c6f96e18bdef01e3e8f622`; original card
`complex-rank-shape-decoder`, scope key `02b31ebd160542c86299`.
[TASK.json](TASK.json) records the **changed** scope, exact object and stop rule.
This is a prerequisite-verification side result and does not meet the card's
physical construction acceptance gate. No replacement invoice or a<D/E budget
is claimed. Selected baseline bindings and the prescribed fixed-word ceiling
positive control were replayed; the selected frontier and frozen inputs are
unchanged. No full selected cold replay or full multiplication proof is claimed.

The initial and immediate refined-object overlap searches covered open PRs
(including drafts), discussion bodies/comments/replies, package notes and the
local ledger. The nearest work supplies the criterion and the open question;
it does not supply this selected-family extra-kernel witness. The claim is at
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18915387.
Exact repository reference pins and historical selected/catalogue provenance
are in [SOURCES.json](SOURCES.json); those reference files are not executed.
The pending source heads and claim are recorded in [TASK.json](TASK.json).

## Open next questions

**Does (G) imply (D) for the family of every frame inside L?** This is the
original question relevant to removing ranks from deeper-puncture replay.
A feasible first step is to use full-frame closure to rule out extra incidence
kernel vectors; the explicit one-frame repair here is a small test case.
The blocker is a missing universal closure-to-rank argument. This certificate
does not answer that question or discharge any later rigidity or supplier
obligation. Structured next-question fields are in [TASK.json](TASK.json).

## Credit and license

Andrey Mas / an664 supplied (D), (G), the chosen-family formulation and the
P107 fixture in https://github.com/CrocSwap/integer-mult-bounds/pull/1560,
head `eb9f6f15f15704949cbd25ca8fbf58063084dd8e`. Josie Elliston supplied the
connectivity-versus-rank question and exact modular-rank methodology in
https://github.com/CrocSwap/integer-mult-bounds/pull/1616,
head `7b3e4624e31647fc2a8b777a181823739b12b36e`.
The underlying decoder/rigidity lineage includes Brett Halligan / burntout76 /
Ninefold (https://github.com/CrocSwap/integer-mult-bounds/pull/1212),
DreamingOfClouds (https://github.com/CrocSwap/integer-mult-bounds/pull/717) and
themilkman216 (https://github.com/CrocSwap/integer-mult-bounds/pull/968).
Their packages are not modified or copied.

Prepared by Aaron Wang / navinor, with help from chatgpt, including a separate
read-only AI review. No independent human or proof-assistant review is claimed.
Apache-2.0.
