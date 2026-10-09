# Shared-edge local circuit on PR168 v4 paired cubes and paid balanced transfer

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{659180578557293}{10^{18}}
=0.000659180578557293.
$$

The exact prerequisite is eumemic's PR168 at `4a3c769e5c5430e7114c4d3e099ff34664677f17`. This package changes only the per-cube local channel circuit of its complex word: the three local sums $A[1,0]$, $A[1,1]$ and $A[2,1]$ are assembled from edge sums along direction 0, which the $G[1,2,\cdot]$ channel already shares, instead of edges along directions 2, 2 and 1. The circuit has 29 additions per cube instead of 27, but the carrier closure admits 11,364 arcs instead of 10,704, so the virtual auxiliary stock falls from 13,372 to 13,042 roles. The modules, fused outputs, nested schedules and all other inputs of PR168 are retained. A new carrier matching, gauge selection, endpoint frame descent and compensated handoffs are regenerated for the new graph, and 44 terminal-output deletions are selected by this package's own checker. The unchanged PR168 physical bit supplier and the paid balanced composition are independently verified.

| Complete paid profile, per group vertex | Complex | Bit |
|---|---:|---:|
| Local / ambient dimension | 22 / 66 | 24 / 72 |
| Scalar virtual auxiliary roles | 13,042 | 19,788 |
| Physical auxiliary roles | 10,688 | 18,028 |
| Compensated handoffs | 2,310 | 1,760 |
| Terminal deletions | 44 | 0 |
| Total persistent roles | 13,328 | 21,548 |
| Rank mass | 878,328 | 1,549,520 |
| Rank deficit | 1,320 | 1,936 |
| Largest child | 20 | 60 |

The complex saving is $b=132438677973/(2\cdot10^{14})=0.000662193389865$. The bit coarse saving is $a_0=6600253783597/10^{16}$. Its established ordinary wrapper uses

$$
\theta=\frac{329807692103940705443}{5\cdot10^{23}},\qquad
A_B=(1-\theta)a_0+\theta\frac{384599}{10^{10}}
\approx0.000659615384207881.
$$

Both supplier moments use outward rational intervals. The bit moment includes the complete worst-case rare-class fallback; the strict atom and internally borrowed-row tolls are paid. **The bit supplier now limits the selected bound:** the transfer saving is $a=A_B<(1-\beta)b-\zeta$.

Run the read-only finite verifier with Python 3.11 or newer:

```sh
python3 -B research/paired-cube-local-168/verify.py
```

It verifies the full source closure, signed graph, original and terminal-modified complex words in both directions, every formal source/target/dirty column, complete target chronology, the bit F2 identity and its defining integer decoder, all used-frame prime witnesses, exact paid moments, full scalar/group/router/row bills, 47 strict inequalities, seven margins and adverse controls. It reproduces `certificate.json` and rejects source drift. No foreign producer or aggregate checker runs for package admission. `--write` is an authoring operation before source freeze.

All 24,601 used bit frame IDs have distinct integer Gram witnesses. Their largest cleared determinant has 118 bits; exact factor identities leave every prime factor below $2^{80}$. The original range $q>2^{80}$ is therefore retained.

The full repository gate applies PR154's isolated snapshot technique:

```sh
python3 -B research/paired-cube-local-168/verify_parallel.py --output /new/path/verification --jobs 8
```

It discovers all 14 native `verify` groups and runs those plus this package in separate clones of one frozen source snapshot. Every group must preserve every input byte; nested jobs are limited to one. The package workflow also verifies Python 3.11, 3.13 and 3.14. The verification baseline includes PR175 at `f1081fabbfadaaaaf7292a40d428dbbb865ce920`: its exact four-file ordered retired-register update preserves compiler selection order and mathematical certificate fields. No new benchmark or whole-suite speed claim is made.

[PROOF.md](PROOF.md) states the construction and retained obligations; [NOTICE](NOTICE) records provenance and assistance. `SOURCE.json` pins every package and prerequisite byte. Matched arithmetic comparisons keep the same suppliers while changing the positive outer backoffs. Adjacent grid exclusions concern only these fixed certificates and parameters.

This is a conditional finite witness. General Clifford/tensor interfaces, uniform weighted bit compilation, internally borrowed rows, paid positional layout, precision/recovery and analytic fixed-tape transfer remain source-specified contracts. It is neither an unconditional multiplication theorem nor a practical runtime measurement.
