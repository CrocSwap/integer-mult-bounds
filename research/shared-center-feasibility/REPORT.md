# Shared-center feasibility: changing both the forms and the central map

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Exact bounded diagnostic; no new multiplication exponent.

## Decision

Stop this bounded round without a larger construction search. **Redundant
centers can reduce support cost in principle, but the tested E8 enlargement
cannot do so, even when the central matrix changes jointly with the forms.**

The previous [discovery report](../geometry-circuit-discovery/REPORT.md)
established a cost of 72 for minimum-rank factorizations of one fixed E8
central matrix. This round permits an extra rowspace direction, arbitrary
numbers of centers within that enlarged space, and every compatible binary
central matrix within it. The minimum is still 72 in all four cases below.
The optimistic target requires at most 43; rank positivity with two equal
axes already requires a cost below 60.

A separate incidence argument addresses a genuinely joint search with no
fixed central matrix or rowspace: **if every E8 center has support span of
dimension at most two, total support cost is at least 96.** It is therefore
not productive to assemble the replacement entirely from such cheap forms.

This does not exclude multiple new rowspace directions, centers supported
on higher-dimensional flats, different geometries, or a different frame
schedule. It does not establish a fundamental barrier for integer multiplication.

## Cost model and the precise enlargement

Use the same 120 rational E8 root lines q_i, in dimension eight, as in the
discovery report. Let C have diagonal one over F2, and require q_i and q_j
to be rationally orthogonal whenever i differs from j and C_ij=1.
Write C=UV. A center is a row v of V, with optimistic copied-center cost

    w(v) = dim_Q span{q_i : v_i=1}.

The aggregate cost is ell=sum_j w(V_j). These are support-containing
frame proposals; an arbitrary frame schedule need not obey this accounting.
Nondegenerate intermediate frames, retained readout and the physical
producer still require proofs before any positive score becomes a network.

Let S be the nine-dimensional binary rowspace of the old matrix
C0=I+(full orthogonality adjacency). We enumerate every nonzero form v
whose rational support dimension is at most two. For each, allow all
central forms in E=S+<v>, not merely v appended to an old basis.
Every v lies outside S, so E has binary dimension ten.

This is a specific new enlargement of the previously parked case. It is
not a rerun of the old minimum-rank basis optimization or a parameter sweep.

## Complete finite catalog and symmetry certificate

The catalog contains all 8,380 permitted v. Each pair of distinct lines
spans a plane containing either two or three of the 120 lines. The code
checks its closure against every root by an integer Gram determinant and
includes every nonempty subset of the closure. This proves completeness
for support rank at most two; no root-subsystem classification is assumed.

Reflection in a stored root q acts on stored labels by

    x -> x - (x.q/4) q,

followed by choosing the representative with first nonzero coordinate
positive. Each of the 120 reflections is checked to permute the exact
root-line list. It preserves rational support dimensions and the binary
orthogonality core. Breadth-first orbit enumeration, rather than assumed
transitivity, gives four cases:

| New form's support | Orbit size | Minimum basis cost in E | Best cost for fixed C0 | Best cost allowing C to vary |
| --- | ---: | ---: | ---: | ---: |
| One line | 120 | 72 | 72 | 72 |
| Two orthogonal lines | 3,780 | 72 | 72 | 72 |
| Two nonorthogonal lines | 3,360 | 74 | 72 | 72 |
| Three lines in a rank-two plane | 1,120 | 74 | 72 | 72 |

Every nonzero form of each representative E is evaluated exactly. There
are 1,023 forms per case. Their support-rank histograms are respectively

    {1:1, 7:1, 8:1021}
    {2:1, 7:2, 8:1020}
    {2:1, 8:1022}
    {2:1, 8:1022}.

The first case illustrates the cost cancellation directly. A coordinate
singleton costs one; the parity over the 63 lines orthogonal to it costs
seven. Together they replace one old full-dimensional cost-eight form
without lowering the sum. The extra center is not free in role accounting.

## Why the variable-matrix result is exhaustive in this space

For target i, an admissible row c of C must satisfy

    c_i=1,
    c_j=0 whenever j!=i and q_i.q_j!=0.

Enumerate all such rows in E. No symmetry or minimum-rank condition is
imposed on C. A proposed center space T can implement a compatible matrix
if and only if it contains an admissible row for every target independently.
Those rows can then be expressed as binary combinations of a basis of T.

If a target has only one admissible row in E, that row is forced into T.
Let F be the span of all these forced rows. The four cases have

    dim(F) = 8, 9, 9, 9;
    dim(E/F) = 2, 1, 1, 1.

