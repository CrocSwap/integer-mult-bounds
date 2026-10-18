# Group A's native widths through the shipped T74 invoice

**Finite native/interface audit; no new kappa or supplier admission.**

Both literal PR2979 providers pass the mixed-entrance check for group A.
Helpers 450, 451, 508 and 509 enter at `[30]` and end at
`W = [256,128,64,38,20,10,1]`. Their emitted residual pair is `115:261`,
with width **six**, not the terminal dimension seven. Helper 331 enters at
zero and uses pair `0:261`, with width seven. Exact native identities include
global phase and both orientations. These widths bind to all 3,330 group-A
placements in the shipped T74 allocation.

The contribution joins the complete direct group-A boundary to its actual
owner placements. It corroborates existing native identities and does not
newly discover the construction, local saving or published complete histogram.
The local comparison and normalized endpoint checks explicitly reuse credited
independent checkers. The claim is in discussion [#2612][thread].

### Existing coverage and the added check

[PR3038][3038] already checks both residual classes within its V45 dependency
cone: `0:261` in both orientations and `115:261` in the inverse-transpose
orientation. The latter also implies its forward identity by conjugation.
The original claim's inventory of PR3006/3008 was incomplete; final overlap
review identified and credited this stronger predecessor before submission.
These residual equalities are corroboration, not newly missing mathematics.

PR3038's roots are helper249/private953. Its pinned receipts contain none of
the five group-A post-wrapper events. For helpers 331/450/451/508/509, this
audit checks 122/19/19/20/20 direct events per orientation. Respectively,
22/19/19/20/20 forward events and 61/3/3/5/7 inverse-transpose events are outside
the earlier cone; the two providers agree. These are per-helper counts and
may share events, not counts of distinct newly proved native identities.
[RESULT.json](RESULT.json) records the exact indices and source-bound coverage
comparison. The PR3038 receipts were inspected, not freshly replayed here.

The added coverage is the complete direct path through each actual post
wrapper, all ten group helper/private normalized endpoints, and the explicit
native-width/ordered-helper/physical-slot join for every group placement.
The complete peer-native closure still remains separate. Concurrent #2612
private-free and final-fill control audits should be consulted before taking
those follow-ups; this package does not reconstruct their work.

## Exact native statement and source binding

The source is [PR2979][2979] at
`be191346391661f4d35fc0d1508d0a6029572576`; the base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) records exact Git blobs and SHA256 hashes.
The 14 construction inputs also match the original PR2979 head byte for byte.
The native producer, exact kernel and retained checkers are authenticated
before execution. No frozen predecessor is modified.

For entrance `E` and terminal `U`, write the native residual as
`S(E,U) = T_U T_E^-1`. The source compiler produces `S = L F_w R`, where
`F_w` is the retained coordinate Fourier primitive on the first `w` address
axes. A separate exact Gaussian-integer kernel checks all 512 columns of
that identity, and the emitted inverse wrappers satisfy

```text
L^-1 S(E,U) R^-1 = F_w,
w = dim(U) - dim(E).
```

For these unitary operators, inverse transpose is entrywise conjugation.
The same chronological wrapper arrangement gives `F_w^-T`, with the
remaining `9-w` axes unchanged. The check does not substitute the adjoint
or reverse the execution order.

| Helper(s) | Entrance | Parent terminal dimension | Parent width | Joint/final width |
|---|---|---:|---:|---:|
| 331 | zero | 8 | 8 | 7 |
| 450, 451, 508, 509 | span(30) | 8 | 7 | 6 |

Here 30 = 20 xor 10 lies in W. Treating the entering helpers as cold would
select the wrong native operator even if a rank field were edited to six.
The cold right wrapper and the entering right wrapper are not interchangeable:
the all-column check rejects that substitution. A different contained line,
`[10]`, has the same dimension but also fails with the actual `[30]` recipe.

