# Three-stage prefix shear chain

**Recursive-interface construction; local cost reduction, no new κ.** Three complete factor calls suffice to apply the block lower-triangular prefix map below. Under the old target-hidden interface, independently expanding the same map by original source paths takes six factor calls, three clean scratch rows, three copied target rows and explicit output accumulation. The construction uses arbitrary dirty targets and no extra connector.

## Contract and construction

Let (V=\mathbb F_2^L). Let (x\in V) be an immutable input and (y_1,y_2,y_3\in V) be arbitrary, independent dirty output rows. Fix arbitrary linear maps (A_1,A_2,A_3:V\to V); no invertibility, commutation or rank assumption is used. A complete call `ADD_i(source,target)` performs `target += A_i(source)`, preserves every other data row and restores its private scratch.

Use these three calls in order:

```text
y1 += A1(x)
y2 += A2(y1)     # reads the updated y1
y3 += A3(y2)     # reads the updated y2
```

Writing initial values on the right, the exact outputs are

```text
Y1 = y1 + A1 x
Y2 = y2 + A2 y1 + A2 A1 x
Y3 = y3 + A3 y2 + A3 A2 y1 + A3 A2 A1 x
```

The result is the product of three elementary shears, expressed as a block map:

\[
\begin{pmatrix}Y_1\\Y_2\\Y_3\end{pmatrix}
=
\begin{pmatrix}
I & 0 & 0 & A_1\\
A_2 & I & 0 & A_2A_1\\
A_3A_2 & A_3 & I & A_3A_2A_1
\end{pmatrix}
\begin{pmatrix}y_1\\y_2\\y_3\\x\end{pmatrix}.
\]

The block formula follows by substitution and holds for every initial state, including nonzero targets. The (n)-stage version uses (y_0=x) and updates (y_i\leftarrow y_i+A_i y_{i-1}) in increasing order. It yields

\[
Y_i=y_i+\sum_{j=0}^{i-1} A_iA_{i-1}\cdots A_{j+1}y_j.
\]

This is a changed sequential interface: an output can become the next call's source after its update. It is not a replacement for independent outputs under a contract that keeps every source read-only and hides every target until the batch ends. Each shear is invertible in characteristic two; if a parent needs the original outputs restored, it must pay the three inverse calls in reverse order.

## Fully charged local comparison

Let c_i be the complete cost of one A_i map application, using the largest price over all source/target ports in either program. It includes child computation, source and target access, private scratch restoration, frame and precision work. Let h2 and h3 be any extra adapter cost for passing an updated output row to the next source port. Let D_chain and D_expand price each program's per-call dispatch, root descriptors, instruction storage and reads, controller work, and allocation/release dispatch not already included in c_i. Let H4 and H10 be the hosting prices of the four live rows and ten rows, respectively. Then the full bills are

```text
chain:    c1 + c2 + c3 + h2 + h3 + D_chain + H4
expansion: c1 + 2*c2 + 3*c3 + 9L + D_expand + H10
```

Thus all child work and per-call access are in c_i; scalar staging is 9L; root program/control and row hosting/allocation remain explicit. The expanded program has six A_i calls, three target-row copies, three clean scratch rows, and the final Y1/Y2 accumulation. The chain has three calls and no extra rows or scalar staging. No memory-to-arithmetic conversion is assumed.
Under a target-hidden batch, compute each source path independently while reusing its prefix. The six terms are

```text
A1 x;  A2 y1;  A2(A1 x);  A3 y2;  A3(A2 y1);  A3(A2 A1 x).
```

This direct expansion costs `c1 + 2*c2 + 3*c3` before staging. It needs three clean length-(L) rows to retain `A1 x`, `A2 y1`, and `A2 A1 x`; the three output rows must be distinct from their read-only inputs and initialized with copies of the initial dirty `y_i`. Scratch initialization, those three target copies, and the final accumulation into `Y1` and `Y2` cost `9L` scalar bit writes/XORs. The three `A3` terms can update `Y3` directly while the target stays unobserved. Thus the comparison includes six map calls versus three, `9L` staging operations versus none, and six additional full rows versus none. Row allocation and release events remain separate charges; no memory-to-arithmetic conversion is assumed.

