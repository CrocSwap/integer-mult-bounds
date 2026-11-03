# Compact permutation controls with dense-row access

For N=2^h, this package compiles an arbitrary input-to-output permutation into
`Nh-N+1` stored control bits and answers every dense layer/wire query directly
from them. The usual distinct-switch Beneš representation has `Nh-N/2` bits.
The exact saving is `N/2-1` switch records, each fixed to zero, on the same
`2h-1` layer topology. Repeated controls at the two wires of a switch count
only once in both figures. Framing, h, input and compiler workspace are separate.

Claim type: constructive implementation and scoped written proof with exact
finite corroboration. No new kappa is claimed.

The network, bypass construction and switch-count theorem are classical
[Waksman](https://doi.org/10.1145/321439.321449), credited prior work. The
contribution is this compact row serialization, its closed address decoder,
a bounded compiler and their exact endpoint certificate for the repository's
recursive pair topology. No minimum-network-size or global literature-priority
claim is made. See also Waksman's
[corrigendum](https://doi.org/10.1145/321450.321465).

## Interface

- `compile_rom(permutation)` uses `permutation[source] = destination` and
  returns an immutable binary tuple. The executable accepts powers of two
  from 2 through 4096 and preserves its borrowed input.
- `address(h, layer, wire)` returns a compact index or `None` for a bypass.
  Both endpoints of a switch receive the same answer; no dense table is built.
- `query(h, rom, layer, wire)` validates the entire ROM and returns its dense
  control bit, including zero at a bypass. Validation is linear in ROM size.
  A batch caller can validate once and use `address` with the admitted tuple.
- `pack_rom(h, rom)` emits canonical bytes with controls packed least-significant
  bit first. `query_packed(h, data, layer, wire)` validates the byte length and
  tail padding and reads the requested bit directly without unpacking.
- `apply_rom(h, rom, values)` applies the permutation to arbitrary payload
  objects. Compiling and applying the inverse restores every wire.

The [proof](PROOF.md) applies to every h>=1. The executable's height limit is
explicit and enforced. This compiler can choose different control bits from a
predecessor compiler for the same final permutation. Its dense-row interface
describes the newly compiled network, not a predecessor's frozen control
strings or intermediate CRT repair keys.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/compact-waksman-row-rom/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/compact-waksman-row-rom
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/compact-waksman-row-rom --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. Both
registered checks run the complete finite domain with warning errors, once
normally and once with `-O`. Expected final marker:

```text
PASS_COMPACT_WAKSMAN_ROW_ROM permutations=40346 larger=36 controls=34 no_new_kappa
```

An independent explicit-wire topology checks every compact address at
h=1,...,12, including every forced zero, and validated public queries. All
40,346 permutations at N=2,4,8 pass. Four specified permutations at each
h=4,...,12 additionally pass, including a nontrivial odd affine permutation.
Each case checks all packed dense queries, all labeled endpoints, correlated
signed dirty payloads, input preservation and inverse restoration. Seventeen
malformed inputs reject, including packed length, type and nonzero tail padding.
All seventeen single-bit mutations of the eight-wire identity ROM change
its observed endpoint.

The byte payload occupies `ceil((Nh-N+1)/8)` bytes. Its unused tail bits must
be zero. Byte alignment can hide a small logical-bit saving; no byte saving
is claimed at N=4,8,16. At N=32, compact and full distinct-switch payloads
occupy seventeen and eighteen bytes respectively, before shared framing.

Every execution prints a generated JSON receipt containing the full inventory,
ordered census digest and SHA256 of all seven package files. `--emit` prints
only that JSON for capture outside the checkout. No receipt is handwritten,
no generated output is left in the checkout, and no predecessor scientific
checker is executed.

## Relationship to current work

ToikY's [PR4192](https://github.com/CrocSwap/integer-mult-bounds/pull/4192)
provides the charged uniform Beneš arena/compiler context. JoyboyBrian's
[PR5092](https://github.com/CrocSwap/integer-mult-bounds/pull/5092) supplies
an encoded producer with dense layer serialization and interleaved child
rows. Cinna Davis's PR4100 supplies their CRT/routing lineage. The pinned
producer is provenance for this topology and interface; its code is neither
copied nor imported. This representation change does not audit those results.

The card `joint-query-controller` has changed scope to a routing-control side
result. It changes the dense-switch storage premise. Its complete native/caller
invoice gate remains unmet. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
conditional kappa `781451/250000000`. The selected frontier is unchanged.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375406)
preceded implementation. Main README searches and live all-state PR queries
found no permutation-routing Waksman package. The similarly named matrix
multiplication algorithm is a different object. Open work, merged work,
recent account submissions and concurrent local claims were checked. These
searches do not cover unpublished work or establish global novelty.

## Open next questions

1. Can the encoded CRT producer implement the path-first coloring and compact
   serialization with a favorable complete tape bill? Start with one four-wire
   encoded permutation, charging construction, validation, query, disposal and
   head returns. This Python implementation and its size saving do not settle
   the missing finite-control lowering or establish a tape-time saving.
2. Can the changed routing choices be integrated into one complete CRT repair
   caller? Rebuild its actual intermediate row keys and compare the complete
   invoice. Matching the final permutation does not preserve old intermediate
   control rows or exceptional-key witnesses.

No production compiler is replaced. Native access, owned erasure, hosting,
stock, precision/tape, compiler admission, analytic recovery and outer costs
remain separate obligations. No selected cold replay, Lean, Docker, physical
runtime comparison or complete multiplication theorem is claimed.

## Credit and code bounds

This contribution was produced by Nick Petalas. Apache-2.0. Independent human
and formal proof-kernel review are unclaimed. Waksman retains the classical
network credit. The CRT context retains ToikY, JoyboyBrian, Cinna Davis and
their full predecessor lineage.

The compiler has no recursion, external calls or shared mutable state. Its
worklist has N-1 nodes; each coloring queue has at most N entries. Loops are
bounded by admitted height/wire/ROM sizes or the stated finite census. Every
function has fewer than sixty lines. Python's managed allocation is a Power
of Ten rule 3 deviation, bounded by N<=4096, S<=45057 and the fixed census.
There is no allocation-free claim. Larger executable heights require revisiting
these bounds. The isolated verifier uses one fixed-path Python module load,
a rule 8/9 runtime-loading deviation with one visible target. It imports no
predecessor code. Warning-strict normal/optimized execution supplies available
diagnostics; explicit semantic exceptions remain active with `-O`.
