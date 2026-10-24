# Lower bounds for small complex units, and the smallest open cases

No new κ.

Jacob Sussman. Apache-2.0. Written with AI agents (Anthropic Claude); see *AI assistance and credit*.

## 1. What this is

A small unit that transforms W arrays with fewer than W·m calls at block size m would give a large saving, since
the saving is ln(mW/s)/ln m for s calls. With a team of AI agents I looked for one and found none. What came out
instead are lower bounds on s at small m, and a short list of the smallest shapes nobody has settled. This note
collects them in one place, with their status, so that others can use them or start from the open cases.

| Result | Game | Status |
|---|---|---|
| The kept-subspace bound: s ≥ W · demand / cap for any subspace that every free step keeps | engine game, on the engine's own definitions | proved in Lean |
| Block 2 never saves: s ≥ 2W | engine game; every game with bounded free steps | proved in Lean; argued by hand in the bounded games (one AI reviewer) |
| Block 3: s ≥ 14W/5, so a block-3 unit saves at most 6.28e-2 and every unit with 4 or fewer arrays is excluded | engine game; widened game | proved in Lean; argued by hand in the widened game (three AI reviewers) |
| Block 4: s ≥ 41W/13, so a block-4 unit saves at most 1.71e-1 | engine and widened games | checked by computer; in the widened game it also rests on the keptness argument, argued by hand |
| From block 4 on: at least 2.9447 calls per array (2.99172 at block 5, 2.97290 at block 6) | engine game | argued by hand (two AI reviewers reproduced every number); its block-4 inputs are checked by computer here |
| Block 3 without phase letters: s ≥ 3W, whatever the address maps | no-phase game | argued by hand (one AI reviewer); its certificate is checked by computer here |
| One array needs m calls | every game with bounded free steps | argued by hand (AI reviewers in two rounds) |
| Two or more arrays need at least max(W + m, 2W) calls | every game with bounded free steps | argued by hand (one AI reviewer for each half) |

Section 7 uses two of these to answer the two questions about small gadgets in David Harvey's recent note on the
proposed o(n log n) algorithm. Nothing here is about κ or about integer multiplication itself: every
result is a statement about units in a stated game.

**Status words.** I use the words of my public repository. *Proved in Lean*: Lean 4 accepted the proof with only
the three standard axioms. *Checked by computer*: an exact computation or a stored certificate, checked by a
separate program. *Argued by hand*: a written argument; no person and no proof checker has checked it. Where an AI
reviewer (an agent whose only job was to break the result) re-derived it, I say so. *Open*: nobody has settled it.

## 2. What was known, and what this note adds

The method and the first cases are not mine.

- **eumemic's #288** (its text is kept on main; the path is in Sources) has
  the certificate method, its "FO lemma", of which the kept-subspace bound is a general form. It shows that m = 2
  never saves in its models ("Hence s ≥ 2W = Wm"). At m = 3 it gives s ≥ 50W/21 in its Clifford model and leaves
  "only W = 2 with s = 5 and W = 3 with s = 8 at small W", and it states the m = 3 case open in its full register
  model. It also gives s ≥ 2W at m = 3 in its enlarged model.
- **Swapnil Jain's papers P1 and P2**, which #288 says "independently prove the overlapping statements" of the FO
  lemma. I cite them on #288's word and have not compared them with this note line by line.
- **jmbarrancoml's #2108** treats #288's five-call case at m = 3: a five-call
  solution "must therefore contain at least four nonmonomial scalar mixing blocks", and "We do not settle the
  five-call problem".
- **The bit side** asks the same question for registers of bits: #468 (three registers at m = 3: "Nine calls are
  necessary and sufficient"), #720 (three target frames need nine calls), #1882 and #2167 (dirty and clean
  auxiliary registers), #825 (a common complete flag), #203 (a pull request still open: a common triangular flag forces s ≥ Wm) and
  #2613 (2-integral matrices never save). These are parallels in other models, not inputs to this note.

What this note adds, item by item. Closest prior work first; then what is new.

