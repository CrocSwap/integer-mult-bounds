# Arbitrary helper terminal frames retain the selected k8 ceiling

**Scoped obstruction; no new kappa.** Allowing every terminal subspace for
all 78 originally restricted helpers, jointly with all 5,413 gate frames,
still gives the favorable primitive ceiling

    0.001690198050302 < best ceiling < 0.001690198050303.

The upper planning bound is
`kappa < 1690198050303/1001690198050303`, approximately 0.001687346101213.
The ceiling gain over the fixed-end word is less than **0.00852%**, excluding
the declared 5% target. The full construction's exponent is unchanged.

[PR1995](https://github.com/CrocSwap/integer-mult-bounds/pull/1995) permitted
only nested contractions inside each original end. This package removes
that cap: ends may rotate, enlarge or become FULL, subject only to containing
the fixed entrance and the unchanged scalar/frame/cleanup contract. The
larger domain has the same certified ceiling bracket. Its attaining four-end profile
is already known from PR1995; the new result is the complete larger-domain
bound, not another discovery of that construction.

## Evidence

The [proof](PROOF.md) fixes the exact R480 selected k8 word, scalar operations,
coefficients/order, entrances, centre/target pins and early/full cleanup
membership/order. The 402 helpers in full cleanup still end FULL. Register
paths remain monotone and gates use common operand frames; arbitrary terminal
orientation does not mean arbitrary nonnested transitions within a call.

- All 78 terminal nodes are free: 32 have complete 374-choice intervals,
  and 46 have complete five-choice intervals. There are 2,589 free gate nodes.
- The complete event graph retains all 106 low-end cone relations as
  zero-charge containments. A new quotient enumerator covers dimensions
  through five; the predecessor implementation intentionally stopped at four.
- Exact rational duals check all **396,241 columns and 103,563 rows in 129
  components**: 100,197 zero residual vectors and 296,044 strictly positive
  ones, at both the ceiling upper endpoint and the 5% target.
- An integral assignment contracts ends 574,575,580,581 and gives
  `{1:2400,2:446,3:416,4:142,5:82,8:8}`. Local mass is 5,582; idle mass is 1,650.
  Its annotated word passes the retained scalar/frame auditor on all
  **704 input columns in both orientations**.
- A separate bitset/covector/integer-root implementation reconstructs every
  domain, edge and cone and checks every dual inequality. It imports no
  primary frame, LP or moment implementation.

The complete endpoint domain has local mass between 5,540 and 5,792, so
idle mass stays between 1,440 and 1,692. The objective charges this variable
idle mass using the favorable rank-51 relaxation. Keeping the old 1,646 idle
units after contracting four ends would falsely pass the 5% target; the
control from PR1995 remains relevant to this enlarged class.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/selected-k8-unrestricted-ends
```

The registered replay runs both exact checkers and the control suite. Normal
replay is read-only, including under `-O`; unchanged retained code is compiled
with its guards enabled. `verify.py --write-expected` explicitly regenerates
the receipt. Compressed DUALS and PRIMAL artifacts are compared by canonical
parsed payload, not gzip stream bytes. Canonical receipt SHA256:
`1891bcf17e86405d265ed4b51b9de6f6059be95c50a5b6c28b21d2ac8057093e`.

The full registered replay passed on CPython 3.12.3, including all 20 control
groups. Both exact checkers also passed CPython 3.14.4 under `-I -O -B`
from a relocated package with read-only files and directories, preserving
all bytes. Subsequent edits record validation and clarify proof prose.

`nominate.py` is optional solver-based discovery, using Python 3.12.3,
highspy 1.15.1, NumPy 2.5.4 and SciPy 1.18.1. Its output is a proposal;
acceptance needs no solver dependency or floating-point decision. The
nomination code caches the solver's copied basis-status lists once, keeping
extraction practical for this larger LP. DISCOVERY.json is diagnostic only.

## Scope and coordination

Single random nonce `5f5984c68e5381ec12276b69c721f48c`, revision-3
`complex-mechanisms / complex-new-helper-inventory`; no reroll. Base main
`1c47876ef742ba64bf9140b0527d63acf656a3b4`. The prescribed baseline-source,
ceiling and lever controls passed. The initial waiver of all affected helper
climb costs, with released mass recharged, had planning headroom; it was not
a realized word or a universal lower bound for the final domain.
[Discussion2000](https://github.com/CrocSwap/integer-mult-bounds/discussions/2000)
records the claim and outcome. Published as [PR2013](https://github.com/CrocSwap/integer-mult-bounds/pull/2013);
mathematical commit `31e788df17a4df614fa5b3605a06d06e60f18bb6`.
TASK.json retains the original card, sources,
predecessor heads and overlap coverage. Metadata search is not a novelty
certificate. The final refresh covered 381 open PRs at 17:00:22 UTC and
643 Discussions at 17:01:43 UTC on 2026-10-14, with complete pagination.
Related PR1995/1186/1996 heads were unchanged. Main
`b6135f9fe8c0783f22bd87992a080575f2943511` preserved every mathematical
input and the selected record, with no package collision. Its new canonical
path validation passed separately; replay-command behavior was unchanged.

This obstruction does not pass the card's physical-construction acceptance
gate. Emitted native programs, phase/wrapper admission, a new physical owner
map, selected cold replay and the global/outer invoice were not replayed.
Fractional ideal idle packing need not be realizable. The theorem does not
claim optimality at every exponent, unique optimal frames, or elimination of
remaining packing headroom below the ceiling. Changed entrances, scalar
rewrites/order, cleanup changes, nonmonotone internal transport, new helper
registers, shared centres or a changed coverage law remain outside scope.

## Open next questions

1. **Change an entrance or scalar dependency.** This changes the forced spans
   that limit the current endpoint freedom. Pin one rewrite, establish its
   arbitrary-dirty identity and complete frame/cone constraints, then screen
   its whole local/idle bill. The blocker is a priced changed-word contract.
2. **Physically host the four-end word.** Compare its annotations with the
   existing rank-seven-end constructions, then run native phase/wrapper and
   complete owner admission. A local optimum supplies no global improvement;
   the available ceiling gain is tiny and precision/outer obligations remain.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Retains navinor's frame method and the chafreaky/PR557, ntedvs/PR776 and
Rohan Guliani/PR815 lineage; Alexander Schwartzman/PR1030 and Cinna Davis/PR1090;
Arham Tahir/PR1583; PR1671 and PR1995; Ross Richardson's uniform fixed-end
audit; Marius-Paul Dumitrean/PR1186 and Cinna Davis/PR1996; Douglas Colkitt/PR1240
and Sagar Thakrar/PR1012; the full selected construction and word-reconciliation
lineage. See NOTICE.md and exact SOURCES.json pins. Apache-2.0; no independent
human or full formal verification is asserted.