The map-call component saves exactly `c2 + 2*c3`. In the two-bit fixture, widths and frames match, so h2=h3=0; row allocation and program control are still reported as separate resources. A concrete supplier may have nonzero adapters, descriptor costs or hosting transitions. The selected result mapping is not established here.

### Exact two-bit fixture

Use (L=2), `A1=A3=U` and `A2=Lw`, where

```text
U (a,b)  = (a+b,b)
Lw(a,b)  = (a,a+b)
```

Each map has two active output coordinates, so a complete application uses two scalar target XORs. U and Lw do not commute. The chain costs three map calls or six scalar map XORs. The target-hidden expansion costs six map calls or twelve scalar map XORs plus 9L=18 scalar staging writes/XORs, has three clean scratch rows and three copied output rows, and must pay six row allocation/release lifetimes. Its arithmetic count is 30 versus 6, and the row inventories are four live rows versus ten. These are exact local resource counts, not runtime measurements.

## Evidence and reproduction

The proof is the substitution/induction above. The verifier checks the actual sequential schedule against the separately written source-path expansion for all `16^3 = 4096` triples of 2x2 matrices over F2 and all `4^4 = 256` arbitrary dirty states, for 1,048,576 cases. It also checks the cost identity, noncommuting positive fixture and four failure controls: stale `y1`, stale `y2`, reversed factor order and omitted final stage.

Run from the repository root with Python 3.10+ and no dependencies:

```sh
python3 -B research/recursive-prefix-shear-chain-seed68355377/verify.py
python3 scripts/research_package.py --package research/recursive-prefix-shear-chain-seed68355377 --check-only
python3.12 scripts/research_package.py --package research/recursive-prefix-shear-chain-seed68355377
```

Expected verifier line: `PASS_RECURSIVE_PREFIX_SHEAR_CHAIN cases=1048576 controls=4 direct_calls=6 chain_calls=3 L2_staging=18 direct_arithmetic=30 chain_arithmetic=6 extra_rows=6`.

Local validation passed on Python 3.14.7: the direct verifier and package `--check-only` both pass. The full package hook requires Python 3.12, which is unavailable in this environment; the registered hosted replay remains pending.

## Predecessors and limits

The scope was changed because Discussion [#1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884) has a live two-call question about cross-feeding composite maps. PR [#1439](https://github.com/CrocSwap/integer-mult-bounds/pull/1439), open PRs [#1524](https://github.com/CrocSwap/integer-mult-bounds/pull/1524), [#1739](https://github.com/CrocSwap/integer-mult-bounds/pull/1739) and [#1780](https://github.com/CrocSwap/integer-mult-bounds/pull/1780) concern mutable sources, connector corrections or delivery cuts. PR [#1637](https://github.com/CrocSwap/integer-mult-bounds/pull/1637) adds a second dirty connector. Their results are not imported. This construction changes the output-to-source lifetime across three factorwise stages and introduces no connector operation.

This is an exact finite-dimensional interface construction. It has not been mapped to the selected supplier's calls, frames, hosting, precision or tape costs. No conditional exponent or new κ follows from the local call reduction. See [TASK.json](TASK.json) for the exact accepted seed, pins, scope change and next supplier question, and [SOURCES.json](SOURCES.json) for source hashes.

## Open next questions

Can a selected supplier call pair use this output-to-source lifetime without an adapter? This matters because only a priced binding to the selected call schedule can transfer the local savings to its recursive cost. A feasible first step is to identify one pair of consecutive calls with matching widths and frames and write the complete entry/exit maps. The blocker is the absence of such a selected-source binding and its hosting/precision receipt.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in the construction, exact verifier, cost accounting and writing. No independent human review or full multiplication theorem is claimed. Apache-2.0.
