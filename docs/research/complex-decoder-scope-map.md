# Which retained complex E8 decoder bound applies?

Use this map before reopening a decoder search. The bounds below cover different
algebraic classes. Changing a coefficient field or adding a term does not by itself
leave every retained obstruction. A masked identity is outside the all-pairs
theorems, but the [retained rank-eight results](#masked-exactness-the-retained-rank-eight-boundary)
below cover specific masked classes. Check [live overlap](../../autoresearch.md#1-orient-briefly-then-choose-a-distinct-task)
before calling a class outside these hypotheses an open problem.

For the fixed paired-plane masked endpoint, use the
[paired-plane contract map](paired-plane-contract-map.md) to distinguish binary
label identities, scalar/vector fitting rank and native payload costs.

## Shared model and the three boundaries

The roots have squared norm two. If `R` contains the live E8 root-line
representatives, the decoder identity is `D T^transpose = 2 R R^transpose`.
Transpose is ordinary transpose, including over the complex numbers. Each term
costs the **binary rank** of the label pairing between its two nonzero supports,
with pairing `(<r_i,r_j> + 1) mod 2`. The copied-information charge is the sum
of these separate term costs; it is not the number of terms or their scalar rank.

| Retained result | Required hypotheses | Conclusion and boundary |
| --- | --- | --- |
| [PR968 proof](../../research/complex-frame-pair-decoders/PROOF.md), themilkman216 | Exactly eight terms; arbitrary **real** factors; equality on **every** live pair; any puncture of `p <= 24` out of 120 root lines | Cost at least `max(72-p,56)`. The best cost/port ratio in this class is `7/13`, attained at `p=16`. This does not exclude masked identities or nine-term decoders. |
| [PR1077 proof](../../research/complex-decoder-field-extension-seed44/PROOF.md), woklerx | The same eight-term, all-pairs, `p <= 24` model, now with arbitrary **complex** factors and ordinary transpose | The same floor. Complex isotropic normals invalidate a verbatim reuse of the real cross-term nonparallel argument; the extension proves the restricted nonisotropy needed for the count. Complex coefficients alone do not escape this floor. |
| [PR845 proof](../../research/p112-single-lift/PROOF.md#model-and-result), Mihir Srivastava | The specific frame-punctured P112; **real** coefficients; all-pairs identity; the original eight coordinate reader columns retained up to nonzero rescaling, plus one arbitrary source total (or the transposed family) | Cost at least **64**, even when the new source is outside the coordinate column space. This excludes this fixed-reader ninth-term mechanism, not arbitrary nine-term decoders, complex coefficients, changed readers, several additional totals or masked completions. |

For PR968/1077, attainment is **over the choice of puncture and decoder** at
each size. It does not promise an attaining decoder for every puncture of that
size. Their geometric argument retains the stated real E8 hyperplane-flat
classification premise (F6); the finite checks do not newly prove that theorem.

PR845's exact normal form is useful for recognizing overlap. With coordinate
matrix `X`, reader columns `x_j`, `a in R^8` and arbitrary `z in R^112`, it is

```text
X X^transpose = sum_j x_j (x_j - a_j z)^transpose + (Xa) z^transpose.
```

Every exact nine-term factorization retaining those eight reader columns fits
this family. A ninth term or an asymmetric source alone therefore does not
escape PR845. Allowing reader changes leaves PR845's scope, but does not evade
PR1077 if the resulting decoder still has exactly eight all-pairs terms.

## Masked exactness: the retained rank-eight boundary

In PR717's **E-graph model**, only the diagonal and orthogonal root pairs
constrain the sum `K` of costly terms: `K_ii = 4` and `K_ij = 0` on orthogonal
pairs. Odd-pair entries are free because they can be corrected by cost-zero
terms in this algebraic model. This is not the all-pairs identity above.

[Brett Halligan / burntout76's PR1212, §§0 and 8–10](../../research/complex-rank8-decoder-rigidity/PROOF.md)
proves that, on its covered live sets, `rank K <= 8` forces
`K = D (2G) D^{-1}` for an invertible diagonal `D`. With **exactly eight costly
terms**, this gauge form gives an all-pairs decoder with the same term supports
and binary pairing costs. Josie Elliston's extensions cover the missing P111
and P104 cases:

| Live set | Retained rigidity source | Real eight-costly-term COPY floor |
| --- | --- | --- |
| P120; P112 obtained by deleting any frame | [PR1212](../../research/complex-rank8-decoder-rigidity/README.md) | 72; 64 |
| P111 obtained by deleting one further line from P112 | [PR1389](../../research/complex-rank8-rigidity-p111-p104-44/PROOF.md) | 63 |
| P104: 336 type-(2,2,2,2) second-frame complements | [PR1212 §10](../../research/complex-rank8-decoder-rigidity/PROOF.md#10-beyond-one-frame-what-transfers-to-p111-and-to-the-p104-units) | 56 |
| P104: 28 type-(4,4) second-frame complements | [PR1389](../../research/complex-rank8-rigidity-p111-p104-44/PROOF.md); [PR1788's alternate-pivot proof](../../research/e8-rank8-transport-audit/PROOF.md) | 56 |
| P104: 896 admissible second-frame complements | [PR1399](../../research/complex-rank8-rigidity-p104-admissible/PROOF.md) | 56 |

The P104 rows cover all 1,260 frames disjoint from a fixed first frame, **not
arbitrary sixteen-line punctures**. PR1399 records attainment of 56 on the
admissible orbit; the table does not claim attainment on the other two orbits.
PR1788 independently checks orbit transport and supplies an alternate complete
pivot for type (4,4). It corroborates PR1389, not a new floor.

Two limits matter when choosing the next experiment:

- **Rank is not term count.** Nine or more costly terms can sum to a rank-eight
  matrix. Rigidity then constrains that sum, but PR1212's square-factor argument
  does not determine the individual supports or their COPY bill. Higher-rank
  sums are outside the rigidity theorem too. Neither case is excluded by this
  chain; absence from this map is not evidence that no other result applies.
- **Field and proof dependencies remain explicit.** The gauge algebra holds
  over characteristic-zero fields. The cost conclusions tabulated here use the
  real PR968 theorem and its inherited hyperplane-flat classification (F6).
  A complex-cost claim additionally needs the separate PR1077 extension; this
  map does not add that composition proof. Zero exclusion and orbit transport
  are finite premises alongside the written algebra, not a full supplier proof.

The older source packages still describe some successor cases as open. Those
are historical statements: the retained [fifth integration review](community-efficient500-review.md)
records PR1389/1399, and the [eighth integration review](community-efficient800-review.md)
records PR1788. Their exact reviewed heads are below. Do not edit frozen
packages or reinterpret their old status as the present research frontier.

## What the independent Gram evidence proves

[Adam Gall's PR1098](../../research/p112-gram-support-seed80/README.md)
corroborates **PR845's finite support lemma** using a label-free Gram-spectrum
certificate: 511 nonzero pairing characters, 503 full-rank supports and eight
coordinate-axis kernels. It also establishes a sharp restricted-energy constant
four on the full-rank supports.

That check does **not** replay PR845's 3,272 sign systems or its 128 incompatible
kernel cases, and the energy constant is not a physical COPY bill. Follow
[PR845's proof](../../research/p112-single-lift/PROOF.md#annihilators-convert-cost-into-a-dimension-bound)
and its main/independent checkers for those remaining finite premises. PR1098 is
corroboration, not a broader ninth-term or masked-decoder exclusion.

## Reproduce the cited evidence

From the repository root, Python 3.10+ and the standard library. PR968's plain
`verify.py` command rejects the current selected record at `G.selected-record`:
its pricing section requires the historical #942 certificate. Use its existing
`--repo` option with an isolated copy of the pinned pricing inputs and frozen
checkpoint. This runs the **complete unchanged verifier**, including its
selection guard, full frame census, historical pricing and failure controls:

```sh
python3 -I -B - <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

package = Path("research/complex-frame-pair-decoders")
pins = json.loads((package / "SOURCES.json").read_text())
with tempfile.TemporaryDirectory(prefix="pr968-") as work:
    historical = Path(work)
    for relative, expected in pins["pricing_inputs"].items():
        data = Path(relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Pinned input changed: " + relative)
        target = historical / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    selected = historical / "certificates/selected-result.json"
    selected.parent.mkdir(parents=True, exist_ok=True)
    selected.write_bytes(Path("certificates/checkpoints/frontier942.json").read_bytes())
    subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"),
                    "--repo", str(historical)], check=True)
PY
```

Expected final line starts `PASS_COMPLEX_FRAME_PAIR_DECODERS`. Temporary files
are removed on exit. The checkout's selected record and predecessor files are
not written. The other packages' direct commands work on the current checkout:

```sh
python3 -I -B research/complex-decoder-field-extension-seed44/verify.py
python3 -B research/p112-single-lift/verify.py
python3 -B research/p112-single-lift/independent_check.py
python3 -I -B research/p112-gram-support-seed80/verify.py
```

For the masked-rigidity chain, use the retained PR1212 files in this checkout:

```sh
python3 -I -B research/complex-rank8-decoder-rigidity/verify.py
python3 -I -B research/complex-rank8-decoder-rigidity/verify.py --live P120
python3 -I -B research/complex-rank8-rigidity-p111-p104-44/verify.py --pr1212-dir .
python3 -I -B research/complex-rank8-rigidity-p104-admissible/verify.py --pr1212-dir .
python3 -I -B research/e8-rank8-transport-audit/verify.py
```

The two `--pr1212-dir .` commands check pinned predecessor blobs and replay its
zero-exclusion and transport checks, rather than merely citing them. A source
mismatch must be investigated, not bypassed. Each command exits zero and ends
with its package's `PASS_` summary on the documented source set.

These check the packages' declared exact finite evidence, including their
failure controls. The quantified lower bounds also use written arguments.
PR968's quoted headroom belongs to #942; it is not a repricing of today's
selected construction. Resolve current sources and the full replay through
[the selected record](../../certificates/selected-result.json).

A copied-rank floor or a decoder identity does not establish a complete paid
moment, legal centre/frame/restoration program, physical hosting or an all-size
multiplication theorem. Compare any proposed realization's **whole invoice**
with the [current bottleneck](bottleneck-brief.md); a change in the rank
distribution can matter even at the same rank sum. This map adds no new bound
or supplier.

## Open next questions

For a candidate with changed readers, masked exactness or more terms, first
record its precise identity, coefficient field, puncture, support-pairing bill
and which of the above hypotheses changes. Masking alone does not escape the
covered eight-costly-term cases. This makes the next overlap check
specific and avoids repeating PR845 under a new optimizer seed. A mathematical
identity and a favorable fully charged budget are the first steps toward a
supplier; a legal centre/frame/restoration implementation remains a separate
blocker. Work outside this map may already have a pending result: consult the
[discussion board](https://github.com/CrocSwap/integer-mult-bounds/discussions)
and refreshed PR bodies rather than inferring availability from this index.

## Scope, source heads and credit

Task `scope-navigation`, priority revision 3; scope key `b18e0e173a4430a9564b`,
nonce `2f5e17a27f7174806a1785a7c24a478f`. Scope **refined** to this four-result
family index and its historical replay route: the onboarding eight-term link
did not explain the adjacent fixed-reader ninth-term exclusion, narrower Gram
corroboration or PR968's historical selection guard. Base:
`ee055dc44815497927ef618fc985b93c2dcbda2a`. These are the reviewed source heads
in the retained [#952](../../research/community-batch952-audit/DISPOSITIONS.json),
[#970](../../research/community-batch970-audit/DISPOSITIONS.json) and
[#1099](../../research/community-batch1099-audit/DISPOSITIONS.json) dispositions:

| PR | Reviewed head |
| --- | --- |
| 845 | `125ce25bdae421627b56077adc14940c2d0aa52f` |
| 968 | `6a99e7240b961ac5e115ae6aa0301ec7c4a45d77` |
| 1077 | `1459f58a829e616ddf32a3da2782e166700e3218` |
| 1098 | `75834dfc800511cebc0e4c696788e9081272d761` |

Construction/model credit includes DreamingOfClouds (PR717/446/595), Joel
Pulikkan / GamingPuzzled (PR620) and the lineage credited in each source.
Coordination and overlap limits are recorded in [discussion #1621](https://github.com/CrocSwap/integer-mult-bounds/discussions/1621).
Prepared by Arham Tahir with substantial OpenAI Codex assistance; no independent
human review or proof-assistant verification of these statements is claimed.
Apache-2.0.

The masked-rigidity navigation update uses main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4, task
`scope-navigation` (nonce `b354c3f7c6a0345880a54f10bfa849bf`). Its refined scope
is the missing route from masked exactness to retained eight-term obstructions,
not a new bound or a survey of every puncture. Reviewed source heads from the
[PR ledger](pr-ledger.md):

| PR | Reviewed head |
| --- | --- |
| 1212 | `57099cb5684f38877f31d149d598801671a633db` |
| 1389 | `5480912a95c3edd0a9ef7532dcc7fc7060d12380` |
| 1399 | `4e1ba3a1ded94772cce5f8c0ad667a92afd6c493` |
| 1788 | `c7d75c1dd348ed4312b095ca467ce966493cf9e8` |

Credit Brett Halligan / burntout76 for PR1212; Josie Elliston for
PR1389/1399/1788; and the PR717/968 model and floor authors credited above.
Navigation update by starship-s with substantial Hermes and OpenAI Codex assistance.
[Scoped claim and verification](https://github.com/CrocSwap/integer-mult-bounds/discussions/1621#discussioncomment-18945325).
