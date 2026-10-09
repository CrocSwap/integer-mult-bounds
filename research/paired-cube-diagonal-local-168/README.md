# Face-diagonal local circuits on both suppliers of PR168 v4 paired cubes

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{166261725903847}{25\cdot10^{16}}
=0.000665046903615388.
$$

The package applies to `main` at `3b6b66891c0ac888521cf591fe306c6286601d4f` (which integrates Dugongue's #186 on top of my #181 and eumemic's #168). Its construction inputs are eumemic's PR168 at `4a3c769e5c5430e7114c4d3e099ff34664677f17`; the twelve PR168 v4 files it executes or pins (compiler, physical checkers, package bit checker, parent certificate, frame-theorem note) are carried byte-identically in `references/pr168-v4` with their digests, so the package is self-contained on `main`. On the complex side this package replaces the per-cube local channel circuit by a configuration found by random restarts and coordinate descent over PR144's circuit options: the sums $A[0,0]$, $A[0,1]$ and $A[1,1]$ are assembled from the two face diagonals, $A[1,0]$ from direction-2 edges and $A[2,\cdot]$ from direction-1 edges; the channels $G[0,1,\cdot]$ and $G[0,2,1]$ use edge differences and $G[0,2,0]$, $G[1,2,0]$, $G[1,2,1]$ use fixed-coordinate differences; $F=A[2,0]+A[2,1]$. The circuit has 33 additions per cube instead of 27, but the carrier closure admits 12,189 arcs instead of 10,704, so the virtual auxiliary stock falls from 13,372 to 12,877 roles. The modules, fused outputs, nested schedules and all other inputs of PR168 are retained. A new carrier matching, gauge selection, endpoint frame descent and compensated handoffs are regenerated for the new graph, and 44 terminal-output deletions are selected by this package's own checker. On the bit side it keeps the face-diagonal bit local circuit, our physical layer and the 34 terminal sinks of PR189; both suppliers and the paid balanced composition are independently verified.

| Complete paid profile, per group vertex | Complex | Bit |
|---|---:|---:|
| Local / ambient dimension | 22 / 66 | 24 / 72 |
| Scalar virtual auxiliary roles | 12,877 | 19,348 |
| Physical auxiliary roles | 10,523 | 17,554 |
| Compensated handoffs | 2,310 | 1,760 |
| Terminal deletions | 44 | 34 |
| Total persistent roles | 13,163 | 21,074 |
| Rank mass | 867,438 | 1,515,392 |
| Rank deficit | 1,320 | 1,936 |
| Largest child | 20 | 60 |

The complex saving is $b=665489485337/10^{15}=0.000665489485337$. The bit coarse saving is $a_0=668298937775631/10^{18}=0.000668298937775631$. Its established ordinary wrapper uses

$$
\theta=\frac{133575656392233867107}{2\cdot10^{23}},\qquad
A_B=(1-\theta)a_0+\theta\frac{384599}{10^{10}}
\approx0.000667878281961169.
$$

Both supplier moments use outward rational intervals. The bit moment includes the complete worst-case rare-class fallback; the strict atom and internally borrowed-row tolls are paid. **The complex supplier limits the selected bound:** the transfer saving is $a=(1-\beta)b-\zeta<A_B$.

Run the read-only finite verifier with Python 3.11 or newer:

```sh
python3 -B research/paired-cube-diagonal-local-168/verify.py
```

It verifies the full source closure, signed graph, original and terminal-modified complex words in both directions, every formal source/target/dirty column, complete target chronology, the new bit graph through the retained package checker, our physical bit layer, the terminal-modified bit word's F2 identity and its defining integer decoder, all used-frame prime witnesses, exact paid moments, full scalar/group/router/row bills, 47 strict inequalities, seven margins and adverse controls. It reproduces `certificate.json` and rejects source drift. No foreign producer or aggregate checker runs for package admission. `--write` is an authoring operation before source freeze.

All 24,459 used bit frame IDs, including every descended operation frame, have distinct integer Gram witnesses. Their largest cleared determinant has 118 bits; exact factor identities leave every prime factor below $2^{80}$. The original range $q>2^{80}$ is therefore retained.

The full repository gate applies PR154's isolated snapshot technique:

```sh
python3 -B research/paired-cube-diagonal-local-168/verify_parallel.py --output /new/path/verification --jobs 8
```

It discovers all 16 native `verify` groups of `main` and runs those plus this package in separate clones of one frozen source snapshot. Every group must preserve every input byte; nested jobs are limited to one. The package workflow also verifies Python 3.11, 3.13 and 3.14. The verification baseline is `main`, which already carries PR175's retired-register update. No new benchmark or whole-suite speed claim is made.

[PROOF.md](PROOF.md) states the construction and retained obligations; [NOTICE](NOTICE) records provenance and assistance. `SOURCE.json` pins every package and prerequisite byte. Matched arithmetic comparisons keep the same suppliers while changing the positive outer backoffs. Adjacent grid exclusions concern only these fixed certificates and parameters.

This is a conditional finite witness. General Clifford/tensor interfaces, uniform weighted bit compilation, internally borrowed rows, paid positional layout, precision/recovery and analytic fixed-tape transfer remain source-specified contracts. It is neither an unconditional multiplication theorem nor a practical runtime measurement.
