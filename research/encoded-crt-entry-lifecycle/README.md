# Encoded CRT numerical entry lifecycle

A source-operation refinement of the retained PR5053 current-child numerical
consumer. A unary width guide and canonical paired streams initialize a real
fixed 64-slot arena with eight protected caller words; every owned numerical
and record cell is initialized, consumed and retired by local operations.
The actual producer executes unchanged, including its encoded width guard.

The proof covers all admitted widths, exact lazy/eager allocation correspondence,
canonical padding, repeated successful calls, complete retirement, a per-call
operation envelope and uniform retained tape backing. It is not a literal
binary compiler or a complete multiplication theorem. Inputs, including the
guide and dirty caller words, are supplied. Malformed-input rollback is not
claimed. No selected result or predecessor source changes.

Run `python3 -B research/encoded-crt-entry-lifecycle/verify.py` (also with `-O`).
`RESULT.json` is the complete typed frozen receipt. `--write-result` explicitly
regenerates it. All scalar fixture construction, reference arithmetic, output
inspection and original lazy-arena calibration in the verifier are observers;
they are excluded from the new algorithm and are not supplied for free to it.

First working example: left moduli5,7 with current coordinates1,5 and right
modulus13/current9 returns lower11, product35, offset7/current3. It runs through
the actual initialized context at widths10,16,24. Repeated calls and padded
right coordinates exercise persistent allocation order and cleanup.

See PROOF.md for quantified hypotheses and VALIDATION.md for reproduction.

## Open next questions

* Produce the unary guide and canonical descriptors at one genuine upstream
  caller with a complete placement and restoration invoice.
* Lower this complete numerical session to literal finite binary control;
  preserve allocator order and the full retained-backing contract.

## Attribution

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0. The unchanged
numerical producer is PR5053 at ef9da0a9ac29cf86610a52e3a183bdb28508aa74;
its word/record primitives come from the credited PR4025 preparation source.
The source CRT specification and observer oracle retain Douglas Colkitt and
OpenAI Codex attribution in `research/unconditional-batched-crt/NOTICE.md`.
All consumed bytes are pinned in SOURCES.json. The retained source-operation
proof is a dependency, not independent formal-kernel acceptance.
