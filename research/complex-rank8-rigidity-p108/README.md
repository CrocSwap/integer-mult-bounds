# Rank-8 masked decoders are gauge-rigid on every P108 unit (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It continues the rank-8 rigidity line of
PR1212 (burntout76, open, head `57099cb5`), PR1399 (`4e1ba3a1`), PR1419 (`81b8997b`), PR1425 (`4b707c22`) and
the P109 package (PR1469). It answers PR1469's open next question.

PR1419's extension lemma makes P112 minus X rigid whenever X lies inside a frame of P112. For |X| = 4 that leaves
168 of the 180 FRAME0-stabiliser orbits of quadruples, 6132952 of 6210820. This package proves rigidity on all
168 with PR1425's per-unit method ([PROOF.md](PROOF.md)). Each representative has:

- a pivot frame passing PR1212's (I3), (I4) and gluing;
- PR1399's Lemma 9 connectivity for the remaining lines;
- a new DRUP refutation for (I2) zero exclusion, 361027 lemmas in total.

**Coverage without a census.** The verifier does not enumerate the 6.2 million quadruples. Every quadruple
contains a triple, and the 24 triple orbits are cheap to compute. So every quadruple is equivalent to a
*candidate*: a triple-orbit representative plus one line. There are 2517 candidates:

- 49 lie inside a P112 frame, which is the PR1419 case;
- for each of the other 2468, `COVER.json` gives a word in the generators that carries a unit's quadruple onto
  it, and `verify.py` replays every word.

That the 168 units lie in distinct orbits comes from the census and is not needed by the argument.

**Consequence.** With PR1419, every P108 unit (P112 minus any four lines) is rigid. Every decoder with exactly
eight costly terms in the E-graph model there has cst ≥ 60, which is PR968's 72 − p at p = 12.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 2.5 minutes:

```sh
python3 -I -B research/complex-rank8-rigidity-p108/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_P108: checks 174; 168 rigid units cover every P108 quadruple outside a P112 frame; with PR1419 every P108 unit is rigid; floor 60
```

What `verify.py` does:

- **Builds everything itself.** It has its own E8 model, triple orbits, cover-word replay, pivot conditions,
  CNF builder and two-watched-literal RUP checker. It replays all 168 proofs from `PROOFS.json.gz` (about
  6 MB) and pins the SHA256 of each decompressed proof and each CNF.
- **Controls.** The gauge pattern satisfies each CNF. Each proof fails without the "some entry vanishes"
  clause. An empty-clause-only proof is rejected.

To regenerate `UNITS.json`, `COVER.json` and `PROOFS.json.gz` (about 40 s, 8 processes), run the command below.
It needs python-sat (1.9.dev15, Glucose 4.1, used here), numpy and scipy. numpy only proposes the orbit grouping;
the verifier checks every word.

```sh
python3 -I -B research/complex-rank8-rigidity-p108/make_proof.py --out-dir /some/new/dir
```

**One-time cross-check, not part of `verify.py`.** OpenAI Codex wrote a census independently, from a
specification only. It finds the same 180 quadruple orbits, with 12 inside a P112 frame (77868 quadruples,
matching PR1419's count) and 168 open. The argument above does not need that census.

**AI review.** A read-only adversarial review, also by Codex, checked the coverage argument. It confirmed that
every triple orbit's representative is used, that frame containment is invariant, and that every cover word
replays. It also checked the P108 edge cases, such as classes with a single live row. It found no soundness gap,
and its wording point on orbit distinctness is applied above. This is not a human review.

## Not covered

- **Inherited steps.** These are cited, not re-derived:
  - PR1212's Lemmas 5–6, §7 assembly and §10 transport;
  - PR1399's Lemma 9;
  - PR1419's Lemma 10 with its P104 inputs, for the frame-contained quadruples.

  All of these PRs are open, as is PR1469, which is the P109 package. This package does not depend on it, since
  Lemma 10 is not used between depths here. PR968's premise (F6) is inherited through the floor. Attainment of
  60 is not checked.
- **P107 and deeper**, and **nine or more costly terms**.
- The written proof has had no independent human review. There is no construction and no κ change, and every
  condition of the selected record is unchanged.

## Open next questions

**P107 to P105, and a structural zero-exclusion lemma.**

- *Why it matters.* PR968's floor goes to p = 15, which is P105. With PR1419's Lemma 10, rigidity of every P105
  unit would give every intermediate depth at once.
- *A feasible first step.* Run the same pipeline on the P107 candidates, each a P108 orbit representative plus
  one line, to measure the proof volume. In parallel, look for a pivot-local argument that excludes zeros from
  the *trans* and *diag* families alone.
- *The blocker.* The per-orbit certificates already take about 6 MB at P108, and P105 has on the order of 10⁵
  orbits. No structural replacement for the DRUP step (I2) is known.

## Credit

- **burntout76 / Brett Halligan (PR1212):** the theorem, (E), the CNF families of Lemmas 4 and 8 (reimplemented
  here), the pivot reduction, Lemmas 5–6, §7 and the transport.
- **themilkman216 (PR968):** the floor 72 − p.
- **DreamingOfClouds (PR717):** the E-graph model.
- **PR1399, PR1419, PR1425, PR1469 (JosieElliston):** Lemma 9, the extension lemma and coverage rule, and the
  per-unit pipeline.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code, covering
the proof, coverage argument, verifier and write-up. OpenAI Codex independently recomputed the orbit census and
reviewed the package. Apache-2.0.
