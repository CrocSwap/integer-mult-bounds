# An all-depth exact component grid for QQ16 F0 to B1

For every positive common tensor depth lambda, the actual literal full-cover
F0 then B_1_2 arithmetic reference admits the sufficient format

```
quantum = h 2^(-71-19(lambda-1))
signed width = P + 215 + 38(lambda-1).
```

Inputs in all 704 persistent fields must have Gaussian dyadic components in
h Z with magnitude strictly below 2^P h, uniformly over all cover owners.
The eight owned private fields enter zero. Arbitrary bounded dirty helpers
and correlations are allowed. The complete 712-field F0 state carries into
B1. Native numerators and constant-product partials are included.

This closes PR3270's explicitly one-layer numerical-domain restriction.
Its one-layer constants and evidence retain their credit. The new
[proof](PROOF.md) gives a symbolic induction in lambda, rather than
extrapolating a few sampled tensor depths. [RESULT.json](RESULT.json) binds
all 53,118 events and 270,288 symbolic observations. The lambda=1 projection
reproduces the predecessor's complete primitive trace, both stage-cut and
final-state hashes, all operation counts and exact maxima.

The separate numeric interpreter explicitly repeats coordinate Gaussian
lines at depths 1,2,3,8. Its grid guards are 71,90,109,204. It shares input
loading and event expansion but no symbolic bound, envelope or dispatcher.
Five behavioral groups exercise the tensor-interior inequality, carried
state, invalid native/cover maps, domain/zero cases and private source/type/
usage/receipt corruptions. The original coefficient acts once on the port;
it is not raised to the tensor depth.

## Cost and scope

N=2^(73 lambda) complex payload coordinates per owner. The symbolic numeric
reference uses at most

```
(372322 + 110760 lambda) N + 12 W-bit word operations,
2112 N additional conceptual cover-component transfers,
1426 N + 12 W-bit numeric storage words.
```

Only coordinate Gaussian-line work multiplies by lambda. Tensor monomials
can be applied as single signed permutations using the reusable buffer.
Their address/sign calculations remain unpriced, as do code/control
storage, cover routing, recursive tariffs, entry-grid conversion and F17
consumption. W-bit arithmetic is reference work, not a unit-cost claim on a
fixed-word machine. This is not a favorable complete supplier invoice.

Tensor-native, bridge, cover closure and endpoint semantics are inherited
from the exact canonical QQ16 source. The new result certifies numerical
execution relative to that reference. It does not prove literal
common-coordinate helper restoration, provide an admitted caller input
format or change selected science/kappa. PR3293's helper-return operator
and PR3294's exact-prefix inverse are distinct unused results. No full
N-dimensional payload is allocated or executed. No Lean, Docker, selected
cold replay, independent human or proof-kernel approval is claimed.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -Werror -B scripts/research_package.py \
  --package research/qq16-all-depth-producer-grid
```

The three registered commands are the direct scripts below. Each is
read-only except for private controls beneath TMPDIR. Set TMPDIR and
PYTHONPYCACHEPREFIX to a private external directory before replay.

```sh
python3 -Werror -B research/qq16-all-depth-producer-grid/verify.py
python3 -Werror -B research/qq16-all-depth-producer-grid/independent.py
python3 -O -Werror -B research/qq16-all-depth-producer-grid/test_verify.py
```

The direct commands also work in a Git-free source export containing the
four declared canonical inputs at their repository-relative paths. The
pending PR3270 proof, README and receipt are retained byte-identically with
original paths, Git blobs, commit and SHA256 pins. Fresh CI needs no pending
PR Git object. Primary verification authenticates the exact fixed source
manifest, input/provenance usage and retained bytes. Receipt comparison
uses canonical JSON encoding, distinguishing true, 1 and 1.0.
`verify.py --output NEW_PATH` writes an absent receipt and refuses overwrite.
SOURCES.json is itself byte-pinned; changing it requires an explicit source
binding update. [ENGINEERING.md](ENGINEERING.md) records implementation bounds
and exceptions. [CHECKS.json](CHECKS.json) records actual verification.

## Open next questions

Can a named caller supply this bounded dyadic grid and the actual required
entry/exit representations without repaying the numerical saving? First
bind that caller's input precision, dirty-state range, frame adapters and
F17 consumption. The complete routing/address/control/recursive bill is
the blocker. This package does not reserve a construction expansion or
another guard optimization. The structured question is in TASK.json.

## Sources and research decision

Canonical base `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
Source PR3270 is pinned at `4a83f89c3865d21521b4a72bb71e3a23c3aadbb7`.
The original joint-query-controller card is refined to the actual
producer-interior, multi-layer numerical implication. Physical caller and
consumer admission are explicitly outside this bounded result.

Public overlap includes 342 open PRs through 21:05:35 UTC and 2137 Discussion
records through 21:06:07 UTC with complete pagination. The 2630 closed/merged
body snapshot has the older 20:44:55 cutoff. Exact PR3270 status/head and
current #2727 handoffs were checked. Arbitrary diffs and unpublished work
are not exhaustively searched. The sibling geometry predicates are distinct
and unused. The canonical investigation is
[Discussion #2727](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19004308).
Family decision: close this explicitly missing numerical-domain implication
and stop. Unknown consumer/physical costs remain unknown.

Credit commdata2338/PR3226/3235 for the finite native grid and producer defect
envelopes; Nick Petalas/PR3270/2965/3250/3258 for the one-layer and numerical
context; Sricharan Vagvala's pair-first reference; Ali Romman, Tekalign,
Ross Richardson, Arham Tahir, ywz65 and the retained QQ16/native/geometry
lineage. Frozen predecessors remain unchanged. New work is Apache-2.0.
Internal computational review is separate from scientific admission.