This width is exact within the monomial/Fourier/monomial format: every column
of `F_w` has exactly `2^w` nonzero entries, and invertible monomial factors
preserve that count. Thus a checked width-six residual cannot be represented
by such a format with fewer than six Fourier axes. This is not a lower bound
for arbitrary native circuits or a claim that the 512-by-512 operator has
matrix rank six; it is unitary and has full matrix rank.

The verifier regenerates both complete emitted programs with the unchanged
transport/emitter and reconstructs the full serialized adapter file using
the original generation convention. The uncompressed `LOCAL-CHECKS.json`
and `RESIDUAL-ADAPTERS.json` hashes match PR2979's retained native receipt.
Both regenerated event streams also match the counts and canonical event
digests inside that pinned receipt.
Generation is not presented as an independent checker. The independent part
compares each selected original entrance/terminal pair, direct scalar clock,
climb and cleanup lifetime against the emitted records, then decodes the
selected native recipes through the separate exact kernel.

Each provider has 22 distinct group-A climb pairs, two shipped residual pairs
and two parent residual pairs checked exactly. The emitted climb ranks are
`1,1,1,1,1,2` for 331 and `2,2,1,1` for each entering helper. The parent
residuals are generated comparison identities; no complete parent native
program is regenerated. The final pair keys and adapter hashes are bound to
the shipped program, rather than to an interchangeable candidate recipe.

There are 112/11/11/12/12 direct scalar operations for helpers
331/450/451/508/509 and their private buffers, respectively. Scalar clocks
include intervening operations on other roles. Moving a direct operation
across a disjoint scalar therefore fails the check even when its order among
the helper's own operations is preserved. Private operations occur after
allocation and before free; the inverse left wrapper follows cleanup.

## The group, its control and the invoice

The retained [PR2993][2993] checker reconstructs group A on each parent word
and a control with the same 21 partner-frame edits but only helper331 lowered.
No scalar or cleanup operation changes. Their exact local differences are:

```text
joint:      -H1 + 20 H2 - 14 H3 + 2 H4 - 2 H5
single331:  3H1 + 20 H2 - 14 H3 + 2 H4 - 2 H5
```

`Hr` means one paid rank-r child. Substitution into the source's integer
surrogate and its 2,091,300-unit width guide reproduces joint margin
`+42,541` and single margin `-58,943`. The four additional endpoints save
exactly four H1 children locally. This control keeps the group's partner
frames fixed; it does not optimize every possible single-helper frame path.
The guide is not an independently certified physical idle tariff.

The new time-major recount reads every one of the final allocation's
271,728 placements, checks role completeness, source windows, per-call
physical-family uniqueness, capacities and compact prefixes, and bills all
149,184 bins including empty bins. Original helper names map to ordered
helper indices `107,226,227,279,280`; those are explicitly joined to the
emitted native residual widths. Replacing helper450's width six with terminal
dimension seven fails the actual allocation check.

| Item | Exact count/profile |
|---|---|
| Calls | 250 base + 416 extra = 666 |
| Local profile per call | `{1:2445,2:706,3:232,4:108,5:18,8:8}` |
| Width inventory | `{4:26,5:2,6:16,7:52,8:99,9:213}`, mass 3,283 |
| Actual idle bill | `17310 H1 + 4956 H3 + 1728 H5 + 28190 H48` |
| Complete recursive bill | `{1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190}` |
| Complete rank mass | `4,816,512 = 65,088 * 74` |
| Nominal physical stock | `66,304 + 408 + 8 + 91 + 2 = 66,813` |

The complete recursive moment input is therefore
`sum(n_r * (r/73)^(1-a)) / (896*74)`. All 91 private names remain charged.
The five group-A private buffers already exist in the parent; stage one
retains 86, and five later extractions produce the final count 91.
The independently recounted final bill agrees with the source. It includes
the other four groups, later extractions and rewrites, so it is not an
isolated group-A gain attribution or a legal whole-supplier single-control
comparison. Those counterfactual allocations are not supplied here.

