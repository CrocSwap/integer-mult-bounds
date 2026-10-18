# Scoped rewrite identity and complete precision invoice

For distinct z registers a,b,x over F2, elementary transvections satisfy

```text
[b += x][b += a][a += x] = [a += x][b += a]
[a += x][b += a][b += x] = [b += a][a += x].
```

For the first relation, both sides send a to a+x and b to b+a+x, leaving x
and all other registers unchanged. The second is its reverse. The deleted
b<-x edge commutes with each retained edge, so its position among the three
edges is immaterial. When every intervening elementary transvection commutes
with all three edges, those intervening operations can be moved aside and the
same identity applied. Target-read barriers are checked using all donors; A/B
section boundaries cannot be crossed. Same-destination donor groups comprise
commuting transvections, but all other donors remain in the window check.

The witness uses 55 specific occurrences with distinct roles in one A/B section.
The verifier locates each occurrence in the current word, checks its donors,
commutation window, orientation and common frame, deletes b<-x, swaps the
relative order of b<-a and a<-x, and retains every other donor. It reconstructs
the exact committed candidate without importing discovery code. It also checks
all five complete phase maps, the dirty full-word endpoint in both directions,
and the literal reverse z-cleanup C. One forward ADD and its cleanup mirror
disappear per move:2*55=110. D, scatter and all geometry fields are identical.

Native legality checks every source-access frame, all physical MOVE paths,
arbitrary dirty columns and private COPY lifetimes. Comparing the complete
non-ADD records separately ensures the saving does not omit a frame change,
COPY, restoration or recursive child. The actual E8 paid rank histogram and
rank mass 5129 match the complete baseline; no rank claim is inferred from
frame-label cardinality. All copies retain rank7.

For the signed/arithmetic lift, begin every regular input with positive bound1
and a private copied register with bound0. An ADD replaces the destination
bound by destination+source; COPY duplicates its source bound, and ERASE clears
the private bound only after symbolic equality with the unchanged original.
Taking every intermediate maximum in each full orientation gives cancellation-free row-l1 envelopes F=13721 and B=3663878. The independently reproduced native
prefixes agree exactly. Consequently the pinned K=2 local and K=4 nine-stage
bridge formulas give

```text
2^6  F^3 B^2 = 2219316669212827291362119936 < 2^104
2^18 F^5 B^4 = 22973795977533615901914742933524089773622692690264064 < 2^192.
```

The strict caps are checked as integers, including equality-at-cap negative
controls. Further controls reject a wrong retained-edge order, wrong duplicate
occurrence, intervening noncommuting gate, omitted COPY/ERASE, omitted paid D
gate, boolean frame ID and duplicate JSON key. A positive control confirms that
using the predecessor's semantically exact C still reaches the endpoint, while
a negative control rejects it as nonliteral cleanup. The native staged checks
add 96 separate omitted-bridge controls.

These statements establish this finite circuit and its stated envelopes under
the inherited arithmetic/recursive interfaces. They do not prove the unresolved
semantic-D supplier lemma, global circuit optimality, eleven-stage192-bit
admission, or a new conditional multiplication exponent.
