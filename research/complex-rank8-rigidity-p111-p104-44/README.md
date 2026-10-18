# Rank-8 masked decoders are gauge-rigid on P111 and the type-(4,4) P104 units (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It extends PR1212 (burntout76,
`research/complex-rank8-decoder-rigidity/`, open, head `57099cb5`) and depends on that PR's zero-exclusion
lemma.

PR1212 proves the following in PR717's E-graph (masked) model. Every rank-≤8 solution K of
`K_ii = 4, K_ij = 0` on orthogonal live pairs, with odd entries free, is `D(2G)D⁻¹`. It proves this on
P112, P120 and the 336 type-(2,2,2,2) P104 units. As a result, decoders with exactly eight costly terms
keep PR968's floor there. Its PROOF.md §10 names two remaining gaps:

- **P111** (112 units): one class keeps three live rows, and its block has no complete class.
- **Type-(4,4) P104** (28 units): two blocks carry no live class, so Lemma 6's cocycle step has no witness.

This package closes both gaps ([PROOF.md](PROOF.md)):

- **Lemma 5′.** A class with three live rows has the same Lemma-5 form. PR1212 notes that the group
  relations again force two cases, and that case (ii) has rank 1 < 3. What is new here is the `b` side:
  without a square class matrix, the in-class equations force `γ_f γ′_f` to be constant, because the three
  pairwise sign products span the non-trivial characters.
- **Lemma 6′.** The gluing works whenever the usable classes through each pivot pair are connected and an
  explicit three-triple path exists. This holds on both units with 14/14 and 12/14 usable blocks. The
  argument is multiplicative and is valid over any field of characteristic 0.

**Consequence.** In the E-graph model, every decoder with exactly eight costly terms has `cst ≥ 63` on every
P111 unit (attained by PR717's P111 hits) and `cst ≥ 56` on every type-(4,4) P104 unit. Sharpness of 56 on
these units is not checked.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 1 s:

```sh
python3 -I -B research/complex-rank8-rigidity-p111-p104-44/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_P111_P104_44: checks 26; P111 three-row 1, blocks 14/14; P104-44 blocks 12/14 path-glued; floors 63/56; zero exclusion cited from PR1212
```

To also replay PR1212's zero-exclusion DRUP refutations and orbit transport (about 15 s), first make a
checkout of PR1212's head. The verifier checks the git blobs of its `verify.py` and two `.drup` files, then
runs it:

```sh
git fetch origin pull/1212/head && git worktree add --detach /tmp/pr1212 57099cb5
python3 -I -B research/complex-rank8-rigidity-p111-p104-44/verify.py --pr1212-dir /tmp/pr1212
```

The verifier is an independent implementation, with its own E8 model, classes, witnesses, gluing and
assembly. It imports nothing from PR1212. It checks units and pivots given as root vectors and confirms that
these match PR1212's pivot indices. The controls show four things:

- two-row classes are not forced;
- P111 needs Lemma 5′;
- the path condition rejects a rank-deficient block set;
- a perturbed entry breaks (2).

## Not covered

- **The 896 admissible P104 units** (PR717's P104 among them). Four classes keep only two live rows, and
  Lemma 5′ fails there. PR1292 (Navinor) proves local rigidity only.
- **Nine or more costly terms**, including PR717's mixed-β problem.
- **Zero exclusion** is PR1212's DRUP result, replayed but not re-derived. The flat classification premise
  (F6) inherited through PR968 is unchanged.
- The written proof has had no independent human review. There is no construction and no κ change, and
  every condition of the selected record is unchanged.

## Open next questions

**Rigidity on the admissible P104 units.** This matters because PR968's 7/13 ratio is attained there, so an
off-orbit masked solution there would be the cheapest escape from the floor. The first step is a two-row
variant of Lemma 5 that uses the cross-block relations (5) with the neighbouring four-row classes to fix the
one-parameter in-class family. This is blocked on writing that argument. The in-class relations alone
provably do not suffice (`control.two-row-not-forced`).

## Credit

- **burntout76 / Brett Halligan (PR1212):** the theorem, the proof skeleton and every lemma reused here,
  zero exclusion, the transport, and the handoff naming this step.
- **themilkman216 (PR968):** the eight-term floor.
- **DreamingOfClouds (PR717):** the E-graph model and the P111 decoders.
- **Navinor (PR1292):** local P104 rigidity.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code,
covering the proof, verifier and write-up. Apache-2.0.
