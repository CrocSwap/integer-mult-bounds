# Error propagation through the complete QQ16 decoder

PR2540 supplies an exact native decoder. PR2603 supplies exact caller grids
assuming exact children. This package supplies a different local obligation:
**sufficient Hilbert-norm bounds for errors at every completed ADD, native
child and cover map of that unchanged word**. No supplier or kappa changes.

| Signed propagation envelope | Every initialized cut | Final fields |
|---|---:|---:|
| Input coefficient P | 240 | 121 |
| Independent absolute defects A | 1529 | 818 |
| State-relative weighted defects K | 2298 | 1253 |
| Native-only defects | 192 | 96 |
| Cover-only defects | 280 | 140 |

All interior peaks occur in local scratch F0 after event 1717 (zero based).
A concrete constant-owner/payload signed-error execution attains 841 there,
which already exceeds the final-field envelope 818. The larger 1529 bound is
conservative; no sharp operator-norm claim is made.

For entry norm at most B and the specified state-relative local defect u,

```
M <= 240 B / (1 - 2298 u)
all-cut error <= 551520 u B / (1 - 2298 u),   2298u < 1.
```

Therefore `u <= 2^(-b-21)` suffices for error at most `B*2^-b`, for all
integers b>=0. The norm is the maximum over owners of individual payload
Hilbert norms, at arbitrary positive tensor depth. This is not a component
rounding format or a claim that 21 bits is minimal.

The contract retains exact owned CLEAR, exact frames/addressing/control and
the separate temporal-entry assumptions. Sixteen capture ADDs can err and
their retained errors survive B1. The inherited B1 execution, retention and
current-entry errors are outside this calculation. Borrowed restoration
becomes approximate. Exact CLEAR removes private contents but cannot remove
errors previously copied out: an explicit private-error execution changes
56 final outputs. See [PROOF.md](PROOF.md) for all quantifiers and limits.

## Reproduce

Standard-library CPython 3.12; normal verification is read-only:

```sh
python3.12 scripts/research_package.py --package research/qq16-child-defect-bound
```

The registered suite authenticates and reruns the complete unchanged PR2540
checker; recomputes 2,680 changed-field boundaries and 2,136 fault sites;
checks 66,101 coefficients with a separately written reverse traversal; and
performs 2,324 literal execution equalities, including state-dependent faults,
private error escape, failed exact borrowed restoration and an attained
interior witness. Git-free export, read-only replay and three actual source
or typed-receipt corruptions are checked. `verify.py --write` creates an
absent receipt only; it cannot overwrite evidence.

The written unitary-frame/triangle/feedback proof establishes the all-depth
implication; finite replays authenticate this instruction stream and its
coefficients. Separate AI proof/code review and optimized scientific replay
passed. No independent human review, proof assistant or hosted CI is claimed.

## Open next questions

* Compose this decoder contract with measured errors in actual F0/B1 and
  retained storage. Those entries share a trajectory; derive its source-bound
  constants before adding this decoder's error budget.
* Implement a physical child/ADD with this completed-instruction Hilbert
  defect and exact control/CLEAR contract. Conversion from per-component
  rounding to Hilbert error must account for payload size.
* Tighten the conservative operator envelopes if the precision saving pays
  for the required implementation. The 841 witness does not prove 1529 sharp.

## Credit and scope

The exact decoder, invoice, sources and notices from ywz65's PR2540 and its
PR2511/2512 lineage are retained unchanged. Credit Ali Romman and the retained
QQ16 construction, thakrarsagar's L2 retention work and starship-s's F0/cut
decoder. The method is the standard signed Hilbert-defect and feedback
argument applied by PR2096, PR2166 and PR2503 to other P104 words. Their
coefficients are not imported. PR2603 concerns exact real-box caller grids.

New source-bound stability proof, independent sensitivity engines and controls
prepared by **ywz65**, with substantial OpenAI Codex assistance in derivation,
implementation, testing, writing and separate-agent review. Apache-2.0.
Native child internals, retention, global hosting, all-size supplier admission
and a physical precision format remain open. Selected and frozen files are
unchanged. Exact pins, assignment and overlap coverage are recorded in
SOURCES.json, SNAPSHOTS.json and TASK.json.
