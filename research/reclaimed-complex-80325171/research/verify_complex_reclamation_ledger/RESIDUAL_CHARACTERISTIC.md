# Exact alternating-residual test for the reviewed binary frame families

Let F be a nondegenerate subspace of binary Euclidean space and let c(F)=P_F 1,
where P_F is its orthogonal projector and 1 is the all-ones vector. For every
x in F, x dot x=x dot1=x dot c(F). Nondegeneracy therefore shows that F is
alternating precisely when c(F)=0.

If U subset V and both are nondegenerate, put R=V intersect U-perp. Then
V=U orthogonal-direct-sum R, so c(R)=c(V)+c(U). Hence a positive-rank residual
R is alternating if and only if c(V)=c(U). Equal frames have rank-zero residual
and require no recursive child; they must not be reported as positive-rank
alternating calls.

The frame characteristic can be obtained without dense elimination:

- Empty frame:0.
- Coordinate span on cover M: the bit mask M.
- Common-pair-star span with core C, cover M and rank r:
  (M XOR C) XOR (C if r is odd, otherwise0). Its generating triple vectors are
  orthonormal and each has odd weight, so the characteristic is their XOR.
  A singleton triple has C=M and r=1, yielding the same formula.
- B-center hyperplane with normal 1+e_i (even ambient h): e_i.
- Target triple hyperplane t-perp, with t dot t=1: 1+t.

Every rank and containment still needs separate verification. Equal
characteristics without nondegeneracy/nesting do not prove a valid residual.
Tensor lifting by a norm-one odd triple line preserves the Gram form and this
alternating/nonalternating distinction.

The original bounded `review_checks.py` independently computes residual bases
for all2,663 nested pairs among254 h6 frames, verifies nondegeneracy, and compares
this criterion against every residual basis vector's parity. All agree;86
positive-rank residuals in that exhaustive fixture are alternating. This is a
transcription control for the formula, not a replacement for the general proof
above or a claim about the pending h24 trace.
