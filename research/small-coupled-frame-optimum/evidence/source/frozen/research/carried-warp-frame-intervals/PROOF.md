# Sharp marginal frame intervals and the extremal price test

This is a written proof about the binary frame contract defined below. The
finite exact replays supplement it. No formal proof kernel, physical phase
admission or multiplication theorem is claimed. Prepared by 1337isnot1337 with
substantial OpenAI Codex assistance; Apache-2.0.

## The graph and the quantified statement

Let V be F₂^h for any finite positive h. Let D be a finite directed acyclic
multigraph whose vertices are topologically numbered. Each edge e:a→b carries
an invertible linear map G_e:V→V. A specified subset of vertices has prescribed
subspaces F_v. A feasible assignment consists of subspaces U_v≤V such that

    U_v = F_v at each prescribed vertex;
    G_e(U_a) ≤ U_b for every edge e:a→b.

Assume at least one feasible assignment exists. Define L in topological order:

    L_v = F_v                              at prescribed vertices;
    L_v = sum_{e:a→v} G_e(L_a)              otherwise.

The empty sum is the zero subspace. Define H in reverse topological order:

    H_v = F_v                              at prescribed vertices;
    H_v = intersection_{e:v→b} G_e^(-1)(H_b) otherwise.

The empty intersection is V. Then:

1. L and H are feasible, and every feasible U satisfies L_v≤U_v≤H_v.
2. For each single vertex v and each subspace S with L_v≤S≤H_v, there
   exists a feasible assignment U with U_v=S. It is constructed by adding
   the prescription U_v=S and recomputing the lower propagation.

This is a standard order propagation argument applied to this caller. Choices
at different vertices remain coupled by the edges. The statement concerns
one prescribed marginal at a time, over all subspaces, not a registry search.

## Proof of the bounds

Compare against any feasible U. Forward induction gives L_v≤U_v: this is
immediate at prescribed vertices, and a sum of images of contained subspaces
is contained in U_v at an unprescribed vertex. Backward induction gives U_v≤H_v,
using inverse images and intersections. Thus L_v≤H_v.

For an edge a→b, if b is unprescribed its recurrence contains G_e(L_a).
If b is prescribed, the existence of a feasible U gives
G_e(L_a)≤G_e(U_a)≤F_b=L_b. Hence L is feasible. For H, an unprescribed a
satisfies G_e(H_a)≤H_b by definition. At a prescribed a, use feasibility and
the already established backward bound to get G_e(F_a)≤H_b. Thus H is feasible.
The implementation checks these prescribed-vertex compatibility conditions
explicitly and rejects empty intervals.

## Proof of complete marginal attainability

Fix v and S between L_v and H_v. Keep L unchanged before v, prescribe S at v,
and propagate sums of images forward. Incoming edges at v remain valid because
their images are contained in L_v≤S.

At each later vertex w, the extra contribution from S is the sum of G_path(S)
over paths from v to w whose internal vertices are unprescribed. This follows
inductively because linear isomorphisms preserve sums of subspaces. At the first
prescribed endpoint w on any such path, the reverse recurrence gives
H_v≤G_path^(-1)(F_w). Consequently G_path(S)≤F_w. The original lower contribution
was also contained in F_w, so prescribing F_w causes no conflict. That vertex
resets the downstream contribution to its fixed F_w. This proves compatibility
at every prescribed vertex and constructs the required feasible assignment.

## Binding the graph to the native word

The input is the exact frame-carrying program constructed by Dugongue's PR4971
at head 0130b196145a43a7d305de41f49e56e8e8556378. It retains Cao Yifan's native
round-three source and the credited native/helper lineage.

Each live field holds a pointer (v,A), meaning that its current frame, before
any next paid climb, is A(U_v). Initially v is its prescribed entrance and A=I.
A weighted whole-field swap exchanges the pointers. A native warp of signed
operator k changes A to G_k A, using the inverse map for negative k.

A scalar contact between live fields creates one vertex u and an edge
(v,u,A) for each operand. Both pointers then become (u,I). A scalar SCALE
commutes with the frame and creates no constraint. A scalar contact with the
owned cell retains its supplied frame as a prescribed vertex. Every live
terminal frame is prescribed. Owned-center events and all scalar coefficients
are retained. The graph is acyclic because every new contact is later in the
word than the pointers feeding it.

Every feasible graph assignment has a sufficient chronological realization:
before a contact u, climb each operand from A(U_v) to U_u. The edge constraint
makes this an ascending nested climb. At a warp carry the actual frame by G_k;
at a weighted swap carry it with the exchanged field. Restore each prescribed
terminal frame by its final edge. This realizes exactly the binary contract.

Conversely, any schedule in this contract with the same scalar contacts, swaps,
warp maps and fixed boundaries defines such a graph assignment. Between two
contacts, invertible maps preserve containment, so any ascending climbs can be
deferred through the intervening warps to the next contact. The composed map
on that edge therefore sends the earlier contact frame into the later one.
This is the precise schedule class to which the sharp bounds apply.

These statements concern subspaces and normalized linear actions. They do not
prove that every new canonical frame transition has the required physical
absolute phase or uniform implementation. The separate replay checks all
632 independent-input normalized rows, actual G-image warp conditions, frame
chronology, paid ranks and owned-cell clearing for each emitted candidate.

## Paid rank and the two extremal profiles

The sum of the dimensions of the 632 live frames changes only at paid climbs.
Swaps permute its terms and the invertible warp maps preserve each dimension.
Consequently every ascending realization with these fixed entrances and exits
has the same total live paid rank. The eight retained rank-eight owned-center
jobs add a fixed 64. The complete source and each realized schedule have total
paid rank 5,327.

For a paid profile n_r, define C_k(n)=sum_r n_r min(r,k). For any concave rank
price f on {0,...,9} with f(0)=0, put d_j=f(j)-f(j-1). Direct summation gives

    f(r) = r d_9 + sum_{k=1}^8 min(r,k) (d_k-d_(k+1)).

Every curvature coefficient d_k-d_(k+1) is nonnegative. Equal total rank cancels
the linear term when comparing profiles. Therefore C_k(source)≤C_k(candidate)
for every k implies that the source price is no greater for every such f.
A positive cut difference yields strict inequality for every strictly concave f,
including f(r)=r^t for 0<t<1.

The exact differences candidate minus source, for k=1,...,9, are

    least:    [347, 375, 60, 30, 0, 0, 0, 0, 0];
    greatest: [500, 427,115, 12, 0, 0, 0, 0, 0].

Both extremal schedules are thus strictly more expensive than the source for
every power price in the relevant range. This rejects these schedules as a
paid-profile improvement with the other invoice terms held fixed. It does not
optimize the intermediate assignments or include a new physical/compiler bill.
