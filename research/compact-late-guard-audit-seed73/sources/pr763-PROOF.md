# Interior compact carries and exceptional-stream repair

This is a mathematical audit of the address map in
[`notes/compact-control-movement.tex`](../../notes/compact-control-movement.tex),
especially its “Later source” and “Guards and deterministic repair” paragraphs,
and of the map represented by
[`scripts/audit_compact_controls.py`](../../scripts/audit_compact_controls.py).
The source snapshot is commit
`66849e1475c930fd7732b1a0067ffee7e1e95f60`; the accompanying source manifest and
receipt pin the audited files. Production sources are unchanged.

The arguments below are integer/address arguments. They neither establish a
fixed-tape implementation or its cost nor supply the complete temporary fields
at recursive nodes. The omitted highest selected target bit is outside this
map, as it is in the existing checker. The manuscript supplies that bit through
a separate elementary XOR.

## 1. The guarded four-step identity

Let `n = f - 1 >= 1`, `G >= 1`, `B = 2^G`, `0 <= rho < K`, and
`j_i = rho + iK`. The low `n` target segments have length `K`, begin at `j_i`,
and are disjoint. They fit in the target slot of length `(n+1)K`, including
`rho = K-1`.

Write a target segment as `v_i = 2g_i + a_i`, with `a_i` a bit, and the
corresponding compact temporary digit as `w_i`. Assume

```
0 <= w_i <= B-2,
2B <= g_i < 2^(K-1)-2B.
```

For any control bit `z_i`, the first target update adds `2 z_i w_i`.
It leaves the parity `a_i` unchanged. The guard guarantees that its result
stays within the segment: the increase is at most `2B-4`, and both endpoints
have more margin than this requires. Consequently the packed target update
causes no inter-segment carry and changes no outside target bit.

The temporary load therefore changes digit `w_i` to `w_i+a_i`. The upper bound
`w_i <= B-2` ensures that this load has no compact inter-digit carry, including
at the highest compact digit. The second target update gives, as an integer,

```
v_i + 2 z_i w_i + z_i (1-2(w_i+a_i))
    = v_i + z_i (1-2a_i)
    = 2g_i + (a_i xor z_i).
```

That final value is within the same segment, so the second packed update has
no inter-segment borrow. The unloading bit is
`(a_i xor z_i) xor z_i = a_i`; subtracting it restores `w_i` without a
compact-digit borrow. Each back-field swap/rotation/swap sandwich restores
the arbitrary back field as well. The four-step operation thus flips exactly
the controlled target parities, restores the entire temporary and back fields,
and leaves every `g_i` unchanged.

This proof uses the unsaturated temporary bound for *each* execution. After
the first execution the temporary digits have their original values and the
target guards are unchanged. The same hypotheses therefore hold for the
second execution, even if the compact control load between them has carries.
The control digits themselves need no bound beyond being radix-`B` digits:
the four-step identity reads only their parities.

## 2. Exact later-source carry formula

In the later-source construction, let `u_i` denote the original digits of
the front compact control field and let `c_i = x_{j_i}`. Assume the temporary
and target hypotheses of Section 1, but impose **no saturation exclusion on
the `u_i`**.

The compact source load adds `sum_i c_i B^i` modulo `B^n`. Its ordinary radix
carry recurrence is

```
k_0 = 0,
k_{i+1} = floor((u_i + c_i + k_i)/B),
u'_i = u_i + c_i + k_i - B k_{i+1}.
```

Each `k_i` is a bit. Since `B` is even,

```
(u_i mod 2) xor (u'_i mod 2) = c_i xor k_i.
```

The first guarded identity flips target parity `i` by `u_i mod 2`; the
second flips it by `u'_i mod 2`. Section 1 applies to both and proves that
there are no other target changes. The source field is unchanged throughout,
so the final inverse source load subtracts the same compact integer and
restores `u` modulo `B^n`. Thus the exact later-source map on this guarded
domain is

```
S(state).y = state.y xor sum_i (c_i xor k_i) 2^j_i,
S(state).x = state.x,
S(state).u = state.u,
S(state).t = state.t,
S(state).b = state.b.
```

All spectator bits are unchanged. The selected positions are distinct, so
the map equals the ideal low-selected-bit XOR **if and only if**

```
k_1 = ... = k_(n-1) = 0.
```

The outgoing carry `k_n` is harmless: it is discarded by the compact modular
load and has no subsequent target control digit. This includes `n=1`, when
there are no interior carries and no `u` exclusion is necessary.

There is also an equivalent condition that uses the original source bits
directly:

```
for every i < n-1: not (u_i == B-1 and c_i == 1).
```

