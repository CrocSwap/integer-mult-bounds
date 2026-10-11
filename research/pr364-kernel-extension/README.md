# Two extra kernels and five retimings composed with PR366

Conditional exponent saving:

`κ = 804942957146173674940857 / 1000000000000000000000000000`

approximately **0.000804942957146173675**, an increase of
**3.1679146887e-9** over [PR366](https://github.com/CrocSwap/integer-mult-bounds/pull/366)
at `d3d84202e528d6e147a8ea62463ae5c0125997cf`
(`0.000804939789231485`). The bit side binds; E8 is unchanged.

This composes two additional rank-two response kernels and five additional
frame retimings with **all 123 retimings from Rohan Arun's PR366**. The
complete resulting word is rebuilt, checked and priced. Published gains
are not added numerically. This is a conditional finite construction and
exact assembly bound, not an unconditional multiplication theorem.

## New construction

The two pivots and their donors are:

| Pivot | Donors |
| --- | --- |
| 7848 | 7850, 7920, 7922 |
| 7107 | 7109, 7484, 7486 |

Both use existing frame 69022, spanned by `e6-e7` and `e18-e19`
(zero-based coordinates). Each pivot's binary target response equals the
XOR of its three donors' responses. The inherited kernel emitter removes
20 compensation reads, installs the two rank-two entrances, inserts six
setup ADDs and six restoration ADDs, and rechecks the complete word.

The earlier search trimmed the total entrance rank to a multiple of five
for its 60-replica bank normalization. **100 physical replicas** allow the
four extra rank units to remain, with exact width-100 banking and no
padding. This replication change alone does not improve the moment; it
permits the untrimmed word to have integral stock and exact banks.

An independent connected-group descent found a three-gate triangle that
can move jointly from rank 13 to rank 12, enabling a two-gate move from
rank 15 to rank 14. Of that search's 90 changes, 85 overlapped PR366's
later published selection. This package retains the **five additional
changes** and all 123 published changes. Their register sets are disjoint;
source binding and the complete simultaneous assignment are checked.
The signed scalar instruction sequence and every endpoint are preserved
by retiming. New frames must contain the actual integer source spans.

| Quantity | PR366 | This construction |
| --- | ---: | ---: |
| Records | 405680 | 405678 |
| Local unit ADDs | 357770 | 357762 |
| Local paid rank mass | 168690 | 168686 |
| Helper residual rank sum | 131850 | 131846 |

Relative to PR366, the local paid-child histogram changes by
`{1:+8, 2:+8, 3:-11, 4:+2, 5:-2, 6:+1, 7:-1, 8:+1}`.
The kernel introduces no frames. The full retiming introduces 55 bases
relative to PR364, including the 53 from PR366.

With 100 replicas, each of five stages uses 131846 banks. Literal stock is
1043230; normalized stock is 208646. Every residual block is used once,
every bank has width 100, and the normalization factor is 20.

Final records SHA-256:

`7b4bb2f0944d422699501ccb9a9d1cdde5b8fbe8a7877b16ee844a73f7b92139`

## Replay

From a checkout containing the unchanged PR364 package:

```sh
python3 -m pip install -r research/pr364-kernel-extension/requirements.txt
python3 -B research/pr364-kernel-extension/verify.py \
  --output /tmp/pr364-kernel-extension-proof \
  --boost-include /path/to/boost
```

Use a fresh output directory outside `research/`. Python 3.11+, a C++17
compiler and Boost headers are required. Omit `--boost-include` when Boost
is on the default include path; `--cxx /path/to/compiler` selects a compiler.
Assertions must remain enabled. The inherited shell replay requires source,
output, Python, compiler and Boost paths without whitespace; the wrapper
rejects such paths before doing work.

The verifier replays the entire pinned PR364 package, including its
historical control and E8 supplier. It reconstructs the pinned PR366
selection and reproduces its published price, then rebuilds the two kernels
and 128-gate composition using the inherited emitters. It checks:

- Both intermediate and final words: nesting, exact frames, nondegeneracy,
  COPY lifetimes, integer source spans and formal F2 columns.
- Exact remapping of all 123 upstream gates and unchanged assigned bases;
  five additional gates, disjoint registers and unchanged signed scalar
  sequence through the full retiming.
- Independent packed-integer replay of all 10010 local columns. Omitting
  any of the 12 new setup/restoration ADDs must break the operator.
- Independent physical legality and all 11930 five-stage formal columns,
  including omitted-bridge controls; the payload prefix bound is 93 bits.
- Exact 100-replica banking, stock and all consumed changed-frame ranks.
- Both rational moment engines with the full inherited `10^-16` fallback
  density and `32m²` rank-one fallback per paid child. The coarse saving and
  next `10^-24` grid point are separated strictly.
- Eight finite ordinary-bootstrap steps and all 47 strict outer constraints
  at `η=10^-24`, `β=10^-9`; the next final `10^-27` grid point is rejected.

`CERTIFICATE.json` is emitted only after the complete replay succeeds.
The committed `EXPECTED.json` pins the portable exact arithmetic and finite
receipts, and every fresh run must reproduce it. Machine paths, clocks and
the package's own manifest hash are excluded to avoid a self-reference.
Source hashes bind the exact word and receipts. Both package manifests
are checked again at completion. See `PROOF.md` for the dependency argument.

## Conditional scope and attribution

The source package's native downstream admission, changed projector
charts and complete finite invoice remain open. The new replication count
has exact aggregate banking and stock; no new native bank/chart or finite
invoice admission is claimed. All-size compiler, common-ancestor charts,
routing, restored-row, prime-supply, precision/recovery and analytic
interfaces remain conditional. Binary payload exactness is the retained
bit contract; no signed integer decoder equality or new Lean proof is
claimed. Eight finite bootstrap levels use the same inherited recursive
transfer as the source's three levels.

Rohan Arun supplies PR364 and PR366's 123-gate retiming. Chafik Boukhalfa
supplies the inherited transcript, shared-donor kernel, frame descent and
banking methods. The new contribution is the two retained entries, their
integral replication count, five further compatible retimings and exact
finite verification and assembly. These are established mechanisms; no
invention of those methods or global optimality is claimed. Jacob Sussman
supplies E8, integrated by DaysSky. All preceding credits are retained in
`NOTICE.md` and the unchanged source notices.

Prepared with substantial OpenAI Codex assistance; Apache-2.0.
