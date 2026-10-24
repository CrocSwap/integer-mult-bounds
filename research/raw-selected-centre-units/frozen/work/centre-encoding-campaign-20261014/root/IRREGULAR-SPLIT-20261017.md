# An irregular 38-port split with two dyadic units

The actual supplier has a 38-port selected set for which both the ordinary
block and the normalized original-X response are dyadic units. A union of
complete orthogonal eight-port minors first gives these two properties at
40 ports. Thus complete minors impose a restriction that the actual matrix
does not require.

This result gives an exact scalar code for the raw selected exchange
family. It does not give a complete supplier or a cheaper final decoder.
The budget-geometry worker found the set. The coordinating worker checked
it separately against the pinned supplier matrix and checked both full
inverse identities. No native emission for this irregular set is claimed.

## General test

Work over the Gaussian dyadic ring. Let the actual matrices satisfy
`R K=14 I_8`, with `K=R^T/4`. Choose any selected set S and let U be its
complement. Define

    D=R_S K_S,    T=D-13I,    H=I_U-K_U R_U.

The determinant identity for rectangular products gives `det(H)=det(T)`.
Thus H is a unit over this ring exactly when T is a unit. In that case,

    H^-1=I_U+K_U T^-1 R_U.                              (1)

This follows by multiplication, since `R_U K_U=14I-D=I-T`.

For the raw selected backward word, put `z=(Q_S a,u)` and let
`E=diag(-I_S,I_U)`. Apply H inverse to completed ordinary X, then apply
the completed-X upper correction `X_S += K_S R_U X_U`. The full result is

    X = diag(Q_S^-1,-I_U) (b,v) + A z,
    Y = (Q_S a,v),
    A = E+K T^-1 R.                                    (2)

The raw exchange proof keeps each Q factor in this order. It does not
commute Q through a row of R or K. Both added scalar factors act on the
completed X bank.

Let `W=I-D`. The second determinant identity is

    det(A)=det(E) det(W)/det(T).

Consequently, when H is a unit, the original-X response A is a unit
exactly when W is a unit. Its inverse is

    A^-1=E-E K W^-1 R E.                               (3)

For verification, use `R E K=14I-2D`, so `T+R E K=W`. The ordered
Woodbury identity then gives (3). This second condition is separate
from invertibility of the complete two-bank raw word. That complete
word remains a unit even when A has a kernel, since Y retains selected
original data.

These tests are statements about the dyadic ring. Fixed odd division on
an exact common grid can admit additional rational units. A failed
dyadic test is not an obstruction to the required computation.

## Actual witness

Use zero-based port indices

    1,3,4,17,18,19,20,23,24,26,27,29,35,36,38,39,40,42,45,
    60,63,66,69,74,75,77,78,84,86,88,97,99,104,105,107,108,109,111.

There are 38 selected and 74 ordinary ports. The matrix R is read from
`../lanes/new-core-transfer-20261017/INTERFACE.json`, SHA256
`c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746`.
This is the interface extracted and independently checked for both new
provider words.

Put `G=R_S R_S^T` and let

    L=I+(E_02+E_03+E_14+E_15)/4,

where E_ij is the elementary matrix with its nonzero entry at row i and
column j. Direct exact calculation gives

    52I-G=32 L L^T,
    det(52I-G)=2^40,
    det(4I-G)=2^28.

Since `D=G/4`, these identities give

    det(T)=2^24,    det(W)=2^12,    det(A)=2^-12.

Both T inverse and W inverse have only dyadic entries. The checker
constructs them by exact rational elimination, then verifies (1) and
(3) in both orders on all 112 coordinate vectors. It also checks the
full Gram identity and the stated unipotent factor directly from R.

The witness is constructive. It refutes a 40-port lower bound for this
unit criterion. It does not establish the smallest possible selected
set, a lower bound on native children, or a useful complete decoder.

## Reproduction and limits

Run from the workspace root:

    python3 -I -B work/centre-encoding-campaign-20261014/root/check_irregular_split_20261017.py

Expected output:

    PASS_ROOT_IRREGULAR_38_PORT_UNIT

The receipt is `IRREGULAR-SPLIT-20261017.json`, SHA256
`0a8d22fa0b523c261243e9b19cfd51926c9b515a9e6f9a962d1e3b5170105a8f`.
The check uses the standard library and does not import the search
worker's code. It rejects an incorrect centre constant and omitted
selected signs.

An implementation can form eight current-chart queries in the eight
existing owned private fields, apply the finite centre inverse, scatter
the result, and clear those fields. This describes a scalar construction
at a common-frame boundary. Its exact emitted gates, scalar invoice,
private lifetimes, and full native word still need separate checks.
Actual inter-call views, owner histories, selected phase corrections,
controller composition, and recursive cost remain open.

Research and verification used OpenAI Codex under the user's direction.
The user has not authorized publication. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
