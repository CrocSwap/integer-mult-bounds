# Changes between the fourteen subdivisions and the final productive split

Starting from the fourteen-subdivision word, three entire banks move from charts 1061, 1063 and 1040 to charts 796, 798 and 585 respectively. A fourth bank moves the three ports 94072, 20000 and 99806 from chart 712 to chart 867. The last move collapses paid leg 99806. New leg 70 carries the one shared subtotal available when slot 20000 reads. The four edits save 0.6995634410096856 signed units across 48 calls at the fixed round target. The bank journal gives the donor and reader clocks, chart frames, signed ranks and the common subtotal. Its output is the input to the sparse projection below. [Bank journal](BANKS.json) · [Joint literal replay](overlay.py)

## Sparse source projection after 14 subdivisions and four chart edits

The exact parent is `d8f7a310dee37764336019dc3ff099be2ec0d2cf39f6bc318b0fac502a705495`. The layout hash is `60ced30a6d7b69c580c8822756f38c11c0d2a904e3ed1235fbbfd176419e36d3`. Applying the source projection after the subdivisions and chart edits gives `6eba6bb65015df98cf103ce6d12fdd982ba4dcd24a69000bcc58e05477b17c19`. Rational replay compares all 1,278 output rows and all 1,278 adjoint rows on arbitrary independent inputs. [Complete literal edits](OVERLAY.json.gz) · [Intermediate operator and price](../evidence/overlay-operator.json) · [Final operator and price](INDEPENDENT.json)

Use the transposed scalar graph. Let $V_j$ denote the original value at slot $j$, and let $V_{-1-r}$ denote independent public input $r$. The source chart is 240. The receiving chart is 394 and the only terminal chart carrying a response is 3. The local source form is

$$
g=f(V)=V_{-960}-(V_{-638}+V_{-637})/16-(V_{-636}+V_{-332})/8-V_{-324}/4+V_{-94}/4.
$$

On every original input column, the receiving-bank form $h_B$ and the terminal-bank form $h_C$ independently give the same $g$.

$$
\begin{aligned}
h_B(V)&=-V_5/16-V_{96857}/4-V_{96968}/32-V_{99020}/4+V_{99022}/4+V_{99766}/4,\\
h_C(V)&=-(V_{90540}+V_{90542}+V_{93982})/8+V_{96847}/2.
\end{aligned}
$$

The change injects $v_{93997}=4$, $v_{96857}=-4$, and $v_{103019}=-8$ into the corresponding original producer forms, with all public input responses zero. Write $P$ for the propagated response. Direct rational replay gives $f(P)=0$ and $h_B(P)=h_C(P)=1$. Its only nonzero terminal response is $P_{155099}=-8$.

Define $V_j'=V_j-P_jg$ on every original slot. The source remains $f(V')=g$. If the original producer at $j$ is $F_j$, then $P_j=F_j(P)+v_j$ and $V_j'=F_j(V')-v_jg$. Both $h_B(V')$ and $h_C(V')$ vanish. The elimination substitutes the following local expressions for the two surrendered slots on every surviving producer and terminal row, including the producer of the new restoration slot.

$$
\begin{aligned}
V'_{96857}&=-V'_5/4-V'_{96968}/8-V'_{99020}+V'_{99022}+V'_{99766},\\
V'_{93982}&=-V'_{90540}-V'_{90542}+4V'_{96847}.
\end{aligned}
$$

The edited rows form an acyclic local graph. Induction on its regenerated schedule gives the claimed projected values on every surviving row. Slot 71 sends $g$ from chart 240 to chart 3, and its only terminal correction is $-8g$ at row 155099. This restores the complete transposed map. Returning to the forward orientation transposes the restored map. The separate endpoint computations check both maps directly.

The two removed transfers cost ranks 1 and 3. The new transfer costs rank 4. All productive counts survive, so the exact credit across the caller is $48(H_1+H_3-H_4)$. At κ `0.00386380485468` the mixed increment exceeds `0.415714729509591692126890039165450543` and the full signed margin exceeds `5.114122621700211289093028895443430160`. At κ `0.00386896184248` the mixed increment exceeds `0.416267641476530766634368243983996571` and the full signed shortfall lies between `0.154068328120620816710055508254842724` and `0.154068328120620816710055508254842725`. The maximum coefficient size in the changed scalar rows is 13 bits. The rational row and price replay are evidence for the combined physical and ordinary qualification.
