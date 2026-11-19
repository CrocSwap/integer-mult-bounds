# The sharp chart-3 ingress threshold at chart 278

## Communication model

Use the pinned #7786 word on 1,289 independent rational inputs. Remove its two-slot route $278\to288\to127$. The proposed collapse sends from 278 directly to 127. Chart 278 originally receives six scalars from chart 3, two from 11 and two from 58. It has no original public inputs or terminals. It emits nine surviving scalars besides its old slot 95914. Permit simultaneous rational-linear recoding of every one of these ten incoming and nine outgoing payloads on its original route. The 387 terminals outside 127 must retain their original values on all inputs. The 901 surviving deposits at 127 may change, and 127 may recode its outputs using its entire stock. All operations beyond these specified edits retain their original rules. The source word has no egress from 127.

To count the core ingress capacity, allow additional rational-linear sends from the three existing ingress donors to 278, and additional direct sends from 278 to 127. The nine surviving egress routes remain charged at their original grades. Each core slot carries one rational scalar obtained by a fixed linear operation. The following result allows arbitrary many additional sends from charts 11 and 58 and from 278 to 127. An instance with seven core slots actually needs only the two original sends from each edge donor and a single direct send. [Original word and attribution](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation) · [Six paired edits considered in #7795](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/STOCK.md) · [Previous cooperative frozen-cut result](https://github.com/apoursh/integer-mult-bounds/blob/c44a0313cb1aee8b94803691529d1c109779f2f2/research/p104-receiver-relay/PROOF.md)

## Six exterior demands saturate all six core channels

Work in the dual space of the public input coordinates. Write $E$ for the span of the two edge senders' frozen stock. They have two local public scalars and four original incoming scalars each. These incoming values have all arrived before the first surviving egress from 278. The core donor 3 has only its initial public coordinates. Thus the edge stocks used by any legal edit lie in $E$, even if we grant all twelve atoms at the start.

Write $h_1,\ldots,h_6$ for the six original core messages in chronological order, at slots 94953, 95493, 95884, 95982, 96109, 100334. Expanding their exact public forms and the twelve edge atoms gives rank 18. Hence modulo $E$ all six core forms are independent. Let $H=\operatorname{span}(h_1,\ldots,h_6)$ and write $H'$ for the span of the new core messages in a proposed repair.

Treat the nine surviving egress values as boundary variables, in their original slots. With those variables prescribed, the rest of the exterior is a fixed linear circuit. The ten ingress changes can reach an exterior observation only through these nine egresses. The removed slot 95914 had only one reader, 88, and the receiver has no egress. If $P$ is the matrix of exterior responses to the nine boundary variables and $y,y'$ are the nine old and new forms, equality of the exterior implies $P y'=P y$. The common contribution from public inputs outside the boundary cancels identically. The exact matrix on the 387 exterior terminals has rank eight. Its sole invisible direction increases slot 95887 and decreases slot 100336 by the same amount. In particular, preserving the exterior allows the individual egress values and some retained receiver deposits to change.

Now consider just six rows of $P y$, listed below in the core basis **after quotienting by $E$**. The native nine boundary forms are computed at chart 278, so this quotient is well defined. All omitted contributions are edge-sender forms. [Exact row reconstruction and pulse check](check_exterior.py)

| Exterior terminal | $h_1$ | $h_2$ | $h_3$ | $h_4$ | $h_5$ | $h_6$ |
|---|---:|---:|---:|---:|---:|---:|
| 154880 | 0 | −1 | 0 | 0 | 0 | 0 |
| 154881 | 0 | −1 | 1 | 0 | 1 | 0 |
| 154887 | −1/4 | 0 | 0 | 0 | 0 | 0 |
| 154895 | 0 | 0 | −1 | 0 | −1 | −1 |
| 154950 | 0 | −1 | −1/4 | 0 | 0 | 0 |
| 154959 | −1/4 | 1 | 0 | 1 | 0 | 0 |

This matrix is nonsingular. Every new egress form belongs to $E+H'$, so the six equalities force $H\subset E+H'$. If there are at most six core sends, the image of $H'$ modulo $E$ has dimension at most six. It contains all of the six-dimensional image of $H$, hence it equals that image. It follows that **all new chart-278 stock and emissions lie in the fixed 18-dimensional space $E+H$**, regardless of the legal local re-encodings. This finite-capacity conclusion is the part that would fail with a seventh core slot.

## A separating public input

Set all unlisted coordinates to zero and use the following rational input.

| Coordinate | 663 | 770 | 780 | 825 | 1055 | 1225 | 1238 | 1239 | 1288 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Value | −2 | −2 | −1 | −1 | 218/1395 | 17/2 | 1888/333 | 64/27 | −1/845660160 |

The input annihilates the twelve edge atoms and six original core forms, all nine old egresses, and all 901 old surviving receiver arrivals. The original terminal 155442 equals $x_{674}-x_{780}=1$. Under any proposed repair with at most six core sends every new scalar leaving 278 vanishes on the same input. Each old egress also vanished, so the unmodified exterior still supplies its *original* values at all 901 surviving deposits on this input, even though these deposits were allowed to change as operators. Every new direct send from 278 vanishes as well. Receiver 127 has no primary coordinates and sees the same data here as on zero. It cannot recover the required value on both inputs, even with a deterministic nonlinear readout. A second checker independently reconstructs these nine values by backward substitution through the native word. On the displayed support the annihilating equations have rank eight, so the input is uniquely determined there by the normalization $y_1=1$. [Full forward evaluation](check_input.py) · [Independent reverse reconstruction](check_separator.py)

## A matching seven-slot construction

Keep all ten original ingresses to 278 and all nine surviving egresses. Write $d$ for the original deposit 94217. Its form at chart 11 is $d=x_{674}-v_{90590}-v_{90592}$, where $v_{90590}$ and $v_{90592}$ were originally transmitted from chart 3 to 11. Both are rational forms of chart 3's public coordinates. At the old time of 95914 transmit
$$
s=x_{780}-v_{90590}-v_{90592}
$$
from 3 to 278. At the old time of 88, chart 278 sends the single direct scalar $z=d-s=x_{674}-x_{780}$ to 127.

Return $z$ for old terminal $y_1=155442$. Both affected native terminals $y_1,y_2=155490$ used 88 with coefficient one. Their original difference $y_2-y_1$ therefore uses only retained receiving terms. For the second terminal return that local difference plus $z$. The verifier builds the literal chronological word, checks all dependencies and owners, expands both changed terminals in all 1,289 independent coordinates, and checks that the other 1,287 terminals have no changed reader. It also detects a sign error in the direct packet. This construction is feasible even with all 901 old surviving deposits preserved exactly. [Constructive operator replay](check_repair.py)

These checks prove the exact capacity threshold of seven core ingresses. If the original ten incoming and nine surviving outgoing ports stay funded, a required direct replacement costs at least the grade-two extra ingress and the grade-seven direct send. The construction attains this paid-port bill. At the enrolled $p(r)=r^{1-0.00387981257853}$, relative to the two removed transfers of grades two and five, the excess over 48 rational calls obeys
$$
94.966797106425725799489376 < 48[p(7)-p(5)] < 94.966797106425725799489377.
$$
The new ingress, written directly on native public coordinates, has 299 nonzero terms. Its largest numerator and denominator have bit lengths 30 and 7. This accounts for paid scalar ports in the stated rational model. A full caller would additionally need a legal local arithmetic schedule, coefficient and conversion budgets, and all other accounting required by the construction.

The result leaves other donor routes, edits beyond these nineteen local rules, and retirement of funded ports open. Prepared by apoursh with substantial OpenAI Codex assistance.
