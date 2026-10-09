# Review of CrocSwap PR97

Reviewed 9 October 2026. This is a bounded local review, not external expert
endorsement or a completed end-to-end integer-multiplication proof.

## Verdict

[PR97](https://github.com/CrocSwap/integer-mult-bounds/pull/97) at
[`f5f9c56e637463cac1e300d1589ccf42838f688a`](https://github.com/jacklightChen/integer-mult-bounds/tree/f5f9c56e637463cac1e300d1589ccf42838f688a)
is a substantive interface audit and repair, not just another exponent search.
I found no failing identity or numerical certificate in the checks below.
It reports **κ=63965813/10^12=0.000063965813**, using the same Swapnil round7/round6
inputs as our work and main's retained balanced assembly.

This number is below our alternate-stack conditional number
`0.000063982820832686571`, but PR97 establishes several interfaces that our
earlier audit expressly left unresolved. Comparing the numbers alone would
misrepresent their verification scopes.

## What PR97 changes

1. It expands the bit word into literal forward/reflected events. Within 160
   commuting fan groups, recipients are ordered by their starting frame rank.
   Exact nesting still relies on the independently checked frame chains;
   rank alone would not suffice.
2. It handles nonzero auxiliary entrance gauges and proves both tensor-stage
   exits. Two tensor connectors and the copied rank-one correction remain
   charged. The dirty-scratch registers are restored rather than erased.
3. It supplies signed complex phase accounting. A complex inverse reverses
   the word **and negates coefficients**. The rank-one endpoint requires an
   **inverse** child and an address translation. Binary XOR cancellation is
   not a valid replacement for this complex argument.
4. It recomputes the literal scalar bound, semantic precision constant and
   product row reservation, then uses main's 47 strict constraints and 7
   margins. It intentionally gives up the slightly larger number from
   Swapnil's different analytic stack.

## Fresh checks run here

| Check | Fresh result |
|---|---|
| Exact imported new files | 14 Git blobs verified; 6 executable/frozen dependencies byte-verified |
| Bit ledger | 1,080,616 events ; 32,408 formal input/scratch basis columns; forward and reflected shear pass |
| Complex ledger | 535,744 events; 124,369 actual geometric transitions; 24 copied centers; pinned histogram matches |
| Signed small scalar controls |Complete h8/h10 basis controls pass; missing cancellation and wrong inverse sign reject |
| Full complex support |All 4,096,576 h24 coefficients verify `AMV=I` |
| Author's Fourier endpoint control |All 65,536 h4 addresses pass; both bad corrections fail 32,768 addresses |
| Independent Fourier reconstruction |131,072 address/scalar-basis cases pass; both bad corrections fail 32,768 addresses |
| Exact moments |Separate rational logarithm/exponential implementation encloses both moments below 1 |
| Retained assembly regeneration |All 47 slacks and 7 margins pass; next 10^-12 κ grid point rejects |

The independent phase check reconstructs the encoded-to-decoded factors of
stage one, the two common connectors, stage two's signed inverse, and the
copied correction. It does not merely substitute the author's simplified
final formula.

Fresh logs and hashes are in [RECEIPT.json](RECEIPT.json), numerical controls in
[independent-results.json](independent-results.json), and exact source pins in
[MANIFEST.json](MANIFEST.json). The native h4/h5 rational tensor script was
read but not executed: SymPy is unavailable in this environment. Its
commuting-idempotent formulas were inspected algebraically. The complete
native rational frame/flag suite and 138-file source verifier were not rerun
for this review; earlier local checks of the unchanged geometry are separate
evidence.

## Compatibility with our saturated frames

I reran PR97's **unchanged bit event-ledger code** with our exact saturated
candidate, SHA256
`97df9481e5ae70645b8325315616aa0334ee990480e357bf0e21feb0a66447f4`.
Both complete scalar maps and reflected continuity pass. Its histogram delta
is exactly

```text
width 1:   -177100
width 507:  -31878
width 509:  -24794
width 511:  +56672
```

Total rank remains 57,403,754,177, and maximum child remains 527. The inherited
complex network, semantic bridge and row-degree stock are unchanged.

Using our certified saturated bit saving with PR97's main assembly yields
the local compatibility certificate

```text
κ = 2559149/40000000000 = 0.000063978725
```

All 47 strict slacks and 7 margins pass; the next 10^-12 κ grid point rejects.
The gain over PR97 is `807/62500000000 = 1.2912e-8`. Exact results and attribution
are in [saturated-balanced-compatibility.json](saturated-balanced-compatibility.json).

This is a compatibility experiment. A publishable combined integrated
witness still needs its own complete source manifest and end-to-end package
validation. It adopts Chen's endpoint/phase repairs and retains the stated
main analytic/tape assumptions. It does not establish a global fastest
algorithm or measured runtime improvement.

## Limits and potential weak points

- The all-size fixed finite-alphabet tape implementation, analytic routing,
  precision/recovery and prime/denominator arguments remain inherited written
  lemmas. Finite replay cannot prove their full uniform complexity bounds.
- Common rational basis existence uses finite generic determinant arguments,
  with symbolic zero constraints. It is not a single explicitly instantiated
  rational basis covering the entire tensor family in the replay above.
- Complex basis wrappers must realize the ambient mod4 phase convention,
  including any linear phase translation introduced by basis changes. The
  pair endpoint controls support the stated convention; they do not execute
  all recursive tape-level wrappers.
- The authored h24 support identity plus commutator argument proves the
  signed scalar map. The h24 ledger does not run a dense full physical tensor
  coefficient replay or an actual integer multiplier.
- The public PR had no comments at the final refresh. Hosted run 37854885755
  concluded `action_required`; it is not a passing hosted CI receipt. The
  PR's staged local `make verify` coverage is separately described in its
  imported VALIDATION.json and was not fully reproduced here.

These are scope limits, not discovered counterexamples.

## Credits and references

- **Zhihao Chen / jacklightChen**, [PR97](https://github.com/CrocSwap/integer-mult-bounds/pull/97):
  reflected scheduling, fan-order clarification, gauged exit proof, signed
  complex endpoint controls/correction and retained-assembly integration,
  with the disclosed Codex assistance. Any combined result should explicitly
  credit these contributions.
- **Swapnil Jain**, [pinned round7/round6 source](https://github.com/Swapnil-jain/integer-mult-kappa/tree/741e7aa078392553815df7926ee17ac5e25a8c38):
  deferred readouts, V leaves, lifted frames, h24 producer, frozen inputs,
  flag/staircase family, and original Claude assistance disclosure.
- **icekylinx**, main `structured_bulk_assembly.py`, derives semantic/product-row
  and combination formulas from **Zhihao Chen PR23** and the **RaD** transfer.
- The upstream preserved notices additionally attribute **Avi Eisenberg /
  ikeboy PR62**, **RaD / hipotures PR41**, **Rohan Arun PR44**, **Aurel Prosz /
  Paureel**, **James Chang PR34**, and earlier authors. Imported LICENSE,
  NOTICE, module headers and historical AI disclosures are retained.

Recheck commands, after the saved isolated replay trees have been prepared:

```bash
python3 experiments/pr97-review/independent_audit.py
python3 experiments/pr97-review/combine_with_saturated.py
```
