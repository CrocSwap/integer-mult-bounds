# Balanced split frames with shared sums and reusable live controls

**κ = 10366199626713 / 200000000000000000 = 0.000051830998133565**

The conditional bound is `T(n) = O(n (log n)^(1-kappa))`.
This is **0.9788258% above our original PR #74 result**, **0.8097927% above
pinned PR #71**, and **0.8082664% above PR #75's claim observed on 8 October
2026**. The later PR #79 claim `5.1745625472866e-5`, observed at 19:55 UTC on the same
date, is also below this result by **0.1649853%**. These compare asymptotic exponent savings; they are not measured
multiplication speedups.

| Quantity | Original PR #74 | Pinned PR #71 | This composition |
| --- | ---: | ---: | ---: |
| h23 auxiliary roles | 27,698 | 27,455 | 27,136 |
| h25 auxiliary roles | 36,310 | 36,015 | 35,744 |
| Physical width | 136,157,010 | 135,075,665 | 133,862,024 |
| Conditional κ | 5.132858076595e-5 | 5.1414646104039e-5 | 5.1830998133565e-5 |

## Construction

Compose eumemic's PR #69 column-balanced coarse sums with Chafik Boukhalfa's
PR #71 anchored split recursion and next-use-aware live reclamation. Apply
our original-envelope node order before carrier matching, then relabel the
geometric coordinates and recompute the actual fixed-basis profiles.

The balanced graph has 67,460 / 94,993 active additions, compared with
PR #71's 68,771 / 96,718. Every prescribed output is unchanged. The complete
physical words pay for all XORs, frame raises, copied centers and data blocks.
The width now lies below `2^27`; its role-logarithm and product-row constants
are recomputed in the exact certificate.

## Evidence and reproduction

- [Proof, scope and contributor credits](PROOF.md)
- [Exact certificate](certificate.json)
- [Selected graph and coordinate choices](selection.json)
- [Immutable source manifest](SOURCE.json)
- [Independent dense scalar audit](graph-audit.json)
- [Independent exact arithmetic audit](independent-audit.json)
- [Verification receipt](validation.json) and [raw log](verification.log)

Use Python 3.11 or newer and a C++17 compiler with unsigned 128-bit support:

```sh
make balanced-split-frames-verify
```

This regenerates both words from pinned sources, checks their selected raw
hashes, audits the complete scalar graph, independently replays every input
and dirty basis vector in both orientations, reconstructs every literal frame
transition and exact profile, and checks the full paid recurrence and assembly.
The two replay dimensions contain 30,678 / 40,344 basis coordinates.
Both profiles have zero CRT disagreements. Independent arithmetic verifies
all 47 strict inequalities, seven margins, adjacent-grid rejection, and
exclusion of the complete pinned PR #71 profile at the new bit saving.

The earlier full-suite receipt in `../ordered-frames/validation.json` covers
that historical source state. Current upstream checks and formal packages
remain separate CI jobs. The new source archives retain original notices
and original root documentation so predecessor pins remain unchanged.

All inherited analytic, all-size compiler, fixed-tape, precision, routing,
prime-selection and recovery hypotheses remain assumed. This is a verified
finite conditional witness, with no global-optimality or practical-speed claim.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance. Original
PR #74 remains available in `../ordered-frames/`; all predecessor credits and
licenses remain applicable.

Concurrent PR #75–#79 work is acknowledged; no priority claim is made.
