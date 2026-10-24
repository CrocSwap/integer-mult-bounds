# Exact two-call capacity of homogeneous query chains

**Conditional operator theorem, author-checked; no new kappa or native supplier.**
For every n>=2, two calls to a homogeneous chain U_n=I+Q J_n and its actual raw
inverse transpose can deliver exactly

    r = 2 floor((n-1)/2)

independent Q jobs while restoring the other arbitrary input fields. Every
boundary uses only scalar mixing and the global monomial P=Q^2. For odd
n=2m+1 the explicit circuit uses 5m-2 scalar ADDs, m swaps and 3m signed-P
scales. A different weighted cyclic middle boundary attains n-2 jobs for every
even n. Counts are field macros; physical movement and precision remain unpriced.

| Chain fields | Q jobs from two calls | Restored spectators | Boundary ADDs | Swaps | Signed-P scales |
|---:|---:|---:|---:|---:|---:|
| 3 | 2 | 1 | 3 | 1 | 3 |
| 4 | 2 | 2 | 5 | 7 | 5 |
| 5 | 4 | 1 | 8 | 2 | 6 |
| 6 | 4 | 2 | 11 | 12 | 6 |
| 7 | 6 | 1 | 13 | 3 | 9 |

This extends the three-field conditional identity in Cinna Davis's
[PR4698](https://github.com/CrocSwap/integer-mult-bounds/pull/4698), whose frozen
source/proof are pinned in [SOURCES.json](SOURCES.json). The proof also shows
that no two-call word in the scalar/global-P ring can produce more jobs, even
with arbitrary restored dirty workspace. It permits any inverse/transpose
orientation and arbitrary invertible boundaries over that ring. Broader physical
monomial/address operations and isolated small tensor widths are excluded from
the upper bound. The constructive identities hold at every positive width.

[PROOF.md](PROOF.md) gives the all-length constructions, restricted optimality
proof, width qualification and complete conditional moment ledger.
[verify.py](verify.py) checks all independent inputs symbolically over
Z[q]/(q^4-1) for every length 2 through 32, every boundary count, both parity
circuits, thirteen semantic mutations, 256 finite dirty-workspace rank fixtures,
and the tensor-width qualification. These finite checks supplement the written
proof; they do not prove physical realizability or certify multiplication.

## Budget and expansion decision

With n transverse rank-b main fields per provider, autonomous helper moment H_t
and complete paid moment P_t, the two-call surplus is

    2 H_t + r(2b+1)^t + (n-r)(2b)^t - 2 P_t.

Writing E=P_1-H_1-nb, the C=0 rank surplus is r-2E. A new physical offer
needs E<r/2 to pass this positive-rank test; the full moment at the proposed
saving and every later cost still need checking. Directly building the chain
from its n-1 unary queries loses at least 2(n-1)-r moment units for every
0<=t<=1 with b>=1. Longer chains alone do not repair that bill.

**Decision: retain the proved module; stop direct unary synthesis.** No native
expansion is warranted until a named changed provider has a complete favorable
budget. The retained-center source has heterogeneous charts and incoming helper
noise, as recorded in [Discussion4840](https://github.com/CrocSwap/integer-mult-bounds/discussions/4840).
No native homogeneous offer is obtained from its scalar Jordan chains.
Acquisition, actual chart maps, dirty restoration and independent helper targets
are unknown for the proposed longer chain. Physical movement/precision,
completion, compiler, BIT and outer recovery remain unrun and unpriced.

## Reproduce

From the repository root, using only the Python standard library:

```sh
python3.12 -I -B research/homogeneous-chain-extraction/verify.py
python3.12 -I -O -B research/homogeneous-chain-extraction/verify.py
python3.12 -B scripts/research_package.py --package research/homogeneous-chain-extraction
```

[RESULT.json](RESULT.json) is deterministic and must match replay. No Lean,
Docker, all-history suite or selected-frontier replay is required for this
scoped theorem. The selected conditional kappa remains 0.00302015. See
[TASK.json](TASK.json) for the exact base, original assignment, overlap boundary,
claim, and explicit expansion gate. Upstream and frozen predecessors are unchanged.

## Open next questions

- Can an actual changed native provider supply even one five-field homogeneous
  chain with excess E<2, arbitrary spectator/helper restoration and a positive
  full moment? Begin with its literal source/target chart contract and complete
  two-orientation invoice; stop on an unfavorable optimistic bill. No provider
  meeting this allowance is identified here.
- Can a named additional free physical monomial/address operation exceed this
  ring-restricted capacity? Begin with one actual source-compatible operation
  and replay the full endpoint on all independent inputs. The broader physical
  operation model is outside the optimality proof and still needs a full bill.

## Credit and scope

Cinna Davis / 1337isnot1337 supplies PR4694's coupled retained-center extension,
PR4698's helper normalization and conditional three-chain consumer, and the
PR4440/4470 controller lineage. Retain Cao Yifan / intqwq, zxv, Jacob Alan
Sussman, Ryanson Jonathan and all cited native/compiler/precision predecessors.
Their actual native construction is not replayed or modified here. The new
contribution is the all-length proof/circuits, restricted workspace bound,
and explicit acquisition allowance. Prepared for Cinna Davis with substantial
OpenAI Codex assistance. Apache-2.0. No independent human or proof-kernel
acceptance is claimed.
