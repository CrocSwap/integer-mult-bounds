# An owned canonical row producer

One fixed 3,397-location, fifteen-tape program emits a complete canonical
padded-rotation row from four borrowed descriptors. It constructs every wire
address on tape, preserves inputs, clears private bodies and guards, and
returns every head. For `N=2^h`, the complete bounds are
`T<=1280N(h+4)` and `K_after<=K_entry+N+20(h+4)`.

Read [PROOF.md](PROOF.md), [program.py](program.py), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md). The unchanged
PR7735 point graph is embedded with relocated control targets and return
jumps. No host loop supplies query addresses. The output remains owned.
There is no new kappa or complete CRT caller claim.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/owned-canonical-row-producer
```

Both registered commands print:

```text
PASS_OWNED_CANONICAL_ROW_PRODUCER 15 tapes; complete owned rows and returns
```

Two instruction paths compare all bits, complete returned states, head
positions, write counts and historical intervals for 213 complete small
rows, seventeen historical rows and six larger rows through 4,096 bits.
They also check all 3,237 retained source instructions, four numeric-domain
rejections, three semantic/retirement controls and two alias rejections.
The all-height result follows from the written invariant and loop counts,
not the finite range. See [VALIDATION.md](VALIDATION.md).

## Scope and remaining costs

The caller supplies correctly encoded descriptors, distinct owners, blank
windows and framing. The producer returns one owned row. Current-state CRT
descriptor production, conversion, payload use, transport and output disposal
remain caller obligations. The output-linear arithmetic stream in PR7740
has no direct physical lowering here. The complete generic PR5092 producer
has a different workload, so no matched speedup over it is claimed. All five
framework assumptions and the selected frontier remain unchanged.

## Open next questions

1. Can the three-rectangle stream reach output-linear literal transitions?
   Start with the sharp `(6,53,25,7)` row and lower its phase/run countdowns.
   Descriptor preparation and complete ownership returns must be charged.
2. Can an actual CRT consumer use this exact row owner without a host rewrite?
   Start with its current-wire query order and descriptor encoding. Bind the
   real producer, transport, payload use and row disposal before pricing a
   complete workload against retained ROM reuse.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained notices preserve Jerry Chen, Nick Petalas, Cinna Davis and the
full predecessor lineage. Separate interpretation is not independent human
or formal-kernel acceptance.

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19719352).
