# Framed necessity of H2-sem condition 2 (scoped falsification)

## Proposition

Let W be the pinned selected R439 word
(`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`). Write H2-sem
for the exact contract of PR1194
(`research/r439-semantic-d-contract-seed10/PROOF.md`):

1. zero-frame D gates with distinct Y/H operands and no source reads;
2. no target feeds a helper or source inside D (retained H1 inside D);
3. complete D operator (x, y, h) → (x, y + N h, h) for a fixed binary matrix N.

Let F4 be the *target-feeding-helper wrap* recorded as a boundary probe in
PR1782: with the seed-42 best oriented pair (a, b) = (277, 434) and the unique
last D target t written exactly once at index k = |D| − 1,

- prepend and insert the restored conjugation a += t; …; a += t with the closing
  restore placed immediately before gate k;
- on every earlier gate that reads a, replace a by a ⊕ t in the source list.

**Claim (scoped).** On this F4 word:

- H2-sem conditions 1 and 3 hold, and the semantic matrix N equals the raw
  helper response K of (A, scatter, B) and the baseline N;
- frames at the D/A cut equal the baseline;
- condition 2 fails;
- the complete framed sectional replay on all 661 basis columns equals the
  desired dirty boundary (x, y, h) → (x, y + x, h), and the independent
  literal forward/reverse XOR programs agree;
- the proof-only virtual splice that restores the original target-only D still
  passes every inherited H1–H5 / U / J / K / C flag.

Consequently, on this exact instance, condition 2 is **not necessary** for the
framed endpoint substitution conclusion that the chronological bridge is meant
to transfer. It remains a hypothesis of the written PR1194 block argument; this
note does not supply a general replacement lemma that drops condition 2 for
every wrap.

## Exact costs (F4 versus baseline)

| Quantity | Baseline | F4 | Delta |
| --- | ---: | ---: | ---: |
| D gates | 111 | 113 | +2 |
| D source reads / D ADDs | 18085 | 18154 | +69 |
| Whole-word ADDs | 24305 | 24374 | +69 |
| Paid profile | {1:1323,2:1342,3:79,4:44,5:102,6:11,7:19} | same | 0 |
| Rank mass | 5129 | 5129 | 0 |
| Positive F | 49347 | 50535 | +1188 |
| Positive B | 1113070 | 2995586 | +1882516 |
| Local guard `64 F³ B²` | 93 bits | 96 bits | still < 2^104 |
| Nine-stage guard | 177 bits | 183 bits | still < 2^192 |

F4 is a necessity probe, not a saving construction: it raises ADD count and
envelopes while leaving the paid profile fixed.

## Why the endpoint can hold without condition 2

Condition 3 already forces every helper and source row of the D operator to be
the identity and every target row to be the identity plus a helper-only shear.
The temporary target→helper conjugation in F4 is closed before t's own write, so
the net D matrix still meets condition 3. Non-D sections are byte-identical to
the baseline, so the raw K, the virtual original-D splice, and the continuation
after the D/A cut are unchanged. Equality of the D operator on F₂ coefficients
gives equality on every F₂-module stream (PR1194's module argument), and the
framed sectional replay confirms the cut frames match.

Condition 2 is therefore independent of the endpoint identity on this instance:
it fails while the framed dirty boundary holds. The inherited checker still
reports `H1_no_target_feeds_z` (and the documented syntactic H2 / K failures),
so F4 is *not* admitted by the published H2-sem contract; the claim is only that
condition 2 is not required for the endpoint conclusion itself.

## Controls

- **Unrestored feed.** Dropping the closing a += t breaks condition 3 (a helper
  row moves).
- **Late restore.** Closing the conjugation after t's own write breaks condition 3.
- **C1 contrast.** The PR848 helper-temp wrap on the same pair satisfies all
  three H2-sem conditions and saves 65 D reads; it is the admitted comparison
  point, not the necessity witness.
- **Baseline.** The unwrapped word passes every inherited flag and matches the
  same endpoint and paid profile.

## Limits

No new κ, no supplier adoption, no claim that every target-feedback wrap is
safe, and no rewrite of PR1194's published hypotheses. All-size compiler,
hosting, tape/rounding and analytic obligations remain inherited. Finite
replay supports the scoped falsification; it is not a formal proof of the
multiplication theorem.
