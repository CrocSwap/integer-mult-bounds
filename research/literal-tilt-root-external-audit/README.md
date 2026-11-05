# External certificate of the literal tilt root

For the declared nine-atom law in [alephnan's PR6713](https://github.com/CrocSwap/integer-mult-bounds/pull/6713), pinned at `cd666f05c4e9006025b634687cc493911c8371c8`, this source-aware audit proves that the tilted mean equals ln(5) at exactly one real parameter alpha*, and certifies the strict bracket

```
98981438244597/10^14 < alpha* < 98981438244599/10^14.
```

The source already states its inherited bracket and author-side endpoint checks. This is external coverage and a centering bridge, not discovery of the root, a new exponent or a claim of a source gap.

Write A(t)=sum P_r*r^t and m(t)=sum P_r*r^t*ln(r)/A(t), with the exact positive multiplicities in [CASES.json](CASES.json). Differentiating gives m'(t)=Var_t(ln r)>0 for every finite real t: all tilted probabilities are positive and ranks 1 and 2 are distinct. The limits are 0 and ln(48), so m(t)=ln(5) has exactly one solution. Two outward rational endpoint enclosures then locate it. [PROOF.md](PROOF.md) keeps this monotonicity argument on m; the unnormalized residual need not be globally increasing.

The primary uses rigorous atanh logarithm and Taylor exponential series. The separately authored oracle uses composite Simpson integration of 1/x with an explicit fourth-derivative error bound, and binomial exponential sandwiches evaluated by directed squaring. Neither uses floats, Decimal, the source numerical engine or a peer calculator. Each recomputes its own complete retained packet. Different rigorous methods intentionally produce different interval endpoints; matching packet bytes is not required.

Both blind firsts passed before peer certificate reads. Their six common metadata/control/conclusion fields agree, and all 17 paired intervals overlap. Coarse outward residual enclosures valid for both methods are

```
left:  [-16574,-16569] * 10^-18
right: [ 27276, 27281] * 10^-18.
```

Both signs are strict. All nine log intervals and the normalizer, numerator, mean and residual at both endpoints are retained. Each engine executes seven actual controls, including reevaluating the bracket after changing the rank-two multiplicity. The normal and optimized retained-certificate modes passed for both engines. [VALIDATION.md](VALIDATION.md) distinguishes this completed evidence from subsequent external, registration, export, cold and hosted checks.

The earlier [PR6723 audit](https://github.com/CrocSwap/integer-mult-bounds/pull/6723) established its finite-H hypotheses uniformly throughout this same bracket, centered at the actual tilted mean m(t). At alpha*, m(alpha*)=ln(5) exactly. Thus its probability, variance, third absolute centered moment and support bounds apply to the exact mean-ln(5) tilt. This closes that historical premise bridge; it does not discharge selected analytic recovery or the full flow theorem.

Default checker execution is read only. It authenticates the exact metadata and eight engine/input paths, regenerates all interval values and controls, and compares its whole actual retained certificate. `--certificate PATH` selects a packet for the same validation; only `--emit PATH` writes. [VERIFY.json](VERIFY.json) contains registered commands. Source inputs are inert text only, with Git/SHA256 provenance in [SOURCE-PINS.json](SOURCE-PINS.json). Prior source-aware review exposure is disclosed there; these are separately authored calculations, not blind human review or proof-kernel acceptance.

## Open next questions

1. Can the exact-root bridge be carried through the source's complete flow onset and boundary terms? First bind the local-limit hypotheses to the precise target/paid recurrence and retained finite onset. The present certificate checks the law and tilt, not those recurrence obligations.
2. Can the selected caller's analytic-recovery condition be established with its actual kernel, complement and leaf/error ledger? First state that caller's exact contract and test the missing analytic estimate there. Root digits and a historical uniform-H result do not supply it.
3. Can all numerical preparation and precision costs be charged in the physical supplier? First bind one complete source/caller execution and its input, output, scratch and precision ownership. No such physical invoice is certified here.

The full flow, approximation, onset, kernel, leaf, complement, boundary, production, precision and caller bills remain. All five selected assumptions remain open at their proper gates. There is no changed paid profile, kappa, frontier, adoption or merge claim.

## Credit

alephnan/PR6713 supplies the source law, local-limit development and retained endpoint work. CubeJerry/PR6329, zxv/PR4436/4483, Ryanson Jonathan and pinterbanget/PR4459/4467, DLamdata/PR6118, Nick Petalas/PR6125/6128, CinnaDavis, Jacob Alan Sussman and retained native, precision and analytic contributors retain their lineage. PR6723 supplies the earlier external uniform-H audit. Exponential-family variance, series remainder bounds, Simpson quadrature and exponential sandwiches are classical methods. ToikY with substantial OpenAI Codex assistance supplies this source-aware external premise closure and separately authored calculators. Original notices are retained in [inputs/NOTICE](inputs/NOTICE); see [NOTICE](NOTICE).
