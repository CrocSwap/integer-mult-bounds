# Numerical lifetimes of the selected BIT two-bank Layout

The unchanged `layout.Layout` in Jose Manuel/jmbarrancoml's PR2697 has these
coordinatewise numerical Word bounds above **all** live entry residents:

| Successful call | Additional residues | Additional indices | Return ownership |
| --- | ---: | ---: | --- |
| Constructor | 0 | 4 | Retains three indices |
| `physical` | 0 | 1 | Returns one owned index |
| Unary `extents` | 6 | 3 | Restores numerical entry state |
| Binary `extents` | 6 | 4 | Restores numerical entry state |
| `fibre` | 6 | 0 | Restores numerical entry state |
| `close` | 0 | 0 | Consumes the three Layout indices |

Each index bound is attained. The residue peak in `extents` is exactly six
if at least one executed power exponent is positive, and zero otherwise.
The binary call on a one-position bank gives the zero-exponent example.
The other positive-size calls above attain their residue bounds. Coordinatewise
maxima need not occur at the same instant on every input.

This closes the Layout component explicitly excluded by Ross Richardson's
[PR2810 directory/ADD handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2810).
The [written source proof](PROOF.md) covers the valid successful-call domain;
finite execution corroborates its constants and exact returned cardinalities.
It does not establish the rest of `Consumer.apply`, a full reserve, physical
placement/movement, supplier admission or a new kappa.

## Sources and reproduction

[SNAPSHOT.json](SNAPSHOT.json) pins unchanged exports from Nick Petalas's PR2801
`e2564b80b86fb77610b4b78701e5446a76fbe962`, whose runtime is PR2697
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. All eleven exports, including the
predecessor notice and conditional caller proof, authenticate before execution.
Relative links in the frozen caller proof retain their original PR2801 meaning.
The loader compiles the original seven runtime modules and the unchanged
`Geometry` class from `numeric.py`; it does not execute the unrelated numerical
form/coefficient classes. It bypasses bytecode caches. No predecessor changes.

From the repository root, using Python 3.12 or later and its standard library:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-layout-numerical-lifetime
python3.12 -I -O -Werror -B research/selected-layout-numerical-lifetime/verify.py
```

The registered replay also runs [test_verify.py](test_verify.py) under `-O`.
`verify.py --emit` prints a fresh receipt. Ordinary verification is read-only
and compares the complete typed [RESULT.json](RESULT.json), so booleans do not
compare equal to integer receipt fields.

The 45 fixtures cover 555 complete unary/binary `extents` calls, 195 physical
maps, and every constructor, fibre and close. They use dimensions 1, 2, 3 and
64; one or two columns; parent widths 1, 3, 7, 64 and 127; moduli 3, 9 and 5;
both embedded and flat maps; and zero or three unrelated borrowed Words in
each arena. All positions/pairs are checked in banks of at most six positions;
larger shapes use five named boundary positions. Independent integer formulas
check every returned cardinality, its separate high-bit margin and the single
gap factor. Literal scans verify preserved entry slots, bytes and heads,
erased freed slots, and occupied symbols including permanent templates.
The receipt counts 713,905 allocations inside the extent calls.

Nine defect/boundary test groups include one-Word-underbudget witnesses for
constructor, unary/binary indices and residue scratch; omitted power and leaked
index defects; literal gap and zero-exponent outputs; rejected reversed atoms;
source/manifest corruption and boolean/integer receipt substitution. The reversed-atom witness leaves two allocated
indices, showing why successful restoration is not exception rollback.

## Selected adapter implication

Conditional on the pinned [PR2801 caller inventory](evidence/CALLER-ENTRY.md),
an adapter action enters `extents` with `(0,12)` caller-owned Words above
`Consumer.apply` entry residents. Binary `extents` therefore fits `(6,16)`
and returns to `(0,12)` before the ADD callback begins. Its temporaries do not
coexist with coefficient scratch. Consequently this phase fits inside PR2810's
conditional `(37672,34)` adapter-ADD allowance, which now also covers that
ADD's preceding `Layout.extents`. This is a conditional composition, not a
fresh replay or admission of those predecessor lemmas. [PROOF.md](PROOF.md)
states the inherited premises and remaining phases.

## Scope, decisions and credit

The initial random draw suggested selected packing. We explicitly chose the
current priority-5 selected-stock handoff instead of another packing census.
`TASK.json` records that override and the changed scope from a complete selected
m73 stock envelope to this pending BIT caller component. The baseline binding
check passed; it was not a full selected cold replay. The expansion decision
is narrow and finish this component. The canonical claim and result are in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960449).
Freshness and overlap coverage are recorded in `TASK.json`; metadata searches
do not cover arbitrary diffs or unpublished work.

Credit Jose Manuel/jmbarrancoml for PR2697's implementation and retained
framework, normal-form and hosting lineage; Nick Petalas for PR2759's primitive
lifetime analysis and PR2801's caller boundary; and Ross Richardson for PR2810's
directory/ADD proof and the handoff. The earlier PR2753 logical inventory by
David Arias remains distinct. The unchanged [source notice](vendor/NOTICE.md)
retains the full lineage. This contribution by Nick Petalas is Apache-2.0.
The independent internal source review is recorded in `VALIDATION.md`; no
independent human review or formal-kernel proof is claimed.

## Open next questions

1. Join initialization, `Geometry` construction, validation Callback, child
   entry and non-ADD primitive phases under the same `Consumer.apply` entry
   baseline. Start by tracing the validation Callback's resident overlap with
   the eight persistent caller indices. Missing simultaneous lifetimes block
   a whole-caller numerical allowance; the local Layout constant does not.
2. Bind a complete phase ledger to actual physical banks, markers, templates,
   erased backing capacity and movement. First apply the existing bank codec
   to one real caller phase. The complete caller inventory and charged access
   schedule remain prerequisites. Count, record and payload tapes also need
   their separate bounds.
