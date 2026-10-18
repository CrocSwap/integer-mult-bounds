# Generator-priced affine target sharing

**Scoped negative result; no new \(\kappa\).** In the formal
\(\mathbb F_2[\mathrm{AGL}_2(\mathbb F_2)]\) model with two target registers,
four paid address generators, and all six rank-one scalar idempotents, both
\[
\operatorname{diag}([h],[h])
\quad\text{and}\quad
\operatorname{diag}([h],[h^{-1}]),
\qquad h(x_0,x_1)=(x_1,x_0+1),
\]
have exact minimum cost **8 calls**. The direct words use four calls per
target. A complete formal radius-seven search finds no saving, even though the
general homogeneous displacement-rank floor is only four calls.

This tests a new cost rule: only the two coordinate shears and two coordinate
translations have unit price. PR #1333 prices every rank-one affine address
map at one call and proves the general displacement-rank floor. Its stated
generator-priced follow-up leaves room for a sharing gain; these two exact
endpoints do not realize it. The result is limited to two registers and the
two displayed target profiles.

## Exact model and complete cost

Work in the noncommutative group algebra
\(\mathbb F_2[G]\), \(G=\mathrm{AGL}_2(\mathbb F_2)\). The paid labels are
\[
a(x_0,x_1)=(x_0+x_1,x_1),\quad
b(x_0,x_1)=(x_0,x_1+x_0),\quad
u(x_0,x_1)=(x_0+1,x_1),\quad
v(x_0,x_1)=(x_0,x_1+1).
\]
Each costs one. A call chooses any of the six rank-one idempotents
\(N\in M_2(\mathbb F_2)\) and applies
\[
D_N(g)=I+([g]+[1])N.
\]
Free scalar \(GL_2(\mathbb F_2)\) mixing is retained as the inherited
optimistic relaxation. Moving it through the paid factors conjugates each
idempotent; augmentation \([g]\mapsto1\) forces the net scalar map to be the
identity, so enumerating all six idempotents covers interleaved free mixing.
Address labels outside \(\{a,b,u,v\}\) are forbidden.

The target \(h\) has a shortest address word *abav*, length four, and
\(\operatorname{rank}_{\mathbb F_2}[A_h-I\mid b_h]=2\). Its inverse
\(h^{-1}(x_0,x_1)=(x_1+1,x_0)\) has shortest word *abau* and the same rank.
Thus each endpoint has direct cost 8 and the general displacement-rank floor
4. The mechanism had at most four calls of optimistic headroom. There is no
helper register or copied information; both arbitrary-input target registers
are represented in the exact endpoint. Each address call is charged once.
Physical/compiler realization, recursive supplier costs, precision, hosting,
and admission into the selected bit construction are outside this local model.

The selected conditional record remains **complex-binding** according to
scripts/research_baseline.py. Consequently even a local bit saving would not
by itself change its \(\kappa\); this result claims no supplier-wide saving.

## Exact search and controls

Each paid factor is a formal involution because every allowed address label
satisfies \(g^2=1\) and every \(N\) satisfies \(N^2=N\). For a word of at most
seven calls, split its factor sequence after at most three calls. The verifier
enumerates exact states in the radius-three and radius-four balls. If \(P\) is
the prefix and \(T=QP\) the endpoint, then the required suffix is
\(Q=TP^{-1}\). Every state is the full \(2\times2\) matrix of 24 formal
coefficients; no finite address representation is used for acceptance.

The two independent implementations agree on 6,457 radius-three states and
90,859 radius-four states, with their canonical state digests in
CERTIFICATE.json. The first uses packed row-major \(AGL_2\) matrices and a
rank-one update. The second enumerates all 24 permutations of the four address
points and multiplies the two formal coefficients of each factor directly.
Neither finds a word of length at most seven for either endpoint. The direct
eight-call words replay coefficient by coefficient, so the minima are exactly
eight in both stated cases.

The replay also verifies all 24 paid factors, all 24 formal group elements,
all six idempotents, factor involution, both direct words, rejection of every
single-call deletion from each direct word, and a changed-target/order
mutation. These checks establish the finite algebraic result only.

## Reproduce

From the repository root:

    python3 -I -B research/bit-affine-generator-sharing/verify.py
    python3 -I -B research/bit-affine-generator-sharing/independent.py
    python3 scripts/research_package.py --package research/bit-affine-generator-sharing

The first two commands should print PASS_BIT_AFFINE_GENERATOR_SHARING and
PASS_BIT_AFFINE_GENERATOR_SHARING_INDEPENDENT. TASK.json records seed, base,
changed scope, exact cost model, stopping rule, and next question. SOURCES.json
pins the retained AGL predecessor review/proof. No predecessor implementation
is imported.

## Overlap and attribution

Gareth Davidson (@bitplane), PR #1333, supplies the broader AGL group model,
the displacement-rank floor, and the generator-priced next question. Related
coordinate-CNOT-only linear targets are recorded in TASK.json. Two nearby
Discussion #1317 claims use three registers: comment 18918042 studies
\(\operatorname{diag}([a],[b],[aba])\) with only the two CNOT labels, while
comment 18918291 studies \(\operatorname{diag}([a],[b],[h])\) with labels
\(a,b,t_x\). The latter shares the map \(h\), but changes both the target tuple
and the address alphabet. This package prices \(a,b,t_x,t_y\) and gives exact
two-register minima for \(\operatorname{diag}([h],[h])\) and
\(\operatorname{diag}([h],[h^{-1}])\). Open PR #1696 submits a scoped exact
five-call result for the three-register CNOT-only target
\(\operatorname{diag}([a],[b],[aba])\); this package adds the two affine
two-target profiles under the four-label alphabet. A separate current claim,
Discussion #1700, studies rational rank-one frames with two independent
address relations; its group and cost premise differ. No selected-result or
physical-supplier change is claimed.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. There has
been no independent human review. New work is Apache-2.0; predecessor files
remain unchanged.

## Open next questions

Could a third target register or another explicitly priced affine target family
permit sharing? First choose one three-target endpoint, compute its direct
generator lengths and displacement-rank floor, and stop if the fully charged
optimistic gap is zero. This package does not cover larger target tuples,
workspace, or a physical/compiler admission.
