# Layer phases in the spectator terminal product

This addendum keeps the bytes of SPECTATOR-TERMINAL-PRODUCT.md fixed.
Its proof hash is
588446b16cfcda173ce78092d6ef53ecec41ba5de54f7fae5191e836c326fb54.

Suppose the complete endpoint for layer j is E_j=T_j in that note.
Let S_j be a monomial operator on the active coordinates of layer j,
tensored with identity on z and on every other layer. It must not have
a coefficient that depends on z. Then S_k commutes with T_j for k!=j.
With S_all=prod_j S_j, the exact identity is

```text
(S_m T_m S_m^-1) ... (S_1 T_1 S_1^-1)
 = S_all (T_m ... T_1) S_all^-1.
```

Thus the inverse is S_all M^-1 Q_all^-1 S_all^-1. It still contains
only one native C_D call after the stated gather. All the S factors
can be included in the monomial wrappers. They still have an execution
cost. This claim uses disjoint support, not only the fact that a map
fixes the address bit z: a z-dependent diagonal phase need not commute
with the z flip in T_j.

The actual conversion in the retained layer proof has
S_j=i^(sum of the current selected bits). It has the required support.
The source identity is H0=b S C S, with b=(1-i)/2, in
`upstream/build/sections/05-layers.tex` at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. If a native routine returns
E_j C_j, the converted routine returns

```text
(S_j E_j S_j^-1) H0_j.
```

This places the code before the current outer twiddle. It does not
place the code after a complete Fourier round. The current DIF twiddle
depends on the branch that H0_j just produced and on unprocessed bits.
It is not supported only on layer j and cannot be included in the
commuting S_j factors above. The established current-twiddle limitation
therefore still applies.

To use the one-C_D terminal, a construction must prove a complete-round
portwise endpoint after the twiddle, implement an exact typed encoded
twiddle, or return the raw H0_j operation. The affine spectator
realization and the terminal product identity do not prove any of
these three statements. No all-size improvement is claimed here.
