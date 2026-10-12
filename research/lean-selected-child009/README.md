# One selected Clifford child: exact canonical identity

This package formalizes the interpreted f19 recipe children[7], directed
0→9 (empty frame to [11], rank 1), for every complex payload and arbitrary
spectator coordinates. It proves the actual finite source basis/Q constants
and L C0 R = K C0 K⁻¹, retaining right offset 1/global phase 1. C0 uses the
source Gaussian coefficients (1+i)/2 and (1−i)/2.

Five unchanged accepted sources are included. Two existing sources are pinned
to PR509 and PR513, with their exact public outputs/runtime base retained from
PR528. The complete dependency order is in DEPENDENCIES.json. There are 58
printed reference probes; upstream Stream has none. Lean 4.21.0 and the exact
Mathlib pin are retained. The external inventory is a 2,213-module published
base plus 156 exact extension rows. Reproduction state/results have one owner:
REPRODUCTION.json, hash-referenced by PROVENANCE.json.

The retained construction reports conditional κ = 1517760977820331/10^18
= 0.001517760977820331. KAPPA_CONTEXT.json records the author's literal
source-context check. This package does not prove that multiplier bound.

Raw packed-nine-bit executor/event equality, remaining recipes and wrappers,
expanded coefficient/tableau work, full dirty rows/columns, owner/stage charts
and costs remain open. The proposed 119-record rank-one family is excluded.

Attribution is retained in NOTICE.md, PR509-NOTICE.md and
SELECTED-SOURCE-NOTICE.md. This is one source-bound finite operator proof,
reusing existing monomial, Gaussian and generic stream algebra.

## Offline reproduction

The checker requires Linux with /proc for its stated memory measurements and
resource review. The Lean proof sources themselves are portable.

Use the exact PR509 source root, PR513 source root and PR528 runtime-inventory
root pinned in DEPENDENCIES.json, plus the existing Lean 4.21.0/Mathlib cache.
The command downloads nothing and does not run the selected Python supplier.

```sh
python3 check.py --lean /exact/lean-4.21.0/bin/lean \
  --mathlib-root /exact/mathlib4 \
  --pr509-root /exact/pr509/research/e8-lemma-g-lean \
  --pr513-root /exact/pr513/research/lean-sequential-bank-bindings \
  --runtime-base-root /exact/pr528/research/lean-complete-bank-endpoint \
  --build-dir /new/isolated/build
```

This public command supports a fresh seven-source replay. The maintainer's
measured retained-prefix experiment is recorded only in REPRODUCTION.json:
it reuses the two exact PR528 output quadruples and checks only the five
included sources. ACCEPTED_CHECKS.json retains immutable reference identities.
The checker validates all 58 named probes, all 2,369 cached source/object pairs
and first-match paths. Each job has a 60-second/4-GiB hard limit and stops after
a PASS above 45 seconds or 3.5 GiB VM; optional --slot-service uses the existing
shared FIFO without changing proof inputs. No object cache is bundled.

Repository-wide scientific checks, including make verify and
make gen4-bank-verify, remain separate candidate obligations; this component
checker does not imply their execution or an exact-head hosted-CI result.
