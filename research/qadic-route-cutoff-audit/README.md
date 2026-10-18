# Exact route width after binary/radix conversion

**Conditional interface audit; no new κ or stock coefficient.** For the
fixed-header BIT routes of Jose Manuel's [PR2157](https://github.com/CrocSwap/integer-mult-bounds/pull/2157),
an ordinary call padded from a radix-q high field and converted back to radix q
has **exactly the original atom width w**, not a larger unspecified multiple.
The combined padding calls the previous ordinary routine on **q²V** symbols.
This supplies the width connection requested in [PR2972](https://github.com/CrocSwap/integer-mult-bounds/pull/2972)'s
first open question for this particular route reduction. It does not supply
the completed ordinary routine or its reserve.

Scientific base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The selected conditional value remains κ = 0.001672660197076918 (#1094).
[SOURCES.json](SOURCES.json) pins the exact route code, its proof, the retained
binary/radix conversion and the inherited stock receipt. Predecessor packages
are unchanged.

## Statement and proof

Fix an odd integer q ≥ 3 (in the supplier, an eligible fixed odd prime), an
integer atom width w ≥ 2 and arbitrary complete prefix, intervening and suffix
coordinates. Let Q = q^(w−1) be the range of each high field. The actual
`completed_swap_oracle` in PR2157 computes

```
u = (Q-1).bit_length() = ceil(log2 Q),     P = 2^u.
```

For b = ceil(log2 q),

```
w <= u <= b(w-1).
```

Indeed Q > 2^(w−1), whereas Q ≤ 2^(b(w−1)). Thus binary width and radix-q
width are different units. There is no q-independent bound u ≤ Cw for all
eligible primes q: already at w=2, u=ceil(log2 q), and primes are unbounded.
For a concrete control, q=257,w=4 gives u=25, not 4. This does not refute
PR2157, whose constants explicitly depend on fixed q.

Now discharge the **binary** ordinary call using a completed **radix-q**
ordinary routine and the retained conversion in
`five-stage-source527-banks/proof/three-stage-cover-rows.tex`, subsection
“Uniform saving and return to binary addresses”. It pads each binary field
of range P to radix-q width t = ceil(log_q P).

Because Q is odd and greater than one, it is not a power of two. Consequently

```
q^(w-1) = Q < P < 2Q < qQ = q^w,
```

so **t = w exactly**. This holds at every width, independently of any cutoff.
The width is also the least possible for a complete radix-q field containing
P. Using t=w−1 discards actual binary addresses. The hypothesis matters:
q=4,w=2 gives Q=P=4 and t=1.

To check completion, pad the two Q-fields to P-fields, then pad the two
P-fields to q^w-fields. Keep the prefix, middle and suffix coordinates in
order. Apply the completed radix-q ordinary interchange, then remove the two
padding layers in reverse order. Both genuine rectangles are invariant under
interchange. Zero dummy records remain zero, and the resulting genuine
packet is the exact interchange, with all spectators preserved pointwise.
This uses a **completed ordinary endpoint**, not a raw reversed call.

If V is the original complete Q-by-Q packet volume, the inner call volume is

```
V * (P/Q)^2 * (q^w/P)^2 = q²V.
```

This is an exact called-volume identity; it is not a total tape-space bound.
Both padding layers have sequential implementations and cost O_q(V) for fixed
q. If the completed radix-q callee costs at most C V' t^(1−a) on its supplied
volume V', the composed call costs at most
`C q² V w^(1−a) + K_q V`. Its internal borrowing, cleanup, physical workspace
and all-width uniform contract remain inherited obligations. There is no free
padding or ordinary primitive in this bill. PR2157's fixed call multiplicity
is unchanged: one ordinary call for a column-field swap, two for a reversed
source/target addition, and none for an ordered addition. At w=1 the high
range is one and the source emits **no** such ordinary call.

## Connection to the stopped stages

Use either recorded branch of the source-bound PR1990 receipt. For j=2,…,7,
PR2972 already establishes `s L_j − L_(j−1) ≥ 1`. Given e ≥ 2^L_j and
w=ceil(e^s), the converted radix-q callee has

```
t = w >= e^s >= 2^(s L_j) > 2^L_(j-1).
```

Thus these fixed-header routing calls land inside the previous stopped range,
when that range is measured in radix-q digits. If the previous routine instead
has binary-width cutoffs, the separately proved u ≥ w gives the same lower
membership implication in binary digits. These are alternative interface
readings, not an identification of their units or cutoff constants.

For the radix-q reading the handoff's proposed upper factor is **c_R=1**;
`log2(c_R)=0` satisfies all twelve inherited positive routing rooms. No bound
on log q is needed for this width statement. Its q² volume constant still
depends on q. The twelve margins and rooms in [EXPECTED.json](EXPECTED.json)
are inherited comparisons, not new cutoff mathematics. The new result is the
source-bound conversion and its completed padding/cost argument.

This does not establish H1, H2, H3, a selected stock coefficient, the complex
m=73 producer, weighted-leaf routing, a data-dependent all-size compiler or
formal verification of multiplication. In particular it does not certify
that a proposed previous-stage implementation satisfies the completed
spectator/row-return contract. No selected construction failure was found.

## Reproduce and evidence

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/qadic-route-cutoff-audit
```

Expected: `PASS_QADIC_ROUTE_CUTOFF_AUDIT packets=48 roundtrips=4 cutoff_pairs=12 controls=8 stock=unresolved`,
five passing boundary tests and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The replay authenticates predecessor bytes **before** compiling them; it
does not load their bytecode caches. A separate forward-scatter address oracle
checks actual predecessor swaps and both source orders of a −1/2 ADD on 16
(q,w) pairs: q=3,w=1…4; q=5,7,w=1…3; q=11,17,31,w=1…2. Every packet contains
complete prefix/middle fields and a distinct binary payload record for every
coordinate tuple. It checks all output bits, ordinary-call widths, multiplicity
and complete padded-volume invoices. These small-q fixtures are outside the
selected supplier's q>2^80 admission domain; the written arithmetic/padding
lemma, rather than finite enumeration, covers that domain. Four complete, gapped
two-layer roundtrips cover (3,2), (3,3), (5,2), (7,2). The innermost ordinary
endpoint there is an explicit dense oracle, not a physical callee.

Eight controls catch omitted carry, floor padding, omitted source-order swaps,
an undercharged width, three false width/factor claims and a truncated radix
return. Five tests additionally challenge source corruption, a silently
introduced stock coefficient, a failed cutoff premise, an excluded radix and
a nonzero dummy rectangle. The exact full receipt is compared, and checks
remain active with optimized Python. These finite replays support the written
width/padding proof; they do not prove all-size supplier realization.

The bounded experiment is exhaustive only over the stated 48 packets and four
roundtrips. Seed 73 assigned the adversarial-audit track; no randomized search
was run. The stop rule was this one interface, 16 small parameter pairs and
the twelve inherited cutoff pairs. [TASK.json](TASK.json) records the three
candidate tasks, local claim and overlap coverage.

## Open next questions

1. **Can a reached previous-stage ordinary routine discharge this completed
   call?** Bind one actual route invocation to a supplied callee with complete
   spectator/row restoration and a uniform tariff. The missing callee/kernel
   and reserve implementation block adoption; the width lemma alone cannot.
2. **Do the other ordinary sites obey comparably explicit width/volume bills?**
   Start with one weighted-leaf or high-part-exchange site, retaining its own
   input units and completed contract. Those sites and the data-dependent
   all-size lowering are outside the fixed-header source audited here.

## Credit

Jose Manuel (@jmbarrancoml), PR2157 at
`eb1bf93950e9b14f7fadca7892866e9f29a26ad3`, supplied the route reduction,
carry-aware stream code and oracle-bound fixed-header proof. Its generic
ordered-affine method, Nick Petalas's PR2140 carry work, DaysSky's PR442
hosting theorem and the DreamingOfClouds/eumemic selected BIT lineage retain
their existing credit. The inherited ordinary binary/radix embedding and
completed-row mechanism come from the retained cover/PR185/PR387 lineage,
including Rohan Arun. Hiroki KUMAZAKI (@kumagi), PR2972 at
`d6b883f97d2fd176171553b695005a132156d961`, supplied the cutoff pairs and
width handoff, following Philippe Van Velzen and Riquelme Soares's stage-2/3
work. ToikY's PR1990 at `c3bd90d9a8d9202c063700ae443e83825780e056`
supplied the receipt on Josie Elliston's PR1956/PR1965 stock-fit work.

New contribution: the exact conversion-width and combined-volume argument,
its scoped connection to that handoff and the independent packet checks.
Prepared for Sricharan Vagvala (@theon199) with substantial OpenAI Codex
assistance. No independent human review or proof-assistant result is claimed.
Apache-2.0; predecessor notices remain in their original packages.
