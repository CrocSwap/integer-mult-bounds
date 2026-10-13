# Global hosting proof for the 504-helper increment

## Result and scope

The frozen construction has **global kappa = 0.001517760977820331**, represented exactly as `1517760977820331 / 10^18`. The complex moment root is certified in

$$
0.001520068077832496458155
< b <
0.001520068077832496458156.
$$

The lower endpoint supplies the admitted complex exponent. The complex side remains binding against the inherited bit exponent `0.001565442026981656908596`. The final `EXACT-ASSEMBLY.json` checks the two moment engines and all 47 outer steps. The result uses the same inherited all-size compiler, exceptional-cover, precision/tape, and analytic-transfer contracts as the preceding 112-port result; the finite hosting argument below does not re-prove those contracts.

The controller parameters remain `v = 112`, `h = 9`, `L = 9`, `T = 8`, `K = 4`, and `m = 73`. There are 7,168 live data families and 7,682 physical families, including 504 reserved tableau families, eight centers, and two coefficient-work families. The final construction uses **no helper banks**.

## Supplier and exact global profile

The selected supplier has 504 helpers: 152 residuals of width eight and 352 of width nine. Its paid profile is

$$
H_{\rm local}=
2028H_1+752H_2+156H_3+392H_4+56H_5+56H_6+8H_7.
$$

Its rank mass is 6,240. This equals the unchanged data and center costs plus the actual residual mass:

$$
6240=2(112)(8)+64+(152\cdot8+352\cdot9).
$$

Every entrance reduction is therefore charged through the actual emitted local profile. The new scalar, phase, and residual-wrapper receipts are bound by file hashes; no old 560-helper local checks are used as evidence for the new supplier.

The following table gives the **actual allocation over all eight replicas**. A row counts pending children, not distinct physical families. Multiple helpers within one pending child occur in different complete invocations.

| Parent rank | Whole residual widths hosted in the child | Children | Paid remainder rank |
|---:|:---|---:|---:|
| 8 | 8 | 5,376 | 0 |
| 16 | 8 + 8 | 2,784 | 0 |
| 16 | 9 | 800 | 7 |
| 32 | 9 + 9 + 9 | 3,583 | 5 |
| 32 | none | 1 | 32 |
| 48 | 9 + 9 + 9 + 9 + 9 | 2,759 | 3 |
| 48 | none | 825 | 48 |

Consequently the 7,968 nonzero remainder children are exactly

$$
2759H_3+3583H_5+800H_7+H_{32}+825H_{48}.
$$

Adding 72 copies of the local profile gives:

| Rank | Paid children |
|---:|---:|
| 1 | 146,016 |
| 2 | 54,144 |
| 3 | 13,991 |
| 4 | 28,224 |
| 5 | 7,615 |
| 6 | 4,032 |
| 7 | 1,376 |
| 32 | 1 |
| 48 | 825 |

The arithmetic identities are

$$
\begin{aligned}
\text{local rank mass}&=72\cdot6240=449280,\\
\text{remainder rank mass}&=71424,\\
\text{total rank mass}&=520704,\\
73\cdot7168-520704&=2560.
\end{aligned}
$$

Thus the saving comes from the new paid-rank distribution. The stock-normalized rank deficit remains 2,560.

## Executable whole-owner construction

The discovery program uses the inherited `ASYNC-6` complete-call order and its existing busy windows. Its integer variables couple each pending-child pattern directly to the times and widths assigned to that pattern. This coupling is essential: an aggregate pattern/time nomination can have no physical refinement.

The successful model restricts discovery to a small collection of pure width-eight and width-nine patterns, with integer repair patterns. It finished in approximately 1.82 seconds in the recorded run. Its integral time assignments are expanded by bipartite edge coloring into **36,288 literal helper roles**. The frozen witness is `inputs/OWNER-PLAN.json` together with `inputs/OWNERS.json.gz`. Replaying the frozen witness requires no optimizer.

For every complete invocation, the 504 helper owners and 224 active data owners are 728 distinct physical families. Every helper is scheduled once; its owner's actual idle window contains the whole invocation, including the relevant bridge exclusions. Residual footprints are disjoint within each pending child, and their occupied coordinates form a prefix. The remaining suffix is the paid child listed above. Each width-eight helper also has an explicit spectator coordinate and the selected local supplier's paid normalization wrapper.

The emitted construction contains **2,352 distinct orthogonal 73-column maps**. It has 10,944 entering-helper roles and 27,407 roles borrowing a family from another replica. `ACTUAL-SIGMAS.json.gz` stores the literal maps. `IDLE-REMAINDER-FRAMES.json.gz` stores the actual orthogonal axes of all 7,968 paid remainders.

A same-owner shrinking experiment was also feasible, but its actual remainder profile was inferior. It is not the witness used for this result. Neither a local-only rate nor a chronology-free fractional LP value is substituted for the final physical assignment.

## Admission and reproducibility

`prepare_supplier_base.py` binds the new local artifacts to the unchanged 112-port data routes and exact data phase recipes. The retained `port_restriction` metadata describes the historical Round19 data-port restriction; `supplier_substitution` and the fresh source-artifact hashes identify the new local word. Its conservative parent gives each helper a dedicated bank per stage and lists every bank-complement frame. `emit_supplier_hosted.py` removes all those banks and inserts the frozen whole-owner assignment, actual spectator routes, and remainder children.

`audit_supplier_hosted.py` then performs one independent pass over the serialized controller and ownership data. It imports neither the emitter nor the allocator. It checks complete-call ordering, every owner busy window, full-family exclusion, all residual and spectator maps, source hashes, and the exact paid histogram. The default run does not repeat mutation tests or a phase cold replay; inherited mutation mechanisms remain available through `--mutation-controls`.

The resulting `ASYNC-AUDIT.json`, `OWNERS-AND-PROFILE.json`, and remainder-frame receipt bind the hosted template hash

`ed47b5454779f7ad6b32ae492a13f8b5172b11c94c3877cbc5cc5d7a4c357738`.

The separate fresh invoice checks the new scalar/Horner counts and finite bounds. Its global prefix allowance is 225 bits within the retained 512-bit budget, and its physical row coefficient is 16,467 within the retained 20,161 bound. Exact assembly then produces the global kappa stated above.

The minimal reconstruction sequence is:

```text
python prepare_supplier_base.py --data-base BASE112 --local LOCAL_FINAL --out NEW_BASE
python emit_supplier_hosted.py --base NEW_BASE --owners OWNERS --plan NOMINATION --out HOSTED
python audit_supplier_hosted.py NEW_BASE HOSTED AUDIT/ASYNC-AUDIT.json
```

These three reconstruction and admission scripts use the Python standard library. The discovery allocator additionally uses NumPy and SciPy, but it is not part of the frozen-witness replay.

## Why changing the supplier was necessary

For the preceding 560-helper word, the fixed `L = 9`, `m = 73` data-stock relaxation has widths `18 x 7`, `154 x 8`, and `388 x 9` per invocation. Dropping all timing and integrality constraints while retaining the same pending-child inventory gives the exact ordinary-moment upper endpoint

`b < 0.001460506721431481043439`.

The rational primal/dual certificate is `evidence/PR523-FIXED-WORD-CEILING.json`. It leaves less than 0.03% improvement over the previous complex exponent through replica count, ordering, or allocation alone within that fixed geometry. It is a statement about the former word and pending-child inventory. It does not bound the new 504-helper supplier. The present improvement changes the local paid profile and residual inventory, then closes the actual whole-owner construction and global assembly.
