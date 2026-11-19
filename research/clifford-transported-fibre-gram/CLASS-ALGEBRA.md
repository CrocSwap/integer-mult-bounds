# Recognizing relative classes and compiling the central kernel

Use columns in the four-qubit binary Pauli convention. Bits 0 through 3 pair with bits 4 through 7. For each symplectic map $S$ and each of the 256 vectors $v$, find the first monic linear dependence of the sequence $v,Sv,\ldots$ by binary elimination. Record its polynomial and the bits $\langle v,S^jv\rangle$ through that degree, including the final bit. A symplectic conjugation permutes the vectors and preserves both quantities. The resulting histogram is therefore constant on each conjugacy class.

The included native representatives cover all 81 ordinary classes of $G=\mathrm{Sp}(8,2)$, of order 47,377,612,800. Their histograms are pairwise distinct. This finite check proves that each accepted symplectic input has an unambiguous class label. The two ordinary columns that coincide across every rationalized character are combined for the central calculation. The other 79 columns stand alone. Thus relative maps supplied by the caller can be located in the rational table by evaluating a histogram, with no group enumeration.

Let $n_j$ be the rational-class sizes, $r_B$ a sum of the ordinary characters in Galois orbit $B$, and $d_B$ the common constituent degree. Orthogonality gives the orbit length $m_B=\sum_j n_jr_B(j)^2/|G|$ and $d_B=r_B(1)/m_B$. For per-element coefficients constant on rational classes, the central character transform and its inverse are

$$
 T_{Bj}=n_jr_B(j)/r_B(1),\qquad (T^{-1})_{jB}=d_Br_B(j)/|G|.
$$

All packet sums are real on these classes. Put $F_j=(-64)^{\dim\operatorname{Fix}(S_j)}$. The integer class matrix is $M=T^{-1}\operatorname{diag}(TF)T$. Its column at the identity is $F$. The width-13 Gram operator uses $M/16^{12}$. Apply powers or scalar polynomials to class coefficients in this 80-dimensional space. Use the resulting coefficient at the relative class for each requested source/target pair.

`native_classes.g` obtains ordinary representatives and character values directly from the natural group acting faithfully on the 255 nonzero vectors, using GAP 4.14 (The GAP Group). Reversing the order of the high four coordinates transports the native antidiagonal pairing to the Pauli convention. The class ordering is derived from the histograms. An optional rebuild compares signatures, sizes, fixed dimensions and every packet entry, so arbitrary choices of representatives may vary. From this directory run

```sh
gap -A -q -b -T native_classes.g > /tmp/sp8-classes.json
python3.12 -IB build_classes.py /tmp/sp8-classes.json
python3.12 -IB check_classes.py
```

The registered Python replay also checks 405 changes of symplectic basis, packet orthogonality, the adjoint identity $n_iM_{ij}=n_jM_{ji}$, all character eigenvectors, the identity coefficient of the squared kernel and the two width-13 spectral endpoints.