- *Kept-subspace bound.* #288's FO lemma; this adds a Lean proof on the definitions of a Lean engine, with scratch
  arrays and singular mixing allowed, and a family of certificates (the hook) that works at every block size.
- *Block 2.* #288 (a) in its models; this adds a Lean proof in the engine game, and the same bound in games whose
  free steps mix neighbouring digit columns (argued by hand).
- *Block 3.* #288's 50W/21 and #2108; this adds 14W/5 in the engine game (Lean). In that game it excludes the
  shapes #288 left open (2 in 5 and 3 in 8; the first is the five-call question of #2108). I have not checked
  whether #288's full register model lies inside the engine game or the widened game, so I do not claim to settle
  those cases in #288's model.
- *2W at every block.* #288 gives s ≥ 2W at m = 3 in its enlarged model, and a doubled-import bound, E + σ ≥ 2W in
  its notation, which "agrees with P1's 'at least 2W children' row"; this adds 2W at every block in every game with
  bounded free steps, including games whose free steps mix neighbouring digit columns (argued by hand).
- *Block 4 and above, block 3 without phases, W + m, the open-case list.* I found no hub package with these. That
  is a search result, not a proof of novelty.
- *One array.* #288's row (f) says "The target still costs m per register" on the bit side; this adds a
  complex-side argument that covers scratch arrays and free steps that mix neighbouring digit columns.

#288 also proves that one natural kind of certificate cannot exist at m = 3 ("No torus-invariant FO certificate
exists in characteristic ≠ 2"; one of its hypotheses is that the certificate "gives a rank-linear bound"). The hook
is a certificate at m = 3, but it proves only 14W/5, not the 3W that would settle m = 3. I have not examined how it
relates to that obstruction.

## 3. The model, in plain words

- **Arrays and calls.** An array holds 2^m complex numbers, addressed by x in F_2^m. A *call* applies the 2-point
  kernel C = aI + bX along one direction v to a whole array: C_v = aI + bX_v, with a = (1+i)/2, b = (1−i)/2 and X_v
  the shift x ↦ x + v. This is exactly David Harvey's C_v and the direction letter of OpenAI's Lean engine. The
  target is C^(⊗m) on each of the W arrays; done one array at a time it costs W·m calls. "W in s" means W arrays
  in s calls.
- **Digit width.** Inside the recursion every entry of an array is itself a sub-array, so a unit must stay right
  when C is replaced by C^(⊗f) for every number f of digit columns. All bounds here are for such units. This
  matters: at width 1 a call is a sum of two free steps, and with one zero scratch array C^(⊗3) costs no call at all
  (checked by computer here, part `width`); the same program is wrong at width 2.
- **Games.** They differ only in what is free.
  - *Engine game*: the letters of the Lean engine in my repository. OpenAI's letters (calls, shifts, mixing of
    arrays by any rational matrix, with any number of scratch arrays) plus two free letters I added: invertible
    XOR-linear maps of the address bits, and phases i^(z·x + c).
  - *Widened game*: also every permutation of the addresses (Toffoli included) and every pattern of phases 1, i, −1, −i.
  - *No-phase game*: the engine game without phase letters, with any complex mixing.
  - *Commutative slice*: calls, shifts and any complex mixing only.
  - *Games with bounded free steps*: every free step touches a bounded number of entries per row, whatever the
    width. This includes all of the above and also maps that mix neighbouring digit columns.

How Harvey's models sit among these is in section 7.

## 4. The method in one page

**The kept-subspace bound.** Take a subspace N of the data space (at some width f) that every free step keeps. For a
letter g, let raise(g) = dim(N + gN) − dim N. Follow the dimension of what the program's state adds beyond N in each
array. It starts at 0. A free step never raises it. A call raises it by at most the *cap*, the largest raise of one
call. At the end each finished array contributes the *demand*, raise(C^(⊗m)). So W · demand ≤ cap · s. Scratch
arrays, copies, erasures and singular mixing are all allowed. The proof is in [PROOF.md](PROOF.md), section 1.

