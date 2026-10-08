# Envelope-ordered carry exchanges on anchored split frames

The selected finite conditional witness gives

    kappa = 51738676045141 / 10^18
    bit saving = 25870676537201 / (5*10^17).

It is 0.6287052980% above PR75's reported conditional saving
257077122735047/(5*10^18). The exact publication-policy comparison is

    kappa - (201/200)*kappa_PR75 = 66174375396553/10^21 > 0.

This comparison concerns complete conditional exponents; it is not a
comparison of role counts or uncharged scalar-graph scores. PR75's
different nonlinear provider-circuit method is not incorporated here.

## Construction and inherited dependencies

Start with Chafik Boukhalfa's PR71 at
`1bef94fd40a746452548c84a4a8f8834670a3113`: anchored split vector `[1,1,2]`,
the cover-core schedule for h23, reverse-node for h25, actual profile-cost
slot selection, pending live controls and next-use pricing.

Apply the scalar-node reorder from Thomas DiFiore's PR74 at
`9ee3e9e1d451cd62e7d55a3c66e0280304dcb653`. Source input IDs remain fixed;
non-source nodes are grouped by their original envelope and ordered by
`(union.bit_count()-core.bit_count(), -core, union, first_node)`, preserving
the within-envelope node order. Every argument and output ID is mapped
through the same bijection; envelopes and provenance are carried along.
The complete scalar verifier is rerun. Thus the addition DAG is relabeled
without changing its linear forms or envelope containments.

The relabeling changes the compiler's region/edge enumeration and output
basis choices, as well as the meaning of h25's reverse-node tie order.
The existing scheduler rechecks every scalar dependency and eligible
carrier for forward orientation. The selected maximum-cardinality carry
matching is then improved by the preserved three-pass, strictly improving
single-edge exchange procedure, derived from Alejandro Zarzuelo Urdiales's
PR70 carried-signal exchanges. The discovery score uses exact integer
midpoint logarithm weights and actual fixed-basis profile entropies.
Each exchange preserves matching cardinality, eligible edges, unique uses
and independence of desired-output rows plus retained input unit rows.
This score is a search heuristic, not the recursive cost certificate.

Finally, the unchanged PR71 engine emits literal XOR operations, with
the inherited dirty wrapper M,J,M^-1,V,M,J,M^-1,V. Complete input/dirty
basis execution in both orientations passes during both compilations.
No dirty role is assumed initially zero. Reclamation still uses explicit
linear dependence witnesses and pays all frame raises of targets and
controls, including pending controls. All copied centers, endpoints,
data geometry and the complex layer remain charged.

## Complete profile and arithmetic

The selected roles are R23=27256 and R25=35720. For N=4073300,

    W = 2N + 2300*R23 + 1771*R25 = 134095520.
    total recursive rank = 575*W - 1846900 = 77103077100.

The complete literal transition profiles have zero CRT disagreements.
The exact directed moment accepts the reported bit saving and rejects
the adjacent larger point at denominator 10^18. Assembly uses the existing
backoff h=1/10^12, preserves all 47 strict inequalities and seven margins,
and rejects the adjacent kappa grid point. Eventual arithmetic cutoffs
are included in the certificate.

Width has crossed below 2^27. The bridge therefore recomputes
`wire_bits=W.bit_length()=27`, product-row coefficient `9*27+20*30=843`,
and degree gap `2000-(51/25)*843=7007/25`. Degree 2000 and suffix slope
8000 remain unchanged. The semantic complex-layer constants are unchanged
and revalidated. The first screen correctly rejected a stale value 28;
that failure log is preserved. `width_bridge.py` derives these fields from
the actual width; it does not suppress bridge validation.

`selected-both/MANIFEST.json` pins all selected runtime/artifact sources
and the exact inherited baseline closure. Independent serialized replay,
an independent rational moment enclosure, and fresh profile regeneration
are run by `validate_selected.py`; its separate receipt states their status.
Until that receipt exists these checks are pending. Broad repository tests
and a fresh portable deterministic recompilation remain pending at freeze.

This is a finite conditional witness. All inherited ordered affine
residual compiler, all-size recurrence, scalar overhead, routing, prime
selection, recovery, fixed-tape, precision and analytic-transfer obligations
remain hypotheses. No global optimum, unconditional multiplication theorem
or practical runtime improvement is claimed.

## Attribution and reproduction

Thomas DiFiore's PR74 supplies the envelope-node ordering; Chafik
Boukhalfa's PR71 supplies the selected split/alignment and next-use score;
Alejandro Zarzuelo Urdiales's PR70 supplies the exchange method; Rohan
Arun's PR65/67 supply schedules, exact arithmetic and profile-cost selection;
Dominik Scholz's PR68 supplies pending live controls. Avi Eisenberg's
PR62 graph, eumemic's PR57 reversible compiler, Chafik's PR60 ranked
reclamation, and the complete inherited author chain retain credit.
This composition and its width-bridge derivation were prepared for Dominik
Scholz with substantial OpenAI GPT-6 Astra assistance. All Apache-2.0 and
source-specific notices remain in force.

From this directory (with the exact PR71 archive at
`../round6-pr71/baseline`), run these sequentially into a fresh directory:

```sh
python3 run.py --h 23 --work-dir /tmp/ordered-exchange-23
python3 run.py --h 25 --work-dir /tmp/ordered-exchange-25
python3 screen_width.py --h 23 --work-dir /tmp/ordered-exchange-23
python3 screen_width.py --h 25 --work-dir /tmp/ordered-exchange-25 --other-profile /tmp/ordered-exchange-23/profile-23.json
python3 validate_selected.py --bundle selected-both --output validation-receipt.json
```

Use assert-enabled Python and C++17. This machine requires the process-local
compiler override
`CXX='c++ -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk'`.
The original archived compiler bytes are not edited. The first screen of
h23 alone includes baseline h25 solely to generate its actual profile;
the final h25 screen composes both fresh profiles.
