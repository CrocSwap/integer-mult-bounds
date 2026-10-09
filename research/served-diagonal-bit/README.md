# Served diagonal operations on PR200's bit word

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{692144604250060}{10^{18}}=0.000692144604250060 .
$$

That is **+1.088%** over PR217 (`684696826673891/10^18`, the best completed claim) and **+1.330%** over PR205 (`683061299399923/10^18`).

| Construction | Bit coarse saving | Conditional kappa |
|---|---:|---:|
| PR205: PR200 word, packed | 6.83528e-4 | 0.000683061299399923 |
| PR217: butterflies and optimized frames, packed | 6.85166e-4 | 0.000684696826673891 |
| Served word, unpacked | 6.86716e-4 | 0.000685800818606951 |
| **Served word, packed** | **6.92624e-4** | **0.000692144604250060** |

## What is new

PR200's bit word mixes each partner pair on its data registers: the carrier register gets `x_c + x_d`, and the passive register keeps `x_d`. The same word also builds `x_c + x_d` again in auxiliary registers. At 373 of these operations, the control register is a pure copy of `x_d`, made by one copy operation and used once.

This package reads `x_d` straight from the passive data register at those 373 operations. It then deletes the 373 copies and their copy operations. To keep the passive register's frame chain nested, the pair's partner mix moves to right after the injections. The passive chain gets one extra 3-dim stop: `line → mix → F_i → full`.

| Per copy | PR200 | Served |
|---|---:|---:|
| Logical auxiliary roles | 18,908 | 18,535 |
| Physical chains | 17,114 | 16,741 |
| Stock `W` | 20,634 | 20,261 |
| Deficit | 1,936 | 1,936 |
| Coarse bit saving | 6.77774e-4 | 6.86716e-4 (+1.32%) |

Every frame stays one of PR200's witnessed frames. The 34 terminal sinks, the 1,760 aliases, the gauges and every other operation are PR200's.

**Checks.** `bit/served_prove.py` checks the served word completely, in the same way as PR200's `bit/prove.py`:

- all 20,295 formal columns in F2 (identity) and over the integers (defining decoder), with no sampling;
- exact frame geometry with PR200's PR168 v4 integer backend, including each served frame and the new passive chains;
- PR200's 34 terminal sinks through a forked terminal compiler, with the scalar bill retained;
- PR200's paid-moment certification, imported unchanged;
- seven adverse word controls and three terminal controls, all rejected.

**Banks and arithmetic.** PR205's completed banks (PR197's construction) then apply with new counts: 3,300 small banks and 41,423 large banks over three copies, so `W = 55,283` and the deficit is `5,808`. Three finite ordinary-leaf levels and PR193's unchanged 47-constraint assembly give κ. The bit branch binds; the complex supplier (`700918443859411/10^18`) has slack.

`PROOF.md` gives the argument.

## Verify

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds a1175449f34d39ff933d9d8ab23ced1f32b290ec
git worktree add --detach ../served-bit-pr200 a1175449f34d39ff933d9d8ab23ced1f32b290ec
git fetch https://github.com/CrocSwap/integer-mult-bounds 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git worktree add --detach ../served-complex-pr193 187e1010ac8b259af8e9b5166f68b64bc27b4b47
python3 -m pip install -r ../served-complex-pr193/research/source-assisted/requirements-round13.txt
python3 -B research/served-diagonal-bit/verify.py --complex-root ../served-complex-pr193 --bit-root ../served-bit-pr200 --full
```

`--full` takes about five minutes on Linux. It runs:

1. PR193's and PR200's unchanged package verifiers;
2. `patch.py`, which derives the served word again from PR200's frozen word and must match the frozen files;
3. `bit/served_prove.py`, the complete check of the served word and its sinks;
4. PR205's charts, banks and colouring on the served word;
5. the arithmetic, the independent audit and the bank endpoint controls.

Without `--full`, the saved receipts are used, and only the pins and the arithmetic run. The terminal compiler needs Linux (`resource`).

## Scope and credit

This is a conditional finite construction and composition. It is not an unconditional multiplication theorem or a speedup claim. The all-size compiler, analytic, precision, restored-row and fixed-tape hypotheses are inherited exactly as in PR200, PR205 and PR197.

The served operation is new. Credit for everything it builds on goes to:

- Chafik Boukhalfa (PR200) for the bit word, its sinks, witnesses and verifier, which the served checks fork;
- Rohan Arun (PR205) and Evan McKinney (PR197) for the completed banks and their code;
- PR193 for the complex supplier, and icekylinx for the source-assisted method and the paired-cube framework;
- eumemic (PR168), jamesyc (PR166) and PR185/187 for the backend, the terminal lemma and the leaf composition;
- hcg890 (PR217) for the previous best claim.

Prepared by Avi Eisenberg with Anthropic Claude assistance. Apache-2.0.
