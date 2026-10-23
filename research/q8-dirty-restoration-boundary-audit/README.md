# Q8 dirty-restoration boundary audit

## Question and scope

For the `t <= 2` attainment proposal in [PR #3697](https://github.com/CrocSwap/integer-mult-bounds/pull/3697), does the repeated coordinate-projector witness restore every non-target register as a full operator over `F2[Q8]`? Can a legal word pass a diagonal-only endpoint check while changing a dirty spectator?

The proposal head inspected for this audit was `b5fa8645bff6db3ff219815e6fc820a4f08b0572` on the live PR. Its [verifier](https://github.com/CrocSwap/integer-mult-bounds/blob/b5fa8645bff6db3ff219815e6fc820a4f08b0572/research/q8-min-length-census/verify.py) compares `endpoint(...)` to `wanted(...)` as complete role matrices. The underlying minimum bound is inherited from PR #3589; this audit does not re-prove it.

## Result

The proposed witnesses restore spectators exactly. For a target role `a`, let `N = e_a e_a^T`. Then `D_g = I + (1 + [g])N` is diagonal over `F2[Q8]`, with `[g]` in coordinate `a` and `[1]` in every other coordinate. Repeating the call three times puts `[g]^3 = [z g]` in coordinate `a` and leaves every spectator equal to `[1]`. This is an identity for every role count, not an inference from the finite checks in `verify.py`.

The exact negative control uses two roles and the legal rank-one idempotent `N = (1,1)^T (1,0)`, for which `(1,0)(1,1)^T = 1` over `F2`. Three calls with label `i` produce diagonal `[zi],[1]`, as required for one negative-i target, but the lower-left entry is `[1]+[zi]`. Thus a diagonal-only checker accepts a word that does not restore the dirty spectator. The full matrix check rejects it. This does not expose a defect in PR #3697: its verifier compares the complete matrix with the complete target matrix.

The independent calculation is in `verify.py` and uses only the Python standard library:

```sh
python3 scripts/research_package.py --package research/q8-dirty-restoration-boundary-audit --check-only
python3.12 scripts/research_package.py --package research/q8-dirty-restoration-boundary-audit
python3 -B research/q8-dirty-restoration-boundary-audit/verify.py
```

It checks the Q8 multiplication law and associativity, replays all six one- and two-target endpoint types with zero through three extra roles, and checks the leaking control against both the diagonal-only and full-matrix predicates.

## Related overlap

Open PR [#3705](https://github.com/CrocSwap/integer-mult-bounds/pull/3705) makes the same `t=1,2` call-count claim. Its verifier checks the inherited count condition and cube powers, but does not replay a role matrix. This audit stays on the #3697 handoff and adds the operator-level restoration check; it does not restate either count result.

## Attribution and limits

Credit Nick Petalas and the cited PR #3589/#3570/#3578 lineage for the Q8 model, mixed-negative lower bound and endpoint question. This is an independent boundary check of PR #3697's explicit witness and full-matrix acceptance rule. It makes no new minimum-length, physical-call, restoration-cost, supplier or kappa claim. `SOURCES.json` pins the task card and selected record at the assignment's base; the proposal source itself is cited by its exact public commit above and is not a runtime input.

## Open next questions

- **Question:** What concrete physical caller can implement these formal Q8 factors while restoring its real scratch state?
- **Why it matters:** Exact formal spectator identity does not price physical state preparation, temporary workspace or restoration.
- **First step:** Bind one proposed word to a native bit-supplier source path and enumerate the complete input, scratch and output state transitions.
- **Blocked by:** PR #3697 supplies no native conversion or physical invoice.
