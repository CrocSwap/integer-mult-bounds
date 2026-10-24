# Executed checks and evidence boundary

Scientific baseline and publication refresh: canonical main
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, 2026-10-22.
The relevant guidance, selected result and three live source inputs did not
change at the refresh. PR4610 input head:
`1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`.

Completed on CPython 3.12.15, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/controller-thinning-global-ceiling
python3.12 -B scripts/check_research_commit.py --package research/controller-thinning-global-ceiling --check-source-history
git diff --check
```

The registered replay reconstructs both the actual-profile and free-centre
certificates. It checks every maximum and both adjacent differences, both
tight lower endpoints, the uniform derivative bound, both small-exponent
inequalities, all 12,744 source masks and every source projector for the
declared p<=5 cases. Its second command rejects four actual mutations:
live source hash, frozen Git blob, frozen bytes, and an owned-job deletion
whose source hashes were also rebound.

The original arithmetic input and its committed snapshot have the identical
Git blob `c89e009ca4a5ad316c69f0371d885d72045ba415`. The package's local
attributes preserve its CRLF bytes. Earlier authoring runs caught and fixed
a JSON tuple/list comparison and Git line-ending normalization; the normal
registered replay passed after those fixes. `--write` is not substituted for
the registered check.

The exact interval engine is the source-pinned rational Taylor/atanh engine
from higher-moment-strictification, credited to zxv. Floating discovery is
not used by acceptance. The written dominance and calculus proof has not
received independent human or proof-assistant review. The finite source
binding does not prove the retained endpoint contract for unexecuted p.

The current selected cold replay, historical suites, Lean and manual hosted
workflows were not run: no selected construction or shared code changed.
Hosted CI status must be checked separately. No native, physical, compiler,
BIT or outer admission is established by these arithmetic checks.

The final live PR refresh included concurrent #4658, #4654 and #4660.
Their descriptions were inspected and the overlap/escape scope recorded in
README.md. Their full sources and proofs were not independently replayed.
