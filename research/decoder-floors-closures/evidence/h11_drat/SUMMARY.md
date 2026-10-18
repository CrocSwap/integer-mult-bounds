# h = 11 DRAT evidence (attached after opening; no claim changed)

This folder attaches proof-checking logs for Theorem H11 (README §3.2), which the README records as kissat-checked.
It adds evidence only. The statement, scope and labels in README.md are unchanged.

Counts, from `dratH11b.log.txt` and `dratH11.log.txt` (one line per query: kissat result, then drat-trim result against that query's own CNF):

- T(11): 522 / 522 distinct CNFs `s UNSATISFIABLE : drat VERIFIED`.
- G(11,3): 46 / 46 orbit representatives `drat VERIFIED`. Rep 12's line in the older log is not verified; the newer log verifies it.

Driver: `dratH11b.sh.txt`, which runs `../h10/drat1b.sh` on `../h10/hk.py` and `../h10/hk3.py`, both byte-identical to the shipped copies.
Every run was capped at 20 min, used kissat only, and checked the text DRAT with drat-trim.

The encoding options used by these runs come from `hk3.py`. They differ from the kissat runs recorded in the README:

- `RREF=1`: the ψ and φ constraints depend only on their spans, and every subspace has a unique reduced row-echelon basis. So imposing RREF on both tuples keeps exactly one representative per (span, span).
- `ORTH=1`: adds φ_i·ψ_j = 0. This clause is implied, because rowspan V[A] = (ker V[A])^⊥ over F2.
- `GAUGE=A`: the gauge clique may be any non-orthogonal 8-clique; `A` takes the first one inside A.

Each option either adds implied clauses or removes symmetric duplicates, so UNSAT of the encoded CNF implies UNSAT of the original query.
SAT controls stay SAT under the same options: T(11,2,1,p65) and T(11,1,2,p1) with RREF+GAUGE=A+ORTH, and T(11,0,3,p3) and T(11,2,1,p3) with RREF.

The proofs themselves are not shipped because of their size. To regenerate one, run the logged command line.