For sufficiency, induction starts with `k_0=0`; the stated condition prevents
every carry into a represented successor digit. For necessity, the first
violation has zero incoming carry and creates an interior carry, which the
exact formula detects at the next selected target position.

This is a universal integer derivation under the stated hypotheses, not an
inference from the accompanying finite enumeration.

## 3. Expanded sufficient good set

The original manuscript excludes every saturated `u` digit. A strictly weaker
source-independent sufficient condition is to exclude saturated digits only
for `i < n-1`, while keeping all original temporary exclusions and target
guards. The highest `u` digit may take its complete range. For each fixed
guarded target and unsaturated temporary, this increases the number of allowed
`u` fields from `(B-1)^n` to `B(B-1)^(n-1)`.

The source-dependent criterion in Section 2 gives a further exact
characterization of equality with the ideal map within the domain where the
temporary and target hypotheses hold. These statements do not claim that
every state excluded by the target or temporary predicates must fail.

Either expanded set is invariant under the ideal map `T`: that map changes
only target parities, so it preserves `g_i`, `u`, `t`, `x`, and `b`. The
original repair proof therefore applies unchanged if its bad predicate is
replaced consistently by the complement of either expanded set. This audit
does not modify the production predicate or claim an improved layer exponent.

## 4. Why destination keys fill the marked holes

Let `D` be a finite complete address rectangle, `E` its chosen bad set, `T`
the ideal map, and `S` the actual modular rotation/swap sequence. Assume:

1. `S` and `T` are bijections of `D`;
2. `T(E) = E`;
3. `S(q) = T(q)` for every `q` outside `E`.

Then `S(D\E) = T(D\E) = D\E`. Bijectivity implies `S(E) = E`.
Consequently `R = T composed with S^(-1)` is a permutation of `E` and is the
identity on its complement.

After running `S`, the record occupying address `q` originated at `S^(-1)(q)`.
Its correct destination is therefore `T(S^(-1)(q))`. Extracting the records
currently in `E`, assigning these keys, sorting them, and reinserting them
into the marked holes has two distinct correctness requirements:

- The keys are distinct and their address set is exactly `E`, so every hole
  receives one record.
- The record at key `r` originated at `T^(-1)(r)`, so payload identity agrees
  with the ideal map.

The first condition alone is insufficient. For example, the incorrect key
`T(q)` also permutes `E` and hence fills every hole, but generally delivers the
wrong payload. Likewise, composing the inverse and ideal map in the opposite
order need not work. The inverse must reverse the actual modular operations,
evaluating each offset from the *current inverse controls*; the guarded integer
identity cannot replace that inverse on bad addresses.

## 5. Scope of the finite quotient rectangles

For the audit parameters `n=2, K=5, rho=4, G=1`, both wide slots have 15 bits
and each compact field has two bits. With the unused earlier-source `u`
included as a spectator, the complete physical address rectangle has

```
15 + 15 + 2 + 2 + 2 = 36 bits.
```

The finite representatives enumerate the three selected source bits (8
values), target bits 4 through 14 (2048 values), and all temporary/back fields.
The earlier-source enumeration has `8 * 2048 * 4 * 4 = 2^18` states. The
later-source enumeration additionally includes all four values of `u`, giving
`2^20` states. The source's highest selected bit is included in these counts
although it is unused by this low-selected-bit gadget.

Every omitted source bit is a spectator because the offsets read only the
selected source bits and never change `x`. The four omitted low target bits
are spectators because every target rotation is a multiple of `2^rho`;
selected-bit extraction and the guard predicate also ignore them. No other
rotation or swap changes these bits. The unused earlier-source `u` is a
spectator. Hence the omitted factors are respectively

```
earlier: 2^12 * 2^4 * 2^2 = 2^18,
later:   2^12 * 2^4       = 2^16.
```

The representative address-map checks lift by these independent spectator
translations to `2^36` physical addresses in each of these two particular
rectangles. This is a structural lifting argument, not a claim to have
individually enumerated `2^36` states or to cover all parameter values.

The represented highest target bit must be retained: bad-address carries may
reach it even though the intended gadget omits its XOR. For hole-filling
checks, fixing `x` and `b` is safe because both maps preserve these entire
fields on all addresses. Partitioning by `t` would be unsafe: bad-address
executions can change it. A quotient key sort establishes a finite address
permutation and payload correspondence, not the time or tape cost of a
physical stream implementation.

Finally, this binary compact radix has only `t_i=0` as an unsaturated digit.
It cannot witness failure caused by deleting only the target guard. A
separate `G=2` negative control is needed to exhibit that dependency.
