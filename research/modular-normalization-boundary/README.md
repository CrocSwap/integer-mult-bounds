# Modular inverse normalization: exact metric boundary and paid query word

**Scoped proof and scalar construction; no new kappa.** This completes
[Nick Petalas's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363231).
It distinguishes three lift domains and corrects the stated SWAP cost error.
The [proof](PROOF.md) gives all quantifiers, the full word, prices and credit.
The [receipt](RESULT.json) records exact finite evidence.

Let N=2^b, a=p^(-1) mod N for odd p, and m=min(a,N-a).

| Boundary | Exact optimal Lipschitz constant |
|---|---:|
| Residue cycle to residue cycle | m |
| Integer-line lift, ordinary distance | m |
| Periodic integer lift from the residue cycle | N-m |

For fixed 1<p<N, m>=(N-1)/p. For p=3 the exact value is
`(2^b-(-1)^b)/3`. Thus an unrestricted numerical conversion can have
nonvanishing output ambiguity even when its input error is half a grid unit.
Exact digital residue arithmetic and restricted reachable domains are outside
this obstruction. The periodic lift distinction is necessary: at N=8,p=3,
the first two constants are 3 and the third is 5.

The handoff's pairing-three cut has a literal 19-instruction completion
with one supplied invertible payload query. It restores the outside dirty
coordinate exactly. A payload-swap query retains the inverse-normalization
expansion at the full endpoint. Two separately paid SWAPs are present.
Replacing each by three ADDs and one NEGATE gives a verified 25-instruction
word. Three ADDs alone give a signed swap and cannot implement a SWAP
modulo N>=4. Both words retain all scaling and reduction costs.

This is an indexed scalar calibration. The query, coefficient preparation,
conversion, physical access/routing, recovery and compiler costs are separate
paid obligations. No favorable complete recursive bill, native Gaussian
implementation, selected assumption discharge or frontier change is claimed.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/modular-normalization-boundary
python3.12 -B scripts/check_research_commit.py --package research/modular-normalization-boundary --check-source-history
```

Expected markers are `PASS_MODULAR_NORMALIZATION_BOUNDARY`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The registered runner checks both normal and optimized execution.
The default verifier compares the stored receipt without changing it.
`--output NEW_FILE` writes a separate receipt and refuses to overwrite a file.

Finite evidence covers 63 metric contexts and all 73,533 unordered pairs,
8,805 independently enumerated periodic lifts, 255 inverse-three precision
formulas, all 1,638 invertible two-by-two query matrices modulo 2,4,8,
19,656 full basis forward/inverse checks, 768 exhaustive binary dirty cases
and 30 wider cases through 257 bits. Every one of the 19 and 25 instruction
omissions is detected at modulus 32. Additional controls cover the signed
swap, lift-domain confusion, full-endpoint amplification, numerical ambiguity,
nonunit inversion and confusion with real division.

No predecessor scientific suite, selected cold replay, Lean, Docker,
independent human review or proof-kernel verification is claimed. The
finite enumeration supports the written all-size proof; it does not replace it.
Sources in [SOURCES.json](SOURCES.json) are provenance, not imported code.
The verifier is standalone and has no runtime source dependencies.

## Open next questions

Can one actual native producer stay in exact residue arithmetic with paid
conversion and exact recovery, or prove a restricted reachable domain?
First export one complete producer/query/consumer boundary and its full
invoice. The present obstruction does not decide those alternatives.

## Credit

Nick Petalas supplied the released metric candidate, pairing-three prefix,
19-instruction completion proposal and disclosed cost error. This work
reconstructs the completion, repairs and tests the paid expansion, distinguishes
periodic lifts, and publishes the exact proof and executable evidence.
Gareth Davidson / @bitplane supplied the exact quotient backend and its scope
in [PR #1159](https://github.com/CrocSwap/integer-mult-bounds/pull/1159).
Its unchanged source retains shhxera, androolloyd, Sagar Thakrar, Chafik
Boukhalfa and the classical register lineage. General congruences, cycle
metrics and two-point ambiguity arguments are classical; no global literature
priority is claimed. Prepared by Ali Romman with substantial OpenAI Codex
assistance. New work is Apache-2.0.
