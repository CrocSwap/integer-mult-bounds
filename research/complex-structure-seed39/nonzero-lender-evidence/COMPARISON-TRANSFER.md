# Exact comparison transfer, not a seed39 exponent certificate

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Apache-2.0. This note identifies the numerical target for the complete
supplier/outer verification. It does not admit either package's theorem.

The inspected comparison is open PR2374 at immutable head
`5449da65da12bdfd94675dccc38731eaa91e93b6`, package
`research/gmx-t74-borrow43-handoff`. The live metadata acquired on
2026-10-15 matches that pin. The copied `PR2374-check_ledger.py`,
`PR2374-SPEC.json` and `PR2374-OUTER-CLAIM.json` are exact source bytes,
with SHA256 pins in `check_comparison_transfer.py` and its receipt.
An open PR's claim is a comparison target, not evidence of acceptance.

Let C be the certified complex-supplier endpoint, D the endpoint digits,
R=10^(-D-80), F=10^(D+46), and B=10^(-D-22). The actual ledger chooses
b=C-R, q=C-2R and epsilon=1-(1025/1024)R. Its final value is

    kappa = floor(F*epsilon*q)/F - B = C - 1/F - B.

The last equality is checked in the source at lines219–221: C*F is an
integer and 0<C-epsilon*q<1/F. For this pin D=3000, so the exact relation
is `K=C-10^-3046-10^-3022`. The claim's complete decimal string hashes to
`b14d377d6aa465aafd8d8f23953a210763744fbc7a538fd378f89c48704885be`.

Reproduction:

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_comparison_transfer.py
```

Expected: `PASS_PINNED_PR2374_EXACT_ENDPOINT_TRANSFER_IDENTITY`.
This uses Python rational arithmetic independently of the ledger's imports.
It rejects the historical b/(1+b) transfer, omitted backoff and omitted grid
step as reproductions of this exact claim.

Consequently, for a new candidate that fully satisfies the same outer
construction and its own fixed-grid hypotheses, the necessary numerical
comparison is `C_new > K + B_new + 1/F_new`, with b_new=C_new-R_new.
Comparing a supplier moment near the incumbent K is the relevant screen.
Using K/(1-K) would impose the older transfer and a spurious larger target.
A moment below1 at K is only a screen: it does not certify an endpoint
above K+B_new+1/F_new, or establish the complete construction.

Remaining obligations for seed39 include literal global owner allocation
and windows; all global recursive ranks; physical stock including76
private zero buffers and corresponding CLEAR work; source-access and warp
routing/adapter charges; strict supplier finite admission and all its
negative controls; bit-supplier nonbinding checks; and the complete outer
ledger, bootstrap cutoffs, source-prime padding and inherited all-size
assumptions. The old PR2269 parent admission in this session remains
unestablished due to recorded serialization/reuse failures. Native local
success cannot substitute for that missing global/parent evidence.

Credit for the comparison construction and transfer belongs to PR2322
(Vlado Vojdanovski), PR2374 and its kernel/owner lineage (Jeremy Kothe),
PR2349/2363 (mason-hale), PR2312/2226 (including Cinna Davis), PR2309
(Dugongue), PR2315 (Sagar Thakrar), PR2161/2180 and PR2168/2184
(dataisfire), PR1786 (Chafik Boukhalfa, using Tim Trudgian's prime theorem),
PR1673 (Vlado Vojdanovski), PR1758 and the other predecessor contributors
credited in the retained PR2374 metadata. This note rechecks one arithmetic
identity; it does not claim their construction as new seed39 work.
