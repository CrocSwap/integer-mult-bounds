# Exact countdown backing inside native ADD

This package supplies one non-payload component requested by
[PR2902](https://github.com/CrocSwap/integer-mult-bounds/pull/2902), following
[PR2882](https://github.com/CrocSwap/integer-mult-bounds/pull/2882)'s private
storage interface. It proves the exact retained `Counter.tape` array-length
maximum for unchanged PR2697 `stream.add_pass`, including cleared tapes and
old/new constructor overlap.

For positive spectators U,G,S and modulus M>=2, put
`p=bit_length(U)+3`, `m=bit_length(G)+3`, `s=bit_length(S)+3`, and
`r=bit_length(M)+3`. The exact native Counter peak is
`p+r+m+max(m,r)` when S=1, and `p+r+m+max(m,r+2s)` otherwise.
The [source proof](PROOF.md) states the encoding and ownership premises.

A callback allowance H composes as `max(C,H)` only when its private Counter
backing becomes unreachable before return and it captures no native frames or
references. A successful native fixture clears and retains callback tapes,
reaches 82 cells, and falsifies the proposed 64-cell phase maximum without
that condition. This is a storage component, with no selected-frontier change.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/selected-add-counter-backing
```

Portable direct replay also works without Git or network access:

```sh
python3.12 -I -Werror -B research/selected-add-counter-backing/verify.py
python3.12 -I -Werror -B research/selected-add-counter-backing/independent.py
python3.12 -I -Werror -B research/selected-add-counter-backing/test_verify.py
```

[RESULT.json](RESULT.json) records 63 complete native fixtures and one callback
counterexample. A separate write-observed census covers 162 fixtures. Nine embedded controls and five separate tests check domain,
source integrity, lifetime omissions and typed receipts. The normal verifier
writes nothing. `--write NEW_PATH` writes a new receipt and refuses overwrite.
[VALIDATION.md](VALIDATION.md) records environments, independent checks and
implementation constraints. [TASK.json](TASK.json) records scope and overlap.

## Open next questions

- Join Natural extent backing, numerical arenas and callback/program/field
  records at actual ADD cuts. This is needed for total private A. Start from
  the existing numerical-word audit and this Counter proof, retaining each
  category's ownership baseline. Simultaneous backing and callback lifetimes
  are still unbound.
- Prove physical erasure, placement and reuse after the full caller ledger is
  joined. Reachable array lengths do not establish those physical obligations.
  Use the active wrapper work in Discussion2319 before assigning new work.

## Sources and credit

Jose Manuel / jmbarrancoml, PR2697 at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, supplied the native caller and
retained primitive/source527 lineage. Its [notice](sources/PR2697-NOTICE.md)
and Apache-2.0 license are preserved. The five source modules are byte-identical
exports with Git blobs and SHA256 hashes in [SOURCES.json](SOURCES.json).

kumagi's PR2882 supplies the complete packet-loop backing envelope and private
interface, following Ross Richardson's PR2874 return-cut accounting. Nick
Petalas's PR2902 supplies native payload maxima. The existing
[selected numerical-word audit](../selected-stream-directory-numerical-audit/README.md)
counts numerical Words rather than Counter backing. These results retain their
own credit and limitations.

Nick Petalas. Substantial AI assistance was used, including a separate source
derivation and checker review. Evidence is author-checked; no independent human
or formal-kernel review is claimed. The selected record and frozen predecessors
are unchanged.
