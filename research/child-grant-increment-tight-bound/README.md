# Sharp from-zero cost for the actual child-grant increment

For the unchanged increment macro in thu-nmrc PR6719 at
`3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`, the total cost of k>=1
consecutive calls from temporary zero satisfies the sharp homogeneous bound

`C(k)=13k-7*popcount(k)+5*bit_length(k) <=15k`.

Equality holds exactly at k=4, where the actual first four calls cost 60
transitions. Thus15 is the least uniform coefficient for this macro with
no additive allowance. The exact formula is already stated by the source;
its 18k bound is valid but looser. The leading asymptotic coefficient remains 13.
This result does not assert an optimal increment algorithm or a new generic
binary-arithmetic theorem. `PROOF.md` supplies the all-k argument.

The tape starts with LEFT at0, head1 and RIGHT alone at1, representing
temporary zero. Positive outputs are canonical LSB-first binary packets.
Growth cells beyond RIGHT must be owned and physically blank. Every branch,
write, unit move and goto, including the complete rewind, is charged. The
following wrapper HALT is excluded. Setup, caller loops, descriptor conversion
and eventual retirement need their own bills. Starting from arbitrary n changes
the bound: one call on n=3 costs 25, so 18 is not a universal per-call limit.

## Actual source and verification evidence

Six original source/proof/NOTICE objects are pinned by Git blob and SHA256.
The shared emitter authenticates the producer, machine and counter bytes,
extracts only the unchanged increment definition, and uses the retained
assembler/rewind helpers to emit its actual 17-instruction table, including
the wrapper HALT and rejection continuation. It does not execute the whole
producer/router/checker or the source Machine/Tape runtime.

Separately authored sparse-dictionary and dense-list interpreters check that
table. They **share this authenticated candidate construction**, so their
independence is in transition execution, not an end-to-end independent
constructor. Each checks 1,024 persistent from-zero increments and ten
independently initialized all-ONE carries with lengths1,2,3,4,8,16,32,64,128,256.
All measured rows, canonical packet markers, returned head1, visited positions,
active sentinels and the untouched spectator tape are checked. The eight
controls per engine include actual wrong-write/return/default-guard tables,
the actual25-step call on3 and strict JSON proof-data rejection.

Both sealed first runs passed before either consumed a peer certificate.
The complete certificates match byte for byte: 21,390 bytes, SHA256
`a1b9beb4baf46867a36b227f6427f65c267c5651e2dcfd10dd0a34186b7febcf`.
The whole table hash is
`55236602d6819cb9d7025cfddd2858e60c34f670d47464d187b6fe7c07fdad8c`.
On managed CPython 3.12.14/macOS 26.5.2 arm64, the first sparse/dense runs
took 0.051865125/0.156017291 seconds, with peak RSS of 30,670,848/30,638,080 bytes.
Exact commands, clocks and raw-output hashes are retained in the first records.
Four subsequent actual-certificate normal/optimized checks passed.

Default commands regenerate and compare every field of the actual retained
certificate, not only summary flags:

```sh
python3.12 -I -B primary.py
python3.12 -I -O -B primary.py
python3.12 -I -B oracle.py
python3.12 -I -O -B oracle.py
```

The explicit `--emit PATH` mode writes a regenerated certificate;
`--certificate PATH` selects a packet for tampering checks. Source/case/schema
and the complete core-file manifest authenticate before emission/execution.
`VALIDATION.md` records additional CLI-tampering, committed/export/cold and
hosted outcomes; none is inferred from the two first runs. Finite execution
corroborates the macro, while the written proof establishes all positive k.

## Scope and credit

The 15k coefficient does not recost the complete quotient/product generator,
linked router/consumer,94V/13V or1000V/100V bills, codec/stack return, physical
supplier or recursive invoice. Owned blank growth, temporary-zero initialization,
full caller lifetimes, H-from-width, ancestor/depth handling, precision, native
realization, compiler/outer use and all five selected assumptions remain explicit.
There is no paid-profile, κ or selected-frontier change, full multiplication
proof, human acceptance or proof-kernel claim.

Credit thu-nmrc for the macro, existing formula and child-shape application;
David Arias/PR2776 for the machine, assembler and rewind/counter lineage;
Jose Manuel and JoyboyBrian for earlier binary-control/divisor work;
Ali Romman/PR5829 for whole-high batch geometry; and the retained segment,
stack, codec and output-return authors. Classical binary-counter amortization
remains classical. ToikY with substantial OpenAI Codex and separate AI
implementation/proof roles supplies this scoped external macro check and
sharp homogeneous refinement. Apache-2.0; original notices remain exact in inputs/.

## Open next questions

- Can the sharper local coefficient improve the complete charged child-shape
  producer bill? Bind its actual increment call counts and initialization,
  scan, rewind, marker and retirement costs at the same source head first.
  The full quotient/product and linked-consumer ledgers were not replayed here.
- Can this counter potential be carried through actual nested child ownership
  and reuse? Start with one real producer-to-child lifetime, including its
  initial value, owned blank growth and final retirement. Complete production
  dispatch, physical stock/precision and recursive transfer are separate blockers.
