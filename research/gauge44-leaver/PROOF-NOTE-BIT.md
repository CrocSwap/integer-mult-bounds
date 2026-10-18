# PROOF-NOTE-BIT: citing the PR589 bit supplier with a derived rank-mass deficit (gauge44)

This note is BitCap's `PROOF-NOTE-BIT.md` from `complex-571-cold14-k492-bit589`, adapted to the gauge44 package. It
covers the only verifier change relative to #645's package (`research/gauge44-global`): the bit supplier changes from
PR543 to PR589. The complex side is #645's construction, unchanged: supplier word, recipes and every complex check in
`code/assemble.py`. The only complex-side change is the repacked owner map (`data/PLAN.json`, `data/OWNERS.json.gz`),
with expected values re-derived in `data/SPEC.json`.

## Changed sites

The changes are in `code/assemble.py`, plus one new stage in `verify_global.py` and a new file
`code/bit_supplier_controls.py`. The independent (non-verifier) `independent/price_profile.py` is ported to PR589 as well. Every other `.py` file equals #645's.

| # | site | before (#645) | after |
|---|---|---|---|
| S1 | bit input | `inputs/PR543-EXPECTED.json` from the multicold source, blob pin `b61d8598…` | `inputs/PR589-EXPECTED.json`, shipped in this package, blob pin `e293ddc5…`, through `load_bit` |
| S2 | bit deficit | literal `9984` | `bit_deficit(word, live)` = T(2Kv − L·cst), with L = 9, T = 32, K = (L−1)/2 = 4 |
| S3 | profile binding | (none) | Σ r·n of the bit profile = `bit.rank_mass`; moment width `BIT_M = 1 + 7L` asserted = 64 |
| S4 | pipeline binding | (none) | the record's `nine.pipeline` names the nine-stage template with 32 replicas |
| S5 | citation / receipt | input hash names the PR543 file | `bit_supplier` cites PR589 (head `a5afc8c6`, merged as `b3eb785a`, path `research/e8-bit-p111-tuned/tune/EXPECTED.json`) and records v = 111, cst = 63, COPY ranks [7×9] and the derived deficit 10272 |
| S6 | `verify_global.py` | (none) | stage `bit-supplier-controls` runs `code/bit_supplier_controls.py`; it requires status `PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS`, exactly 12 rejected controls and derived deficit 10272 |

The shipped `inputs/PR589-EXPECTED.json` has git blob `e293ddc557742637f9f679f083a1a282d87b1b13`, which equals
`origin/main:research/e8-bit-p111-tuned/tune/EXPECTED.json`.

## Why the derived deficit is correct

**The identity.** The rank-mass identity of #545 and #555 is M·live − mass = T(2Kv − L·cst). Its source is
#555's README, "Rank-mass identity", and `code/adapt9p.py`, whose audit carries `DEFICIT=T*(2*K*V-L*CST)`.

**The parameters.** The bit word has v live ports and decoder constant cst, the sum of the nine retained totals' COPY
ranks. The nine-stage chain is #463/#510 with 32 replicas, so L = 9, T = 32, K = 4 and M = 1 + 7L = 64. The live data
wires number 2KvT.

**The constraints checked.** The verifier asserts all of:
1. cst = Σ copy_ranks, with exactly `retained_totals` = 9 entries, each in (0, 8].
2. live = 2KvT. For #589: 2·4·111·32 = 28416.
3. Σ r·n over the priced profile = the record's `rank_mass` = 1808352.
4. M·live − Σ r·n = T(2Kv − L·cst). For #589: 64·28416 − 1808352 = 10272 = 32·(888 − 567).

Check (4) is #645's `check_moment` guard, unchanged. So v, cst, the profile and live must all agree.

**PR543 consistency.** The same formula reproduces #645's constant: PR543 has live = 30720, so v = 120; its nine
totals have COPY rank 8, so cst = 72; 32·(960 − 648) = 9984.

**The deficit does not raise c.** `check_moment` uses the deficit only as an equality guard. The moment engines
compute from (profile, m = 64, live, z) and never read it. The bit value c is established only by the unchanged
acceptance tests at the same exact endpoints, with the bit bad-residue surcharge retained: accept at c and reject at
c + 10⁻²⁴, by both engines.

## Effect on the outer chain (differs from the k492 package)

