# Selected bootstrap cutoffs omit the carried constant

**Scoped audit of one finite lemma instantiation. The numerical κ is unchanged and no new bound is claimed.**

The selected record's assembly (`research/community-frontier1094-audit/ASSEMBLY.json`, SHA-256 `1122cb3a…`)
records seven finite bootstrap cutoffs per branch (`bootstrap[*]` and `conservative_bootstrap[*]`). The frozen
PR1087 `code/assemble.py` computes them as

    cutoff_log2 = max(ceil(36/gap^2), ceil(2*(4+512)/gap)),

so it takes `ceil(log2 C) = 512` at every stage. Two proof notes state the lemma these numbers instantiate:
[PR387's PROOF](../bootstrap-depth-audit/sources/pr387/PROOF.md) and
[FINITE_BIT_ACCOUNTING](../five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md), "Finite ordinary bootstrap
and cutoff". In both, the stage constant C dominates "previous ordinary constants". Both also fix the next
constant as `C_large + C_old*2^(L*(a_(j+1)-a_j))`. That carried factor alone gives the next stage
`log2 C >= L*(a_(j+1)-a_j)`, far above 512.

## Result (exact rationals)

- All 14 recorded cutoffs reproduce from the receipt's endpoints, the chain start `a0 = 384599/10^10` and
  the formula. Stage 1 is valid in both branches.
- **Stages 2–7 fail in both branches (12 of 14).** The test uses the most favorable carry: `C_old = 1`, no
  `C_large`, and the recorded (smaller) previous cutoff. Each recorded cutoff then pays only about half of
  the required linear term. The shortfall ratio is `1.996649…` at every failing stage.
- **Closed form.** The binding gap is `δ_i = s − a_(i+1) = s(s − a_i)`, so `δ_(i+1) = sδ_i` and
  `a_(i+1) − a_i = (1−s)δ_i/s` exactly. Any valid stage-i cutoff has `L_i ≥ 36/δ_i²`, so the next carry is
  at least `36(1−s)/δ_(i+1)` bits. The quadratic cutoff `⌈36/δ'²⌉` gives `Lδ' < 36/δ' + δ'`, while the rule
  needs `Lδ' ≥ 8 + 72(1−s)/δ'`. Both hold only if `δ'² − 8δ' > 36(1−2s)`, which is impossible for `s < 1/2`
  and `δ' < 8`. As δ → 0 the shortfall tends to `2(1−s)`. The argument uses only the recurrence and the
  formula. It therefore applies to any stage after the first whose recorded cutoff is the quadratic term.
  With a fixed allowance that is every stage once `18/δ − 4` exceeds the allowance, which is all of them
  here. This predicts the same failure in the T37 lineage (1024-bit allowance) and in the deeper chains of
  open PRs #1424, #1586 and #1724. **Only the selected record is checked by the registered verifier.**
- **Supplementary scan.** `scan_receipts.py` is not part of the registered replay. It reads every in-repo
  `research/*/ASSEMBLY.json` that records cutoffs: 12 receipts and 23 branches, including the #741, #799,
  #890, #942 and #1042 frontier audits and the T37 1024-bit receipt. It checks stages 3 onward using
  recorded exponents only, with no assumed chain start or allowance. All 114 such stages fail the
  minimal carry.
- **Corrected chain.** Take the least cutoffs that satisfy the rule, with `ceil(log2 C)` carried as
  the upper bound `max(512, ℓ + ⌈L·Δa⌉) + 1`. "Least" is relative to this propagated bound and the
  receipt's own assumption that each stage's fresh constants stay below `2^512`. It is not a minimum
  over the actual, unmeasured constants. The corrected cutoffs are about `2^(i−1)` times the recorded ones: stage 7 has 48 decimal
  digits instead of 46. The carried constant reaches about `1.9·10^25` bits. A positive control substitutes
  these cutoffs in memory and confirms that every stage then pays the carry.
- **The numerical κ calculation is unaffected.** The pinned outer engine (`engines/outer.py`, `c1ebb521…`) has signature
  `assembly(bit_saving, complex_saving, bridge, kappa, eta, beta)` and never reads a cutoff. Both branches'
  κ reproduce exactly from the chain end, η and the 10^-18 grid. At fixed depth the asymptotic statement
  needs only *some* finite cutoff per stage. That conclusion still rests on the bootstrap lemma itself,
  under either repair below. This package does not discharge that obligation.

So the recorded `cutoff_log2` values are not valid instances of the lemma **as written**. The finding is
conditional on that wording. It is a receipt/proof-text inconsistency, and this audit does **not**
establish that the bound fails. There are two repairs:
(a) carry `C_old` into the cutoff, which yields the exact corrected chain above; or (b) restate the lemma so
that previous-algorithm tolls are absorbed against the new constant (which already exceeds
`C_old·2^(LΔa)`), so that C counts only fresh toll coefficients. Option (b) is the usual "choose the induction constant
large" argument, and we expect it to go through. The recorded numbers would then be valid, and only the
proof text would change. It still needs a written argument, which this package does not supply.

Related work: [complex-t37-validation](../complex-t37-validation/README.md) (`check_bootstrap_reserve.py`) and
[frontier1042-invoice-audit-seed81](../frontier1042-invoice-audit-seed81/README.md) check the same cutoffs
against a *fixed* 512/1024 allowance. Those checks are correct for a fixed allowance. This audit asks
whether a fixed allowance matches the lemma. [bootstrap-depth-audit](../bootstrap-depth-audit/README.md)
and [t37-bootstrap-depth-seed60](../t37-bootstrap-depth-seed60/README.md) study the number of levels, not
the cutoffs.

## Reproduce

```sh
python3 -B research/bootstrap-cutoff-carry/verify.py
python3.12 scripts/research_package.py --package research/bootstrap-cutoff-carry
python3 -B research/bootstrap-cutoff-carry/scan_receipts.py   # supplementary, unregistered
```

Expected: `PASS_BOOTSTRAP_CUTOFF_CARRY_AUDIT recorded=14 fail_with_carry=12 stage1_valid=2 corrected=14
kappa_independent=1 controls_rejected=6`, in well under a second. The run uses the standard library only.

The verifier checks every input against [SOURCES.json](SOURCES.json). It reads `code/assemble.py` from the
pinned `upstream1087.tar.gz` and binds the lemma text, the 512 formula and the cutoff-free outer signature.
It compares its summary with [RESULT.json](RESULT.json), which records digit counts and a hash of the
corrected cutoffs.

Six controls must be rejected:

1. a recorded cutoff shifted by one;
2. the next-grid κ;
3. a shifted starting saving;
4. a corrected cutoff minus one, which shows the corrected chain is minimal;
5. the recorded cutoffs under the carry rule;
6. the pinned outer engine source, mutated in memory so that `assembly` takes a `cutoffs` argument.

Controls 1–3 test the receipt binding, 4–5 the carry rule and 6 the κ-independence check. One more
positive check: dropping the carry from the corrected chain reproduces the receipt's 14 cutoffs
exactly.

## Not checked

- Whether `C_old` must enter the lemma's C at all, that is, whether repair (b) holds.
- What the fresh per-stage constants actually are. The 512 allowance is taken from the receipt.
- Open PRs' receipts (#1424, #1586, #1724 and others). The in-repo scan covers stages 3 onward only, and
  it is not pinned.
- Every inherited all-size, precision, hosting and analytic obligation of the selected record.

## Open next questions

1. **Does repair (b) hold?** Write the stage-j induction with the new constant A ≥ C_old·2^(LΔa) and
   check whether the cutoff needs only fresh toll coefficients. If it does, the recorded numbers stand
   and only the proof text changes. If it does not, every lineage's recorded cutoffs need the carry.
   *First step:* restate the FINITE_BIT_ACCOUNTING induction with explicit toll terms. *Blocked by:* the
   toll inventory is spread across inherited proofs.
2. **Open PRs with deeper chains.** The in-repo receipts all fail (see the scan). Do the open PRs #1424
   (12 levels), #1586 (82) and #1724 (240) also fail, and how large do their corrected cutoffs get?
   *First step:* run `scan_receipts.py` on each PR head's receipt.

## Credit

The cutoff lemma and the next-constant rule come from rohanarun's PR387 PROOF and eumemic's five-stage bank
proof (`five-stage-source527-banks`). The bootstrap chain and the 512 allowance are retained in the frozen
PR1087 assembler (Jeremy Kothe's package, with its credited lineage) and Rohan Arun's PR1094 selected receipt. The outer engine is credited in its
header. Fixed-allowance checks are by Tekalign (complex-t37-validation) and Wronskode (frontier1042 invoice
audit). Prepared by Josie Elliston with Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
