# Native realization gate: direct E8 root-line adapter fails

The prior schematic signed mixed-carrier bank places new scalar values on binary labels \(u_i+u_j\). This is a valid **formal vector-space** line but not an existing E8 **root line**.

In the standard P104 label realization \(u_r=(\mathrm{rootBits}(r),1)\in\mathbb F_2^9\), every root-line label has ninth coordinate 1, whereas a sum of two root-line labels has ninth coordinate 0. Hence no two-root sum equals any root-line label. This applies to all 120 E8 root lines, not just one selected decoder.

`root_line_gate.py` reconstructs the exact 120-by-120 mod-2 pairing signatures from 240 doubled-coordinate E8 roots and checks all 7,140 distinct pairs. No XOR of two root signatures equals another root signature. This is independent of the selected P104 frame.

**Implication:** a proposed implementation cannot simply relabel a mixed sum as another primitive root-line carrier. One must exhibit a legal generalized frame/phase and scalar word, or another encoding. The result does **not** rule out all arbitrary one-dimensional subspaces of the nine-dimensional label space, nor block generalized-frame constructions.

Required next gate: specify permissible registers, phase conversions, and source/copy/erase/restore primitives; compile an exact signed example; count the extra child ranks and cleanup operations; then compare the full paid moment with current selected frontier. Until then, the 30.8% ADD and 41% frame-rank savings are schematic rather than multiplication bounds.

## Follow-up: rank-two home frame avoids the line-label obstruction

The even-parity obstruction excludes *single original E8 root-line names* for mixed values, not the rank-two subspace `U_ij=span(u_i,u_j)` built from **two existing root labels**. A mixed auxiliary can stay in `U_ij` throughout target delivery in the relaxed source/target frame trace. For each target whose support contains both indices, `U_ij` is contained in its target sink, and a single signed arithmetic ADD reads the value.

`rank2_gate.py` constructs these home frames, executes exact symbolic target outputs, returns each original source to its rank-one home, reverses every mixer preparation, and erases all 16 auxiliaries to frame zero. It checks all 2288 signed target cases. Across 4096 cube-edge banks, the 8-edge bank has **320 ADDs, 1520 frame-rank moves, 16 auxiliaries**; the stipulated direct baseline has 416 ADDs, 2224 frame-rank moves. There are six symmetry-related minimizing 8-edge bank masks.

Per 8-edge bank, mixer build+erase costs 64+64 frame-rank units and 32+32 signed ADDs; target paths supply the rest. The two-dimensional carrier home adds a small modeled read cost relative to a non-root composite rank-one label, but eliminates the requirement for a non-existent physical root line. The earlier rank-one bank with explicit cleanup is separately checked by `zero_restore.py` and costs 320 ADDs / 1408 rank units, but still needs new line-alphabet realization.

**This does not certify a native carrier.** The real E8 compiler must prove a legal rank-two carrier storing the mixed scalar, correct operator phase, source access, routing, physical inverse, precision, live helper ownership, all child rank charges, and a complete selected-moment budget. Generalized algebraic frame inclusion alone does not establish these properties.
