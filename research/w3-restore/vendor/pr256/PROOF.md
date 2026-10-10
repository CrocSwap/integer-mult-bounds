# The source-assisted complex words as explicit numbered programs

**Claim.** The complex words of PR #194 (PR #168's frames, PR #193's reuse pairs) and PR #233 (PR #168's frames,
PR #200's maximum-weight reuse pairs) are each one explicit program in Jacob Sussman's certificate format gcert/1:
12,052 numbered registers (1,320 sources x, 1,320 targets y, 9,412 slots), a table of 18,248 frames, and one gate
list per phase (before and after the star scatter), accepted by his reference checker `gx.check1`
(jacobalansussman/wht-power-saving-lean, `tools/gx/gx.py`, commit `f010392c`; vendored unchanged in `gx/`).
In the bridged five-stage word of that repository (m = 5h = 110, W = 4v + R = 14,692) the PR #233 program is
certified at saving a = 7547/10⁷ with exact rational bounds (7548/10⁷ rejected); Sussman's own mirror
`gxdry.py` prices it at 7547361/10¹⁰ against 7474547/10¹⁰ for the circuit of #193. No new κ: the bit supplier
binds in every current assembly.

## 1. What the checker checks (Sussman's conditions, as implemented in `gx/gx.py`)

- **E0, E1 (labels).** Every register has a start frame (x: its port line; y and slots: the zero frame) and a
  final frame (x and slots: the full frame; y: the perpendicular of its port, dimension h − 1). Every gate names
  one frame; every register named by a gate moves to that frame, and every move is a strict nesting of reduced
  echelon subspaces of F₂^h. The rank of a move is the dimension difference; the block histogram counts moves
  by class (x, y, s) and rank; the c class counts the retained totals at their frames.
- **E2 (scatter cut).** Between the two phases, h = 22 retained totals sit in slots at their recorded frames and
  every target is still at frame 0; the star rule scatters total k into target t with coefficient 1/3 when
  coordinate k lies in port t and −1/6 otherwise.
- **E3, E4 (shape).** Gates are fan-out ('out': one source, several targets) or fan-in ('in'); phase 1 has only
  x→slot and slot→slot gates; targets are written only in phase 2.
- **E5 (exact scalar identity).** Replaying every gate on the x-content of every register with exact rationals,
  each target ends with exactly its source and each source is restored (the K blocks are undone).
- **E6 (price).** N = Σ rank·count over the histogram equals R·h + 2v(h − 1) + cst, cst = Σ dim of the retained
  totals' frames = 22·20 = 440.

## 2. How the program is built (`gcert_emit.py`)

The input is the output of PR #184's tool chain on the aligned word: `complex_frame_flow.py --witness` (the flow
DAG: one node per (phase, frame), the value channels on every edge, the births, retirements and reads) and
`exact_complex_flow_lift.py` (at every node an invertible completion Q as a list of elementary row operations,
and the coordinates of every read in the node's inputs). The emitter numbers one slot per physical flow
coordinate (v source copies at the port lines, then every birth; a kernel reuse continues a slot) and, node by
node in the lift's topological order, at the node's frame:

1. copies the original sources into their first slots (phase 1, port line);
2. emits every read: side and deferred reads as fan-outs from the slots that carry the read value into the
   targets of the root, with the coefficients ±1/2 of PR #194's contract (`contract_v4.py`: responses ±3 and
   −3c on the ledger scaled by 6); a centre read is a retained total, formed in place in one of its retiring
   input slots (the nine inputs of a centre node retire untouched);
3. emits the completion as fan-outs with one target: the lift stores the row operations that take Q to the
   identity, so they are replayed in reverse with inverted coefficients; a swap only relabels positions; a
   scaling changes the unit of a slot (wanted = λ·stored, as Sussman's `gxconv.py`) and every later coefficient
   is rescaled;
4. names, as extra registers of the node's last fan-out, every coordinate that passes through the node
   untouched: the flow charges each edge, and the block histogram of the program must be the flow's ledger.

After the last phase-2 node the program applies, for each parity class of each cube, the K block 1 − J/2 of
PR #144's decoder on the four source registers at their parity 3-space (three fan-in/fan-out gates, the class
head carrying the sign), reads each mixed source into its antipodal target (Hamming distance 6 inside the
cube) at that target's cap frame, and undoes the K blocks at the full frame. This is PR #194's contract read as a
program: the scatter, the side and deferred responses and the K responses are the terms whose sum the contract
checks to be 6·I.

## 3. What is reproduced

- The control (PR #194's word) has the block histogram of Sussman's published certificate of #193 in every class
  and rank (70,169 blocks, N = 262,944), and `gx.check1` accepts it; `gxdry.py` prices it at his 7474547/10¹⁰.
- The PR #233 program (69,683 blocks, N = 262,944) is accepted; its per-invocation ledger
  3(x + y + s + c) + 2v·e₂ is PR #233's certified child histogram (`certificate.json` of PR #233, vendored), so the
  program is the word PR #233 certifies through PR #184's lift and contract, now as one explicit transcript.
- Five-stage price (as PR #225, Proposition E; ledger H₅ = 5·H_inv + 2v(e₄₂ + e₂₁ + e₄₆ + e₄) stated by PR #250
  for PR #234/#209's layout): the moment Σ n_r (r/m)^{1−a} at m = 110, W = 14,692 is below W at a = 7547/10⁷ and
  not at 7548/10⁷, with the exact bounds of `scripts/moment.py`.

## 4. What is not claimed

The program is checked here by Sussman's Python reference checker and Python mirror, not by the Lean kernel
(his repository checks the #193 program in Lean; the same generators apply to this file, and a kernel build of
the generated modules is reported in the pull request, not in this package). The emitter has no proof of its own:
it is validated by the two checks above (the control reproduces an independently rebuilt certificate, and the
result reproduces PR #233's certified ledger). No κ changes.
