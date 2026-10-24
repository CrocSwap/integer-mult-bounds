# A complete local residual contract for the inverse-coded pair

The guard `P=p+ceil(9f/2)+5` suffices for both pair outputs at every f>=1,
provided the two actual inverse kernels return at most two grid units of
error and each of the other six residual vectors has at most one. The new
proof includes FULL and Gaussian errors, which PR #5322 treated as zero.
It also proves `||Q^-1 C Q||_(infinity,real)=26*2^f` for the actual code.
The complete paid Gaussian profile and kappa do not change.

[PROOF.md](PROOF.md) gives the chronological identity, unequal site budgets,
quantified proof, source credit and limits. [RESULT.json](RESULT.json) records
the exact checks. [SOURCES.json](SOURCES.json) pins canonical main
ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority 7. The scoped
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19151016)
excludes the active native-history construction.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/physical-pair-full-residuals
python3.12 -I -O -W error -B research/physical-pair-full-residuals/verify.py
```

Expected marker: PASS_FULL_PAIR_RESIDUAL_TRANSFER. Both modes check 63
chronological cases, all 5,824 block premises, 3,072 literal rows/columns,
12 actual source-kernel vectors and 500 guard widths. Source modules load
from authenticated source bytes. The written proof covers the all-width
result. No full physical caller, provider-accuracy, Lean, compiler or
selected-frontier replay ran.

## Open next questions

Bind each returned residual allowance to one physical provider and include
its input range, internal precision, movement and cost. A changed or shared
boundary caller still needs an affordable complete invoice. TASK.json states
the next check and blocker.

## Credit

JoyboyBrian's PR #5069 supplies the pair; PR #5035 supplies the finite kernel.
Dillon's PR #4933 supplies the normalizers and terminal formula. PR #5322
supplies the inverse-only error transfer. PROOF.md links these predecessors.
The retained native, controller, precision and compiler authors keep their
credit. New all-site theorem and checks: Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0. Author-checked, not independent acceptance.
