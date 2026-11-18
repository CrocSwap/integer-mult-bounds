# Why the changed public interface works

Use a rational scalar at each public entrance. Each paid instruction reads an exact linear combination of scalars at one chart and installs its result at a second chart. A terminal reads scalars at its own chart. The prescribed physical chart operators are unitary. The scalar network describes the circuit in these chart coordinates. The catalogue checks the phased operators that convert between them.

The parent scalar operator is a direct sum of the 104 port maps and the identity on independent helper coordinates. Write this operator as $U$. Every edit protects all 400 main coordinates. Retired helpers have an isolated identity row while the journal is in use. The final graph deletes the input and output of each such row.

## Remove a helper and its paid returns

Choose an independent helper coordinate $r$. At its source chart take a linear form $s$ in local banks with a nonzero coefficient on its input. Its full expansion also has a nonzero coefficient on $x_r$. For each listed receiver, the journal supplies local banks whose linear combination has exactly the same full expansion as $s$. Impose $s=0$. At the source, solve for the old pivot input. At each receiver, solve for one arrival in that receiver's equation. Substitute these solutions in every reader of the respective pivot. Erase the paid instruction for each eliminated arrival.

For arbitrary values of the surviving inputs there is a unique old $x_r$ that satisfies the constraint. The outputs for these inputs were independent of $x_r$, since the old helper was an identity summand. Thus the restricted old circuit has the required outputs. The schedule and the bank checks establish that each substitution uses available local values. The witness expands the source and every receiver relation on all old inputs. Some steps remove a target and a paid transfer of equal rank. These steps permit later changes of the graph.

## Split one helper using a local observation and a controlled input

Work in either orientation. Suppose helper $r$ goes from chart $A$ to chart $Z$. At chart $C$ the old network offers a readout with entrance covector $s$ and a calibration with value $y U x$. A pulse is a specified vector of additions to local send instructions and terminal reads at $C$. The witness checks its full terminal response $t$. A source direction $w$ has the same response, $U w=t$. Both $s$ and $w$ use only inputs at $A$. Both $y$ and $t$ use only outputs at $Z$. The pulse has zero response at the readout and calibration. The three scalars $s w$, $y t$ and $t_r$ are nonzero.

Give the shortened helper an arbitrary input $h$ at $A$. Give a fresh helper an independent input $g$ at $C$. Let $x^0$ contain the other original inputs and have coordinate $r$ equal to zero. In the old source banks use

$$
v=x^0+w\frac{h-sx^0}{sw}.
$$

The readout at $C$ now returns $s v=h$. At $C$ apply the pulse with amplitude $(g-yUv)/(yt)$. Write $b=Uv+t(g-yUv)/(yt)$ for the resulting old output vector. Its decoded value $y b$ is $g$. Install this value as the fresh return at $Z$. For every $i$ other than $r$ at which $t_i$ is nonzero, install $b_i-(t_i/t_r)b_r$. All other surviving outputs keep their values.

Indeed $b-Ux^0$ is a scalar multiple of $t$ and $(U x^0)_r=0$. These local corrections recover every component of $U x^0$ except the surrendered coordinate, which the readout now returns at $C$. The two new owners earn the exact ranks for $A$ to $C$ and $C$ to $Z$. This argument permits different source and return covectors and different nonzero normalization factors. The implementation checks the actual rational responses and the final acyclic schedule. [Split construction](split.py) · [Equation checks](witness.py)

## Transpose, reroute and count

Transposing the scalar graph reverses each paid edge, exchanges the public entrances and terminals, and transposes the full linear map. A helper identity summand remains an identity summand in this orientation. The journal can therefore apply a restriction or split to the transposed graph, then transpose back. A paid pivot or hub reroute uses the retained recoding identities. Both the final forward propagation and a separate reverse propagation check the entire resulting operator.

The compact graph keeps the first-plane partner of each live port at offset 112. It gives each surviving helper exactly one public label. Each of the 16 calls receives fresh helper owners. The signed caller supplies the root targets and the external paid operations at their actual multiplicities. Price every job of rank $r$ at $r^{1-\kappa}$. The complete margin is the sum of the productive prices minus the sum of the paid prices. The replay checks the signs on both sides of its crossing with directed bounds. It also checks a strictly interior probe, the physical resource bounds and the outer compiler inequalities. [Complete application](application.py) · [Physical and price evidence](results/application.json)

## Three restrictions that enable the last three splits

For role 1400, the transposed relation removes arrival 98393 at chart 280. This changes the forward readout for helper 294 at chart 288. The source-steering product is 2, the return-decoding product is 1/2 and the pivot component is 3. Bank 89199 supplies the calibration. Under the alternate forward restriction, 16 readout coefficients differ. Input 10 alone changes the readout by one unit.

For role 1401, the chosen restriction removes arrival 91108 and permits the second split at chart 288. The alternate relation gives 16 incorrect coefficients in the pulse response. For role 1409, the equation removes arrival 96030. Its source includes one half of the input at stable role 549. This coefficient is needed at that point in the journal. The alternate relation gives 27 incorrect response coefficients for the split at chart 306. The controls rebuild the full prefix in each case. [Rational journal](EDITS.json) · [Worked counterexamples](results/witness.json)

The search used modular linear algebra to locate possible receiver relations, causal pulses and paid reroutes. It also tested smaller sets of earlier edits to identify conditions for a split. The final replay uses rational arithmetic for every chosen relation and integer arithmetic for all public columns. The certificate establishes this construction's price. Optimality across possible helper bases remains open.
