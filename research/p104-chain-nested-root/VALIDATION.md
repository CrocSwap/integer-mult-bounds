# Verification record

Executed on 2026-11-07 with CPython 3.12.14 and the standard library, on a
checkout of the base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Complete scientific replays

| Run | Result | Elapsed seconds |
|---|---|---:|
| Receipt regeneration (`verify.py --write`) | PASS_CHAIN_NESTED_ROOT | 313.33 |
| Standalone normal replay | PASS_CHAIN_NESTED_ROOT | 308.67 |
| Standalone optimized (`-O`) replay | PASS_CHAIN_NESTED_ROOT | 182.93 |
| Registered normal replay | PASS_CHAIN_NESTED_ROOT | 286.32 |
| Registered optimized replay | PASS_CHAIN_NESTED_ROOT | 181.15 |

The registered command was:

```sh
python3.12 -B scripts/research_package.py --package research/p104-chain-nested-root
```

It returned `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `completed`.
Every replay reproduced the committed `RESULT.json` exactly.

## Coverage

The replays rebuild the #6824 native word from the #6702 word (payload SHA256
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`, unchanged) and
recheck it: all 801 x 801 endpoint coefficients, all 2,940 used native maps by signed
Pauli action and absolute phase, and 5,120 changed-pair columns.

The new caller (event SHA256
`03ecddfd75d0dbe325fcc489a50ae7657364482f0d887d81fa131ff6bf41fe70`) is rebuilt from the
family formula and compared with `CALLER.json`. Checked: exact root algebra and every
chain-merge hypothesis; forward and reverse replay of all 400 coefficients; a separately
written adjoint; a separately written symbolic root product; the literal word at `Q = ±1`;
and the line and dual of all 16 merged idles read from the word.

Also checked on the literal word: all 7,488 caller contacts by two implementations, the
adapter inventory (225,784 elementary maps), the field allocation, the independent invoice,
both exact interval engines, strictification, compiler and the 54+4 outer inequalities at
conditional kappa 16859/5000000. The raw crossing from the package is in
(0.0033718004754, 0.0033718004755).

The gate shape (4,4,1|1,4,4) is replayed both ways. Its histograms equal the retained #6726
caller's minus one cancelling pair `T_32 = P_32 = 208`, and both engines place its crossing
in (0.00330823456614, 0.00330823456615).

Negative controls reject a deleted LOCAL, QUERY, IDLE_ONE, LAMBDA and ADD; a shrunk or grown
merged idle; a merged idle on the wrong line (primary and independent audit); a wrong phase
on a thin query, a LAMBDA and an output target; aliased native inputs; aliased caller inputs
(a clean check that source and destination roles differ, before replay); an unpaid idle in
the invoice; a wrong root coefficient; omitted main, idle and query adapters; an omitted
contact phase; aliased native helpers; and an insufficient BIT budget. The #6824 lift
controls still pass.

## Recomputed bounds

Ordinary bound 488,177,792 (was 535,415,008), below 10^9. Compiler grid gap
1/20,000,000,000 (was 1/1,750,000,000). Physical contacts 7,488, recomputed and the same
count. Strictification ratios: gamma 0.94044, delta 0.87816, both below 31/32. The public
inventory 772, owned labels 29, owned lifetimes 47 and peak 14 are unchanged, as the native
word is unchanged. The claim is below the retained BIT saving .0034.

The five inherited framework assumptions remain. Whole idles at ranks 48 to 64 extend the
rule #6726 used at rank 40, with no new compiler proof. Hosted CI, a materialized full
multiplier, formal proof-kernel acceptance, human peer review and authentication of
historical pending-commit ancestry are not claimed.
