# An eight-bit algebra-faithful A5 address carrier

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Result and boundary

The formal A5 alphabet in Wentao Li's [#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089)
has an explicit action on eight binary address bits whose extension to
`F2[A5]` is injective. The two generators have literal address circuits of
4 and 12 CNOTs. On a 256-entry array, fixed in-place programs implement the
same permutations with 360 and 510 data XORs, using no extra data bit.
Every input entry may be arbitrary. One natural four-bit copy distinguishes
the 60 group elements but fails to preserve the formal group algebra.
Two copies are therefore necessary and sufficient within this particular
natural-module replication family.

Claim type: a finite exact construction with a scoped algebraic proof.
This supplies a concrete nonabelian address carrier for the escape route
identified by Cinna Davis's [#3914](https://github.com/CrocSwap/integer-mult-bounds/pull/3914).
It does not supply an admitted BIT supplier, a recursive child invoice,
a physical fixed-tape implementation, or a new kappa. No minimum over all
binary affine representations, or optimal CNOT circuit, is asserted.

## Construction

Write `F4=F2[w]/(w^2+w+1)`, encode `a+bw` as `a+2b`, and set

```text
X = [1 1]       Y = [ 0  w]
    [0 1]           [w^2 1].
```

Their determinants are one. They correspond to the predecessor's generators
`x=(1 2)(3 4)` and `y=(1 3 5)`. The standalone verifier constructs the paired
closure, obtaining a bijection between all 60 even permutations and all 60
determinant-one matrices. It checks all 3,600 multiplication pairs, so the
identification uses an exact finite isomorphism rather than an assumed
presentation. The classical isomorphism `A5=SL2(F4)` is not a novelty claim.
No predecessor endpoint search or lower-bound program is replayed.

Let the address set be `M2(F4)`, a set of 256 elements encoded by eight bits.
A group matrix acts by `M -> gM`, or by its natural four-bit action on
each of the two columns. Define `P_g e_M=e_(gM)` on array basis vectors.
Then `P_g P_h=P_(gh)`. The orbit of the identity matrix is precisely
`SL2(F4)`, and its stabilizer is trivial. Consequently,

```text
(sum_g c_g P_g) e_I = sum_g c_g e_g.
```

The 60 vectors on the right are distinct array basis vectors. Thus a zero
operator forces every `c_g=0`, proving injectivity of the algebra map.
Entrywise application therefore also preserves every matrix identity and
inequality in `M_r(F2[A5])` for arbitrary finite register count `r`.
Here inequality means distinct formal matrices remain distinct operators;
no norm, numerical inequality or implementation tariff is transferred.

The complete eight-bit orbit inventory is one singleton, five orbits of
size 15, and three regular orbits of size 60. The rank-zero matrix gives
the singleton. A rank-one matrix has one of five row-space lines, and each
such class has 15 elements. Each nonzero determinant gives a 60-element
regular orbit. These disjoint classes account for all 256 addresses.

## Why one natural copy is insufficient

On `F4^2`, the natural action has the orbits `{0}` and its 15 nonzero
vectors. The nonzero formal element `J=sum_(g in A5) [g]` acts as zero.
At zero it has multiplicity 60; at every nonzero orbit image it has
multiplicity `60/15=4`. Both are even, so every coefficient vanishes in
`F2`. Yet the action is faithful as a group action: a matrix fixing every
vector fixes a basis and equals the identity.

This is the obstruction the second copy removes. A faithful group action
alone is insufficient for transferring a full formal group-algebra model.
The regular-orbit criterion is classical; this package provides its explicit
carrier, generator circuits and data programs for the repository's A5 labels.

## Literal address and data invoices

For one column use bits `(u0,u1,v0,v1)` with
`u=u0+w*u1`, `v=v0+w*v1`. An ordered pair below means
`target ^= control`. Execute left to right.

```text
X: (2,0), (3,1)
Y: (0,1), (1,2), (2,1), (3,1), (0,3), (3,0)
```

The resulting outputs are

```text
X: (u0+v0, u1+v1, v0, v1)
Y: (v1, v0+v1, u0+u1+v0, u0+v1).
```

Execute each word on bits 0..3 and again with every index increased by
four. This gives 4 and 12 address CNOTs. Address-coordinate instructions
compute a destination index; they are not data-array XOR instructions.

For an actual data permutation, enumerate each generator's disjoint cycles.
A cycle `(a0,a1,...,ak)` uses swaps `(a0,a1),...,(a0,ak)` in that order.
Each swap uses the three data instructions `A[a]^=A[b]`, `A[b]^=A[a]`,
`A[a]^=A[b]`. No clean temporary or discarded data is needed. The resulting
push action sends the old entry at `M` to `gM`, in the stated orientation.