**The hook.** At block m and width f = j + 2, inside V ⊗ Λ^(j+1) V with V = C^(2^m), take
N = span{e_x ⊗ e_T : x in T}. Every free letter that acts inside one array (a shift, an address map, a phase)
keeps it, because it sends each address to one address and multiplies by a number, the same in every column; mixing
of arrays is handled by the bound itself. One call raises it by at most (2^m/2)·C(2^m − 2, j).

| block m | width f | cap | demand | calls per array | status of the numbers |
|---|---|---|---|---|---|
| 2 | 3 | 4 | 8 | 2 | proved in Lean |
| 3 | 5 | 80 | 224 | 14/5 | proved in Lean |
| 4 | 9 | 27,456 | 86,592 = 16 × 5,412 | 41/13 | cap proved in Lean; demand checked by computer |

At block 3, two calls in a row raise the hook by at most 144 (checked by computer), so the 6.28e-2 cap also holds
when grouped calls are priced the way the Lean engine prices them.

**Block 3 without phase letters** uses a different certificate: the span of the 24 "face" triples in Λ³(C^8) at
width 3, with cap 8 and demand 24 in every basis, so 3 calls per array. Address maps do not keep it, so the proof
first trades every address map for extra arrays with relabelled targets (PROOF.md, section 5). With the engine's
phase letters that trade fails, because calls and phases together make CNOT-type address maps. So a block-3 saver
must use address maps and phase letters together (argued by hand).

## 5. What the Lean proves

