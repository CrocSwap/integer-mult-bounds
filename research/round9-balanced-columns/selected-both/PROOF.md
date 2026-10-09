# Balanced columns composed with envelope ordering and carry exchanges

The selected finite witness has

    kappa = 51915547765237 / 10^18
    bit saving = 3244890195589 / 62500000000000000
    roles = 27128 / 35598, W = 133585058
    total recursive rank = 76809561450, deficit = 1846900.

Against PR #74 at `5830ccfca8466aff613767222558e29b57fa8225`, whose
reported conditional exponent is `10366199626713/200000000000000000`,
the exact gain is `10568703959/125000000000000000`, or approximately 0.163125609609%.
Against PR #76 the gain is `5527241253/31250000000000000`, or
0.3418559067%. These are comparisons of specific conditional claims, not
a proof of global optimality.

## Exact graph change

The PR69/77 balanced-column identity replaces each coarse total over two
groups A and B by

    sum_{b in B} (sum_{a in A} e(a,b)).

Every summand still appears once, and each addition has disjoint support.
Support interning may reuse the column sums in interval strips. The exact
adapter is imported from huxint's PR77 at
`83298467291d3bd4b53f76faaef60dbf585be171`; its underlying PR62 pair graph
is byte-identical to the graph preserved in our PR71/PR65 closure.
The `[1,1,2]` split vector and lowest-intact-pair anchor stay fixed.

The graph then uses PR74 envelope-node renumbering, PR65's cover-core h23
and reverse-node h25 schedules, and the three-pass PR70 carry-exchange
composition frozen in PR76. The PR77 cost-ordered clearing compiler is
not imported. The PR71 engine, frame-containment rules, next-use score,
dirty wrapper and every literal charge remain inherited and unmodified.
Every schedule dependency and eligible carrier is checked forward; every
carry exchange preserves cardinality, unique uses and basis independence.

PR77's graph adapter verifies before returning, populating a node-ID
support cache. Renumbering invalidates those cache keys. The local reorder
therefore explicitly clears `support_in` memoization after applying the
node bijection and before verifying again. The initial stale-cache failure
is preserved in `cache-stale-failure.log`. No assertion is disabled.

`dense_audit.py` separately evaluates all active scalar additions over
dense global input bitsets without using the memoized/provenance support
routine. All additions are disjoint, every partial output equals its
specified global support, and the common-point envelopes are exact for
both axes. This preserves the original scalar/data-output interface and
I+J geometry; it does not assume a cheaper data layer.

## Physical and arithmetic evidence

Both compiler words pass complete input/dirty basis execution in both
orientations. Actual fixed-I+J profiles have zero CRT disagreements. The
full paid child list includes all promotions, clearing controls, endpoint
copies, data growth and the inherited complex branch. The exact moment
accepts the stated bit saving and rejects the next denominator-10^18 grid
point. All 47 strict assembly inequalities and seven margins pass, with
the original h=1/10^12 backoff. Width-derived bridge fields are recomputed
by the preserved round7 helper: bit wire logarithm 27, product-row
coefficient 843, degree 2000 and degree gap 7007/25.

The manifest freezes the selected artifacts and exact source closure.
Independent serialized replay, profile regeneration and the independent
rational moment check are recorded in the completed separate validation receipt. The receipt binds the original
freeze manifest preserved under `provenance`; only proof/comparison metadata
changed in this package, with every runtime and physical artifact unchanged. Broad repository checks
and portable deterministic regeneration are not claimed here.

All inherited all-size compiler, fixed finite-alphabet tape, analytic and
semantic reduction, routing, precision, prime setup and exact recovery
obligations remain conditional. Arithmetic cutoffs are not practical
runtime thresholds or a proof of the complete multiplication theorem.

## Reproduction and credit

From this directory with the exact PR71 archive at
`../round6-pr71/baseline`, execute sequentially:

```sh
python3 run.py --h 23 --work-dir /tmp/columns23
python3 run.py --h 25 --work-dir /tmp/columns25
python3 screen_width.py --h 23 --work-dir /tmp/columns23
python3 screen_width.py --h 25 --work-dir /tmp/columns25 --other-profile /tmp/columns23/profile-23.json
python3 dense_audit.py
python3 validate_selected.py --bundle selected-both --output validation-receipt.json
```

Use assert-enabled Python and C++17. This machine needs
`CXX='c++ -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk'`.

Credit eumemic PR69 for balanced coarse columns; huxint PR77 for the
anchored balanced-column adapter; Thomas DiFiore PR74 for envelope ordering;
Chafik Boukhalfa PR71 for anchored splits and next-use scoring; Alejandro
Zarzuelo Urdiales PR70 for exchanges; Rohan Arun PR65/67 for schedules,
profile costs and arithmetic; Dominik Scholz PR68/76 for pending controls
and the prior composition; Avi Eisenberg PR62, eumemic PR57 and the full
retained author chain. This further composition was prepared for Dominik
Scholz with substantial OpenAI GPT-6 Astra assistance. Apache-2.0 and all
inherited notices remain. No CI or repository integration changes are included.
