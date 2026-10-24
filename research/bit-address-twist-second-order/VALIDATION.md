# Validation and evidence boundary

Author execution on 2026-10-23: CPython 3.12.12, macOS 26.5.2 arm64,
standard library only. Primary work began from a fresh clone of canonical
main at `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority revision 7.
The task's scientific/provenance pins remain at that commit.

## Executed checks

The selected orientation helper passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a scientific cold replay.
The unchanged predecessor `bit-address-twist-register-floor/verify.py` passed.
Its all-order result was used as orientation, not counted as new coverage.

The new direct verifier passed in both modes, with byte-identical JSON output:

```sh
python3.12 -I -W error -B research/bit-address-twist-second-order/verify.py
python3.12 -I -W error -O -B research/bit-address-twist-second-order/verify.py
```

Both report `PASS_BIT_ADDRESS_TWIST_SECOND_ORDER`; a direct run takes about
one second on this host. Relevant coverage is 11,664 reduced local cases,
511 nonzero linear forms, 36 permutation twists, two non-permutation `PBQ`
fixtures, 110 sparse finite-group/quotient comparisons, three representative
orders, and the direct positive control on all 165 basis vectors. The
all-order conclusion is a filtration argument in PROOF.md, not an inference
from these three orders. The written proof also covers all dimensions
`m >= 2` and general allowed odd-denominator frames/twists, which are not
exhaustively enumerated by the finite verifier.

The metadata check and both registered replay commands passed:

```sh
python3.12 -B scripts/research_package.py --package research/bit-address-twist-second-order --check-only
python3.12 -B scripts/research_package.py --package research/bit-address-twist-second-order
```

The registered runner reported `PASS_REGISTERED_RESEARCH_PACKAGE` with
`outcome=negative-result`. No helper, workflow or selected source was edited.

## Controls

The committed verifier rejects deletion of `P_0`, removal of the private
twists, and substitution of `E11` for `E22` in the diagonal calls. It checks
the even-denominator boundary and the loss of information from omitting the
second layer or erasing polynomial squares.

Five separate development mutations were run on disposable copies of
`verify.py`, each normally and under `-O`. All ten executions failed with
the indicated assertion-independent `ValueError`:

| Mutation | Detected by |
|---|---|
| Omit square terms from `frame_poly` | `binomial parity` |
| Drop the summed dirty-input increments | `all-order dirty obstruction` |
| Omit the source-side inverse twist in `compile_call` | `non-permutation twist oracle` |
| Use `x[r]` instead of `y[r]` for the sparse paid source | `finite group oracle disagrees with quotient action` |
| Substitute `t00*t22` in the expected dirty residual | `all-order dirty obstruction` |

A separately coded supporting-agent finite-set calculation also produced
the displayed dirty residual for forward/reverse orders and an exact
nine-call positive control. Its initial binomial expansion was corrected
during primary review; the corrected normal/optimized outputs agree. This
is supporting development evidence, not independent scientific acceptance.
The committed verifier provides its own reproducible sparse oracle.

## Coordination and publication

The handoff-first value check found the specific second-order request still
open. The cached pre-claim search covered 305 open PRs, 4,300 closed PRs,
4,091 Discussion records and all 6,690 tracked local note records, with
complete pagination. An immediate live check covered 307 open PRs and the
25 recently updated Discussions; no overlapping second-order claim appeared.
PR4953 had no review/comment continuation when checked. Such coverage is
advisory and excludes unpublished work and arbitrary diffs.

Canonical coordination is Discussion #4999, with one short pointer under
the original #1166 handoff. Upstream was refreshed to
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1` during verification; governing
guidance, selected record and predecessor sources were unchanged.

Committed-byte/source-history and fresh export replay are recorded in the
PR publication evidence. The registered runner needs Git; a standalone
export uses the two direct commands above. Export integrity authenticates
transport bytes, not the proof.

## Unrun obligations

No full selected supplier/outer replay, native layout/price, all-pattern
search, Lean proof or independent human review was performed. The full
two-sided seven/eight-call problem remains open. This package changes no
selected frontier, merges no PR, and supplies no complete multiplication
theorem. Hosted CI, when available, is additional execution evidence only.

Prepared by Krzysztof Wójt / krzysztofwojt with substantial OpenAI Codex
assistance. Apache-2.0; predecessor credit is retained in README.md.