X fixes 16 addresses and has 120 two-cycles, giving 120 swaps and 360 data
XORs. Y fixes only zero and has 85 three-cycles, giving 170 swaps and 510
data XORs. The verifier compares every symbolic input column of both full
programs. These are explicit upper invoices, not optimality claims.

For q-bit records at each address, run the same data program on each lane.
The counts scale to `360q` and `510q` bit XORs and preserve every input bit.
The tables are fixed finite lists of 120 or 170 pairs of eight-bit addresses.
Their generation, storage and reads have not been lowered to the selected
tape machine. Arbitrary role mixing, non-coordinate rank-one projectors,
source/target frames, ownership, routing, precision, compiler closure and
outer transfer have no paid native implementation supplied here. Those
unknown costs cannot be set to zero. No larger mechanism search is proposed.

## Reproduction and evidence

From the repository root, with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a5-eight-bit-carrier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a5-eight-bit-carrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a5-eight-bit-carrier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a5-eight-bit-carrier --check-source-history
```

Each direct replay prints `PASS_A5_EIGHT_BIT_CARRIER`. It checks the exact
60-element isomorphism and all multiplication pairs, both complete orbit
inventories, all 60 regular-orbit coefficient columns, the one-copy norm
obstruction on every address, every address circuit input and every symbolic
dirty-data input of both swap programs. Eleven semantic controls cover all eight
single-copy CNOT omissions, noncommutation and the two norm-element tests.
Normal replay authenticates the generated `RESULT.json` against all six
source-file hashes and never rewrites evidence. Only explicit `--write`
regenerates it. Finite enumeration certifies the fixed group and circuits;
the regular-orbit argument proves algebra faithfulness.

## Sources and overlap

Scientific base `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, priority revision 7.
The selected conditional kappa remains 0.00302015. The historical task card
and selected record are provenance, not scientific inputs. SOURCES.json
pins Wentao Li's retained README; its endpoint theorem is cited, not audited.
Cinna Davis's #3914 is a public contextual reference, not a runtime dependency
or an unmerged Git pin. The verifier imports no predecessor code.

The cached intake covers 322 open PR bodies at 09:29:21 UTC and 4,238
Discussion records at 09:30:12 UTC on October 23, 2026.
[OVERLAP.json](OVERLAP.json) retains the generated coverage and focused-query
results; the original complete remote snapshot remains local-only. Only 129 local notes
were initially materialized out of 6,824 tracked notes. Main-tree searches
and merged/all-state PR searches supplemented that incomplete local scope.
No matching eight-bit A5 carrier was found within that coverage; arbitrary
diffs and unpublished work remain outside it. The canonical investigation
is [the advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142735).
The native-carrier question is refined to a fixed finite address realization,
with its missing supplier and tape obligations explicitly retained.

Credit Wentao Li #4089 for the explicit native-carrier question, Cinna Davis
#2246 for the A5 labels and #3914 for the additive-caller distinction,
and eumemic, Ali Romman and the retained register-model lineage.
Classical finite-field, group representation and reversible XOR-swap
constructions retain their mathematical credit. The new contribution is
this exact carrier and its full local address/data programs.

## Open next questions

1. Can one actual BIT caller use the 256-address carrier while preserving its
   source/target frames, independent owners and dirty restoration? Start with
   one literal rank-one-projector call and price all scalar role changes and
   address movement. A source-bound caller and full native tariff are absent.
2. Can an algebra-faithful binary affine A5 action use fewer than eight address
   bits? The present one-copy obstruction excludes only the specified natural
   four-bit action. Start by classifying candidate six- or seven-bit modules
   and checking their full group-algebra kernel. No classification or minimum
   over other representations has been established here.

## Code constraints

The verifier has no recursion, dynamic code evaluation, network, subprocesses
or predecessor imports. Its finite collections have explicit bounds: 256
addresses, 60 group states, 3,600 multiplication pairs and at most 170 swaps.
Functions fit within 60 physical lines. `need` checks remain active under
optimization. Python necessarily allocates managed integers and collections;
this is a bounded-runtime deviation from fixed-allocation Power of Ten rule 3.
At most 256 symbolic rows of 256 bits are live in a data-program check, plus
the fixed group and address tables. The interpreter and JSON library allocate
internally. Warning-strict normal and optimized replay are the available
language diagnostics; no repository-wide analyzer configuration is changed.
