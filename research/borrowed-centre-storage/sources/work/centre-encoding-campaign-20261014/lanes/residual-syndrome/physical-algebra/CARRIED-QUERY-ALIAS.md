# A carried query with an exact selected-port alias

The input full-query logger admits a persistent borrowed cache on the
four actual backward-to-forward windows. The cache can retain an
arbitrary independent input. It follows the native frame of one
selected Y port and is cleared of its query term at the next forward
entrance. This uses eight cache fields per replica, reused in all four
windows. Their complete native history has eight rank-eight children
and one rank-nine child per field. It maps each independent input h to
F73 h.

This is a native transport and cache-restoration theorem. It does not
restore the source code left by the logger. It does not provide a clean
query: while a query is present, the cache contains h plus that query.
The theorem does not admit a complete supplier or change kappa.

The [checker](verify_carried_query_alias.py),
[literal payload](CARRIED-QUERY-ALIAS-PROGRAMS.json.gz), and
[receipt](CARRIED-QUERY-ALIAS.json) pin the actual local word, logger,
source matrix, selected plan, global schedule, and phase recipes.
The payload has SHA256
`677199e44967cb598bdd6b92f23400cf88ac40020e195f07a0c6e5244a3ace0d`
after decompression.

## Local content contract

Use the actual matrix R and the log ports

```text
T = [21, 37, 47, 76, 81, 87, 92, 110].
```

Put Q_T=R_T^-1 R. This symbol denotes the normalized centre read, not
the diagonal native line operator. The actual minor has
R_T R_T^T=4I, so the inverse is dyadic. The all-eight-C-preserving
input logger from the circuit-interface lane has the exact map

\[
 (x,y,h,c)\longmapsto(x-Jy,Gy,h,c),
 \qquad \pi_TG=Q_T.
\tag{1}
\]

Here h comprises the 480 arbitrary helper values and c comprises all
eight arbitrary C values. The local C endpoints are I to I. Every Y
input also has local frame I. Thus the prefix

\[
 c\leftarrow c+Q_Ty
\tag{2}
\]

is a legal same-frame scalar word on arbitrary inputs. It uses no
CLEAR, COPY, or clean-state assumption. After (1), the selected source
output and the cache have contents

\[
 y'_{T_k}=(Q_Ty)_k,
 \qquad c'_k=c_k+(Q_Ty)_k.
\tag{3}
\]

The existing optional cache in the input-source payload adds R y.
Equation (2) is a different literal prefix. The checker emits and
replays it separately. It does not infer selected-port access from an
unnormalized centre vector after the port routes have separated.

## The actual native frames

Let L be the original nine-coordinate space. Let E_s be the fresh
eight-coordinate block of stage s, for 1<=s<=8. Set

\[
 U_s=L\oplus E_1\oplus\cdots\oplus E_s,
 \qquad V_s=E_1\oplus\cdots\oplus E_s.
\]

For a selected port label p, the actual orthogonal chart rho_s(p)
fixes p and swaps its fixed orthonormal complement basis B_p in L
with the unit basis of E_s. The stage-zero chart is I. A local
invocation at cover class d uses the data family at d rho_s(p), with
the original orthogonal address gather. Cover reindexing alone is not
the complete gather operation.

Allocate an independent owner field for each C_k. Give that field
the same port route, address gather, and entry and exit translations
as Y_{T_k}. The local C register is an alias of this owner field for
the duration of the invocation. It is not a new zero workspace field.
The eight owners are distinct from all data and helper owners.

After the Y entry adapter at stage s, its native frame is F_{V_s};
the local source factor is I. The cache has the same frame by the
history below. The complete borrowed local word leaves its local
I factor unchanged. After that word, apply

\[
 H_p=F_L C_p^{-1}
\tag{4}
\]

to C at stages zero through seven, and then apply the actual Y exit
translation. Thus C receives exactly the native output map of Y,
although the local word did not give it that map.

Equation (4) is an exact rank-eight child with a literal translation.
If (p,B_p) is the selected orthonormal basis and

\[
 \eta_p=\sum_{b\in\{p\}\cup B_p}
         \frac{\operatorname{wt}(b)-1}{2}b,
\]

where the sum is binary, then

\[
 F_L C_p^{-1}=X_{\eta_p}\prod_{b\in B_p}C_b.
\tag{5}
\]

More generally, eta_p is the unique translation whose Fourier sign
is the difference between the two displayed orthonormal-basis phase
polynomials. The payload records that translation directly from the
exact phase polynomials. The child uses the orthogonal chart whose
columns are B_p followed by p. Equation (5) holds with scalar phase
one; the checker compares all 512 Fourier eigenvalues for each of the
eight selected labels.

