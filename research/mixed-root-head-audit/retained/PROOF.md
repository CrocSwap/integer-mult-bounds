# Paid arrivals and independent returns

The base is the complete scalar graph from PR 7726. A node reads an exact linear form in the registers at its chart. A paid node sends this scalar to a second chart. A terminal reads a scalar at its final chart. Let $U$ denote the operator from public entrance to terminal. It has 400 main coordinates and an identity on the helper coordinates. Thus an old helper input affects only its own old terminal. The physical chart change acts on the array that carries each scalar. [Base graph and interface](data) · [Source construction](https://github.com/CrocSwap/integer-mult-bounds/pull/7726)

## Change the basis of parallel arrivals

Let $x_k$ denote one paid arrival from $A$ to $B$. Choose a vector $v$ on arrivals with the same endpoints, with $v_k=1$. For each other arrival $j$ send $x_j-v_j x_k$. Both old send expressions belong to $A$. At $B$ use the new arrival plus $v_j x_k$ in each old reader of $x_j$. This leaves every terminal value exact. A unit impulse at the pivot in the new basis now has the response of the whole vector $v$ in the old basis. The joint construction uses disjoint groups of parallel arrivals. Its checks derive the actual donor schedule after all substitutions. [Exact change of basis](construction.py)

## Expose an independent return

In one orientation, an old helper runs from $A$ to $Z$. At $A$ impose a local equation $s x=0$ with nonzero coefficient on its old input $x_r$. Solve it for $x_r$ using the other inputs at $A$. The surviving old outputs retain their values because they are independent of $x_r$.

Let $g$ be the old value of the pivot arrival at $B$. Let $c$ be a calibration at $B$. A readout $f$ at the new return chart must agree with $c+\mu g$ on the constrained old inputs. It must also have the same response as that expression to the pivot impulse. Give the helper a fresh arbitrary input $h$ at $B$ and remove the paid arrival. Each of the following normalizations makes the new return equal to $h$.

Specifically, the single-pivot journal installs $h-c/\mu$ and returns $f/\mu$. Its calibration is unaffected by the pulse. If old terminal $j$ acquires a change $t_j\delta$, its chart supplies a readout with old value $sx$ and pulse response $b_j\ne0$. Subtract $t_j/b_j$ times that readout. The constrained value vanishes and its change cancels the terminal error. The old and new return charts can differ. The journal charges the new rank and removes the old one. [Single-pivot equations and controls](witness.py)

For a group of pivots, solve the local source equations simultaneously. Each old pivot input is a linear form in the surviving inputs at its own source chart. Give each new input its own arbitrary scalar $h_i$. The grouped journal installs $(h_i-c_i)/\mu_i$ at pivot $i$. At the return chart, compare the full readout $f_i$ with $c_i+\mu_i g_i$. Their difference must vanish on all constrained old inputs and on every pivot impulse in the group. Thus $f_i$ returns $h_i$, including when a different input changes. At every surviving terminal $j$, subtract a local readout whose constrained value is zero and whose vector of pulse responses equals that of terminal $j$. This also covers any terminal with zero response. These identities hold for every input by linearity. The witness checks them as rational equations, including the off-diagonal pulse responses. [Grouped construction](construction.py) · [Full-column replay](linear.py)

## Supply an observation with a paid transfer

The split uses an old helper $r$ from $A$ to $Z$. The readout at $B$ measures $s x$ by combining its local bank with one paid transfer from $E$. A different chart $C$ supplies the fresh input, the calibration, and the controlled additions. Let $w$ be a direction supported on old entrances at $A$. Let $t=Uw$ be the response at $Z$, with $t_r\ne0$. The controlled additions at $C$ must have exactly the same full response $t$. The calibration at $C$ measures $yUx$ for a decoder $y$ at $Z$. The readout and calibration have zero response to the controlled additions.

Set the old pivot input to zero in $x^0$. For independent new inputs $a$ at $A$ and $h$ at $C$, use
$$
v=x^0+w\,(a-sx^0)/(sw),\qquad b=Uv+t\,(h-yUv)/(yt).
$$
The readout at $B$ gives $a$. The decoding $y b$ at $Z$ gives $h$. Since $U x^0$ has zero in row $r$ and $b-Ux^0$ is a multiple of $t$, each $b_j-(t_j/t_r)b_r$ returns the surviving old output. All affected outputs have their charts at $Z$. The price includes the transfer $E\to B$, the loss of the old target $A\to Z$, and both new targets $A\to B$ and $C\to Z$. [Split and independent equations](construction.py)

## Replace two paid transfers by one

After the parallel basis change, every reader of the pivot $k$ at $B$ sends to the same chart $C$. Let $G$ be a combination of these outgoing rows with nonzero coefficient on $k$. At a sending chart, the witness gives an observation whose value is $G$ plus known side information at $C$. Send that observation directly to $C$ using one of the old outgoing positions. At $B$, subtract a suitable multiple of $G$ from each other affected outgoing row to eliminate $k$. At $C$, recover the old affected rows from these residuals and the direct observation. This is a change of basis with a nonzero pivot. The two deleted transfers and the new direct transfer are priced at their actual ranks. [Paid pivot](vendor/network.py) · [Local observation check](construction.py)

All four constructions may use the transposed scalar network. Transposition reverses every paid direction, exchanges entrances and terminals, and transposes the whole linear map. A helper identity survives this operation. After each construction the graph returns to its forward orientation. The independent reverse pass propagates every output coefficient back to every input. The physical forward pass uses the retained guarded register schedule and exact integer divisions. [Rational edits](EDITS.json) · [Native replay](native.py)

## Two impulses that need each other

In group 26, paid arrival 101324 goes from chart 117 to 834. Arrival 99605 goes from 117 to 837. Use the compact public input labels from the source map. The two source equations are
$$
s_0=x_{1149}-x_{1152}/2,\qquad s_1=(x_{1152}-x_{1151})/2 .
$$
At chart 144, the local banks can observe $s_0$. They cannot observe any independent combination with $s_1$. For pulses $(u,v)$ the observation changes by $-(u+v)/2$. Terminal 130 at this chart has exactly this error. At chart 177 the available source equation is $s_1$. Its response and the error at terminal 166 are both $(-u+v)/2$. With both source equations imposed, the local observations have zero initial value. Subtract each observation at its terminal to remove both pulses. With only the first equation imposed, the second chart lacks that correction. With only the second equation imposed, the first chart lacks it. These statements concern the two specified source equations and the banks before group 26. The witness eliminates every row in each of the two local banks. [Receiver equations and all public columns](results/witness.json)

## Signed native price

Subtract the parent's productive-minus-paid rank counts from the candidate's. At ranks 1 through 9 the resulting coefficients are
$$
(70,21,0,-27,5,0,0,2,-5).
$$
Their first moment is zero. For $k=1,\ldots,8$ the tails $\sum_{r>k}(r-k)c_r$ are $(-66,-62,-37,-12,-14,-11,-8,-5)$. For a tariff $f$ with $f(0)=0$, discrete summation by parts gives
$$
\sum_r c_r f(r) = f(1)\sum_r r c_r+
\sum_{k=1}^8 \bigl(f(k+1)-2f(k)+f(k-1)\bigr)\sum_{r>k}(r-k)c_r .
$$
Thus every strictly concave rank tariff strictly favors the new native graph. For the recursive power tariff use $f(r)=r^{1-\kappa}$. The complete application counts the native graph at each call and adds the signed caller's own paid and productive jobs. It checks separate directed intervals for the original caller, the original native graph, and the combined construction. [Price tests](application.py) · [Complete invoices](results/application.json)
