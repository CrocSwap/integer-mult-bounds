# Noncommuting stages work for every controller size: the descending-support invariant

**Claim type:** a written proof with a mechanized check. **No new κ.** Together with the reduction lemma of
my #4540, this answers open question 2 of Dugongue's
[#4534](https://github.com/CrocSwap/integer-mult-bounds/pull/4534) ("an all-p inductive free-algebra
identity").

## Theorem

Take #4440's complex p-controller for any `p ≥ 1`, any keep mask, and either the full stage set or the
thick-stage thinning that #4440 and #4470 use. Every word occurring in its operator matrix
`W ∈ Mat_{2p}(ℚ⟨d_s⟩[q, q^{−1}])` is a strictly descending sequence of distinct stage letters.

**Corollary.** Abelianization is injective on the support of `W`. By #4540's lemma, any scalar commutative
factorization `L W_ab R = diag(q^ε d^α)`, for example the one #4440's `factor()` computes, is also a
factorization in the free algebra, with `D_s` noncommuting among themselves and commuting with `Q`. #4534
proved this only for the fixed p16 word.

## Proof

Lines start as empty words, and later operators are prepended on the left. Only two kinds of event add
letters:

- `LOCAL(s, pair, ·)` first shears one line of the pair into the other, which merges words, and then
  prepends `d_s` to both lines.
- `IDLE(pair, S)` prepends the block `d_{max S}⋯d_{min S}` to both lines.

`ADD` merges word sets, and `SWAP`/`SIGNED_SWAP` move them; neither creates letters. So it suffices that
**every prepended letter is larger than every letter already on its target lines.** Follow
`complex_controller_factor.controller`:

1. **Stage order.** Locals run in the order `0, 1, 2, …, 2p`. `LOCAL(2j+1, j)` and `LOCAL(2j+2, j)` act on
   pair `j`. Until its own locals run, pair `j` holds only letters `≤ 2j`, and only from its own middle idle
   and its initial block.
2. **Initial idle**, after stage `2j+1`, on pair `j+1` with `S = {0, …, 2j+1}`. Pair `j+1` is still
   untouched: bridges so far only mixed pairs `≤ j`. So its words are empty, and the block lands on empty
   words.
3. **The bridge `(j, j+1)`** merges words with letters `≤ 2j+1`. Then `LOCAL(2j+2, j)` prepends `2j+2`,
   which exceeds every letter present.
4. **Middle idle**, after stage `2j+2`, on pair `j+1` with `S = {2j+2}`. Pair `j+1` carries letters
   `≤ 2j+1`.
5. **Terminal idles**, after stage `2p` and before the final bridges, on pair `j` with
   `S = {2j+3, …, 2p}`. After iteration `j`, pair `j` is never touched again until this point, and it
   carries letters `≤ 2j+2 < 2j+3`.
6. **Thinning and keep masks.** Thinning deletes letters from prepends. A keep-mask bit `0` deletes a whole
   idle. Deleting letters preserves "new letters exceed old ones".

So every word is strictly descending with distinct letters. ∎

## Mechanized check (`verify.py`)

The actual constructor emits its event stream, with its polynomial arithmetic stubbed out, since the event
sequence does not depend on it. The verifier tracks the largest letter on each line and checks the
strict-increase condition at every prepend. It covers every `p` from 2 to 60, with keep masks all-ones,
all-zeros and three random masks, both with and without thick-stage thinning: **590 cases, all passing**.
A control in which an old stage is prepended again is rejected. `evidence/` records the same check up to
`p = 200` (440 cases). My #4540 already confirmed the full free-algebra identity directly for `p ≤ 14`.

## The BIT controller

#4440's binary controller, `bit.physical_controller` over `F₂[(ℤ/2)^{2p+2}]`, runs the identical stage and
idle schedule. The verifier checks the same invariant on its event stream, with idle bitmasks decoded to
stage lists: **590 more cases**, `p ≤ 60`, five keep masks, with and without thinning. All pass.

Because no letter repeats within a word, the group-ring relation `d² = 1` never acts on the support.
Abelianization is therefore again injective, and the same corollary applies on the BIT side.

## Not covered

- Existence of the commutative factorization for every `p`. This is #4440's constructor claim.
- The physical realization of noncommuting `D_s`. That is #4534's open question 1.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/descending-invariant-allp --check-only
python3.12 -B scripts/research_package.py --package research/descending-invariant-allp
```

The verifier prints `PASS_DESCENDING_INVARIANT_ALLP` in about a minute, using only the standard library.

## Open next questions

1. **A physically priced noncommuting stage family.** This is #4534's open question 1; the algebra
   now permits any `p`.

## Credit

- The controller is Cinna Davis's (1337isnot1337, #4440).
- The question and the p16 theorem are Dugongue's (#4534).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
