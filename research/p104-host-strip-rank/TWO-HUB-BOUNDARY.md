# Two-hub stage packing for e=0 and e=1

Status: a paper argument with exact finite controls, not a Lean proof. It constrains a particular host-incidence class, not every caller or invoice. Sources are PR #7852 at `41beda1d6435760dc99e38bd7e65f36798aad212`; original signed-frame and Gram definitions and the tight pair law are those of its authors. The 3-stage e=0 sign contradiction and the projected-core rank inequality were independently supplied by the `broader_decoders` research lane; the k=76 numeric relaxation example came from `thin_window`. The combination below and the 3-stage e=1 boundary frame were developed here.

## Hypotheses

Work over a field of characteristic different from 2. A signed frame has `P=-I`, two columns at each host stage, and a nonzero determinant for every 2-by-2 diagonal host K block. Write `|iota|=n+2+e`, where all other odd columns count as thins; then source `sgForward` gives `rank K<=2+e`. Stages are ordered by their event time, and for distinct hosts `K_st=sign(t-s) G_st`.

Take a subset S of distinct hosts. Suppose that outside two designated hub roles, every other role meets at most one stage in S. For those hosts each cross-stage Gram block factors as `G_st=U_s V_t`, where `U_s` is the 2-by-2 matrix of the hub B rows and `V_t` the 2-by-2 matrix of the hub A rows. The two hub matrices are not assumed invertible a priori. Everything below concerns this selected principal block; roles and stages outside S may be arbitrary.

## Three-stage e=0 sign law

If `rank K<=2`, there cannot be three selected stages `a<b<c` under those hypotheses. The 2-by-2 diagonal block at each selected stage is invertible, so the selected K has rank exactly 2 and factors into full-rank 2-by-2 block rows `X_i` and block columns `Y_j`, all invertible. The source tight pair lemma then makes each cross block invertible, and therefore all U and V hub factors are invertible. Let `D_i=U_i^-1 X_i`, `E_j=Y_j V_j^-1`. For distinct i,j:

`D_i E_j = +I` if `i<j`, and `D_i E_j = -I` if `i>j`.

Column b gives `D_a=-D_c`, column a gives `D_b=D_c`, and column c gives `D_a=D_b`, impossible in characteristic not 2. Consequently the non-hub co-incidence graph defined below has independence number at most 2. This is stronger than the four-stage alternating-block condition alone.

## Four-stage e=1 law

If `rank K<=3`, there cannot be four selected stages `a<b<c<d` under those same two-hub hypotheses.

For any selected host matrix H, and any host subset J, let `d_s` be the left-nullity of the **full off-diagonal strip within that selected H**. The projected-core inequality is

`rank H[J,J] + sum_{s outside J} d_s <= rank H`.                      (1)

To prove it, choose rows of H indexed by J whose projections on J are independent and a basis of localized null-row combinations from each host outside J. The latter vanish on J, so projection separates the two groups; disjoint outside-host support and invertible diagonal blocks make the localized group independent. This also holds with H transposed for column-strip deficiencies.

Apply (1) to the selected 4-stage matrix. If any row strip has positive deficiency, delete its stage: the other 3-stage principal block has rank at most 2, hence exactly 2 by its invertible diagonal block. The e=0 three-stage sign law contradicts the two-hub support. Thus all selected row strips have rank 2. The same argument on the transpose shows all selected column strips have rank 2. Since each strip factors through the corresponding hub matrix, all `U_i` and `V_j` are invertible. The submatrix on block rows `(a,c)` and block columns `(b,d)` then equals

`diag(U_a,U_c) * [[I,I],[-I,I]] * diag(V_b,V_d)`.

The central 4-by-4 block has determinant 4 and rank 4, contradicting `rank K<=3`. This argument uses the inequalities on the **selected** principal block, not deficiencies measured on every stage in the caller.

## Pair-capacity consequence

Create a simple graph on all k hosts: an edge joins two stages when at least one *non-hub* role meets both. Assume two fixed designated hubs cover all k stages. An independent set is a selection satisfying the two-hub hypotheses. Thus alpha<=2 in the tight e=0 case, alpha<=3 when e=1. The random-order bound

`alpha >= sum_v 1/(deg(v)+1) >= k^2 / (2|E|+k)`

implies the following necessary numbers of **distinct non-hub stage-pair edges**:

* e=0: `|E| >= ceil(k(k-2)/4)`; at k=76, at least 1406.
* e=1: `|E| >= ceil(k(k-3)/6)`; at k=76, at least 925.

For the first inequality, choose a random vertex order and retain a vertex when it precedes all its neighbors; the selected set is independent, and its expected size is the displayed sum. The second is Cauchy-Schwarz. Since a non-hub role of host degree d contributes at most `choose(d,2)` edges, the same number lower-bounds `sum_nonhub choose(d,2)`. It does not lower-bound the number of roles when some have high degree, or a financial/caller cost.

The other lane's k=76 relaxation has two universal hubs, 76 leaves and 73 degree-2 non-hub roles. The 73 edges are 38 disjoint matching edges plus 35 duplicates, so it has 38 distinct edges and an explicit independent set of 38 stages. It is therefore excluded in either e=0 or e=1. In the published relaxation the e=0 configuration was only an abstract invoice witness, never a realized caller. This exclusion does not eliminate other configurations satisfying the relaxation or prove a bound on a legal caller.

## Boundary frame and controls

The script `check_transition.py` builds a rational e=1 signed frame with **three** host stages: n=7, T=4, Q=3, `P=-I`, `(rank G,rank K,rank Kh)=(7,3,3)`. Its host masks are `[0,1,2]`, `[0,1,2]`, `[0]`, `[0]`, `[1]`, `[2]`, `[2]`; hence exactly two universal hubs and five non-hubs local to one host each. Every diagonal K block equals `[[1,-1],[1,1]]`, the fixed type-B gauge, and every cross-stage Gram block has rank 2. The thin transfers have rank-one differences from I, one being a reflection and three transvections. This proves the 4-stage exclusion is sharp **for signed frames**, including that local gauge and q=-1 thin algebra. It is not a verifier-legal word: the full q^4 identity, exact prefixes, contact stage masks and invoice have not been reconstructed.

The script also constructs the e=0 two-host boundary with n=2, no thins, two universal hubs and both host diagonals equal to the same gauge. It has `P=-I` and rank K=2; this shows the e=0 three-stage exclusion is sharp at signed-frame level. It carries the same word-realizability limitation.

Further controls: the source e=0 `CallerSGram.A3/B3` frame; a separate e=1 two-host frame with both cross blocks rank 1; a rank-3 host-matrix example showing deletion of a deficient stage leaves a rank-2 core; determinant 4 for the alternating block, changing to rank 2 when its sign is flipped or in characteristic 2; every partner subset of the `singP` set-RC2 model checked over rationals. The `--mutate` case intentionally changes a thin transfer, fails `P=-I` and exits 1.

```sh
cd .
python3 check_transition.py
python3 check_transition.py --mutate   # expected exit 1
```

The source package's bounded `python3 -B .../verify.py` passed and its exact output is in `pinned-package-python-check.log`. That script verifies the manifest, static declarations and selected regenerated data; it **does not run Lean**. A full kernel build, formalization of the new rank/graph argument, legal-word construction, and complete economic attribution remain open.