In the k492 package the complex side bound under either supplier, so κ did not move. Here it does. With the
gm3 map the complex side certifies b = 0.001654663299688920102557, with research/gauge44-bit589's dz1 map
b = 0.00165526410310589140991, and with research/gauge44-bit589b's L1g4 map b = 0.001655496738330440231813. PR543's c = 0.001653826988146798944268 is
below b, so under PR543 the bit side would bind. BitCap's table gives the PR543 bit-side κ cap as
0.001651096360425895, which is exactly the κ of `research/gauge44-repack`. PR589's c = 0.001733427039589844234749
exceeds b, so the complex side binds again (`binding = complex` in `ASSEMBLY.json`): κ = 0.001651929911890057 for gm3
(conservative 0.001651929909011672) κ = 0.001652528731617094 for dz1 (conservative 0.001652528728737236), and
κ = 0.001652760598550299 for L1g4 (conservative 0.001652760595670246).
Bit589Reviewer recomputed both suppliers with the outer engine and confirmed this. The gain over gauge44-repack therefore depends on this change and on the
assumptions below.

## Negative controls (all must be rejected; the verifier requires exactly these 12)

Each control runs the real `assemble()` on the fresh owner/invoice receipts with one input mutated. The strict run's
`BIT-SUPPLIER-CONTROLS.json` lists all 12 as rejected.

| control | site | rejected at |
|---|---|---|
| `revert_hardcoded_9984` | S2 | `check_moment` deficit guard (10272 ≠ 9984) |
| `ports_112` | S2 | `bit_deficit`: live ≠ 2KvT |
| `decoder_constant_64_copy_ranks_unchanged` | S2 | `bit_deficit`: cst ≠ Σ COPY ranks |
| `decoder_constant_64_with_one_copy_rank_8` (derives exactly 9984) | S2 | `check_moment` deficit guard |
| `eight_retained_totals` | S2 | `bit_deficit`: totals count ≠ 9 |
| `live_minus_one` | S2 | `bit_deficit`: live ≠ 2KvT |
| `profile_rank_mass_plus_one` | S2/S3 | `check_moment` deficit guard |
| `profile_rank_mass_receipt_mismatch` | S3 | profile mass ≠ `rank_mass` |
| `bit_lower_next_grid` | endpoint | `check_moment` reject-side moment test |
| `not_nine_stage_record` | S4 | pipeline binding |
| `tampered_bytes_next_grid` | S1 | blob pin |
| `pr543_file_under_pr589_pin` | S1 | blob pin |

Bit589Reviewer re-traced all 12 rejection sites on the gauge44 word (b589gm3), and they match the table: `code/assemble.py` L191 (`revert_hardcoded_9984`, `decoder_constant_64_with_one_copy_rank_8`, `profile_rank_mass_plus_one`), L48 (`ports_112`, `live_minus_one`), L47 (`decoder_constant_64_copy_ranks_unchanged`, `eight_retained_totals`), L201 (`profile_rank_mass_receipt_mismatch`), L197 (`bit_lower_next_grid`), L179 (`not_nine_stage_record`) and L39 (both blob controls). dz1 and L1g4 run the same code.

The ported `independent/price_profile.py` re-derives the deficit separately (`pr589_deficit`) and checks the same blob pin. Its regenerated receipt on this package's PLAN gives the same κ.

## Inherited assumptions

**PR merge status (`gh pr view`, 2026-10-13):** #589 MERGED 2026-10-12T17:00:38Z. #555 was merged 2026-10-12. #645
is OPEN. Main's review replayed #589 freshly as "supplier-only headroom", and main's *selected* composition still
cites #543.

**Unmerged assumptions:**
1. **#645 itself (open):** the gauge44 factory, its construction steps and all of its retained interfaces and notes.
   These are unchanged here.
2. **This verifier change (S1–S6):** under review (Bit589Reviewer). The PR589 record replaces PR543 as an *input of
   the gauge44 assembly*, a composition main has not selected.

**Assumptions carried by #555/#589 (merged, stated there as review points, not theorems):**
3. #545's punctured unit: a 111-port unit with decoder constant 63 is an admissible bit supplier on the same hypotheses
   as v = 120.
4. #510's nine-stage chain as re-parameterised for v ≤ 120 by #555's `code/adapt9p.py`, including the rank-mass
   identity used in S2.
5. #543's interleaved scalar-interface lemma (H1–H5) for phase-B source rewrites. This is not new: #645 already
   inherits it through PR543.
6. #589's two A-section transports.
7. The same bit bad-residue surcharge model as PR543 (`surcharge_model = {'complex': False, 'bit': True}`).

## Result

The bit-supplier change is the same as in research/gauge44-bit589 and gauge44-bit589b: the code is byte-identical and was signed by Bit589Reviewer. For this package (leaver word fo_hyb, FO_c1 map), the complex side certifies b = 0.001667007898013796187659 and binds under PR589. Under PR543 the bit side would cap κ at 0.001651096360425895. κ is given in the README and `RESULT.json`.
