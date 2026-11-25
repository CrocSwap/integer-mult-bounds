# Lead 2: changed dictionary plus one bridge

This is a scoped negative for a single **address-independent** replacement bridge, and local progress on the broader lead. It does not exclude address-dependent bridge programs or admit a supplier.

Exact source: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, archived #3432 `23db0fe51aba6256db76e07df96a6698752c7d79`, and its pinned PR3148 fill/PR3187 physical semantics. See SOURCES.json. The newer main package `t740-complete-phase-map` is relevant prior work: it proves fixed-word residual phase-function injectivity for owner 0 / port 0, including arbitrary changed dictionaries. Its source proof is used as an attributed dependency, not claimed as our discovery. The older #3296/#3328/#3311/#3272 fixed-dictionary and fixed-bridge results are not being rerun as a new search. Shared-phase-repair-rank #3229 is not used as an unpriced repair.

## Boundary and exact experiment

The eight data streams are arbitrary complex arrays on 73-bit addresses. Hosted prefixes, source accesses, translations, event order, all native local calls and terminal event remain fixed. At owner 0 / port 0, choose the first four unhosted orthonormal axes of terminal residual child 12 (rank 48). Replace each axis `v_i` by the xor of the other three. This is the non-permutation orthogonal four-frame move; the other 44 residual axes and every hosted axis stay fixed. The combined basis remains orthonormal because new axes lie in the old four-dimensional span.

For the four isolated character bits `b_i`, put `s=xor_i b_i`. The new bits are `b_i xor s`. If s=0, weights agree; if s=1, the new weight is 4 minus the old odd weight. Hence the Z/4 phase difference is `2s`, exactly the translation `X_delta`, delta=xor_i v_i. The verifier checks all 16 characters and the exact 8x8 intertwining matrices; the four-bit calculation covers all ambient characters because other coordinates do not enter the difference.

Child12 acts on stream X0 before the final bridge (src0,dst1,c=1). Between it and this bridge, other residual phases and the preceding two bridges fix X0. Thus the altered preceding segment is `D P`, where D translates X0 by delta and P is the old segment; D commutes with the intervening factors. The fixed invertible suffix and prefix force the unique replacement to be `B'(x)=B D(x)^-1=B D(x)`. This is a Gaussian-integer matrix at every character. Its X0 diagonal and the coefficient to X1 vary with the character. Exact multiplication checks `B'(x) D(x)=B` for all 16 possibilities. The unmodified constant bridge fails at an explicit dirty input basis vector. Matrix equality covers arbitrary data and does not assume zero workspace.

## Stronger elementary screen

Any independent residual dictionary and any translation have phase one at character x=0. With only one bridge replaced, all remaining operations at x=0 are unchanged and invertible. Therefore an address-independent 8x8 replacement matrix B' must satisfy `S B' P=S B P`, forcing B'=B. This applies to arbitrary constant Gaussian matrices, not just changing the scalar coefficient. It rules out using a genuinely changed constant bridge to evade a fixed-word obstruction. It does **not** constrain B'(x) away from x=0 if a new address-dependent native program is allowed.

Combining this with the attributed fixed-word phase-map injectivity forces unchanged residual phase functions and independent ranks for this owner0/port0 model. That consequence is conditional on the predecessor's exact proof, whose replay is recorded separately. It is not a new all-port theorem.

## Complete ledger and decision

| Obligation | Result |
|---|---|
| Actual source access / hosted axes | Fixed and pinned; no new access assumed |
| Four changed axes / rank | Constructed exactly; residual rank stays 48 |
| Complete paid child profile | Unchanged even optimistically: zero rank saving |
| Formal replacement bridge | Exact character-dependent matrix constructed |
| Ordinary native scalar bridge | Impossible for a nontrivial difference, by zero-character argument |
| Address-dependent native realization / conversions | UNKNOWN; cannot be charged zero |
| Dirty restoration | Exact eight-stream boundary covered for formal matrix; no full replacement native workspace program |
| New hosting / precision / physical release | UNKNOWN for any changed native program |
| Both supplier caps / comparator | Neither changes in the screened model. Selected κ=0.001672660197076918; live #3624 candidate≈0.001730047552093344159584−10^-46−10^-70, not independently fully replayed here |

The cost-preserving four-frame move cannot increase κ even if its extra bridge work were free. The broader changed-dictionary/changed-address-dependent-bridge lead remains **INCONCLUSIVE**; this experiment isolates a necessary changed contract rather than exhausting that domain. No additive defect repair or unrelated census is justified by this result.

## Replay

`python3 -B research/three-kappa-leads/bridge_screen.py`

`python3 -B research/t740-complete-phase-map/independent.py`

The first is an exact standard-library source projection and finite matrix check; it compares BRIDGE-RESULT.json and authenticates inputs. The second belongs to the credited predecessor and checks its symbolic phase-map theorem, not a changed bridge. No Lean, Docker, optimizer or full selected replay is needed for this scoped conclusion.

## Open next questions

Construct an address-dependent bridge that changes the original factorization and lowers the full residual profile. First give its stream/address action, entry/exit frames and exact native word, then account for all recursive changes, translations, sources, conversion, scratch, hosting and restoration. A formal B'(x) is insufficient; no affordable such program is known. A four-axis same-span rotation alone has zero rank saving, so a future attempt must explain a changed subspace/rank or a separate eliminated native obligation.

Credit all retained source authors, the #3432 and complete-phase-map packages, and the PR3148/PR3187 lineage. New analysis and checks by OpenAI Codex with substantial AI assistance. Astra review is scoped same-session AI review, not human or formal acceptance.
