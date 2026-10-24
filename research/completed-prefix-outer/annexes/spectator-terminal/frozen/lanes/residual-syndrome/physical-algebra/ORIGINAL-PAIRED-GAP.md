# A paired involution for the original complex phase

The original complex line phases admit a two-replica involution. Its
extra maps are translations and cross-replica ADDs. It does not require
the Walsh retarget. The emitted local word retains both original cores
and restores all 944 ordinary helper inputs. It has 16 arbitrary mode
inputs, whose new values are part of the stated output contract.

This result removes a local phase-normalization requirement from the
complementary-gap controller. It does not give free access to the final
odd-phase queries or injections. The paired owner schedule, mode jobs,
complete decoder, and supplier invoice are separate requirements. No
complete kappa improvement is claimed.

## Exact phase and operator order

Let `Q=diag_p(C_p^tensor(lambda))`. On one port, the original native line
has `C_p^2=X_p` exactly. Thus `L=Q^2` is a list of translations, and
`L^2=I`. Pair two replicas with the same stage and address chart. Put

    A = [[0,I],[L,0]],
    T = Q A = [[0,Q],[Q^-1,0]].                       (1)

Here Q denotes the same diagonal port operator on both replicas. A acts
on port arrays, not on the eight centre indices. It is a monomial map.
Since A commutes with Q and `A^2=L`, we have `T^2=I`. Also `L A=A^-1`.
None of these statements moves A through R or K.

Use `K=R^T/4`, `RR^T=56I`, with R and K extended by the replica identity.
The pinned raw core has these local physical frames:

| Role | Input | Output |
| --- | --- | --- |
| X_p | C_p | F |
| Y_p | I | F C_p^-1 |
| mode u_k | I | F |

The common F commutes with each Q_p and each translation L_p. After its
common output F is removed, the exact raw content maps are

    F_core: y'=y+(I-KR)x-Ku,   u'=-u-2Rx,    x'=x;
    B_core: x'=x-(I+KR)y-8Ku,  u'=-u-Ry/4,   y'=y.    (2)

The signs in the backward core are required.

## The forward physical word

Start with arbitrary mode content z. Apply the following physical
operations before both cores:

    u -= R A X_physical.

Because the input X frame is Q, the core mode input is `u=z-RTx`.
After both cores, first apply `u += R X_physical`. The new logical mode
and target then satisfy

    v=-z-R(I-T)x,
    y_1=y+x+Kv.

Next apply `Y_physical += A K U_physical`. The target frame converts this
term to `Q A K v=T K v`. Hence the complete map is

    x'=x,
    v=-z-Gx,
    y'=y+x+Hv,
    G=R(I-T),              H=(I+T)K.                 (3)

The emitter implements the first graph as `u0-=R X1` and
`u1-=R L X0`. It implements the last graph as `Y0+=K v1` and
`Y1+=L K v0`. The translated source or target is translated once before
its ADDs and once after them. This restores its physical address view.
There is no common action of A on the eight mode fields.

## The backward physical word

Before both backward cores, apply, in this order,

    X_physical -= 8 L A K z,
    u = z-RY_physical/8.

The first line changes logical x by `-8 T K z`. Substitution in (2)
gives `x'=x-y-8(I+T)Kz` and `u'=-z-Ry/8`. After both cores, apply

    u += R L A Y_physical/8.

Since `L A Q^-1=T`, this adds `RTy/8`. Therefore

    x'=x-y-8Hz,
    y'=y,
    v=-z-Gy/8.                                      (4)

The emitter uses `X0-=8L K z1`, `X1-=8K z0`, and the two common-frame
mode preloads. Its final graph is `u0+=R L Y1/8`, `u1+=R Y0/8`.
These are pointwise physical ADDs and literal translations.

## Changing charts and one-shot mode gauges

At cover class g, the port phase is `C_(g p)^tensor(lambda)`. Each actual
stage route fixes p. Orthogonal address covariance therefore implies
that every D_s commutes with Q, L, A, and T. The pair must use the same
cover class and stage view in this statement.

Let N_s be the one-shot mode gauge from
`history-encoding/ONE-SHOT-MODE-PROOF.md`. Its input action and its full-F
conjugate are monomial. Applying the phase-gap graphs inside that active
core, before the mode output adapter, gives the routed maps

    G_s=N_s^-1 R D_s(I-T),
    H_t=(I+T)D_t^-1 K N_t.

Their cross-products vanish for every s,t:

    G_s H_t
      =N_s^-1 R D_s (I-T)(I+T) D_t^-1 K N_t=0.       (5)

This is a typed composition consequence of the local endpoint table and
the reviewed one-shot adapters. It does not replace a global native
replay of those adapters and graphs. It makes no equal-chart assumption
and does not identify the distinct centre row spaces.

The frozen `encoded-controller/NILPOTENT-CONTROLLER.md` now applies to
(3)--(5) at the operator level. Its output decoder restores all arbitrary
data and mode inputs when its H and G boundary operations are available.
The two-replica change has not made those boundary operations monomial.

## Local invoice and checks

The two cores are the unchanged payload with decompressed SHA256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
The generated paired payload has decompressed SHA256
`42aeb0902d8b2330f9050718c6d949993111a9fd898acad599ec867bb63a2b20`.

| Item per pair | Forward | Backward |
| --- | ---: | ---: |
| Extra physical ADDs | 2,688 | 2,688 |
| Extra translation maps | 448 | 448 |
| Extra real scalar primitives | 25,088 | 34,048 |
| Complete explicit scalar primitives | 433,924 | 442,884 |
| Retained native events | 10,112 | 10,112 |
| Paid native rank | 11,044 | 11,044 |
| Extra native children | 0 | 0 |

The scalar invoice excludes address-map implementation, owner access,
mode preparation and completion, old-owner backfills, and the global
decoder. It is not a complete real-primitive supplier invoice.

The producer checks both raw core maps on all 704 input columns, then
checks both paired maps on all 1,408 arbitrary input columns. It checks
all 944 ordinary helper outputs. Its free-line algebra uses only
`C_p^4=I`; it does not commute a port line through R or K. Omitting the
input graphs or the translations fails the map check. The native identity
`C_p^2=X_p` gives the all-tensor-depth interpretation.

Run from the workspace:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/emit_original_paired_gap.py

Expected first output:

    PASS_EXACT_ORIGINAL_COMPLEX_PAIRED_PHASE_GAP

Both pregraphs must precede both cores, and both postgraphs must follow
both cores. A serial execution of the cores is valid only if its borrowed
owners do not change the other replica's protected data or modes. The
selected asynchronous schedule is not admitted by this local check.

## Credit and scope

The history-encoding lane supplied the raw full-mode core and the
original physical phase-gap graphs. The coherent-port lane supplied the
complementary-gap and two-replica Walsh argument. The encoded-controller
lane supplied the all-stage nilpotent decoder. The coordinating agent
supplied (1), which uses the original complex translations. This lane
emitted the ordered physical graphs and checked their complete local
maps. Independent review is recorded separately.

This work used substantial OpenAI Codex assistance under the user's
direction. It does not change the selected frontier.
