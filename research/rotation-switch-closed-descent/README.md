# Optimal linear-bit canonical rotation queries

The exact canonical padded-rotation switch can be queried in `Theta(h)`
worst-case bit work and `O(h)` temporary bits. A closed formula replaces
the repeated child descent of PR7504. It returns the same current-wire
predicate without a permutation, network, row ROM, or recursion stack.
This is an arithmetic construction and scoped proof. **No new kappa** follows.

For row `j`, let `d=min(j,2h-2-j)`, `M=2^d-1`, and `t=x mod 2^d`.
The two child interval lengths are

```text
A = floor((a+t)/2^d),
B = floor((s-a+M-t)/2^d).
```

Either zero length means identity. Otherwise a single retained endpoint
formula at height `h-d` and wire `x>>d` gives the answer. This uses a fixed
number of linear binary operations. A family of inputs needs at least
`h-1` offset-bit probes with padded fields, or `h-2` with minimal positive
encodings, so the worst-case order of growth is sharp.

Read [PROOF.md](PROOF.md), [query.py](query.py), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md). The proof
covers every positive height. The executable has a height limit of 65536.

## Evidence and reproduction

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/rotation-switch-closed-descent
```

Both registered commands print:

```text
PASS_ROTATION_SWITCH_CLOSED_DESCENT optimal O(h) bit query
```

The verifier checks all 1,633,182 switch entries in 2,793 networks against
the retained canonical compiler and source recurrence. It routes 152,526
addresses and checks 892,854 descent states. Further checks cover 420 wide
source queries, the 544-bit historical row, explicit height-65536 cases,
bit sensitivities, twelve invalid domains and five wrong-formula controls.
The retained sources are authenticated before use. No historical research
entry point is executed. The finite checks corroborate the written proof.

## Scope

This changes an arithmetic query. Jerry Chen's PR7593 already supplies a
fourteen-tape implementation of the earlier recurrence; its literal program
and quadratic bound remain separate. This package supplies no physical
instruction count, caller runtime measurement, or supplier admission.
All five selected framework assumptions remain. Historical suites, physical
caller replay, selected cold replay, Lean and Docker were not run.

## Open next questions

- Lower the closed formula to a literal fixed-tape program. Preserve the
  borrowed descriptors, return one owned bit, and price clearing and head
  returns. Start with the existing `(h,s,j)=(5,17,6)` boundary. The present
  arithmetic proof does not provide that owned-work contract.
- Compose the query with actual current-state CRT offsets and compare a
  complete workload against retained row-ROM reuse. Start with the existing
  exceptional-key producer. Offset production, descriptor conversion and
  payload consumption remain required costs.

`TASK.json` records the changed audit-card scope and these questions. The
base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. Selected bindings pass; the catalogue assessment is older than
the selected record. The selected frontier is unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Nick
Petalas supplied the endpoint and child formulas; Cinna Davis supplied the
canonical compiler; Jerry Chen supplied related physical lowering. See the
retained notices and credit file. This is source-aware author checking,
not independent human or formal-kernel acceptance. Apache-2.0.
