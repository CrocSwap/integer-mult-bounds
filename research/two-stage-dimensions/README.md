# Two-stage dimensions (47,45)

The conditional final exponent saving is **κ = 16038/10^9 = 1.6038e-5**,
with bit saving `16039/10^9`. This reuses PR29's construction at smaller
factor dimensions. Its basis, full physical accounting, paid correction,
complex circuit and semantic/bulk dependencies remain explicit.

The [proof](../../notes/two-stage-47-45-note.tex) establishes the dimension
substitution. The exact certificate checks the new producers' complete
records, rank mass, three common-basis modular witnesses and their rational
nonvanishing interpretation, 47 strict conditions and seven margins.
The bit moment gap exceeds `2.3e-10`; the final gap exceeds `4.8e-10`.
The product row stock remains `p^47000`.

```sh
make two-stage-dimensions-producer
make two-stage-dimensions-check
make verify
```

The producer rebuilds both changed scalar DAGs, matchings, histograms and
exact integer label audits in temporary storage, comparing complete records.
The verifier replays the generalized assembly at the old parameters and
checks equality with PR29's formula. Negative controls reject the next final
grid point, old guard, old separate exposures and unbatched local calls;
the next bit grid point fails the chosen sufficient enclosure. This last
failure is not an impossibility proof for the true moment.

`patches/two-stage-dimensions.patch` replaces the pinned PR29 manuscript with
the new standalone proof when applied externally. Historical source files
are preserved in this branch. The exact certificate records new source and
producer hashes; all of PR29's SOURCE.json pins are checked. No PDF is
created. This remains conditional mathematical research, not formal
verification or a practical runtime claim.

The comparison base is PR29 `9d963275075fa98f1da821e27757b238dafd6b3c`.
The candidate exceeds PR31's `1.5878574e-5`, which uses additional data-corner
blocks; this contribution uses PR29's original singleton data corner.

Dominik Scholz contributes the dimension search and integration, with
substantial Anthropic Claude Opus 5.5, OpenAI GPT-6 Astra and Codex assistance.
Credit Zhihao Chen (jacklightChen) for PR29 and PR21/23; Aurel Prosz (Paureel)
for the two-stage topology and paid correction; Swapnil Jain for its linked
development; icekylinx for PR24's producers and controlled basis;
RaD/hipotures for semantic/bulk transfers; Rohan Arun for concurrent
geometric improvements; eumemic and every earlier author retained in NOTICE.
Their constructions are not claimed as new. Apache-2.0 is unchanged.
