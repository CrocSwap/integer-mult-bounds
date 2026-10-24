# Admissible quotient kernels of the #4596 word

**Claim type: finite certificate with a scoped proof.** No κ is claimed. The
result is conditional on the open pull request #4596 and on the endpoint
question raised in #4604 (see [Conditions](#conditions)).

DaysSky's open #4596 quotients the nine-axis ambient of the PR4470 complex word
by `span{511}`, re-pads one helper so the word still spans nine axes, and
reports a complex supplier saving of 0.012091850234. Its `PROOF.md` leaves
open "Whether `511` is the unique removable direction". This package answers that
question for the check #4596 itself ships.

## Result

Over all 511 nonzero directions `v` of F₂⁹, build the #4596 quotient word for
`span{v}` and replay it with the shipped literal replay
(`native_extensions.literal_replay` with the `verify_buffers.expected`
endpoint table, both orientations, owned C cleared).

1. **Exactly 32 directions are accepted.** The other 479 all fail the same
   shipped check, "Paid rank and source frame".
2. **The accepted set has an exact description.** The base word has eight centre
   transports, each between the ground frame and a dim-8 frame, charged rank 8.
   Those eight frames are hyperplanes of F₂⁹ with normals
   {7, 25, 42, 52, 76, 82, 97, 127}, of GF(2) rank 4. A direction is accepted
   exactly when it lies outside all eight hyperplanes, that is
   `{v : λᵢ(v) = 1 for all i}`. This is a coset of a 5-dimensional subspace, so
   it has 2⁵ = 32 points, and it does not contain 0. The normals use only bits
   0–6, and each normal is itself outside all eight hyperplanes, so the set is
   `{h + 128i + 256j : h a normal, i, j ∈ {0, 1}}`.
3. **511 is not the best direction.** The best is `v = 153`:

   | Kernel | Main widths | Paid rank mass | Local deficit | Rank surplus | Complex saving |
   |---|---|---|---|---|---|
   | 511 (#4596) | {7: 112, 8: 112} | 4834 | 1744 | 2768 | 0.012091850234 |
   | 153 | {7: 168, 8: 56} | 4778 | 1688 | 3776 | 0.016567169219 |

   The next two are 338 (0.016555611423) and 180 (0.016552449914), both with
   deficit 1688 and surplus 3776. Twenty-four accepted directions, 153 and 511
   among them, keep the helper profile {3: 2, 4: 26, 6: 7, 7: 47, 8: 325, 9: 1};
   the other eight (7, 52, 82, 97, 391, 436, 466, 481) widen both rank-3
   helpers to rank 4. The saving is #4596's invoice and dual-moment screen
   applied unchanged.
4. **No kernel of dimension 2 or more is accepted.** A 2-dimensional kernel
   needs three nonzero vectors outside every centre hyperplane. The accepted
   set is a coset that does not contain 0, so the sum of two accepted
   directions lies in the difference subspace, which meets the coset nowhere.
   The verifier checks this over all pairs.
5. **Under the stronger geometric condition, 511 is unique.** Require that
   every dim-8 main final keeps dimension 8 under the quotient, that is, that
   `v` lies outside all of them. The 112 distinct dim-8 main finals have
   normals of full rank 9, and the only direction outside all of them is 511.
   This is the condition #4596's construction meets; the shipped replay does
   not check it.

So the answer to #4596's question depends on the condition. 511 is the unique
direction that keeps every dim-8 main final at dimension 8, but 32 directions
pass the shipped replay, and 153 prices 37% higher on the complex side.

## What this does not change

The outer κ in #4596 is limited by the BIT side (0.0034), not by the complex
supplier. A larger complex saving does not move it until the BIT admission
chain moves. This package claims no κ.

## Conditions

- **#4596 is open.** The quotient construction, the helper re-padding and the
  invoice are #4596's. This package re-uses them unchanged; if #4596 is not
  accepted, this classification describes an unaccepted construction.
- **#4604's endpoint question applies here too.** pinterbanget's open #4604
  shows that under the 511 quotient every main output frame changes, and that
  the shipped replay compares final frames with the word's own record, not
  with required output charts. The 32 accepted directions pass that same
  replay, so they inherit the same question. If output charts are part of the
  supplier contract, none of the 32 quotient words, including 511, meets it.
- **The 479 rejections come from one hard-coded rank.** `synthesize` charges
  every centre transport rank 8. A quotient is accepted only if each centre
  frame keeps dimension 8, which is the hyperplane condition in item 2. A
  pipeline that recomputed centre ranks would accept a different set; that
  variant is not studied here.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -W error -B research/quotient-kernel-family/verify.py                  # about 30 s
python3.12 -W error -B research/quotient-kernel-family/verify.py --scan 1 255     # about 100 s
python3.12 -W error -B research/quotient-kernel-family/verify.py --scan 256 511   # about 100 s
python3.12 -W error -B research/quotient-kernel-family/verify.py --physical 153   # exact lowering
python3.12 -W error -B research/quotient-kernel-family/verify.py --physical 511
```

The default run checks items 2 to 5: it derives the eight centre hyperplanes
from the base word, checks the normals, rank, coset and pair conditions, checks
the 112 main-final hyperplanes, replays all 32 predicted directions, checks the
declared profiles for 153 and 511 and the two helper profiles, and replays
four rejected controls. The two `--scan` shards replay every
direction and require the shipped replay to accept exactly the predicted set
(item 1). `--physical` lowers every realised transport of one quotient word
exactly and requires Fourier rank equal to the absolute dimension difference,
the convention of the shipped evaluators (`native_extensions.py` line 127,
`verify_buffers.py` line 151).

`quotient.py` builds the base word from the pinned main packages and the
quotient words; it writes no files.

## Limitations

- Finite certificate over one word. The base word is fixed; other words or
  other quotient maps are not covered.
- The complex saving is computed with #4596's float bisection of the dual
  screen. A directed-rounding recomputation during development agreed to
  2·10⁻¹⁷ for 153 and 7·10⁻¹⁷ for 511; that recomputation is not shipped.
- Physical lowering was checked for 153 and 511 only, not for the other 30
  accepted directions.
- No formal proof, no Lean, no selected-construction replay.

## Open next questions

- Does an operator-level endpoint check (#4604's open question) accept any of
  the 32 quotient words, or does it reduce the admissible set to the empty set?
- If centre ranks are recomputed instead of hard-coded, which kernels pass, and
  is any of them better than 153?
- Does a different base word have a centre-hyperplane family of lower rank,
  and so a larger admissible coset?
- Does #4596's controller strictification hold when its controller targets come
  from a quotient word? An unverified local substitution gave a negative margin
  on the delta row for all 32 directions, 511 included. This needs an
  independent check before any outer κ is claimed for the family.

## Credit

This package was produced by Nick Petalas. The quotient construction, helper
re-padding and invoice are DaysSky's (#4596). The base word is Cinna Davis's: query thinning
and helper retiming (#4441), the missing join frame (#4447) and joint helper
boundaries (#4470), on zxv's native supplier. The endpoint-contract question
is pinterbanget's (#4604).
