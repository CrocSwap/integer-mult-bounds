# The p = 10 complex supplier (#327's centre-sharing program)

#315 and #325 price the complex side with #315's centre-sharing program at p = 11 (h = 22, m = 110):
b = 772714351296671/10¹⁸. With the transcript stages the bit root of #325's word reaches 7.7712 × 10⁻⁴, above
that cap, so the p = 11 supplier would bind (κ 7.72117723737704e-4). This package replaces it with DreamingOfClouds'
#327 program at p = 10 (h = 20, m = 5h = 100): the source-assisted complex word of PR #184/#194 compiled with
PR #304's recipe on #327's re-annealed p = 10 modules and the centre-sharing pair module (PR #233 maximum-weight
pairs). Its fallback-inclusive coarse saving is b = 779597612622781/10¹⁸ ≈ 7.79598 × 10⁻⁴, so the bit binds.

## What changed

- **Program.** `inputs/complex/gcert1-p10-centre-mw-flow.json.gz` is #327's
  `certificates/gcert1-p10-centre-mw-flow.json.gz` byte for byte (#327 at commit 40ed045; uncompressed sha256
  `370fae73…23ff`, the hash #327 reports for its local Lean kernel check `wht_main_block_B2Gcc95x`). It replaces
  `gcert1-p11-cmod-centre-mw-flow.json.gz`; `inputs/complex/source-pins.json` binds the new certificate (both
  hashes). Its provenance (the three query modules, the frozen layer, #315's `Graph.finish` patch, #327's record
  and notice) is in `inputs/complex/centre-mw-p10/`, replacing `inputs/complex/centre-mw/`.
- **The five places that pinned the p = 11 program** (listed in #327's PROOF.md §5):
  - `code/complex_labels.py`, `code/complex_scalars.py`, `code/complex_splice.py`: h, v and the centre rank come
    from the certificate and `word_pins.shape()` (h = 20, v = 960, centre rank h − 2 = 18, cst = h(h − 2)); the
    scalar and splice modules are bound to the certificate by `bind(c)`; namespaces (centres, tableau, coefficient
    work stream), the live width 4v + R and the physical width 4v + R + h + 1 are derived from (v, R, h).
    Word-dependent counts that were literals (R, N, frame count, phase gate counts, the invocation histogram, the
    live-transition partition) are strict pins in `word-pins.json` (`complex_*`).
  - `portable_complex.py`: the family check is (m, h, W) = (5h, h, 4v + R) with R pinned; the five-stage ledger
    has the shape deficit 4v − 5h(h − 2) = 2,040 and largest child 2h + 2 = 42, and its calls and rank mass are
    pinned; the scalar expansion bill, the complete local bill and the four stock bit lengths are pinned; the
    mutation controls use the derived namespaces. Every inequality guard is unchanged (local bill < 2⁴⁸, K < 2⁶⁰⁵⁰,
    router < G, literal < E, rows < 20,161, 2·max child < m, …). The completed-child induction identity is
    2B(m − max child) − s − E = (2(m − max child) − 1)·B, i.e. 115·B here (127·B at m = 110).
  - `math_check.complex_supplier()`: m = 5h = 100 and W = (rank mass + deficit)/m = 10,295 = 4v + R; the calls and
    rank mass, W, b and the no-fallback root b₀ are pinned. b is certified with the 10⁻¹⁶ fallback by both moment
    engines with the adjacent 10⁻¹⁸ grid point rejected, b₀ likewise without the fallback (recorded only).
- `code/complex_gx.py` and the vendored `gx.py`/`gxcore.py` are unchanged (#327 vendors the same files, same hashes).

## Values

| | #315 / #325 (p = 11 program) | this package (#327's p = 10 program) |
| --- | ---: | ---: |
| h, v, m | 22, 1,320, 110 | 20, 960, 100 |
| R, N, frames | 9,036, 254,672, 17,861 | 6,455, 165,940, 12,392 |
| five-stage W = 4v + R | 14,316 | 10,295 |
| five-stage calls / rank mass | 351,820 / 1,571,680 | 247,575 / 1,027,460 |
| b (with fallback) | 772714351296671/10¹⁸ | **779597612622781/10¹⁸** |
| b₀ (without fallback, recorded) | 772714354722691/10¹⁸ | 779597615657658/10¹⁸ |

Both roots equal #327's own certified values (`inputs/complex/centre-mw-p10/expected-centre-mw.json`).

## What is not claimed

The five-stage layout at h = 20 (H₅ = 5·H_inv + 2v(e₃₈ + e₁₉ + e₄₂ + e₄), m = 5h, W = 4v + R) is Sussman's generic
B₂ statement applied at h = 20, as in #327; Lean runs of the program are #327's local runs and are not pinned here.
The retained analytic interfaces of the complex side (Lab.inv dirty lifting, gwinB/G0..G4 geometry, NetCert
composition, Clifford synthesis, tape primitives, precision and rows) are inherited unchanged; the finite checks
do not discharge them. The inherited complex texts in `proof/` and `UPSTREAM-PR234-*` describe the p = 11/PR193
programs.
