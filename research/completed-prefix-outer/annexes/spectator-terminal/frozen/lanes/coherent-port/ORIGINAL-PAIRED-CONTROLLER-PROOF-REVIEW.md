# Independent proof review of the original paired controller

Status: PASS in the scope below.

This review reads the final proof in
`../encoded-controller/ORIGINAL-PAIRED-CONTROLLER.md`, with SHA-256
`412f71ddff2294e1013033220d9eab809d37c14f1cbced36727e175c72f0d0a1`.
The related producer receipt has SHA-256
`75b24a3be7ba9bb32501196bc660b5438ea25436b94da83ff55b136c89212496`.
The producer checker has SHA-256
`bbf3381992ee67b9650ef15b26d5d84f3f00d7bdca0d11977399ed85f27a338f`.

This is a separate proof review. It does not repeat the producer's
17-block free-algebra run or its route reconstruction. The local native
contract is the contract checked in
`ORIGINAL-PAIRED-GAP-NATIVE-REVIEW.md`.

## Ordered algebra

Let Q act equally on the paired data replicas. Let A be the specified
port-dependent monomial map, and let T=QA. Then T squared is I and
A commutes with Q. For the defined H_s and G_s, the relations
T H_s=H_s and G_s T=-G_s hold without moving A through R, K, or a
mode gauge. In particular,

```text
A^-1=TQ,
Q H_s=A^-1 H_s,
G_s Q^-1=-G_s A.
```

These are data-side identities. They do not define an action of A on
the centre modes. The proof retains this distinction.

Write L for the response map and Tq for the query map. The relation
Tq L=0 gives the exact inverse of the stated joint map. Direct
substitution gives

```text
D1=D'-LPV=D-L(I-P)U,
-V-Tq D1=U,
D1+L(I-P)U=D.
```

This uses only the stated ordered products. It does not interchange a
query and a response coefficient.

At the physical boundary, let B and C have the stated data-bank
monomial blocks. Then WL=BL and Tq W^-1=Tq C. Substitution into the
logical map gives the displayed physical matrix. Its two rectangular
factors have zero product because

```text
(Tq C)(BL)=Tq(CB)L=0.
```

Here CB is a scalar sign on each data bank. Such signs can change the
bank coefficients but leave every G_s H_t product zero. Thus the same
inverse applies to the physical matrix. This statement does not make
the remaining H and G accesses native-free.

## Mode-only reuse limit

The proof uses the producer's exact source schedule and the fact that
the 112 stage-one port routes are distinct involutions. Under those
stated facts, its witness is exact. With R_s=R D_s,

```text
h=(56I-R_1^*R_1)R_0^*e_k delta_identity,
R_1h=0,
[R_0h]_identity=(3136-224)e_k=2912e_k.
```

The identity coefficient 224I follows from the distinct-route condition:
only equal port indices remain, and each root column has squared norm
4. A constant native payload has Q=I. The paired input (h,-h) therefore
has zero stage-one projected query and a nonzero stage-zero projected
query. The stated schedule makes all its later ordinary query sources
zero. Earlier response errors cannot change this, since every later
query annihilates every earlier response image.

Any invertible map on the full mode state preserves a nonzero mode
signal. A local call with a zero query also preserves that signal up to
its invertible mode sign and gauge. Thus mode-only operations cannot
restore the initial zero mode state for this input. The proof correctly
excludes a new data read, a changed data word, and a mixed data/mode
terminal from this result.

## Review boundary

The ordered inverse, the data-side boundary identities, and the
conditional 2912 witness argument pass this review. The exact source
rows and route-distinctness checks remain producer dependencies. This
review does not claim an independent free-engine or route replay,
owner admission, one-use mode-history admission, a native implementation
of the endpoint decoder, or a complete supplier cost.

The final proof now describes its 100352 expanded scalar terms with
their line and source-map factors. It does not describe these terms as
an implementation by scalar monomial operations alone.