Thus every possible T between F and E can be enumerated: five quotient
subspaces in the first case, two in each other case. For each T, the
certificate either records failure to supply an admissible row, or a
minimum-weight basis and a complete compatible C.

Allowing dependent or additional centers cannot invalidate this lower
bound. Delete any center that is a binary combination of the others and
substitute that combination in U. This preserves C and decreases the
positive sum of support costs. An optimum is therefore a basis of some T;
we enumerate every relevant T. Minimum-weight bases are computed by the
vector-matroid greedy algorithm on the complete exact cost catalog.

This closes the one-direction enlargement even for jointly variable C.
It does not close a space obtained by adjoining two independent new forms.

## A lower bound when C is completely free

The following observation is independent of S and E.

Let S_j be the input support of center j, and put w_j=dim_Q span(q_i:i in S_j).
Every input must appear in some center, since C has diagonal one. Call an
input private to a center if it appears in that center and no other.

If i and k are private to the same center j, their columns in V are both
the j-th coordinate vector. The diagonal condition forces U_ij=1, hence
C_ik=1. Compatibility forces q_i and q_k to be orthogonal. Private labels
within a center are therefore pairwise orthogonal nonzero vectors, and
their count p_j is at most w_j.

Let n be the number of inputs, p=sum_j p_j and A=sum_j |S_j| the number
of input-center incidences. Every nonprivate input appears at least twice:

    A >= p+2(n-p) = 2n-p >= 2n-ell,
    ell = sum_j w_j.

If a catalog satisfies |S_j|<=D*w_j, then A<=D*ell, giving

    ell >= 2n/(D+1).

The exhaustive E8 plane catalog has D=3/2 for support dimension at most
two. Consequently ell>=240/(5/2)=96. This permits arbitrary numbers of
centers and every compatible C; it is stronger than simply counting
covered inputs, which would give only ell>=80.

This is a necessary support-cost bound. It is not a general lower bound
for arbitrary rational matrix frames, nor for a circuit that changes the
support-containing retained-center contract.

## Positive control and why it does not justify expansion

To ensure that the test admits the proposed trade, take four mutually
orthogonal coordinate labels and C=I+cyclic_shift over F2. Its binary rank
is three. Every nonzero rowspace form has even support, and a minimum-rank
factor costs six. Adding one coordinate form enlarges the space to F2^4;
four singleton centers implement the same C at cost four.

This is an exact 6->4 local support-cost reduction using 3->4 centers.
All scalar entries of both factorizations are checked, so it is not a
floating-point or rank-tolerance artifact. However, it is just a calibration
example: the new ell/n is one. The granted two-axis numerator is

    1-2ell/n = -1,

and it introduces another retained center role before charging any
producer, copy, or restoration overhead. It does not provide useful
characteristic separation or a viable finite multiplication network.

The E8 tests do not achieve even this local cost improvement, so no
arbitrary-scratch circuit, copied-stream schedule, ordered physical
profile, or complex counterpart is promoted to a construction. There is
no new witness to integrate into the multiplication assembly.

## Implication for the next research decision

Do not launch a larger blind search over E8 singleton/plane centers or
another choice of basis in these spaces. The bounded diagnostic now closes
those specific options exactly, including the jointly variable central map.

A further run needs a proposed shared identity with several new directions
and adequate support density, or a different way to charge intermediate
frames. The private-input inequality gives a cheap first screen for such
an identity; passing it is not evidence of a construction. We have not
identified a concrete identity that earns a longer run. That is the
remaining missing ingredient, rather than numerical parameter slack.

The existing rank-one two-axis target remains ell<=43 per E8 axis under
optimistic storage and batching. Neither the exact cost 72 nor the all-small
center lower bound 96 supports expanding this candidate toward that target.

## Reproduction

```sh
python3 research/shared-center-feasibility/diagnostic.py --output research/shared-center-feasibility/certificate.json
python3 -m unittest discover -s research/shared-center-feasibility -p 'test_*.py' -v
```

The code uses only the standard library and imports the preserved exact
linear algebra from the discovery pass. The certificate includes every
orbit member, each extended rowspace catalog, all quotient-subspace
decisions, compatible matrices for feasible cases, and chosen center
forms. Tests independently check support ranks modulo 101, replay the
joint optimization and fitting constraints, verify symmetry preserves the
core, and check the private-input inequality and positive control.
See `validation.json` for the run and source-preservation check.
