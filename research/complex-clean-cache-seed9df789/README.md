# Clean-cache channel cost: exact two-port obstruction

**Scoped negative result.** A clean scratch array that caches one read-only
source contribution across exactly two outputs cannot reduce the fully charged
source/scratch/output transport bill. The scratch load and exact restore are
both charged. The result screens one route only; it is not an obstruction for
all nine-array programs and it claims no new supplier or `kappa`.

See [the proof](PROOF.md) for the all-exponent dimension argument and limits.

## Verification

From the repository root, run:

```sh
python3 -I -B research/complex-clean-cache-seed9df789/verify.py
python3 scripts/research_package.py --package research/complex-clean-cache-seed9df789 --check-only
python3.12 scripts/research_package.py --package research/complex-clean-cache-seed9df789
```

Expected mathematical marker:

```text
PASS_TWO_PORT_CLEAN_CACHE ranks=1..64 triples=220480 alt_s_triples=220480 positive_control=3_outputs s=9983/10000 direct2=[25.886876,25.886876] cache2=[27.907043,27.907043] direct3=[38.830314,38.830314] cache3=[35.878812,35.878812] omitted_restore_rejected
```

The finite rank census is an implementation check, not the proof of the
all-dimension inequality. The selected record at the exact base remains
`kappa = 836330098538459/500000000000000000` (decimal `0.001672660197076918`).
Local interpreter availability was Python 3.14.7; the registered Python 3.12
runner was unavailable on this host at the initial handoff.

## Scope and provenance

Task `complex-new-helper-inventory`, seed
`9df78911476a397cf5f04ebb271934af`, priority revision 3, scope key
`5868e5281a1e63d41a22`; base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
`SOURCES.json` pins the selected record and its review, source manifest,
certificate and reproduction instructions, the relevant fixed-block theorem,
the original task catalogue, and the exact interval implementation.

Related but distinct work includes PR #1517 (fixed-inventory cross-block
mixing), PR #1348 (coverage-law threshold relaxation), PR #1605 (rank-one
reblocking), and PR #1633 (overcomplete E8 decoder ranks). The exact latest
open-PR and discussion snapshot and its discussion-rate-limit warning are
recorded in [the local claim](CLAIM.md).

Prepared by Cinna Davis with substantial OpenAI Codex assistance in the
mathematical derivation, exact interval verification, source pinning, and
writing. No independent human review is claimed. Apache-2.0.

## Open next questions

1. **Can a multi-source cache or coded scratch amortize the restore while
   retaining exact helper endpoints?** This escapes the one-source inequality
   and could change a full supplier cost. First write a complete load/use/
   restore frame ledger for two sources and two outputs, then screen the full
   charged channel bill. Blocker: no compatible multi-source endpoint contract
   has been supplied.
2. **Can three-port cache savings be embedded into the selected block's actual
   output support?** The control shows the two-port bound cannot cover that
   interface. First identify a source whose contribution reaches three ports
   in a changed supplier, then include helper supply and restoration. Blocker:
   the pinned fixed-block theorem gives two output ports per input column.
