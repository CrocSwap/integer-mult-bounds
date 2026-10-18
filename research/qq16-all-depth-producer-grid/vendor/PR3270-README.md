# An exact component grid for the full-cover F0→B1 reference

For exactly one 73-axis tensor layer, uniform bounded Gaussian-dyadic data
and dirty helpers admit an exact fixed-grid execution of the complete
literal QQ16 F0→B_1_2 reference: quantum `h 2^-71` and signed width `P+215`
suffice when initial components lie in `h Z` below `2^P h` and private
fields enter zero. The bound covers native butterfly numerators and carries
all fields across the stage boundary.

PR3226 already proves the F0 part. The new result supplies B1 native
interiors, all 528 actual full-cover moves and the carried boundary.
Its direct symbolic density is at most `483082 N+12` W-bit word operations,
plus `2112 N` conceptual cover transfers and `1426 N+12` numeric words per
cover owner, with `N=2^73`. Routing, control and recursive tariffs remain
unpriced. This is a sufficient finite-reference contract, not a sharp bound
or supplier result. [PROOF.md](PROOF.md) states the exact implication.

## Reproduce

Python 3.12 or later, standard library only:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/qq16-f0-b1-exact-grid
```

The registered commands are read-only. Direct `verify.py`, `crosscheck.py`
and `test_controls.py` also work in a Git-free export containing this package
and its two declared inputs at their original paths. The verifier accepts
`--write NEW_EXTERNAL_PATH` to create a receipt without overwriting one.
Use an external `TMPDIR` when required by the session.

The rational and separate integer-lattice dispatchers agree on all 53,118
events, 270,288 primitive observations, completed-cut/output digests and
operation counts. Seven control groups include actual carried state versus
an invalid reset, native component containment, noninvertible owner maps,
out-of-range translations and a rejected one-owner action. These are exact
finite envelope checks. The enormous full payload is not allocated or run.
The 512 normalization belongs only to the nine-axis local kernel, never to
a complete B1 payload. No multi-layer tensor bound is claimed.

## Sources, scope and credit

Canonical base is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision
6. The literal joint-query certificate and selected Clifford/residual archive
are base inputs. PR3226 at `6b17b9b7c76d60726bd87123b9bf9905aa3151dd` supplies
the retained rational/integer primitives, F0 certificate and proof; its four
retained files are byte-identical and authenticated before import. Replay
does not need that pending commit in the local Git object store.

Credit commdata2338/PR3226/3235, Sricharan Vagvala/PR3101 for pair-first native
arithmetic, Nick Petalas/PR2965/3250/3258, Ali Romman for the joint-query
construction, Tekalign's native conventions, Ross Richardson and Arham Tahir
for the dirty-rounding lineage, and the retained supplier/bridge contributors.
Their source notices and attribution remain intact. Apache-2.0.

PR3181's scalar projection/grid is distinct from this native-interior proof.
PR3250 supplies a rounded local child/half-ADD; PR3258 proves local retained
information bounds for that rounded interface. This exact-grid reference
has a changed arithmetic contract and does not invalidate those results.
The current family gate permits this finite producer obligation; downstream
implementation expansion stops here. Physical routing, a paid consumer,
recursive tariffs and all-size compilation remain unknown costs.

Initial overlap covered 310 open PRs and 2,095 Discussion records with complete
pagination at 19:55 UTC on 2026-10-17, plus current heads/handoffs. Closed
diffs and unpublished work were not exhaustively searched. Scope corrections
replaced an invalid 512-payload premise with the full cover and restricted
the constants to one tensor layer before review. The [canonical status](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19003553)
records that history. [TASK.json](TASK.json) gives the exact card and limits;
[SOURCES.json](SOURCES.json) pins sources. The inherited native bridge and
exact endpoint/restoration theorem are not re-proved. No complete physical
backend, supplier, new kappa or selected-frontier change is claimed.

## Open next questions

- Bind one admitted caller's actual entry grid and dirty bound, then compare
  this entire word/storage density and the omitted routing, control and F17
  consumer costs with a complete allowance before optimizing its guard.
- A multi-layer claim needs a literal tensorized primitive order and a new
  lambda-dependent lattice/range ledger. The one-layer constants do not lift
  unchanged. No further construction round is reserved.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
