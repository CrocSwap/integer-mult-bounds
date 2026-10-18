# Read-only transported COPY/ERASE for the covariant dirty reader

**Finite interface construction; no new κ.** We implement

    (X,W) -> (X, W + ε P^t X),       t = 0,1,2,3; ε = ±1,

for the actual native P in [Jose Manuel/jmbarrancoml's PR2742](https://github.com/CrocSwap/integer-mult-bounds/pull/2742), pinned at `8571b04372f539b725e7f27d1ab00c506ca616fd`. All 704 source fields stay unchanged **at every prefix**. Both banks may contain arbitrary correlated dirt; no extra field or CLEAR is used. The opposite sign restores W when X and t are retained. This implements the transported subtraction in that predecessor's caller obligations.

A quarter-turn uses **1,732 scalar operations**, versus 3,336 for the literal source-transform/subtract/source-restore sandwich. After removing avoidable data permutations, a stronger helper-only sandwich uses 2,664. Against that stronger baseline, the new construction saves **932 scalar operations (about 35%)**, or 7,360 retained real-component primitives. These are exact instruction counts, not measured runtime gains or optimality claims.

Both versions still use **240 native payload monomials** and zero positive-rank children for this boundary. No selected centre child is deleted. The accepted κ remains 0.001672660197076918; the pending T74 construction near 0.001717256973467 is a different word and is not changed or admitted here.

## Reproduce

Python 3.12, standard library only, with the three live inputs in VERIFY.json:

```sh
python3.12 -B scripts/research_package.py --package research/covariant-transported-shear
```

Expected: `PASS_READONLY_TRANSPORTED_SHEAR`, four phases, both signs, 1,408 arbitrary input fields, `no_new_kappa`; the independent checker reports eight maps and 22,998 nonzero formal terms. Direct commands are `verify.py` and `independent.py`, both with `-I -B`. Default verification is read-only. `verify.py --emit-words` prints the exact words; RESULT.json binds their canonical hashes without a large committed instruction dump.

## Contract and proof

X and W are disjoint banks with PR2742's 704 input-field types and matching owner/chart interpretation. An identity-field copy between them is an aligned signed ADD. Matching physical placement is a caller premise, not a newly proved owner layout. X aliases neither W nor a writable temporary. Arithmetic is exact.

P acts on 112 data fields as a signed permutation followed by native M, fixes 112 Y fields, and acts on the helpers by a chart. Split the 480 helpers into eight pivots J and the other 472 fields H:

    J = (224,225,226,227,240,241,256,257),
    K(u,v) = (B u + C v, v),
    P_H = K^-1 diag(L,I) K,        L = Q tensor M.

B, C, Q, M, the half-integral B inverse and its 28-operation basis word are predecessor constructions, reconstructed from the actual full dirty reader. Hence

    (P^t X)_J = B^-1[L^t(B X_J + C X_H) - C X_H],
    (P^t X)_H = X_H.

The new word uses W_J as a reversible accumulator, in time order:

1. Apply B, then L^-t to W_J.
2. Add ε(B X_J + C X_H): all 482 signed-unit source loads.
3. Apply L^t, then subtract ε C X_H: all 450 source loads.
4. Apply B^-1.

Its endpoint is `W_J + ε B^-1[L^t(B X_J + C X_H) - C X_H]`. The initial W_J survives because the L powers cancel around the injection. No X field is transformed, and W_H is never substituted for X_H. Afterwards add ε X_H to W_H.

For each signed data edge j -> i of P^t, apply M^-t to W_i, add ε s X_j, then apply M^t. This yields `W_i + ε s M^t X_j`. Remaining identity fields receive one ADD. No work dirt is discarded. The generic block identity is elementary; the contribution is this literal source-bound native implementation, full dirty-state verification and complete local invoice.

PR2742 proves that all data blocks simplify to the same M, including native phases, and all helper operands used here have actual zero frame and identity entry adapter. We rerun its original native checks: all 112 source adapters, eight query blocks and global-phase controls. We additionally check all 448 phase/data frame pairs: M^-t moves the destination into the source's frame before its ADD, and M^t returns it. Helpers remain at frame zero; identity-field copies have matching types. Our new word uses only powers of that monomial and scalar ADD/scale operations. The formal identity over Q[z]/(z^4-1) holds for every order-four payload operator. Substituting the exact native permutation, or its tensor power at any layer count, gives the algebraic all-layer statement. Efficient physical tape realization remains separate.

## Complete local bill and recurrence

The identity phase uses 704 ADDs. Nonzero phases use B and B^-1, the full B/C source injection, subtraction of C, two Q powers and their native monomials. Q quarter-turns use six swaps; the half-turn uses four. Each swap is three signed ADDs and a negation.

| Phase | Full sandwich scalars | Factored sandwich scalars | New ADD | New scales | New scalars | Monomials |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 704 | 704 | 704 | 0 | 704 | 0 |
| 1 or 3 | 3,336 | 2,664 | 1,704 | 28 | 1,732 | 240 |
| 2 | 3,080 | 2,648 | 1,692 | 24 | 1,716 | 240 |

For a quarter-turn, 76 ADDs and 28 scales act within W_J; **1,628 ADDs read X**: 112 data, 584 identity, 482 first helper loads and 450 second loads. The half-turn uses 64 internal ADDs and 24 scales. All 1,408 entry-resident fields remain charged. At tariff eight real primitives per signed complex ADD and two per scale, the new bills are 13,688, 13,584 and 5,632 for quarter-turn, half-turn and identity.

Let N be payload sites per field. Let A(N), D(N), Z_t(N) be the complete costs of an aligned signed ADD, dyadic scale and specified native permutation power, including their memory access. Let F_t(N) charge dispatch/descriptors and placement not already included. The exact boundary recurrence is

    S_t(N) = 1704 A(N) + 28 D(N)
             + 120 Z_1(N) + 120 Z_3(N) + F_t(N),       t in {1,3},
    S_2(N) = 1692 A(N) + 24 D(N) + 240 Z_2(N) + F_2(N),
    S_0(N) = 704 A(N) + F_0(N).

F_1 and F_3 need not be equal. For k boundaries sum the S costs in the actual order. S has no recursive descendants. Every monomial acts on W and needs an in-place permutation implementation or its charged buffer. Machine buffers, physical placement, stream movement and rounded arithmetic are **unresolved, not zero**.

In the abstract logical-access model an ADD reads two cells and writes one; a scale or monomial reads and writes one. A quarter-turn therefore has 3,676N logical reads and 1,972N writes, versus 5,524N and 2,904N for the factored comparator. Instruction/control and physical seeks are additional. This is not a multitape runtime bound.

For the typed child `C_R(D,W)=(D+RW,PW)`, the one-child echo is

    S_0^+ ; C_R ; S_1^- ; C_R^-1.

Its endpoint is D+=RX, with W restored. The complete cost is `S_0 + C_R + S_1 + C_R^-1`; **both child orientations remain**. PR2742's explicit prefix/read/inverse-prefix/P implementation of C_R retains four prefix N or inverse-N executions in this echo. The actual N interval has 936 rank-one and 56 rank-four climbs: four prefixes alone cost rank mass **4,640**, before other scalar/adapter/placement costs. Replacing S_1 changes none of these children. No new complete supplier moment or eight-H8 deletion follows.

## Precision and evidence

Formal row-L1 peaks are 376, 368 and 372 for phases 1, 2 and 3, for either sign, with denominator at most two. Nine additional magnitude bits and one fractional bit suffice for these exact local words. These are sufficient local bounds, not optimized physical precision or a complete approximate recursive error analysis. The new quarter-turn peak can exceed the predecessor action's 374 while fitting the same power-of-two guard.

The primary checker compares all eight generated words against both complete comparators on all 1,408 input columns over Q[z]/(z^4-1). Literal inverse and opposite-sign restoration are separate checks. The second checker reconstructs the reader by forward propagation, independently inverts B, derives the block formula and uses a flat sparse-polynomial interpreter. It imports neither the primary replay nor predecessor mathematical code; it obtains the compiler's emitted word as the object tested. These are two implementations by the same AI-assisted contributor, not independent human review or formal-kernel verification.

Controls reject omitted dirty-helper loads, lost signs, wrong orientation, missing inverse basis and work/source confusion. A coherent helper-identity mutant passes every data/work column but fails dirty source helpers. An endpoint-correct transient source mutation fails the read-only prefix contract. Invalid phases/signs, modified source pins and typed receipts are also rejected with assertions disabled.

Consumed predecessor and native modules execute directly from the authenticated source bytes, with their assertions retained even under `-O`. Two timestamp-valid stale-bytecode sentinels demonstrate that ordinary loading would execute the wrong bytes while this loader ignores them. Credit the contemporaneous [PR2788](https://github.com/CrocSwap/integer-mult-bounds/pull/2788) finding: `-B` prevents cache writes, not cache reads. This source-loading adapter changes no retained mathematical file.

## Research decision and credit

Base `7981b35eb209d0808fe2066bd928cbeff94d00fe`, priority 5, OS seed **50**. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2488#discussioncomment-18959657). TASK.json records the three candidates. An initial destructive pivot reset saved scalar work but did not meet dirty-work restoration. The one evidence-driven pivot was the source-preserving shear. All four phases and both signs are completed; there is no stochastic search or wider optimality claim.

**Expansion decision: stop at this local interface.** No centre child disappears, so a supplier implementation cannot be justified by scalar savings alone. Selected cold replay, new hosting/owners, BIT improvement and outer admission were not attempted. Frozen inputs and the selected frontier are unchanged.

Credit Jose Manuel/jmbarrancoml for P, its chart, native covariance and the transported-ERASE handoff; ywz65 for the dirty reader; Ross Richardson for the dyadic section and typed-cost distinction; Cinna Davis and Aaron Wang for the echo/phase-window lineage; Ali Romman for native tools; and the retained selected construction's contributors. Six consumed predecessor exports, including their original NOTICE, remain byte-identical in vendor/pr2742; VENDOR.json binds exact Git blobs and SHA256 hashes. Tekalign (@tekuuu) prepared the new compiler, proof, checks and documentation with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

- Does a real source-read-only caller need these exact shears with the same bank types? Bind one source/work/output lifetime and replay its complete word. Physical ownership and a useful complete child bill remain blockers.
- Can a changed consumer delete an actual centre child? List old/new native children for the same demanded output before implementation. Covariance or cheaper shears alone do not provide that correspondence.
- Can the 240 monomial traversals and scalar loads share an efficient streaming layout? Start from an explicit owner layout and price source reads and destination permutations; logical-access counts do not settle it.
