# Common-vector growth with endpoint credits

Fix the exact #7334 native word and #7113 signed caller. A chart component consists of role segments between literal MOVEs, allocation events or endpoints, joined whenever ADD or COPY requires them to share a chart. All pure public helper components are eligible, including initial and final segments. Fix main, owned and mixed components and keep scalar order and coefficients fixed.

Choose a common nonzero vector v in F₂⁹. Any subset of eligible components that do not already contain v can adjoin it. Paid edges are literal MOVEs. Each public helper also has a productive edge from its initial to final frame. Keep containment on all edges and positive productive ranks. For an upper bound, paid rank-zero gaps cost zero. The two independent inventories recover 1,517 total groups, 553 eligible groups, 2,573 incident paid edges and 193 incident productive edges.

## Edge prices

Write h(r)=r^(1−κ) for r>0 and h(0)=0. Let c_r=h(r)−h(r−1). The old gap of a nested edge L⊂U is d. Use x and y for selection of its low and high frames.

- If v lies in U, then y=0. Growing L saves c_d on a paid edge and loses c_d on a productive edge. On a productive edge with d=1, forbid x=1.
- If v lies outside U, containment requires x≤y. Growing only U costs c_(d+1) for paid edges and gains c_(d+1) for productive edges. Growing both keeps the gap.
- If neither endpoint can change, there is no changed term.

The sum is the full changed native price in this model. The unchanged caller multiplies it by 17. The lead converts linear weights and hard nesting implications to maximum closure. The independent solver constructs the finite paid-growth edge U→L, source-to-variable reward and variable-to-sink penalty arcs directly. Under x≤y a productive high-only reward equals c*y−c*x, so it supplies one terminal reward arc and one terminal penalty arc. A fixed zero endpoint is represented by the sink when a hard implication or paid-growth penalty needs it.

The optimized independent replay cancels common terminal capacity. If a variable has capacity a from the source and b to the sink, each cut crosses exactly one of those arcs. Subtracting min(a,b) from both capacities reduces all cut costs and the offered benefit by the same constant. Hard capacities are assigned afterward to exceed the reduced offered total. The exact upper is unchanged. Positive and forbidden-cut controls exercise both forms.

## Shared price, exact upper

Independent per-edge rounding gives lower optimum zero and a tiny positive upper across the interval. Its complete 17-copy upper is 17 × 12669598508059006000 / 10^52 raw. This relaxation lets identical increments take different favorable endpoint values on different edges.

Instead, use one shared increment vector for all edges. Let integer a_r,b_r be its outward bounds at scale S=10^52 over the exact old crossing bracket. In scale 2S, the box lies inside the L1 ball with center m_r=a_r+b_r and radius R=Σ_r(b_r−a_r). Each coordinate deviates from its center by at most b_r−a_r. The ball is the convex hull of the 18 vertices m±R e_r.

For each v, the feasible selections depend only on charts and positivity of productive gaps. For each selection its signed price is linear in the nine shared increments. Thus a nonpositive maximum at all 18 vertices bounds it on the entire ball and the exact crossing bracket. Both solvers certify maximum zero on all 511 × 18 cases. The empty selection attains zero. No claimed saving survives within this model.

The calculation leaves changed scalar operations, distinct added vectors, shrinking, altered MOVE timing and changes to main or owned components outside scope. No new operator or recurrence is claimed.
