# A funded endpoint change permits another helper split

This package starts from exact #7120 `b3d68cf1db9bf493ded2d8f4cb922939edc0ef95`, native hash `4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34`. Its complete 26-file export and all nested sources are authenticated, and every source native byte is reconstructed before the new construction.

The boundary group is 3→246, dimensions zero and eight. It now contains roles 231,449,707. The funded split in #7117 moved role 231’s endpoint from chart 127 to 246. In frozen #7115, role 231 has endpoints 3→127 while 449 and 707 have 3→246, so the common-group boundary basis below was unavailable. The present result uses this changed target contract. It retains #7120’s distinct ToikY chart-120 composition.

At source cut 31847, all required fields actually occupy chart 259, basis[21,38,459], dimension 3, nested in chart 246. No MOVE is relocated, inserted or removed. With P the exact prefix and S the suffix, the checker proves

    a = e448ᵀ,
    b = e448 + e1205/16 − e995/16,
    c = e231ᵀ − 4e707ᵀ,
    d = e449/8 − e707/4,
    aP=c,  Sb=d,  ab=cd=1.

The boundary basis G satisfies row231(G)=c and Gd=e231; the cut basis J satisfies row231(J)=a and Jb=e231. The attributed Ali Romman routine emits seven instructions for G and six for J. Their inverses are exact, and every scalar remains in the retained alphabet. Both boundary vectors use only the same independent helper group; all cut vectors and pivot 231 occupy259. Complete rational prefix/suffix checks include every other public input and all owned rows.

For direct inspection, the emitted bases are:

```
G at chart 3:
  x231 += x707
  x707 -= x231
  x231 += x707
  x707 *= -1
  x231 *= -4
  x449 -= x231/8
  x231 += x707

J at chart 259:
  x231 += x448
  x448 -= x231
  x231 += x448
  x448 *= -1
  x995 += x231/16
  x1205 -= x231/16
```

The inverses reverse instruction order and invert each scalar operation. The successor-side instructions use role 1489 for the continuing pivot. The output G uses chart 246.

Apply G⁻¹ at the input boundary, followed by P and J. Coordinate231 then equals its original independent input because aPG⁻¹=cG⁻¹=e231ᵀ. Retire that field at259 and replace its continuation by a fresh independent input z, using new role 1489. After J⁻¹, S and G at the output boundary, the output change is G S b(z−x231)=Gd(z−x231)=e231(z−x231). Every other endpoint remains unchanged. This argument uses neither an inverse of P nor an inverse of S, and retains the owned initialization/erasure assumptions.

The retained target becomes3→259, rank 3. The fresh arbitrary input has target259→246, rank 5. The construction adds 20 ADDs and 6 SCALEs, with no MOVE changes. It has 73,698 events,1,490 public inputs and 1,090 independent helpers. All54 owned lifetimes, peak 43 and 23 rises of mass 56 are unchanged. Complete forward and adjoint checks verify the emitted word, whose canonical hash is `0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc`.

For H_r=r^(1−κ), the native signed gain is H3+H5−H8>0 for 0<κ<1, by strict concavity/subadditivity. The entire paid Counter is unchanged. Across the retained 17-stage caller, ΔT={3:+17,5:+17,8:−17}; ΔP={}. Rank surplus remains 1424 and there is no empty credit. Both exact engines reconstruct the complete source and candidate invoices and reject #7120’s invoice at the new claim.

The scalar bases, new independent input, odd conversions, complete grid/envelope, physical maps, ordinary work, and regenerated compiler/fixed-tape gates are charged in APPLICATION.md. This is a conditional component application under the five retained assumptions; independent human/formal review and maintainer admission remain separate.

Credit Ali Romman for the independent helper/basis identity, Jerry Chen/CubeJerry for native/invoice and causal tools, Matarener for complete discovery kernels/pairing, Rohan Arun for the 17-stage caller/application, ToikY for the retained chart 120 pattern and signed predecessors, DreamingOfClouds, Douglas Colkitt/#7000 reviewers and every retained source notice. The exact current-source construction was prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