The retained [PR3006][3006] reverse-covector engine also checks 40 output
rows: five helpers and five private buffers, two providers, two orientations.
Each is exactly its own input over the full free operator algebra, with
632 original and 91 private inputs. Thus each covered private output is zero
when its private entrance is zero. This extends that engine's checked domain;
it is not a newly independent implementation of the endpoint algorithm.
Deleting actual cleanup gate178, `private1154 += private934`, breaks this
identity and is rejected by the behavioral control.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/rank7-group-a-entrance-audit --check-only
python3 -B scripts/research_package.py --package research/rank7-group-a-entrance-audit
```

Expected verifier output begins `PASS_GROUP_A_ENTRANCE_NATIVE_INVOICE`.
The hook also runs seven behavioral test groups. They cover wrong entrance
and phase, a cold-wrapper alias, omitted/wrong wrappers, premature private
free, changed scalar signs and clocks, omitted cleanup, missing/duplicate
roles, bad capacity, terminal-dimension misuse, source corruption and duplicate
JSON keys. Direct `verify.py --emit` prints deterministic evidence without
rewriting [RESULT.json](RESULT.json). Input hashes are checked again after
the replay. The normal replay writes only temporary work outside the package.

Source production uses fresh temporary script copies and bounded foreground
subprocesses; inherited `PYTHONOPTIMIZE` is removed from those subprocesses.
Authenticated imported checkers are compiled from source bytes rather than
loaded from a preexisting bytecode cache. The finite domain is two 704-name
source words, 512 address columns, 666 calls and 408 helpers. Raw and decoded
inputs are capped at 64 MiB; each source subprocess has a 120-second timeout.

## Limits

The nominal stock arithmetic is a reconciled declaration, not a proof of
physical storage adequacy. The other helpers' native dependency closure,
warps, physical backing and movement, and precision/prefix/tape costs remain
inherited. The 86 other private endpoints were not checked. No complex root
or packing cap, bit supplier cap, outer coupling/release, or all-size,
compiler and analytic implication was independently replayed. Neither
supplier is newly admitted and the selected frontier is unchanged.

## Open next questions

The next useful native check starts from the 55/4/4/5/5 private-touch
inventories for this group and binds every peer transition and warp reaching
those endpoints. It matters because direct local identities do not establish
the whole physical caller. Common-chart and peer-native correctness are the
blockers. After that, the exact PR2979 physical/prefix inputs and both supplier
caps need independent review before using its claimed exponent. Another
lowering census or another surrogate-price evaluation does not close these
obligations. Structured questions are in [TASK.json](TASK.json).

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Marius-Paul Dumitrean supplied PR2979 and PR2942's construction; Dugongue
supplied the PR2969 comparator and PR2839's owner engine. Nick Petalas
supplied the reused PR2993 frame checker and PR3006 covector
engine; PR3008's zero-entrance event audit and PR3014's frozen-parent invoice
are method predecessors. ToikY/PR3038 already checked the two native residual
classes inside the V45 cone; its exact coverage is explicitly retained above.
Ross Richardson/PR2987 supplied the complementary
packing audit, and Gonzalo Mier/PR3079 already replayed the published T74
aggregate arithmetic without owner chronology. Jeremy Kothe supplied frame,
cleanup and rewrite work; Mason Hale and Jeremy Diviney supplied the
paired-extraction chain. The native
compiler retains icekylinx's credit; the separate exact Gaussian kernel is
Sagar Thakrar's. DreamingOfClouds and chafreaky/PR458 supplied the residual
wrapper convention. Earlier helper450 event/scalar audits by bbMisk/PR1611
and ToikY/PR1710 concern the older k8 word, not this changed endpoint.
Retain Tekalign, Yiyang Lu, Cinna Davis and the geometry/owner/native lineage
credited in those sources. Apache-2.0; original notices remain in place.
No independent human or formal-kernel review is claimed.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
[2993]: https://github.com/CrocSwap/integer-mult-bounds/pull/2993
[3006]: https://github.com/CrocSwap/integer-mult-bounds/pull/3006
[3038]: https://github.com/CrocSwap/integer-mult-bounds/pull/3038
[thread]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19001817
