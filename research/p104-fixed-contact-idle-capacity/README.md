# Fixed-contact lane capacity on the signed P104 caller

Four broad idle calls provide only 32 lanes across all fixed-contact
rank-additive idle groups on the exact signed 8+9 caller. The resulting
whole-invoice savings upper is 3.6413453744885866 raw units against a
target shortfall of about 140.1850365635899. The proof covers all
1,361 possible groups in its scope. **NO VERIFIED GAIN.** Conditional κ
change is 0%.

## Scope and bound

Track each logical role through every physical SWAP in the literal
#7113 caller. For an idle call, the closed interval from the position
after its previous non-idle contact through the position of its next
non-idle contact gives an optimistic window for its replacement. The
replay traces 94 literal idle calls. Four rank-nine IDLE_ODD calls on
distinct logical roles each have eight ports and span the entire
caller. The 90 other windows are pairwise disjoint.

A group replaces one lane from each of at least two distinct literal
calls whose windows share a position. Different groups may use
different lanes of the same call. Each physical lane can be used once
and the shared child is charged at the sum of the replaced ranks. The
relaxation grants free setup, routing, phases, ownership, restoration,
precision, tape and ordinary work, and permits arbitrary pairing of
ports across field types. The rest of the #7277 invoice stays fixed.
Each admissible group contains at least one broad call.

For the fixed target
`κ = 10018846261809/2500000000000000`, write
`H(r) = r^(1−κ)`. For every group the saved moment is bounded above by
the sum of the original `H(r)` charges minus `H(sum of ranks)`.
The exact certificate assigns a nonnegative per-lane charge to each
broad call and zero to each narrow call. Each group's total charge
covers its directed saving upper. Summing these inequalities over any
compatible collection of groups charges each call at most its port
count times its certificate value. This bounds the entire collection
without requiring an optimal schedule or an optimal dual. All 366
pairs, 544 triples, 361 quadruples and 90 quintuples pass the exact
inequality.

The complete signed invoice has 110,536 paid jobs, 22,461 productive
fields and rank surplus 1,424. Its directed original target margin
is about −140.1850365635899. Adding the capacity bound leaves an upper
margin of about −136.5436911891013. The reference comparable result
remains #7277 with κ = 0.003645669928698. No physical prototype was
needed. The result establishes a scoped price obstruction on the
retained invoice.

## Replay

From a clean repository checkout with CPython 3.12 and assertions:

```sh
python3.12 -B scripts/research_package.py --package research/p104-fixed-contact-idle-capacity
```

The registered check authenticates the exact literal caller and
#7277 signed invoice by uncompressed SHA-256 and Git blob ID. Both
are bundled as compressed immutable inputs. [Exact source pins](PROVENANCE.json)
record their commit, path and original bytes. The replay rebuilds the
windows backward through the literal caller, enumerates all groups
and independently encloses each tariff using rational logarithm and
reciprocal-exponential bounds. It exercises rejection of a changed
input and a removed broad charge. [Certificate](CERTIFICATE.json)
and [expected receipt](AUDIT.json) give the exact rational bounds
and tested counts. The same replay works without Git or network
access from an extracted verified package export:

```sh
python3.12 -I -B research/p104-fixed-contact-idle-capacity/verify.py
```

The signed invoice is inherited and repriced from its exact frozen
histograms. This package verifies the fixed-contact scope. Native
operator and all-size supplier replay belong to the predecessor's
separate verification.

## Open next questions

Can a separately priced child have rank below the sum of the constituent
ranks? Use the literal selected-stage sets to bound an optimistic
union-rank price over the whole group stock before choosing any site.
A favorable price requires a common-chart arbitrary-input construction,
signed phase, ownership, restoration and a fully charged invoice.
Changed contact order, new native work, and reuse of one lane across
groups are outside this result.

## Credit

#7113 supplies the literal signed caller. #7277 and its #7274 and #7244
predecessors supply the complete comparable invoice and retained native
construction. #7144 proves diagonal body-gauge rigidity on the caller.
#7166 studies rectangular adapters for two paid complex MOVEs. #1920
and #1924 address reciprocal and clean invariant Clifford encodings.
#7207 extends the #7002 coordinate coalescing obstruction to a fixed
independent basis, and #6391 gives an exact signed completion bound on
a different six-field inventory. The bound here prices fixed-contact
lane capacity on the literal #7113 schedule. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
[#7144](https://github.com/CrocSwap/integer-mult-bounds/pull/7144)
[#7166](https://github.com/CrocSwap/integer-mult-bounds/pull/7166)
[#1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920)
[#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924)
[#7207](https://github.com/CrocSwap/integer-mult-bounds/pull/7207)
[#6391](https://github.com/CrocSwap/integer-mult-bounds/pull/6391)

OpenAI Codex and subagents materially assisted proof, implementation,
independent verification and packaging. Apache-2.0. [Notice](NOTICE)