For every stage s<8, this gives the owner-frame output
F_{U_s} C_p^-1, with all global phase terms included. At stage eight,
apply F_L instead of (4). This folds the final missing positive C_p
into the last child. The last child has rank nine. Its output is
F_{U_8}=F73 in the owner cover chart.

The checker derives every cache entrance and exit from the actual
DATA-PHASES entry_Y and exit_Y translations. It checks the full
73-variable quadratic phase, not only its binary symplectic map.
There are 144 such identities. The first eight stages use rank eight;
the last uses rank nine. Thus the complete native rank per owner is

\[
 8\cdot8+9=73.
\tag{6}
\]

For a general orthogonal cover matrix g, conjugation can change the
full F73 by a translation. The same final correction used by the
selected supplier is required on every new owner:
delta_i=(weight(row_i(g))-1)/2 modulo two. This correction is not
omitted from the contract. It has native rank zero but still has
address and scalar-control cost.

## Four exact alias windows

The pinned global schedule gives the following windows.

| Capture | Erase | Active pair | Intervening effect on active Y |
| --- | --- | --- | --- |
| B1 | F2 | 0 | None |
| B3 | F4 | 1 | None |
| B5 | F6 | 2 | None |
| B7 | F8 | 3 | None |

For each of the first three windows, the intervening bridge has the
active pair as its destination. It updates that pair's X and the
next pair's Y. It leaves the active Y unchanged. The intervening idle
advance acts on the next pair. There is no intervening bridge in the
last window.

Capture (2) before the complete B prelude. Run the logger (1), the
cache child (4), and the actual exit adapter. By (3), the query part
of C and the selected Y output now have identical physical native
maps and contents. Advance both to the next local entrance with
their same port route and address gather. At that entrance, before
the complete F prelude, perform

\[
 C_k\leftarrow C_k-Y_{T_k}.
\tag{7}
\]

This removes the query term and retains exactly the transported
independent cache input. The following borrowed forward word
preserves it. The same eight owners can therefore be reused at B3,
B5, and B7.

The cover equation is explicit. If the later invocation is d, the
earlier invocation that used the same physical selected field is

\[
 d_{\rm old}=d\,\rho_{s+1}(p)\rho_s(p).
\tag{8}
\]

The two owner classes in (8) are equal after the last rho factor is
applied. Their address gathers and phase adapters are also equal to
the selected Y history, by the frame identities above. No constant
cover input, cover-invariant query, or equal-port-route assumption is
used. The eight carried rows are port-routed query values. They are
not a common-cover centre vector after the transition.

The restoration is valid even when the current source data already
contains earlier source encodings. Equation (3) is an identity on
all source inputs. It does not require an untouched original y.

## Scope of the carried information

If (2) instead captures the old selected baseline y_T, equation (7)
leaves

\[
 c-R_T^{-1}(R-L_T)y,\qquad L_T=R_T\pi_T,
\tag{9}
\]

with the same port pullback. This is generally nonzero. The receipt
contains an exact single-input witness. Carrying the old selected
baseline is therefore not a substitute for the query in this proof.

The theorem also does not convert a dirty query into a clean one.
An operation that uses C while the query is present must account for
the independent old c. Any such use must leave the stated alias
available for (7), or provide a separate restoration proof.

The later joint source-query exchanges under investigation have a
different contract. If they move old c into the source data, the
native history here still transports their C output. Their full
source-held baseline restoration does not follow from (7).

## Cost and verification

The normalized prefix has eight unit ADDs and 416 half-coefficient
ADDs: 424 ADD macros and 4,224 real primitives. Equation (7) has eight
unit ADDs and costs 64 real primitives. The four windows add 17,152
real primitives per replica, before address control, precision, and
native child execution. The captured complete backward word has
scalar bound 232,390 and the inherited native mass 5,538. The new
cache-native history is additional to that local mass.

Eight independent owner fields per replica receive the 73-rank
history (6). Its paid rank is 584 per replica, equal to their 584
productive rank if those independent owners are admitted. A dependent
query value is not a productive input. The selected private C slots
are not already eight arbitrary owner rows. Owner allocation and the
full recursive layout require a separate admission check.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/verify_carried_query_alias.py
```

Expected first line:

```text
PASS_CARRIED_QUERY_ALIAS
```

The checker replays the captured backward word on all 712 input
columns, including every arbitrary helper and C value. It checks
the following complete forward word under the exact alias relation,
all local scalar-frame accesses, all four actual schedule windows,
4,096 local hole eigenvalues, and 144 full native frame identities.
The original local child kernels are pinned dependencies; this
checker does not repeat their independent kernel replay.

The input source logger, dyadic section, and arbitrary-C local word
come from the coordinating, history-encoding, and circuit-interface
lanes. The source routes and phase corrections come from the reviewed
selected supplier. The residual-syndrome lane supplied the persistent
selected-port alias contract. OpenAI Codex supplied research and
verification assistance under the user's direction.
