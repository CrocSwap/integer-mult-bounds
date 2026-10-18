# Rank-8 masked decoders are gauge-rigid on every P109 unit (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It continues the rank-8 rigidity line of
PR1212 (burntout76, open, head `57099cb5`), PR1399 (`4e1ba3a1`), PR1419 (`81b8997b`) and PR1425 (`4b707c22`). It
answers PR1425's open next question.

PR1419's extension lemma makes P112 minus X rigid whenever X lies inside a frame of P112. For |X| = 3 that leaves
198688 of the 227920 triples. Under the FRAME0 stabiliser they form 19 orbits: 18 contain an odd pair, and one
(1792 triples) is pairwise orthogonal but extends to no P112 frame. This package proves rigidity on all 19 with
PR1425's per-unit method ([PROOF.md](PROOF.md)):

- a pivot frame passing PR1212's (I3) and (I4) with gluing;
- PR1399's Lemma 9 connectivity for the lines outside complete classes;
- a new DRUP refutation of the zero-pattern CNF for (I2) zero exclusion, with 1595 to 2945 lemmas per unit.

**Consequence.** With PR1419, every P109 unit (P112 minus any three lines) is rigid. Every decoder with exactly
eight costly terms in the E-graph model there has cst ≥ 61, which is PR968's 72 − p at p = 11.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 15 s:

```sh
python3 -I -B research/complex-rank8-rigidity-p109/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_P109: checks 25; all 19 open P109 orbits (198688 triples) rigid; with PR1419 every P109 unit is rigid; floor 61
```

`verify.py` is self-contained:

- **Census.** It recomputes the orbit census of triples and the inside-a-frame split, and checks that the units
  hit each open orbit once.
- **Per unit.** It checks the pivot conditions, builds each CNF itself and replays the 19 proofs from
  `PROOFS.json.gz` with its own RUP checker. It pins the SHA256 of each decompressed proof and each CNF.
- **Controls.** The gauge pattern satisfies each CNF. Each proof fails without the "some entry vanishes"
  clause. An empty-clause-only proof is rejected.

`UNITS.json` and `PROOFS.json.gz` are regenerated in about 4 s by the command below, which needs python-sat
(python-sat 1.9.dev15, Glucose 4.1, used here). Deletion lines are dropped, since the checker ignores them.

```sh
python3 -I -B research/complex-rank8-rigidity-p109/make_proof.py --out-dir /some/new/dir
```

Two one-time cross-checks were run but are not part of `verify.py`:

- **PR1212's checker.** PR1212's `rup_check` at head `57099cb5` accepts all 19 proofs on this package's CNFs,
  with the same lemma counts, and rejects every one without the zero clause.
- **Independent census.** A separately written census matches the orbit table exactly: 24 orbits and every
  (size, odd pairs, inside-a-frame) triple. It was written from a specification only, by OpenAI Codex, and
  computed |H| = 344064 with 2025 frames.
- **AI review.** A read-only adversarial review, also by OpenAI Codex, checked the CNF families, the lemma
  hypotheses, subgroup coverage and the RUP checker, including 10000 random fuzz formulas. It found no soundness
  gap. This is not a human review.

## Not covered

- **Inherited steps.** These are cited, not re-derived:
  - PR1212's Lemmas 5–6, §7 assembly and §10 transport;
  - PR1399's Lemma 9;
  - PR1419's Lemma 10 with its P104 inputs, for the 29232 covered triples.

  All of these PRs are open. PR968's premise (F6) is inherited through the floor. Attainment of 61 is not
  checked.
- **P108 and deeper.** The same method applies per orbit, but the open orbit count grows: 168 at |X| = 4 (see
  below).
- **Nine or more costly terms.**
- The written proof has had no independent human review. There is no construction and no κ change, and every
  condition of the selected record is unchanged.

## Open next questions

**P108: four-line punctures not inside a P112 frame.**

- *Why it matters.* P109 is complete with this package. P108 is the next depth: 168 of 180 orbits, 6132952 of
  6210820 quadruples. Both counts were found by this package's code and independently by the census above.
- *A feasible first step.* A trial run of `make_proof.py`'s pivot rule and CNF on all 168 representatives found a
  passing pivot and an unsatisfiable CNF for every one. That is 361027 lemmas, or about 5.9 MB gzipped. The run
  was outside the package and is not certified here.
- *The blocker.* Shipping per-orbit proofs at that size, plus a pure-Python census of 6.2 million quadruples, is
  heavy. Deeper levels grow further, and the bottom level P105 alone has on the order of 10⁵ orbits. A
  structural replacement for the DRUP step (I2) would remove that growth.

## Credit

- **burntout76 / Brett Halligan (PR1212):** the theorem, (E), the CNF families of Lemmas 4 and 8 (reimplemented
  here), the pivot reduction, Lemmas 5–6, §7 and the transport.
- **themilkman216 (PR968):** the floor 72 − p.
- **DreamingOfClouds (PR717):** the E-graph model.
- **PR1399, PR1419, PR1425 (JosieElliston):** Lemma 9, the extension lemma with its coverage rule, and the per-unit
  pipeline.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code, covering
the proof, verifier and write-up. OpenAI Codex independently recomputed the orbit census and reviewed the package. Apache-2.0.
