# Owned-exit cut bound: a lower bound on owned exits of every legal P104 native word (no κ)

**No new κ.** This package proves a counting bound for any native word that obeys the frame law of the P104 native verifier, with owned moves allowed in either direction: across any cut of the frame lattice defined by a vector set `Q`, the number of owned MOVE events that leave the frames meeting `Q` is at least a rank of the endpoint map. For a port clique `W` it is at least `|W|`. The bound is then applied to the native word of #6833 (the 9|9 chain-nested root): it is tight on all 1967 maximal port cliques, and every one-unit end shortening of each owned lifetime, in two stated families, is infeasible, each with a stored certificate. Nothing is priced and no word is constructed.

## Setting

Ambient space `F2^9`; a frame is a subspace of it. Registers are public (the 772 inputs) or owned (born zero, may be cleared dirty, none live at exit). Each register sits at a frame and holds a linear form in the initial public values. Frame law:

* **H1** public MOVEs go strictly upward between nested frames (`E` strictly inside `F`);
* **H2** ADD, COPY and SCALE act at one common frame (an ADD or COPY joins two registers at the same frame);
* **H3** COPY goes only into a zeroed owned register;
* **H4** no owned register is left at exit, so the final publics are all that is read.

Owned MOVEs may go in any direction (the proof does not use their direction, nor that they are nested). CLEAR may be dirty. Helpers, junk registers and a singular endpoint map are allowed. `T[v,u]` is the coefficient of initial public `u` in the final value of public `v`.

For a set `Q` of nonzero vectors let `U_Q` be the set of frames that meet `Q`. It is an up-set: `E` in `U_Q` and `E` inside `F` give `F` in `U_Q`. An **exit** is an owned MOVE event `E -> F` with `E` in `U_Q` and `F` not in `U_Q`. A public ascent never leaves `U_Q`, and an owned ascent never does either, so exits are owned moves that go down across the cut.

## Theorem (owned-exit cut bound)

For every legal word and every `Q`:

> rank `T[ final publics whose final frame is not in U_Q , initial publics whose initial frame is in U_Q ]`  <=  number of owned exits from `U_Q`.

**Corollary (port cliques).** The 104 ports have odd-weight vectors `q_p`. X_p starts at the frame `[q_p]`; Y_p starts at dimension 0 and ends at the hyperplane `q_p^perp` with value `y_p + x_p`. A port clique is a set `W` of ports with `q.q' = 1` for all `q, q'` in `W` (including `q = q'`, since ports are odd). Let `A(W) = {x : x.q = 1 for all q in W}` and choose `Q` with `W` inside `Q` inside `A(W)`. Then `[q_p]` meets `Q` (it contains `q_p`), while `q_p^perp` misses `Q` (every `x` in `Q` has `x.q_p = 1`). The block `T[Y_W, X_W]` is the identity of size `|W|`, so the rank is `|W|` and **every legal native has at least |W| owned exits from `U_Q`.**

## Proof

Fix a word and `Q`. At each time `t` let `M_t` be the matrix with one row per register whose current frame is not in `U_Q`, and one column per initial public register whose initial frame is in `U_Q`; the entry is the coefficient of that initial register in the register's current value. Claim: `rank M_t` increases only at owned exits, by at most 1 each.

* **Start.** `M_0 = 0`: a register outside `U_Q` holds its own unit vector, and its own initial register is outside `U_Q`.
* **ADD** `a += c b` at a common frame `f` (H2). Both registers are outside `U_Q` or both inside, because they share the frame. If inside, `M` is untouched. If outside, the row of `a` gets `c` times the row of `b`: an elementary row operation, the rank is unchanged. **SCALE** by a nonzero `c` multiplies a row: unchanged.
* **COPY** into a zero owned register (H3, H2): a new row equal to a multiple of an existing outside row (or nothing, if inside). The rank is unchanged. **INIT** adds a zero row. **CLEAR** deletes a row. The rank does not increase.
* **Public MOVE** `E -> F` (H1): outside to outside does nothing; outside to inside deletes a row; inside forces `F` inside. The rank does not increase.
* **Owned MOVE** `E -> F`: outside to outside or inside to inside does nothing; outside to inside deletes a row; inside to outside **adds one row**, which is an exit. The rank increases by at most 1.

At the end the rows of `M` are exactly the final publics outside `U_Q` (owned registers are gone, H4), so `rank T[...] = rank M_end <= #exits`. ∎