The Lean files are public in my repository ([lean-block2-block3](https://github.com/jacobalansussman/wht-power-saving-lean/tree/86e575e28ed94890872dcff1bb2621d7ff559cbd/research/block-bounds-and-new-rules/programs/lean-block2-block3),
11 files, 1,662 lines; Lean 4.34.1 and the Mathlib revision pinned by that repository). The hub's intake does not
run Lean, and this package does not ask it to. These are the statements, copied from the files:

```lean
-- TheoremR.lean: the kept-subspace bound for the engine's words (α, ρ, f, N are variables of the file)
theorem engine_lower_bound {σ : Type*} [Fintype σ] {e : σ → ρ} (he : Function.Injective e)
    (hN : Kept N) (cap : ℕ) (hcap : ∀ z : Space α, z ≠ 0 → raise N (matL f (dir z)) ≤ cap)
    (w : GWord α ρ) (hw : GLiveKernel e w) :
    Fintype.card σ * raise N (matL f (kernel α)) ≤ cap * w.cost id

-- Hook.lean: the hook is kept by every free letter; the cap at every block size
theorem hook_kept (j : ℕ) : Kept (hookN (α := α) j)   -- statement only; the `where` proof is omitted
theorem hook_cap (j : ℕ) (z : Space α) (hz : z ≠ 0) :
    raise (hookN (α := α) j) (matL (j+2) (dir z)) ≤
      (Fintype.card (Space α) / 2) * (Fintype.card (Space α) - 2).choose j

-- Bounds.lean
theorem block2_bound {ρ σ : Type*} [Fintype ρ] [DecidableEq ρ] [Fintype σ]
    {e : σ → ρ} (he : Function.Injective e) (w : GWord (Fin 2) ρ) (hw : GLiveKernel e w) :
    2 * Fintype.card σ ≤ w.cost id
theorem block3_cap (z : Space (Fin 3)) (hz : z ≠ 0) :
    raise (hookN (α := Fin 3) 3) (matL 5 (dir z)) ≤ 80

-- Dem3Final.lean
theorem dem3 : 224 ≤ raise (hookN (α := Fin 3) 3) (matL 5 (kernel (Fin 3)))
theorem block3_bound {ρ σ : Type*} [Fintype ρ] [DecidableEq ρ] [Fintype σ]
    {e : σ → ρ} (he : Function.Injective e) (w : GWord (Fin 3) ρ) (hw : GLiveKernel e w) :
    14 * Fintype.card σ ≤ 5 * w.cost id
```

How to read them. `GWord α ρ` is a program of the engine on the arrays ρ, of which the injective map e marks the W
live ones (`Fintype.card σ` = W); the rest are scratch. `GLiveKernel e w` says that for every width f and every input
with zero scratch, each live array ends holding C^(⊗m) of its input. `w.cost id` counts calls (a grouped call of rank
r counts r). The mixing letter takes a rational matrix (`pointL (f : ℕ) (g : Matrix ρ ρ ℚ)`), so the Lean statements
are for rational mixing.

The demand fact `dem3` says that a 280 × 280 matrix has rank at least 224. Lean's kernel is too slow for that in one
piece, so the proof splits it, using the characters of F_2^3, into eight blocks of 28 × 28 and proves in Lean that
the split is valid. Each block is shown invertible modulo 65537 by an
inverse computed outside Lean, which the kernel checks entry by entry (`decide +kernel`, no `native_decide`).
Changing one inverse entry by 1 makes Lean reject the check. `dem3`, `block3_bound` and `block2_bound` depend on
`propext`, `Classical.choice` and `Quot.sound` only; the block checks on `propext` only. The last build took 11
minutes on an 8-core Linux machine with 50 GB, with a peak of 10.06 GB; the eight kernel checks took 562 seconds.
Two AI reviewers checked the development: one restated the theorem in its own words and Lean accepted the same
proof, and it built a one-array program that meets the hypothesis, so the theorem is not vacuous; the other rebuilt
everything in a fresh copy and replayed it with Lean's independent checker. The files were built in a copy of Ryan
Shea's public Lean tree, which pins the same Lean and Mathlib and holds byte-identical copies of the engine files;
they have not yet been built inside a checkout of my repository itself.

This package's `verify.py` re-does, in Python, the exact check the kernel ran on the data file (part `leandata`), but
not the Lean proof that the split is valid.

## 6. The smallest open cases

The engine game unless stated. Savings are ln(mW/s)/ln m.

| m | Best lower bound, calls per array | Largest saving left open | Smallest open shapes (saving) | What is known around them |
|---|---|---|---|---|
| 2 | 2 (proved in Lean) | 0 | none | |
| 3 | 14/5 (proved in Lean) | 6.28e-2 | **5 in 14** (6.28e-2), 6 in 17 (5.20e-2), 7 in 20 (4.44e-2), 8 in 23 (3.87e-2) | 5 in 14 sits exactly on the bound: 14 × 80 = 5 × 224, so every call must gain the full 80. A saver must use address maps and phase letters together (argued by hand) |
| 3, bounded games | max(W + 3, 2W) calls in all, not per array (argued by hand) | 3.69e-1 | 2 in 5 (1.66e-1), 3 in 6 (3.69e-1) | Open in games that make neighbouring-column maps free |
| 4 | 41/13 (checked by computer) | 1.71e-1 | **2 in 7** (9.63e-2), 3 in 10 (1.32e-1), 4 in 13 (1.50e-1), 5 in 16 (1.61e-1), 6 in 19 (1.69e-1) | For 2 in 7 in which each array ends on a call of its own, the best certificate known (the hook at width 9) leaves room of only 640 out of 137,280. With address maps and phase letters only at the two ends (and no mixing between those end letters), 2 in 7, 3 in 10, 3 in 11 and 4 in 13 are excluded (checked by computer). In the commutative slice block 4 never saves (checked by computer) |
| 5 | 2.99172 and W + m (argued by hand) | 3.19e-1 | 2 in 7 (2.22e-1); 3 in 9 (3.17e-1), not excluded by any bound I know | |
| 6 | 2.97290 and W + m (argued by hand) | 3.92e-1 | 2 in 8 (2.26e-1); 3 in 9 (3.87e-1), not excluded by any bound I know | |

Each listed shape is the smallest number of calls not excluded for its number of arrays. `verify.py` (part `table`)
recomputes every figure and every exclusion above from the bounds. Many searches for these shapes found nothing;
those are statements about the searched domains only, and they are told in my repository's
[moonshot sections](https://github.com/jacobalansussman/wht-power-saving-lean/tree/86e575e28ed94890872dcff1bb2621d7ff559cbd/research).

## 7. Two questions in David Harvey's note

David Harvey's note "On the recently proposed o(n log n) integer multiplication algorithm" (20 October 2026,
[subnlogn.pdf](https://web.maths.unsw.edu.au/~davidharvey/research/subnlogn.pdf)) asks two things about small gadgets
that the results above answer. I give the answers with their status, in case they help.

**Where his models sit.** My reading of his text, argued by hand and checked against it by two AI reviewers: his §7.4
model (calls C_v and C_v^(−1), free shifts, adding a complex multiple of one register to another) is inside the
commutative slice. With the relabellings x ↦ Mx of his §6 (M any invertible
matrix over F_2) and rational mixing it is inside the engine game. With complex mixing it is inside the engine game
with complex mixing, which is not in Lean. His butterfly calls (A in his §6, B in §7) differ from C-calls by a scalar
and fixed diagonal phases (B = (1 − i)·S·C·S with S = diag(1, i)), so between relabellings they bring phases with
them.

**(1) One array.** In §6 he writes that Fable told him a single array cannot be done in g < m calls, "but I do not
follow the argument yet". Here is the argument for his single-array programs P_M0 A_i1 P_M1 ⋯ A_ig P_Mg. Follow one
input basis vector e_x. A relabelling sends it to one basis vector; a call sends each basis vector to a combination of
at most two. So after g calls it has spread to at most 2^g addresses. But every entry of B^(⊗m) is ±1, so every
column has 2^m nonzero entries. Hence 2^g ≥ 2^m and g ≥ m. This holds at every width, width 1 included, and with
any free steps that send one address to one address. With scratch arrays and mixing the same count works path by
path through the program, for programs right at every width (PROOF.md, section 4). Status: argued by hand, not
checked by a person; AI reviewers re-derived it (the general version in two rounds). The width condition is needed
there: at width 1, one zero scratch array makes the transform free (section 3).

**(2) The gadget "I ⊗ B^(⊗3) acting on C^4 ⊗ (C^2)^(⊗3)".** In §8 he suggests a brute-force search: "Who knows,
maybe it's possible to write down a non-trivial gadget for I ⊗ B^(⊗3) acting on C^4 ⊗ (C^2)^(⊗3) or something silly
like that." That is 4 arrays at block 3, where plain costs 12 calls. By the block-3 bound, 4 arrays need at least
14 × 4 / 5 = 11.2 calls, and since 14 × 4 = 56 > 55 = 5 × 11, at least 12. So no such gadget exists among programs
that are right at every digit width, which is what amplification needs. Status:

- proved in Lean for C-calls with rational mixing, any relabellings, shifts, phases and scratch (`block3_bound`);
- argued by hand, not checked by a person, for complex mixing and for B-calls. The mixing enters the Lean proof at
  one step that uses only that the kept subspace is a complex subspace. A B-call at width f is (1 − i)^f times a
  C-call between diagonal phases, and neither a scalar nor a diagonal changes the cap or the demand at the one width
  the proof uses.

At width 1 the question degenerates: C^(⊗3) costs no call there (section 3). His remark that "achieving even one
fewer slice call, for a fixed m and W, is enough" is right for programs that stay right at every width, as his
constructions do.

**For a calibration run.** In his §7.4 model as written, blocks 3 and 4 never save: block 3 by the no-phase bound
(argued by hand; one AI reviewer) and block 4 by an exact linear-programming certificate for the commutative slice
(checked by computer; one AI reviewer rebuilt it). Both bounds are for programs right at every digit width. So a
search there must come back empty if it tests each candidate at width 2 or more (or symbolically). Tested at width 1
only, it will find programs with no calls at all (section 3). That makes it a good test of a search program. The
smallest engine-game shapes still open need more than that model: 5 in 14 at block 3 needs relabellings and phase
letters together (argued by hand), and 2 in 7 at block 4 needs relabellings or phases in the middle of the program,
or arrays mixed between its end letters (by the two computer checks in section 6). His §6 B-calls along relabelled axes
supply both.

## 8. How to re-check

```sh
python3 -B research/complex-small-m-lower-bounds/verify.py --part main       # PASS_COMPLEX_SMALL_M_LOWER_BOUNDS_MAIN
python3 -B research/complex-small-m-lower-bounds/verify.py --part controls   # PASS_COMPLEX_SMALL_M_LOWER_BOUNDS_CONTROLS
python3 scripts/research_package.py --package research/complex-small-m-lower-bounds --check-only
python3.12 -B scripts/research_package.py --package research/complex-small-m-lower-bounds
```

Standard library only; both parts together take a few seconds and under 50 MB. `--part main` checks: the block-2
and block-3 caps (exact vectors over the Gaussian integers, and attained), the block-2 demand, the block-3 demand
(a certified minor and the rank of the whole block), the two-call cap 144, the character block of rank at least 28 (two file
formats, two routines), the eight Lean data blocks, the face certificate of the no-phase bound, the block-4
arithmetic and the format of its certificate, the inputs 48,576 and 68,320 of the bound from block 4 on (re-derived
from small ranks, PROOF.md section 7) with the exact block-5 and block-6 bounds and the format of their two
certificates, the width-1 program, and every figure in sections 1 and 6.
`--part controls` feeds it corrupted certificates and false claims (a repeated row, a composite modulus, a row
inside the hook, a 225 × 225 minor, a changed vector, a repeated vector, a cap of 79, the three corrupted certificates of my
repository, one Lean inverse entry plus 1, a face cap of 7, a CNOT that should keep the face span, the width-1
program at width 2, three shapes on either side of a bound, a two-move certificate with a repeated pair or with the
wrong moves in its header, and two moves in the same direction claimed to count as two); each must be rejected.

Not registered (author evidence, outside the hub's limits):
- the block-4 demand: `cc -O2 -o check_m0 author-evidence/check_m0.c && ./check_m0 data/cert_m4_M0.txt` checks
  the 5,412 × 5,412 minor modulo 2,147,483,629 (determinant 1797789153; about an hour and 250 MB);
- the inputs 48,576 and 68,320 on all 16 characters: `cc -O2 -o check_mj author-evidence/check_mj.c`, then
  `./check_mj data/cert_m4_g2_M0.txt A` and `./check_mj data/cert_m4_g3_M0.txt A` for every character A = 0 to 15
  (32 runs, 42 minutes with six at a time on an Apple M4, at most 146 MB each; outputs in
  `author-evidence/out_check_m4_g2.txt` and `out_check_m4_g3.txt`, every one PASS);
- the Lean build (section 5; about 10 GB of memory);
- the written proof of the bound from block 4 on (`author-evidence/induction-across-block-sizes.md`; its AI
  reviewers' reports and programs are beside it in my repository), and the other bounds argued by hand, in my
  repository.

## 9. Limits of this work

- No person has read any of these proofs. Lean checked the Lean statements; AI agents tried to break the rest.
- Each bound is about its game. The Lean statements are for the engine game with rational mixing.
- The bounds are for units right at every digit width, which is what the recursion uses.
- Nothing here bounds κ, and nothing is claimed about integer multiplication.
- The open-case table lists what the quoted bounds leave open. A shape being open does not mean anyone expects a
  unit there.

## 10. Everything else

My repository's [research folder](https://github.com/jacobalansussman/wht-power-saving-lean/tree/86e575e28ed94890872dcff1bb2621d7ff559cbd/research)
has the rest of this work, each section with its programs, statuses and open problems: why the known savers save,
the Reed-Muller family and one-call units, existence routes, frame packing for two arrays, and speed on real
processors. Its `other-fields` folder has notes for readers from neighbouring fields. This note makes no claim from
any of them.

## Open next questions

The same questions, with first steps, are in `TASK.json`.

1. **5 in 14 at block 3** (6.28e-2), exactly on the bound. First step: decide one sector of the S8 sub-game exactly,
   one representative per symmetry orbit, judging each candidate by its end condition at width 6, not by cheap
   tests.
2. **2 in 7 at block 4** (9.63e-2). First step: an exact search confined to address maps in the middle and phase
   letters between calls; or a certificate above 3.5 calls per array, starting from the finite-group form of the
   best-bound relaxation at block 3.
3. **Block 3 in games with bounded free steps**: 2 in 5 (1.66e-1) or 3 in 6 (3.69e-1). First step: finish the
   third-layer case split for W = 2, s = m + 2.
4. **#288's open m = 3 cases in its full register model.** First step: list the free elements that model allows
   and test whether each keeps the hook (any map sending one address to one address, the same in every column,
   does).
5. **Lean for complex mixing, the widened game and block 4.** First step: change the mixing letter to complex
   matrices (one proof step uses it); for 41W/13, split the 16 character blocks further and time the kernel on one.
6. **Blocks 5 and 6**: 2 in 7 at block 5, 2 in 8 at block 6, and 3 in 9 at both. First step: the third-layer
   argument for "2 in m + 2 is impossible"; for 3 in 9, a certificate above 3 calls per array at block 5.

## AI assistance and credit

Substantial AI assistance: the programs, checks, proofs, Lean files and texts were written by AI agents (Anthropic
Claude) under my direction; I set the goals and chose what to pursue. The Lean proofs are checked by Lean's kernel.
No independent human review of this package or of the work behind it is claimed.

Credit: eumemic (#288) for the certificate method and the m = 2 and m = 3 results it builds on; Swapnil Jain (P1,
P2); jmbarrancoml (#2108); the bit-side authors above (aliromman, davidgovea, waynenilsen, navinor, huxint,
thakrarsagar); OpenAI for the Lean engine and cost model this game extends; Ryan Shea for the Lean tree the files were
built in; David Harvey for the questions of section 7; Maximilian Lutz (#4643) for an independent check of the bound
from block 4 on, which found that two of its inputs had no stored certificate and proved its tail for every k.

## Files

- `README.md`, `PROOF.md` (the written arguments, each headed by its status), `TASK.json`, `SOURCES.json`,
  `VERIFY.json`, `verify.py`, `.gitattributes` (`* -text`, keeps the data bytes exact).
- `data/`: certificates copied unchanged from my repository: `cert_m3_dem.json`, `cert_m3_B2.json`,
  `cert_m3_M0.json`, `cert_m3_M0_c.txt`, `cert_m2_M0.txt`, `cert_m4_M0.txt`, the three corrupted ones `neg_m3_*.txt`,
  and `Dem3Data.lean` (the certificate data of the Lean proof).
- `data/cert_m4_g2_M0.txt`, `data/cert_m4_g3_M0.txt`: the minor certificates for the inputs 48,576 and 68,320 of
  the bound from block 4 on (copied unchanged from my repository, added on 23 October 2026).
- `author-evidence/check_m0.c`: the C checker of the block-4 demand certificate (not registered).
- `author-evidence/check_mj.c`, `out_check_m4_g2.txt`, `out_check_m4_g3.txt`: the C checker of those two
  certificates and its output on all 16 characters (not registered).
- `author-evidence/induction-across-block-sizes.md`: the written proof of PROOF.md section 7, an unchanged copy (its
  relative links refer to my repository).

## Sources

- Hub base commit `f626db5c3a3d781d8f7695038776c621651f75e1`; task card `scope-navigation` (catalogue priority
  revision 7).
- Hub work credited: #288 (eumemic; `research/abelian-cayley-metric-scope/sources/pr288-README.md`, quotes from
  sections 1.1 (a), (b), the table row (f) and section 4); #2108 (jmbarrancoml; `research/two-register-three-mix/README.md`);
  #468 (`research/bit-three-register-lower-bound`), #720 (`research/three-register-no-target-flag`), #1882
  (`research/bit-dirty-auxiliary-registers`), #2167 (`research/bit-clean-ancilla-registers`), #825
  (`research/common-flag-frame-obstruction`), #203 (pull request still open), #2613 (`research/bit-full-borel-2adic-floor`); Swapnil
  Jain, P1 doi:10.5281/zenodo.23265442 and P2 doi:10.5281/zenodo.23266393.
- My repository: https://github.com/jacobalansussman/wht-power-saving-lean at commit
  `86e575e28ed94890872dcff1bb2621d7ff559cbd`, folder `research/`:
  - Lean: `block-bounds-and-new-rules/programs/lean-block2-block3/` (`PfLean/TheoremR.lean` lines 382-385 and 153,
    `Hook.lean` 196 and 432-434, `Bounds.lean`, `Dem3Final.lean`, `NegControl.lean`, `logs/statements.txt`,
    `logs/rebuild_2026-10-19.txt` (build of 19 October 2026 on a Colab machine), `skeptic-restatement/`); the
    engine's `GLiveKernel` is in `Work/GFrame/Engine/Letters.lean` (at the repository root, not under `research/`) lines 176-178.
  - Block bounds and certificates: `block-bounds-and-new-rules/README.md` sections 1-2 and its `results.json`
    findings 1-3, 7, 8, 10, 11, 13, 14, 20, 36; `programs/hook-certificates-blocks-2-to-6/` (`check_m3.py`, of which
    part `block3` of `verify.py` is a port, and `check_m0.c`); `data/hook-certificates/` (re-run log
    `rerun_check_m4_2026-10-19.txt`: determinant 1797789153, 56 minutes, 235 MB on an Apple M4);
    `data/engine-bounds-blocks-5-and-6/out_induct.txt` (834241/278850 and 1188222/399685).
  - Bounded games: `moonshot-small-blocks/README.md` section 4.1 and `results.json` findings 1 and 3;
    one array: `theory-of-theories-and-logic/results.json` finding 31 and `notes/zx-proof.md`.
  - No-phase block 3: `reed-muller-and-one-move/proofs/address-maps-per-array-targets-and-block3.md` section 8.9,
    `programs/address-maps-and-small-lift/independent-check/vk_face3.py` (ported in part `face3`), `results.json`
    findings RM1, RM3, RM5.
  - Commutative slice at block 4: `existence-routes/proofs/families-commutative-slice.md` (Theorem 17) and
    `results.json` finding 35.
  - Open cases: `open-problems.md`; `moonshot-block4-block5/results.json` findings 1 and 7 (the 640).
- Added on 23 October 2026, after #4643, in the same repository and folder: commit
  `ce3c2615cff7fc524c1fde3ddb99d151ba4ceee4` (the certificates for 48,576 and 68,320:
  `block-bounds-and-new-rules/programs/hook-certificates-blocks-2-to-6/` `gen_mj.c`, `check_mj.c`, `run_depth.sh`,
  and `data/hook-certificates/cert_m4_g2_M0.txt`, `cert_m4_g3_M0.txt`, `outputs/`) and commit
  `f08d308ff93f4867165a1e80765fe985c06b4edf` (`block-bounds-and-new-rules/proofs/induction-across-block-sizes.md`
  and its AI reviewers' reports beside it; `programs/engine-bounds-blocks-5-and-6/skeptic-checks/fcheck.py`, the
  split that part `depth` uses).
- An update to my earlier hub pull request #4268: its A-fc figure (1.7887046e-3, computed when that pull request was
  opened) has since been proved in Lean at 1.7887045e-3 and verified on the bigospeedrun board
  (https://github.com/bigospeedrun/verifier/pull/29; final verification result `lean_and_axiom_passed`, 21 October 2026).
- David Harvey, "On the recently proposed o(n log n) integer multiplication algorithm", UNSW Sydney, 20 October 2026,
  https://web.maths.unsw.edu.au/~davidharvey/research/subnlogn.pdf: §6 (single-array programs and "I do not follow
  the argument yet"; "achieving even one fewer slice call"), §7.1 (B = (1 − i)·S·C·S up to his normalisation),
  §7.2 (C_v), §7.4 (the allowed operations), §8 (the suggested search).
- Section 7's placement of his models comes from one AI agent's reading of his note against the Lean sources
  (22 October 2026), checked by two more agents, one on the models and one on numbers and statuses. The digit-width
  point and the B-call argument come from the model-checking agent alone; no other agent has checked them. The
  width-1 program is re-checked by `verify.py`.
