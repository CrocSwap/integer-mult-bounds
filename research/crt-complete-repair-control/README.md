# Complete finite control at the actual CRT repair caller

The #4795 key service prices its instructions, but its real surrounding
producer/scanner/repair caller still executes Boolean control in Python and
prices only cell actions. This package lowers the unchanged source ASTs to
one fixed finite-symbol program and executes the complete actual layer:
unary geometry, stencil, dense mask, split, 2,944 direct key calls, stable
12-pass radix repair, reinsertion and disposal. Runtime execution has no
Python source loop, callable key, AST interpretation or host-generated mask.

The successful-domain theorem covers the fixed u2/t2/y8 geometry, arbitrary
opaque 12-bit record labels, and any target-independent 32-bit ROM at target
position 2. The actual canonical fixture has 4,096 records and the source
h3/modulus5/offsets[0,2,4,0] middle layer. Raw post-S data and the supplied
ROM remain explicit inputs. No raw compact macro, twelve-shuttle native
implementation, all-size E(p,ell), binary transition table or new kappa is
claimed.

`compiler.py` expands finite source calls and relocates the entire retained
key program into the split continuation. Mutable locals, short-circuit
conditions, marker loops, fixed role multiplexers and finite stencil/record
symbols all have explicit instruction semantics. Unsupported syntax is
rejected, including loop-else and try-finally. On malformed-input errors the
compiler rejects without claiming the original producer's exception cleanup.
`machine.py` installs and disposes of owned markers and initializes/resets
all finite-control registers through charged instructions.

The full static CFG is cut at charged tape operations; its remaining graph
must be acyclic. Its longest path D bounds every control-only interval, so
T <= (D+1)(C+1), for any execution with C cell actions. The written proof
also bounds all outer actions and every retained key call, without re-adding
the removed host key interface. This completes one local instruction ledger;
it does not claim an improved asymptotic tariff.

## Reproduce

```
python3.12 -B scripts/research_package.py --package research/crt-complete-repair-control
```

`verify.py --light` runs bounded CFG, compiler admission, nested key, radix,
carry, cleanup and alias controls. Full verification checks every actual key
against an independent source oracle, the entire repaired payload, exact bad-only
call set, all borrowed/private roles and heads, and the frozen instruction
receipt. `--write-result` is explicit authoring mode. Exact source/history,
normal/optimized, export and corruption evidence is recorded in VALIDATION.md.

The constructor only allocates fixed blank owned roles and verifies borrowed
object disjointness; it never decodes the unary headers, ROM or payload into
execution decisions. Verifier callbacks observe execution and cannot supply
an operand, key or branch. The local theorem assumes correctly framed inputs;
there is no blanket malformed-input rollback claim.

## Open next questions

1. Lower the whole finite alphabet to binary transitions, with its full constant.
2. Execute raw compact S and its twelve paid dirty-back shuttles on the same data.
3. Connect variable-geometry descriptor/ROM/key generation and the full E bill.

TASK.json records concrete first steps and blockers. These obligations remain
separate from the completed fixed caller and are not automatic continuation.

## Provenance and credit

Base81e9bd69e4a5b00ba9c713a1620e36d576d5522e, priority7. Canonical claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19142272

Credit Cinna Davis #4100 for the compact CRT construction and source oracle;
Hiroki KUMAZAKI #4169/#4174 for current-state reverse keys; ToikY #4201/#4208
for scanner/producer; the #4637 mask bridge, Jose Manuel and Ryanson Jonathan
for retained repair lineage; unpaidmoon and Douglas Colkitt/OpenAI; and the
#4795/#4752 finite-key/query predecessors. Their source algorithms and proofs
are reused, not presented as new. All source files and original notices remain
unchanged and hash-pinned. JoyboyBrian, with substantial OpenAI Codex assistance.
Apache-2.0. Separate agent review is not independent human or proof-kernel
acceptance. Selected frontier and frozen archives are unchanged.
