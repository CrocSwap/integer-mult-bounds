# admission-constant-derivation

**No new κ.** Derives the ordinary BIT admission constants of
`research/query-thinned-controllers` (reused unchanged by #4470,
`research/joint-helper-lattice`) and the controller rank-surplus identity that
`controller.py` checks as a hard-coded literal.

## 1. atom, ordinary, admitted

`query-thinned-controllers/verify.py` fixes C0 = 0.003459 (BIT uniform saving
after tail strictification), C1 = 0.00345 (after delayed cover, with
C0 − C1 > 256/2^26 for the prime rule), a_old = 0.0000384599 and

    ordinary(δ) = (1 − δ)·C1 + δ·a_old,
    admission:  ordinary(δ) < δ < 1 − ordinary(δ),

where δ is the atom power (the linear adapter on width-e^δ atoms saves δ and
must beat the ordinary saving; δ < 1 − ordinary keeps the stock sublinear).
Since ordinary is decreasing in δ, the admissible atoms are exactly the open
interval

    ( C1/(1 + C1 − a_old), (1 − C1)/(1 − C1 + a_old) ) = (0.0034382702…, 0.9999614…).

So **ordinary** is a formula, not a literal, and **atom** is a free parameter
inside this interval: 0.004 is one admissible rounding (ordinary
0.0034363538396), and the old 0.003 lies below the interval, which is the
"old atom rejected" check. The supremum of the ordinary saving over all
admissible atoms is the left endpoint 0.0034382702. **admitted** = 0.0034 is a
rounding below it (relative loss 1.1%). Saturating the 2^26 prime allowance
(C1 = C0 − 256/2^26) would raise the supremum only to 0.0034434.

**κ effect: none.** #4470 needs only admitted > its complex tested saving
0.003020155; the complex side binds. These constants matter only after the
complex side exceeds about 0.0034, and then they are worth at most about +1.3%.

## 2. The surplus identity `48*|thick| - 112` (complex) / `- 111` (BIT)

With P ports of block width b, |thick| = p + 2 thick stages, per-stage helper
target mass H and paid child mass C, the literal counting of
`controller.inventories` gives, for every p and every prefix length a,

    surplus = (p + 2)·(H − C + Σ_ports (2·b_port + 1)) − P.

Proof: helpers and children contribute (p + 2)(H − C). Each prefix/suffix
level j adds a main output of rank 1 + b(j + 1) and an idle call of rank
b(j + 1), net +1 on each of 2 sides of a port, for p − 1 levels in total
(independent of a). The full main output adds 2(1 + b(p + 2)) per port and the
thin queries subtract 2p + 1 − (p + 2) = p − 1 per port. Summing,
2b(p + 2) + 2 + 2(p − 1) − (p − 1) = (p + 2)(2b + 1) − 1 per port.

Both sides have the same local balance s_loc = H − C + (2b + 1)P = 48:
complex 3301 − 5157 + 17·112, BIT 3512 − 5129 + 15·111. The "48" is
therefore this balance, not a property of width 8, and mixed widths only
replace (2b + 1)P by the per-port sum. The verifier replays the literal
counting for p = 2…40 and all a on both sides, matches both committed
controller invoices (complex p = 17: 800, BIT p = 16: 753) and 200 random
mixed-width instances.

## Reproduce

```sh
python3 scripts/research_package.py --package research/admission-constant-derivation --check-only
python3.12 scripts/research_package.py --package research/admission-constant-derivation
```

Runs in a few seconds with the standard library only.

## Open next questions

How far C0 and C1 can move toward the BIT root 0.00346 (see TASK.json). This
is low priority while the complex side binds.

## Credit

Prepared by Mark (Matarener). The constants, controllers and invoices are from
the query-thinned-controllers and joint-helper-lattice packages (#4440, #4470)
and their sources. New work is Apache-2.0. Prepared with substantial Claude Code
assistance.
