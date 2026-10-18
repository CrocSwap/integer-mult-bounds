# A denominator barrier for positive Gram port decoders

**Scoped proof and finite negative result; no new κ.** Positive half-integral
weights with integral Gram factors cannot save full port-space cost. Quarter
weights and signed weights genuinely escape that theorem. On the actual 23
induced C5s of PR1825's paired-plane matching, the specified quarter-integral
E8 menu nevertheless has minimum cost **20**, exactly the direct baseline.

This stops this particular expansion into a supplier. It does not establish a
barrier for arbitrary rational decoders, other matchings or changed physical
interfaces. The selected frontier remains unchanged.

## Written theorem

Normalize the strict scalar endpoint to diagonal one. Let every port carry a
nondegenerate binary space E_i of dimension d_i. A rank-one Gram term costs the
binary pairing rank of the sum of its **complete port spaces** against itself.
For any finite number of terms, positive weights in `(1/2) Z`, and integral
factor entries,

    total cost >= sum_i d_i.

[PROOF.md](PROOF.md) gives the argument for arbitrary term counts, supports and
port dimensions. The diagonal equation forces either one unit-weight occurrence
or two half-weight occurrences per row. The latter form edges of a graph on
columns; orthogonality of distinct incident edge bundles makes their ranks add.
The two sign classes on each edge give the required lower bound.

Under the retained favorable s-stage coverage law, the available deficit is
proportional to `(s-1)/s * sum_i d_i - cost`, hence is strictly negative in this
class even before further costs. This inference is conditional on that coverage
law; it is not a universal lower bound for multiplication.

The restrictions are material. Exact generated E8 controls have 120 line ports
and binary quotient dimension nine:

| Integral-coordinate representation | Weights | Cost |
|---|---|---:|
| Positive scaled E8 chart | eight `+1/4` | 72 |
| Lorentzian E8 chart | eight `+1/2`, one `-1/2` | 81 |

Both fit their strict scalar masks. These are algebraic controls using known E8
geometry, not new suppliers or new κ. They show that quarter is the first
positive dyadic weight scale permitting a saving in this integral-coordinate
model, and that removing positivity also changes the answer.

## Complete finite experiment

PR2484's core `(13,23,35,16,34)` motivated the experiment. We then enumerated
**all 23 induced C5s** in the same 56-plane matching; two different cycle censuses
agree. Each has ten scalar ports. The finite decoder menu is eight coordinate
Gram terms with coefficient 1/4, with each row chosen from these 120 unoriented
norm-four integral E8 roots:

- eight vectors `2 e_i`;
- the 112 signed weight-four vectors supported on affine hyperplanes of F2^3,
  identified up to whole-row sign.

Every nonorthogonal-plane cross entry must vanish; both ports of the same plane
remain independent. The cost uses all dimensions of every touched plane.
There are 16 distinct tariff tables up to cycle rotations and reversal. Exact
integer backtracking exhausts both first-root symmetry classes at cost at most
19 for every table. Each cycle has an explicit five-axis cost-20 witness. Thus
**20 is the minimum inside this finite menu**, not the minimum among all
rational decoders.

The search proof, symmetry justification and stopping rule are in
[SEARCH.md](SEARCH.md). [RESULT.json](RESULT.json) records every cycle, its
class, exact tariff table, anchor and completed node/prune counts. A separately
written C++ implementation derives adjacency from the physical labels and
checks all 46 cycle/anchor cases, without the class reduction. OR-Tools 9.14
also reported infeasibility on the original core, but is not a replay dependency
or the basis of the certificate.

The initial signed half-weight, support-at-most-four MILP ran for 120 seconds,
found cost 20, and retained lower bound 13. That run was **inconclusive**. It is
not included in the completed exclusion. The evidence-driven pivot was to the
quarter-integral E8 menu, with an exact exhaustive implementation.

## Reproduce

Python 3.12, standard library only, typically about one minute:

```sh
python3.12 -I -B research/c5-dyadic-decoder-gate/verify.py
```

Expected: `PASS_C5_DYADIC_DECODER_GATE`, 23 cycles, minimum 20, E8 controls 72/81,
and `no_new_kappa`. Default replay is read-only. The optional independent check
requires g++ with C++20 support:

```sh
python3.12 -I -B research/c5-dyadic-decoder-gate/independent.py
```

It prints `PASS_INDEPENDENT_C5_SEARCH ... minimum=20`. This is exact finite
search corroboration and a written proof, not proof-assistant verification.

## Sources, scope and credit

Scientific base: `31452ecd309f32a97e2e84214719b21297a59018`, priority revision 5, seed **24**.
Pre-submission canonical main: `6ca6f217708b075814de409ad693fea9a2aaa760`;
guidance, selected record and the consumed frozen inputs are unchanged.
The selected #1094 certificate and all 1,579 manifest inputs were authenticated;
its actual construction/review were followed. The reviewed κ was
`0.001672660197076918`; the pending #2766/#2767 claims were approximately
`0.001717256973467002`. No pending claim was treated as admitted.

The small `inputs/` directory preserves the exact PR1825 matching and compressed
bytes of the selected archive's DATA-PHASES member. Authentication checks the
uncompressed original SHA256 before parsing. [SOURCES.json](SOURCES.json) binds
provenance, archive/member identities, source heads and attribution.

Credit Cinna Davis (PR1825/2126), Adam Gall (PR1889 strict mask), ywz65 (PR2471),
Sagar Thakrar (PR2484 C5 core/minrank), Jeremy Diviney (PR2203 full payload bill),
Philippe Van Velzen (full-space tariff, 2-integral and coverage-law work), and
flyingviper (PR2757's different triad-mask rational floors). The selected E8
geometry, compiler and supplier lineage retain their credit. This theorem is
about positive half-integral **Gram** factors; it neither repeats nor extends
Philippe's all-decoder 2-integral theorem without those additional hypotheses.

New proof, searches and checks: Tekalign (`tekuuu`), with substantial OpenAI Codex
assistance. No independent human review is claimed. Apache-2.0; upstream and
frozen predecessor packages are unchanged.

## Open next questions

1. Can signed half-weight or asymmetric factors beat 20 on these physical C5s?
   The theorem excludes neither. Start with one exact full-cost identity and
   retain every cancellation term; the earlier MILP is unresolved.
2. Can a different quarter-integral menu or changed matching improve the cost?
   This census closes only the specified 120-root menu on this matching.
3. A favorable scalar fit would still need the complete native gather/copy/
   scatter/restoration, hosting, precision and other-supplier budget. None is
   supplied here; the failed gate justifies stopping before that expansion.
