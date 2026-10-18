# Sparse P112 masked completions have additive matrix rank

Let R be the112x8 real root matrix for P112, normalized to norm-two roots. Let A and B be arbitrary port sets with **at most52ports each**, and let Q be any complex |A|x|B| matrix. Then

```
rank(2 R R^t + E_A Q E_B^t) = 8 + rank(Q).
```

Here E_A and E_B insert coordinate spikes on the chosen ports; transpose is ordinary, not conjugate transpose. In particular this applies to masked completions when Q is supported only on odd-inner-product entries. Any rank-one factorization of that specified completion needs at least8+rank(Q)terms, **including any cost-zero terms**. This does not give a paid-copy lower bound, since term rank and copied-information rank are different quantities.

The proof also identifies the exact P112 root-code minimum support **53**, over complex coefficients. The52port condition is sharp for unrestricted block corrections: an explicit53x53 rank-one correction lowers the completion rank from8to7. That boundary control changes diagonal entries and is **not** a masked completion; sharpness within odd-only corrections remains open.

## Proof

A nonzero complex root-linear vector Ra has a real root zero set spanning a proper real subspace: if its real span were eight-dimensional, a would be zero. Extend a basis of those roots to a root-spanned real hyperplane. By PR968's retained E8 hyperplane-flat classification, that hyperplane is E7, with63root lines, or one of the other seven types, each with at most42lines. E7 hyperplanes are root-normal hyperplanes. The exact census of all120root normals after removing the canonical frame finds support53for112normals and56for8normals. Thus every nonzero complex Ra has at least53nonzero coordinates: other flat types leave at least112-42=70. Root normals attain53. This uses the same classical classification premise F6 as the predecessor; the finite checks do not replace that premise.

If |A|<=52 then no nonzero root-code vector is supported on A. Therefore [R,E_A] has full column rank8+|A|: a dependence Ra+E_Au=0 would either give a forbidden codeword or force a=u=0. Likewise [R,E_B] has full column rank. Factor the completion as

```
[R,E_A] diag(2I_8,Q) [R,E_B]^t.
```

Left and right inverses of the outside matrices show that multiplication preserves the middle rank, proving8+rank(Q) for arbitrary complex Q. There is no finite-sampling step in this argument.

For the53support control choose a live root normal alpha and c=R alpha. The matrix 2RR^t-cc^t has rank7 because alpha has squared norm2, so2I-alpha alpha^t has one-dimensional kernel. Both spike supports are supp(c), of size53. The implementation doubles root coordinates and clears denominators; its integer matrix8G-cc^t is the same projection up to a nonzero scalar.

## Exact evidence

The independent root enumeration confirms the complete support histogram. Five odd matching corrections on1,2,8,16and52distinct rows/columns have ranks9,10,16,24and60, with explicit edges. A four-entry odd rectangle has correction rank1and completion rank9: counting changed entries instead of rank would give a false bound. Every finite rank lower bound is certified by elimination modulo the explicitly checked prime65521; the displayed factorizations supply equal rational upper bounds. The53support cancellation has rank7, and restoring any one of the53removed roots repairs the root/spike independence.

Python3.12+, standard library, from the repository root:

```
python -I -B research/p112-sparse-completion-rank/rank_check.py
python -I -O -B research/p112-sparse-completion-rank/rank_check.py
python scripts/research_package.py --package research/p112-sparse-completion-rank
```

Complete receipts are compared. No coefficient circuit, changed helper inventory, physical invoice, new kappa, native admission or all-size proof is claimed. All such charges are unpriced; this is only a necessary factorization-rank screen.

## Open next questions

Can an odd-only correction supported on53rows and53columns break additivity? First enumerate rank-one odd rectangles whose row span meets a minimum-support root-code direction. Ordinary projection cancellation is not allowed by the mask. Even a favorable rank result would still require copied-information costs and physical realization.

## Credit and overlap

The geometric model and classification premise are DreamingOfClouds PR717 and themilkman216 PR968, with the complex-coefficient distinction from woklerx PR1077. Pending PR1360 studies a single odd-entry rank-nine completion and its copied-information floor; this rank law covers arbitrary correction matrices and blocks through52ports per side and makes no copied-information claim. PR1180 concerns factor-linear all-pairs costs, not these enlarged spike spaces. Source pins are in SOURCES.json. Prepared for woklerx with substantial OpenAI Codex assistance; Apache-2.0. No independent human review claimed.