Only H1 (public ascent), H2, H3 and H4 are used. Not used: invertibility of `T`, clean CLEARs, any direction restriction on owned moves, helper or junk counts. The bound counts events, not dimension mass: one exit carries one vector whatever its dimension change.

## Application to the #6833 native word

`wB.json.gz` is that native word (772 public registers, 18622 events, 47 owned lifetimes, 24 owned MOVE events, all descending, total dimension change 56). `check.py` replays it against H1-H4 with an exact endpoint map and checks the pins above (X_p initial frame `[q_p]`, Y_p final frame `q_p^perp`, `T[Y_p,X_p] = 1`).

* **Tight on every maximal clique.** The port graph has 1967 maximal cliques (sizes 4:24, 5:96, 6:432, 7:656, 8:759). For each, the identity block is verified and a cut `Q` between `W` and `A(W)` is exhibited whose owned-exit count for the word equals `|W|`; no cut tried gives fewer. The theorem is therefore consistent with the word and attained on all 1967.
* **End shortenings are infeasible.** For each owned lifetime and each end (38 life/end records), replace the end hop by a one-unit-shorter one, all other lifetimes unchanged. Two families:
  * **Core family (246 variants).** The new end frame `F'` is nested between the neighbouring frame `ref` and the old end frame, at one dimension less than the old end (for a one-step hop this deletes the hop). Each of the 246 has a stored `(W,Q)` with fewer owned exits than `|W|`.
  * **Ascending-start family (547 variants).** `F'` is strictly inside `ref` (top ends) or strictly above `ref` (bottom ends), with `|dim F' - dim ref|` one less than the old hop. The new hop ascends, so it never exits any cut; the variant has one exit fewer than the word on every cut where the replaced hop exited. Each of the 547 has a stored `(W,Q)` with exits(word) = `|W|`, the replaced hop exiting, and exits(variant) = `|W| - 1`.

  `certs.json` stores 137 certificates `(W,Q)` and, for each variant (identified by the hexadecimal mask of its frame), the index of the certificate used. `check.py` re-enumerates both families from the word, requires the variant set to equal the stored set, and rechecks every certificate: `W` is a clique, `W` inside `Q` inside `A(W)`, exits(variant) < `|W|`, exits(word) = `|W|`. Only the checked certificate matters, not how `Q` was found.

## Controls

* **Legal fuzz.** 25,000 random legal words on `F2^3` (all 127 cut sets `Q` per word) and 6,000 on `F2^4` (300 random `Q` each): 31,000 words with owned moves in both directions, dirty CLEARs, junk and helper registers, singular endpoint maps allowed, exact rational ranks. **0 violations** of the rank bound. Not vacuous: 15,344 cuts have nonzero rank, 2,051 of them with rank equal to the exit count.
* **Illegal public descent.** The same generator with public MOVEs allowed to descend: **65,551 violations** over 3,000 words, so the checker detects a broken hypothesis.

## Scope

* A **necessary condition** only. A certificate shows that the stated owned-move multiset (all other lifetimes unchanged) cannot occur in a legal native, whatever the rest of the word does with reads, writes, helpers or forks. A survivor of the cut test would not be a feasibility claim.
* It bounds **owned MOVE events**, not dimension mass. The word is tight at 8 events on every clique, so cuts alone cannot exclude removing mass while keeping 8 or more moves, nor edits that change several lifetimes at once, add moves, or change the root. Shortening a middle hop, or splitting hops, is not in the two families; the theorem applies to them by recomputing exits.
* The result is a theorem about the **abstract legal model** above (the frame law with linear coefficients). That the verifier's chart semantics reduces to this model is taken from the lemma list of the P104 designer toolkit package (#6170), not re-proved here.
* If public registers may descend, the theorem fails (control above).

## Exact checks (`check.py`, `verify.sh`, about two minutes)

Standard library only, no repository file read. `python3.12 -I -B check.py` prints the replay, pins, clique, certificate and fuzz lines and ends with the marker `PASS_P104_OWNED_EXIT_CUT_BOUND`. `check.py --quick` runs a short fuzz for a fast look.

## Open next questions

1. Do the cut bounds combine into a bound above 8 owned events, or a dimension-mass bound?
2. Which multi-lifetime edits survive every cut?
3. Is there an entry-form bound that does not need an invertible endpoint map?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
