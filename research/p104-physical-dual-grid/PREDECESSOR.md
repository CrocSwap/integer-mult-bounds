# Physical inverse-transpose of the corrected P104 word

This package realizes the **ordinary physical inverse-transpose** of the
two-target corrected P104 shear in its original **canonical** endpoint charts.
It answers the native-conversion part of [PR2551's handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2551).
The complete finite word has **5,398 events**, **2,070 positive transports**,
rank mass **3,542**, and eight exact zero-restored private erasures. All 150
arbitrary dirty helper logical values restore. No supplier or kappa is claimed.

[PR2497](https://github.com/CrocSwap/integer-mult-bounds/pull/2497) supplies the
full logical clean dual and its zero-restoring collectors. Nick Petalas's
[PR2550](https://github.com/CrocSwap/integer-mult-bounds/pull/2550) supplies the
complementary-frame realization idea. Both explicitly exclude the physical
inverse-transpose contract established here. Their mathematics is credited,
not relabelled as new. The new step uses **conjugated complementary charts plus
416 charged rank-one endpoint conversions**. Ordinary complementary charts
produce a different physical operator.

## Exact boundary and proof

Let S be the real public shear on 358 registers: X stays fixed, Y receives CX,
and the 150 dirty helpers stay fixed. Rows 0 and 1 of C are identity rows; the
remaining 102 rows are the original Gram/2 rows in the pinned P104 port order.
Let i and f be the original forward endpoint frames and Gamma their canonical
unitary charts. The desired operator is

```
F      = Gamma_f S Gamma_i^(-1)
F^(-T) = Gamma_f^(-T) S^(-T) Gamma_i^T.
```

T is ordinary bilinear transpose, not conjugate transpose. Define
Delta_W = conjugate(Gamma_W) = Gamma_W^(-T), using unitarity. The checker also
verifies Gamma_W^T Delta_W = Delta_W Gamma_W^T = I at all 210 distinct boundary
charts, using a separate literal gate-transpose implementation.

PR2497's logical clean dual starts at f and ends at i. Convert its compressed
labels to authenticated physical binary labels, then replace every frame W by
its orthogonal complement W-perp. Common-chart additions remain common;
nested frames remain nested with the same absolute dimension difference.
Keep every rational ADD, sign, and zero/erase event unchanged. Execute all
transports in Delta charts. The usual common-chart induction preserves S^(-T)
on arbitrary logical inputs and preserves zero at each private erase.

The middle starts at f-perp and ends at i-perp. Add the following Delta
transports so its public endpoint charts instead become i and f:

| Role | Input conversion | Output conversion |
| --- | --- | --- |
| 104 X_s: i=line(q_s), f=full | line(q_s) -> zero | q_s-perp -> full |
| 104 Y_t: i=zero, f=q_t-perp | zero -> line(q_t) | full -> q_t-perp |
| 150 dirty helpers: i=zero, f=full | zero -> zero | full -> full |

The authenticated physical dot product is nonsingular, so these complements
are exact. Each of the four nontrivial edges per port has rank one. Every
conversion preserves the logical row; no dirty helper is omitted. The complete
physical operator is Delta_f S^(-T) Delta_i^(-1) = F^(-T).
Restoration means the original logical helper value in its prescribed final
dual chart, not equality of physical input/output arrays when charts differ.

The persistent middle paths increase after complementation. Initial X and
final Y rank-one conversions decrease, and private paths are not monotone.
This package does not admit those excursions to existing owners or transfer
PR2550's monotone claim to the entire extended word.

## Native realization and complete local bill

For A -> B the literal operator is
Delta_B Delta_A^(-1) = conjugate(Gamma_B Gamma_A^(-1)). Conjugation leaves
address permutations/XORs unchanged and negates diagonal phases and C-gate
signs. The retained exact Clifford compiler lowers this operator to Gaussian
monomials surrounding **one positive child** of rank abs(dim B - dim A).
Inverse Fourier signs are represented by XOR adapters, not free negative
children. Every gate stays in the retained finite Gaussian-dyadic alphabet.

Without importing the compiler, the retained independent interpreter checks
all **1,245 distinct recipes**, signed Pauli action and exact phase, and binds
all **2,070 occurrences** to the literal program. All 512 columns of each of
16 private 8 <-> 1 transports are checked, **8,192 columns** total. Monomial
recipes record their address matrices, offsets, diagonal and global phases.

```
1632 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 76 H7 + 8 H8
rank mass 3542 = credited clean dual 3126 + 416 H1
3104 ADDs, 208 signs, 8 zero initializations, 8 exact zero erasures
2070 transports + 3104 + 208 + 8 + 8 = 5398 events
```

This is a complete **finite local native** invoice, not recursive excess cost
or a supplier moment. It is neither an optimum nor a lower bound. Monomial
address/phase work is represented but has no proved tape/runtime or placement
price here. The 416 extra edges are included, not hidden as free chart changes.

PR2551's distinguishing input Y2=delta_0 uses the unchanged C[2,0]=1/2. The
resulting X0[0] is **(-1+i)/64**, required by F^(-T), rather than the backward
chart's zero. A closed nine-factor Gaussian product checks every entry of this
512-address column independently of the frame constructor and compiler.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -O -B research/p104-physical-corrected-dual/verify.py
python3 -I -B research/p104-physical-corrected-dual/verify.py --regenerate
python3 scripts/research_package.py --package research/p104-physical-corrected-dual
```

Read-only verification authenticates every live and retained input before
executing dependency bytes; reconstructs all 14,400 root pairings; regenerates
the complete word; checks all **128,164** endpoint coefficients by sparse
Fraction and separate dense scaled-integer execution; and checks every literal
common frame, private erasure, native occurrence, and the entire saved receipt.
Because each physical value is its verified chart times an exact logical row,
the induction covers arbitrary 512-address input functions, not just scalar
samples; signed Pauli equality plus phase fixes each complete Clifford operator.
Regeneration compares complete decompressed native payloads rather than gzip
container bytes. `--out NEW.json` refuses an occupied output.

Seven controls remove either endpoint conversion or private cleanup, corrupt
native phase/coverage, use unconjugated charts, or confuse adjoint with
transpose. Equivalent boundary bases and a separate transpose/conjugation
identity are accepted controls. `test_verify.py` also covers Git-free relocated
replay, source/executable pins before execution, receipt mutation and output
refusal. These are finite checks, not a formal multiplication theorem.

## Scope

The physical statement uses the original **canonical** endpoint charts.
Intrinsic adapters are not imported into this theorem; a caller requiring that
convention must convert its boundary explicitly. Native unitarity comes from
the pinned primitive semantics. Rounded strict-zero erasure does not follow
from ideal zero restoration (PR2549). The other 102 forward correction rows
remain Gram/2, not identity transfers. No owner map, idle/residual bill,
precision admission, all-size compiler, full supplier or new kappa is supplied.

## Open next questions

- Can the 416 H1 endpoint charge be reduced by fusion? Try one X-entry or
  Y-exit commute/cancellation with full physical endpoint and zero erasure
  checks. The present construction gives no minimum.
- Can actual owners and a rounded private-erasure contract realize this word?
  First price decreasing endpoint edges and private returns. Monotone hosting
  and ideal zero checks alone do not admit those operations or establish a
  favorable recursive moment.

## Provenance, selection and credit

Canonical main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2; priority revision 4.
The picker selected complex mechanisms with nonce
cf5835b1ee9aae06d5f81ac1e8a160bc; the required local ceiling replay passed.
The p104-side-correction card is explicitly changed to PR2551's concrete native
physical-dual handoff. This closes a finite interface, not the card's complete
supplier gate. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2551#issuecomment-6195390717).

PREDECESSORS.json pins PR2497 head 7f2cf129d42030d3eb3975b7d1b07392c6d32a1b and
PR2551 head 249c4034da118da35f1e6009744b81461172bc61, with exact bytes, SHA256 and
Git blobs. Main native/geometry inputs are pinned in SOURCES.json. Retained
source files are unchanged. PR2550's complementary idea is credited; no PR2550
executable or certificate is imported. The ordinary change-of-chart/transpose
identities are standard and not newly claimed.

Credit PR2497/2458/2445, Ross Richardson, commdata2338, Hiroki Kumazaki,
Philippe Van Velzen, Chafik Boukhalfa/1991, Rohan Arun/1972, Adam Gall/1940,
Josie Elliston/1071, Ali Romman/1125/1862, icekylinx/531 and the retained native
compiler/interpreter ancestry. New work prepared for ywz65 with substantial
OpenAI Codex assistance in derivation, code, checking and writing. Apache-2.0.
No independent human, formal-kernel, selected cold-replay, hosted-CI or
maintainer-acceptance claim is made.

Final overlap: 779 open PRs at 15:23:17 UTC and 1239 Discussion records at
15:22:22 UTC on 2026-10-15, reused from complete snapshots; targeted PR2551
comments and all three exact source heads were checked again. Full Discussion
refresh had hit the GraphQL limit; this is bounded snapshot coverage, not a
novelty certificate or a search of arbitrary diffs/unpublished work.

Local validation passed on Python 3.12.14: optimized registered replay, all six
export/integrity groups, normal complete native regeneration, and selected
baseline bindings. Separate OpenAI Codex proof/code review confirmed the chart
algebra, four-edge endpoint bill and scope; it did not rerun the full native
verifier and is not independent human review.
