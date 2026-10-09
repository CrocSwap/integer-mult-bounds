# Served diagonal operations on the PR200 bit word

This package changes one thing in PR200's bit word. Then it applies PR205's completed banks (PR197's construction) and PR193's balanced assembly without change. This file states the change and why the word stays correct. Every argument not restated here is PR200's, PR205's or PR197's, with the same inherited interfaces.

## 1. The partner mixes in PR200

PR200's word has `v = 1760` source lines, `h = 24` and `m = 72`. Each source `s` has a data register. The register holds `x_s` after the injection. The 1,760 sources form 880 partner pairs. Each pair has a carrier `c` and a passive `d`, with orthogonal labels. For each pair the word:

- adds `x_d` into the carrier data register at the 2-dim mix frame, so it holds `x_c + x_d`;
- delivers `x_c + x_d` to the pair's receivers at the cap frame;
- subtracts `x_d` again at the end.

So the passive data register always holds `x_d`. Only carrier registers change. The carrier chain is `line → mix → cap → full`. The passive chain is `line → mix → full`, with children `[1, 22]`.

## 2. The served operation

PR200 also forms the same sum `x_c + x_d` in auxiliary registers. Operation `i = (a, b, n)` adds register `b` into register `a`, and node `n` is the partner diagonal with `args[n] = {c, d}`. `patch.py` finds the operations where all of these hold:

1. before `i`, register `a` holds exactly `x_c`, and register `b` holds exactly `x_d`;
2. `b` is not a root, gauge, source or alias register;
3. `b` has exactly two operations: one copy operation `j` that writes the source node `d` into it, and then `i`;
4. the mix frame of the pair is inside the frame `F_i` of operation `i` (exact containment in PR200's own frame algebra).

There are 373 such operations. All of them are in phase one, and every `F_i` has dimension 3. For each one, `patch.py`:

- deletes register `b` and its copy operation `j`;
- makes operation `i` read `x_d` from the passive data register: `ops[i] = [a, -1-d, n]`, with `served = [i, d, F_i]`;
- moves the partner mix of that pair to the start of the word, right after the injections (`early = true` in the schedule);
- extends the passive chain to `line → mix → F_i → full`, with children `[1, 1, 21]`.

Nothing else changes. Operations, roles and read positions are renumbered compactly. `verify.py --full` runs `patch.py` again on PR200's frozen word and compares its output with the frozen files.

## 3. Why the word is still correct

**Values.** Before operation `i`, register `a` holds `x_c`. The passive data register holds `x_d` at all times. So `a` receives `x_c + x_d`, the same value as before. The checker simulates every register content and checks the operands of every served operation against the node's arguments.

**Early mix.** After the injections, the word reads a carrier data register only at the deliveries and at the final subtraction. Both come after the mix in both schedules. Thus the early mix changes no value that the word reads.

**Dirty registers.** The deleted register `b` takes its adjoint response with it. A served operation reads a data register, not a dirty auxiliary register, so it adds no dirty response.

**Formal check.** `bit/served_prove.py` runs all `2v + 16,775 = 20,295` formal columns in F2 and over the integers. All target columns equal the defining decoder. All source and dirty columns return to their start values. No column is sampled.

**Frames.** Each `F_i` is nondegenerate and contains the passive line. The passive chain `line ⊂ mix ⊂ F_i ⊂ full` is nested, and every other chain keeps PR200's check. The exact integer backend is eumemic's PR168 v4 backend, loaded from PR200's pinned references. The served word uses 24,401 frames. Each one is a PR200 frame with its PR200 prime witness, so every Gram inverse and projector stays valid at every prime `q > 2^80`, as in PR200. No new frame comes in.

**Controls.** The checker rejects each of these changes:

- PR200's three word controls (omitted compensation, missing partner, stale read);
- a served operation that reads the carrier instead of the passive register;
- a zero operation frame;
- a served passive chain without its served stop;
- a served pair whose mix is not early.

## 4. Terminal sinks

PR200's 34 PR166 terminal sinks apply unchanged. `bit/served_terminal.py` is PR200's `bit/terminal.py` with three edits:

- a served operation is not a register-to-register gate, so it has no control use;
- the gate replay adds the passive data register for a served operation;
- the replay applies early mixes after the injections and late mixes at delivery.

The retained scalar bill does not grow (delta −158). The three terminal controls are rejected.

## 5. Ledger

| Per copy | PR200 | Served |
|---|---:|---:|
| Logical auxiliary roles | 18,908 | 18,535 |
| Physical chains (after 1,760 aliases and 34 sinks) | 17,114 | 16,741 |
| Stock `W` | 20,634 | 20,261 |
| Deficit `72W − mass` | 1,936 | 1,936 |
| Coarse bit saving | 6.77774e-4 | 6.86716e-4 |

The deficit stays at 1,936, so the telescoping identity holds with the same loss.

## 6. Banks

PR205's packing applies with new counts. There are three copies, 2,200 rank-20 gauges (220 distinct frames, the same charts as PR205) and 14,541 other physical chains:

```
6·3300 = 9·2200,      2·3300 + 3·41423 = 9·(16741 − 2200).
```

Thus `W = 3·2·1760 + 44,723 = 55,283` and the deficit is `5,808 = 3·1,936`. The largest child is 22. The chain/bank multigraph gets a proper 9-edge-colouring, and an independent check rejects a duplicated colour.

## 7. Arithmetic

`arithmetic.py` and `audit.py` are PR205's, with the served word's numbers. The paid moment includes the 10^-16 rare-class fallback. Two independent moment engines exclude the next 10^-18 grid point. Three finite ordinary-leaf levels start from the served word's completed ordinary supplier. PR193's complex supplier does not bind. The unchanged 47-constraint balanced assembly certifies κ, and the next 10^-18 κ point is rejected. `certificate.json` holds every value.

## 8. Limits

The finite checks establish the served word, the sinks, the charts, the banks, the moments, the leaf recurrence and the assembly arithmetic. These remain inherited assumptions, as in PR200, PR205 and PR197:

- the completed-core contract;
- the general Clifford interface;
- uniform weighted compilation;
- restored rows;
- fixed-tape transfer.

PR193's disclosed limits on the complex side also remain.
