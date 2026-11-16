# CONDITIONAL κ = 0.0036614625547 — 1445/1461 courier and helper-226 re-stop on #7620 (premises: exactly #7620's)

**κ = 0.00366146255478988…, ×1.00009831 (+0.009831%) over
[#7620](https://github.com/CrocSwap/integer-mult-bounds/pull/7620)** (SYLforge's stationary primal/dual
composition, conditional κ 0.003661102618151). The official `evaluate_recursive_power` bracket (256 bits) is
[0.0036614625547, 0.0036614625548]; the claim 0.0036614625547 is below the exact crossing 0.00366146255478988.

> **Premises (inherited, nothing new).** Conditional on exactly #7620's premises: its five framework
> assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`),
> its reading of the 167 CLEARs (74 original + 93 stationary lifetimes), and its fixed allocation of
> 17·68 = 1,156 owned banks. This word's rows, end charts, owned data (47 owned MOVEs, 167 lifetimes,
> peak 50, all 1,018 owned observations) and all 167 CLEAR contents are identical to #7620's. If #7620's
> premises are refused, this word is void with #7620.

## The edits

Two changes to #7620's word (77,194 → 77,196 events; per native call ADD +2, nothing else).
[data/edits.json](data/edits.json) lists every event by #7620 index (18 deletions, 8 insertion groups).

1. **Courier (funded-return) move on 1445/1461.** Transit 1445 drops chart 755 (3→755→757 becomes 3→757).
   Courier 1461, co-present with 1445 at chart 3, carries 1445's content through the determinant-one shear
   pair `1461 += −2·1445`, `1445 += (2/3)·1461` and stops at 757, where the inverse shears
   `1445 += −(2/3)·1461`, `1461 += 2·1445` decode. The 207/971 reads of 1461 slide earlier to chart 3, the
   395 read becomes `1461 += −(3/2)·395`, and the 1157 read at 755 is unchanged in effect. Both shear
   coefficients are 5-smooth (alphabet of main's #7000 check); non-dyadic literal events 5,901 → 5,903.
2. **Helper 226 re-stop.** 226 goes 3→86→260→**906**→127 instead of …→719→127 (dimensions 3→6→9 become
   3→7→9). Its encode `990 += −226` (the courier pair 226/990 already in #7620) is slid earlier, to chart
   260 right after 226's last chart-260 write; MOVE 473 719→906 slides earlier, to just after `990 += −473`
   at 719; 473 receives 226 at 906. A harmless swap of two independent MOVEs (224 and 226) into chart 260 comes
   with it.

Chart pairs: two new, both strictly nested — (3,757) dimension 0→6 and (260,906) dimension 3→7; (719,127) and
(755,924) leave the MOVE pairs. Rows (all 1,569), end charts and header equal #7620's.

## Price

Native paid delta per call {1:+1, 2:+1, 3:−3, 6:+1}; over 17 calls {1:+17, 2:+17, 3:−51, 6:+17}.
Paid positions 110,145 (unchanged), productive 22,461, rank surplus S = 1,424 (unchanged).

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` against #7620: `uniformly_better`, strictly negative for r^(1−C),
  targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits): `new_cost_lower` at C = 0.0036614625547, 0.0036611026181
  (#7620) and 0.0036576002522 (#7617); `new_cost_higher` at C = 0.0036614625548.

Ordinary bill (17 calls, #7000 formula) 785,021,584 → 785,022,672 < 10^9; precision bit bounds 303 / 299 / 299
unchanged; common grid 2^25·1125 with 40 numerator bits equals #7620's. An independent read-only audit found the word sound
relative to #7620 (exact replay; official #7000 native engine with bad_inputs 0; strictification gate
passed, γ 0.941422, δ 0.908156; 24/24 rejecting controls; every one of the 1,018 owned observations — operation,
source-row content and destination-row content — identical to #7620's).

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-courier-restop-on7620
```

`check.py` (standard library; `core` and `columns` modes are registered as two commands, `all` runs both; the
column tests use worker processes) authenticates the vendored #7620 word, rebuilds the new word from the edit
list, replays both exactly over the rationals with legality checks, requires every row, end chart, owned MOVE,
lifetime and the header to equal #7620's and all 167 CLEARs to erase #7620's content, checks that only registers
226, 1445 and 1461 change their MOVE chains (endpoints kept) and that the changed routes are exactly those
described above, locates the encode/decode shears of 1445/1461 and 226/990 and checks them as exact inverses in
reverse order around the transit MOVE, requires exactly the two new strictly nested chart pairs, recomputes the
invoice and κ and reproduces #7620's crossing, and runs rejecting controls (wrong coefficients, dropped or
sign-flipped encodes and decodes, transit MOVE after its decode or kept at 755, flipped ownership flags,
reversed or non-nested MOVEs, encode retagged at 719, re-stop MOVE after its consumer, 473 MOVE left late, old
395 coefficient) plus a tampered invoice.

**Affected-pair column tests.** #7620's native runner pins an exact census of 837 affected chart pairs (versus
the #7481 comparator) and tests each with 512 forward and 512 adjoint Gaussian columns plus absolute-phase
checks. This word's census is 846: the 837 pinned pairs, minus (719,127) (no longer a route of any changed
register), plus the 10 pairs on the old or new routes of the changed registers — (3,755), (3,757), (260,906),
(755,757), (755,924), (757,923), (757,924), (906,127), (923,127), (924,127). `check.py` carries the equivalent
tests, written independently from the description in #7620's files (read as data; nothing from #7620 or its
dependencies is executed): for each pair it builds F_a† F_b from the two nine-bit stabilizer frames, compiles it to
a child recipe monomial·Fourier^r·monomial, requires exact public ascent rank r = dim b − dim a, equality of
signed Pauli action and exact absolute phase with the direct circuit, equality of all 512 forward and 512 adjoint
Gaussian columns (846 × 1,024 = 866,304 columns), and rejection of a wrong absolute phase. Controls: a non-nested
pair, shifted-offset recipes and global-phase errors on both new pairs are rejected. The new word's hash and
event census are pinned in `check.py`; `data/affected-pairs-7620.json` is the pinned census copied as data.

## Conditional premises and what is not rerun

The claim carries exactly #7620's premises (above) and the signed #7113 caller and BIT premise of the base. This
package does not rerun #7620's full native/signed 17-stage application, signed catalogue, outer predicates or
precision/tape counts (header, rows, grid and owned data are unchanged); the audit above ran the official #7000
native engines on the word. No upstream maintainer has reviewed the package.

## Credit

The base word is SYLforge's #7620 (and #7616, on which it builds, with the packages named in their notices). The
courier pattern is the crowd's: Clear1nsight's #7244/#7274/#7314/#7334/#7481 funded-return chain, rohanarun's
#7480 and #7277, CubeJerry's #7577 and petalas's #7326 (see [NOTICE](NOTICE)). The same pattern was applied on
earlier bases in our [#7615](https://github.com/CrocSwap/integer-mult-bounds/pull/7615) and
[#7617](https://github.com/CrocSwap/integer-mult-bounds/pull/7617). DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. Apache-2.0.

## Open next questions

**The premises.** A ruling on #7620's inherited assumptions and its 167-CLEAR reading (`owned_erasure`,
clear-form-gap Q1) decides #7620 and this word together. See [TASK.json](TASK.json).
