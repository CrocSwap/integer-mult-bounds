# Rank-8 masked decoders are gauge-rigid on P112 minus an odd pair, which completes P110 (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It extends the rank-8 rigidity line of PR1212
(burntout76, open, head `57099cb5`) and PR1399 (open, head `4e1ba3a1`). It answers PR1419's open next question.

PR1419 shows that rank-8 rigidity of PR1212's system (E) passes to supersets. That makes P112 minus any
orthogonal pair rigid, but it cannot reach an **odd pair**, because no frame contains one. The 2912 odd pairs
form two FRAME0-stabiliser orbits, of sizes 224 and 2688. This package proves rigidity on both, by PR1212's
method plus PR1399's Lemma 9 ([PROOF.md](PROOF.md)). Each orbit representative has a pivot frame with:

- **(I2) zero exclusion**: a new DRUP refutation per orbit, 1893 and 2320 lemmas;
- **(I3) and (I4)**, plus gluing, on the complete classes;
- **Lemma 9 witness connectivity** for every line of an incomplete class, with all six column pairs
  witnessed.

**Consequence.** With PR1419, every P110 unit (P112 minus any two lines) is rigid. Every decoder with exactly
eight costly terms in the E-graph model there has cst ≥ 62, which is PR968's 72 − p at p = 10.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 2 s:

```sh
python3 -I -B research/complex-rank8-rigidity-p110-odd/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_P110_ODD: checks 26; both odd-pair orbits (224 + 2688) rigid; with PR1419 every P110 unit is rigid; floor 62
```

`verify.py` is independent of PR1212's code. It has its own E8 model, stabiliser orbits, classes, witnesses,
gluing, Lemma 9 checks, zero-pattern CNF and two-watched-literal RUP checker. It replays the shipped
`proof-meet4.drup` and `proof-meet2.drup` against CNFs it builds itself, and pins the SHA256 of both the proofs
and the CNFs. Its controls:

- the gauge zero pattern satisfies the CNF without the "some entry vanishes" clause;
- the proofs fail without that clause;
- a bare empty-clause proof is rejected.

To regenerate the proofs, which needs python-sat (python-sat 1.9.dev15, Glucose 4.1, used here):

```sh
python3 -I -B research/complex-rank8-rigidity-p110-odd/make_proof.py --out-dir /some/new/dir
```

As a one-time cross-check, not part of `verify.py`, PR1212's `rup_check` (head `57099cb5`) accepts both proofs
on this package's CNFs, with the same lemma counts, and rejects them without the zero clause.

## Not covered

- **P105–P109 punctures containing an odd pair**, and orthogonal punctures outside a frame (see PR1419's
  census). The method here applies per orbit, but the orbit counts grow quickly with |X|.
- **Inherited steps.** PR1212's Lemmas 5–6, §7 assembly and §10 transport, and PR1399's Lemma 9, are cited,
  not re-derived. Both PRs are open. PR968's premise (F6) is inherited through the floor. Attainment of 62 on
  these units is not checked.
- **Nine or more costly terms.**
- The written proof has had no independent human review. There is no construction and no κ change, and every
  condition of the selected record is unchanged.

## Open next questions

**P109: three-line punctures with an odd pair.**

- *Why it matters.* With this package P110 is complete. P109 is the next depth, and PR1419's census leaves
  198688 of its 227920 punctures uncovered.
- *A feasible first step.* Enumerate the FRAME0-stabiliser orbits of 3-subsets of P112 that are not inside a
  P112 frame. Then run `make_proof.py`'s pivot rule and CNF per orbit, which is about 1 s per unit here.
  Lemma 10 of PR1419 reduces the work: any rigid sub-unit settles every superset.
- *The blocker.* The number of orbits is not yet known. Each orbit needs its own certificate, unless a
  rigid sub-unit is found first.

## Credit

- **burntout76 / Brett Halligan (PR1212):** the theorem, (E), the CNF families of Lemmas 4 and 8 (reimplemented
  here), the pivot reduction, Lemmas 5–6, §7 and the transport.
- **themilkman216 (PR968):** the floor 72 − p.
- **DreamingOfClouds (PR717):** the E-graph model.
- **PR1399, PR1419 (JosieElliston):** Lemma 9 and the extension lemma with its census.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code,
covering the proof, verifier and write-up. Apache-2.0.
