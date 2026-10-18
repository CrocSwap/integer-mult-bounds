# Finite construction and fixed-family ceiling

Use the unchanged PR1107 local supplier. Its independently recounted paid
profile is `(2406,432,424,142,82,8)` at ranks `(1,2,3,4,5,8)`; its 480 helper
widths have multiplicities `(56,32,32,120,240)` at `(4,5,7,8,9)`.

For `0 ≤ s < 9`, `0 ≤ r < 37`, order calls by `(37s+8r,s,r)`.
Each replica retains the original stage order and hence all thirty original
physical source events, including its nine bridges. PR858's event expansion
reconstructs strict idle intervals. The independent PR890 checker reconstructs
them separately from the original event stream.

The frozen flow groups together only identical capacity/interval pairs. Each
group retains the complete list of physical `(replica,child)` windows, with
112 distinct port families per window. A pattern with multiplicity `N` has
`N` bins. For every width `w`, its integer time flow totals `N` times the
pattern multiplicity of `w`; at each invocation the total flow is at most `N`.

Split each width's flow among that many left vertices of degree `N`. Add
dummy left vertices to fill the unused capacity of the time vertices. This
gives a regular bipartite multigraph of degree `N`. Successive perfect
matchings decompose it into `N` bins. Every matching is checked to be a
permutation using positive edges, and every used edge is removed. Consequently
each bin has its exact pattern and receives at most one helper per invocation.
`construct.py` performs the entire decomposition with exact integers and
checks its reconstructed flow against the frozen one.

Assign bins to their listed physical windows and port numbers in order; lay
their helper slices consecutively. The independent audit checks all 159,840
roles for strict bridge-aware timing, whole widths, complete per-call helper
coverage, distinct physical families, disjoint prefix slices, and literal
orthogonal 73-axis charts. These checks also detect aliasing between different
idle children of the same physical family. The residual idle profile is
`{1:5424,48:11320}`. Adding 333 local profiles gives the profile in CLAIM.json.

The retained PR942 parent lift has bank groups `(8,8,8,8,5)` and shared restored
private workspace. Its independent parent checker is unchanged. The emitted
controller removes the dedicated banks and uses the frozen whole-owner map.
The strict invoice charges the enlarged 1,024-bit prefix reserve. It derives
prefix 775 and row coefficient 17,495, and binds every provider artifact to
the fresh native replay. Both moment engines certify the same root bracket:

```
0.001677148804883116146676 < b < 0.001677148804883116146677.
```

The retained bit endpoint is `1733427039589844234749 / 10^24`. All 47 strict
outer constraints hold at `κ = 1674340686401949 / 10^18`.

For the fixed-family ceiling, retain PR795/890/942's signed helper prices
`(-1,-20,-8,-2,4)` and bin bonuses `(2,4,8,-13)` for capacities
`(8,16,32,48)`. There are `(672,448,448,448)` bins per replica. The new word
leaves idle mass 14,832 and signed budget −1,192 per replica. The retained
supporting-inequality proof therefore gives rank-one credit
`48*(-1192)+13*14832 = 135600`. At 37 replicas, the attained rank-one count
is `37*135600/925 = 5424`, with the remaining mass in rank 48.

`price.py` re-enumerates all 1,163 bin patterns by two methods, checks the
supporting inequalities with both exact arithmetic engines, and evaluates
the outer reduction at both ends of the root bracket. Both yield the same
`10^-18` grid tick. Thus this construction attains that fixed-family grid
ceiling, even when other call orders and replica counts are admitted in the
relaxation. This statement does not bound different local words, capacity
families, helper interfaces or bit suppliers.

All retained all-size and realization hypotheses are unchanged; this proof
and its executable evidence establish the finite conditional composition.
