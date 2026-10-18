# Reuse coefficient work inside adjacent JP8 scalar runs

**Finite complex-supplier circuit improvement; no new κ.** On the selected
PR626 JP8 word, retaining one prepared coefficient across adjacent compatible
additions saves **18,510 forward** and **46,400 backward** real-component
primitives beyond PR696's per-macro lowering. Every logical scalar operation,
frame, recursive child and non-scalar event retains its original order.

| JP8 orientation | Selected Horner invoice | Per-macro lowering (PR696 mechanism) | With adjacent reuse | New saving over per-macro |
|---|---:|---:|---:|---:|
| Forward | 257,232 | 200,380 | 181,870 | 18,510 |
| Backward | 257,280 | 200,396 | 153,996 | 46,400 |

These are exact primitive counts, not execution-time measurements. The total
reductions from the selected invoice are 75,362 and 103,284. Only the final
column is new beyond the credited per-macro mechanism. No selected emitter,
certificate, owner map, source package or `upstream/` file is edited.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python3 -B research/complex-coefficient-reuse/verify.py
```

Expected final line:

```text
PASS_JP8_COEFFICIENT_REUSE columns=716+9 savings=18510,46400 controls=14
```

The command is offline and read-only. It checks the exact source pins,
regenerates the lowering, replays both complete scalar programs, reconstructs
the retained local invoice and compares every field of [EXPECTED.json](EXPECTED.json).
It checks 716 logical input columns (including all 492 dirty helpers) plus
arbitrary initial values of eight private centres and one coefficient work
register. The private inputs are erased; the logical helpers are restored.
The forward and inverse-transpose scalar boundaries are checked separately.

The 14 negative controls include omitted preparation/halving/clearing, wrong
sign or target, corruption between target updates, source aliasing, and crossing
source/coefficient/frame/phase boundaries. An endpoint-neutral excursion checks
that intermediate growth cannot hide behind correct endpoints. Additional
positive controls cover mixed signs, repeated destinations, dyadic magnitudes,
and the signed denominators of inverse scale macros.

To write a fresh certificate for comparison, pass `--write /tmp/reuse.json`.
This explicit mode writes only its named output. It still checks all inputs,
replays and negative controls, but deliberately does not compare EXPECTED.json.

## Scope of the experiment

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected conditional κ is `51110230636731/31250000000000000`, from PR626
at `660de893d27bb7abd1d5b01b1640207528a5c851`; the reviewed PR622 construction
head is `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
[SOURCES.json](SOURCES.json) pins every consumed source and receipt, using
decompressed payload hashes for gzip inputs. The verifier also binds the
canonical word and local program to the selected package's SPEC.

OS assignment seed **39** selects the complex-supplier track and, by
`39 mod 2 = 1` in `[CK, JP8]`, the JP8 provider. [CLAIM.json](CLAIM.json) records
the three candidates, decision, time budget and local claim. The exact domain
is all maximal contiguous runs of scalar additions in both pinned JP8 programs
with the same source, same absolute non-unit dyadic coefficient and same frame.
No target may equal that source. Every non-scalar event, scale, copy, clear,
unit coefficient, or change of source/magnitude/frame ends a run.

This is a deterministic census and rewrite, not a stochastic search. The
stopping rule is exhaustion of the two 27,909-event programs. Completed
coverage is 1,087 runs / 3,496 scalar events forward and 1,088 runs / 7,336
scalar events backward; the longest runs have lengths 28 and 64. The checker
verifies maximality. The certificate hashes the complete run inventory and
primitive stream and includes the seed-selected 40th run in each orientation.
No optimality claim is made outside this exact rewrite rule.

## Mechanism and complete local cost

Consider a run of `m` additions `T_i += ε_i q S`, where `q = a/2^b > 0`,
`q != 1`, `ε_i` is ±1 and each `T_i != S`. The source cannot change inside
the run. With the existing private work register `W`, perform:

1. Copy `S` to `W`; use binary Horner doubling/addition to form `a S`;
   halve `b` times to obtain `q S`.
2. Apply the original ordered signed updates `T_i += ε_i W`.
3. Clear `W` once at the end of the run.

All source reads, copies, doubling, halving, accumulation and clearing are
literal, billed primitives. Let
`P(q) = 1 + (bit_length(a)-1) + (popcount(a)-1) + b` be the preparation cost
per real component. Separate copy-initialized macros cost `m(P(q)+2)`;
the fused run costs `P(q)+m+1`. The saving is therefore
`(m-1)(P(q)+1)` per real component, or twice that for complex data.
The largest backward run has 64 targets, so it is still a fixed finite macro.

For example, forward events 13,587–13,590 read `L638/4` into `L166`, `L214`,
`L130`, then subtract it from `L151`, all at frame 423. Four separate
copy-initialized macros cost 20 primitives per real component; one copy,
two halvings, four signed additions and one clear cost eight. The saved
24 real-component primitives are fully included in the census.

No helper or stream is added: the inventory remains 492 logical helpers,
eight private complex centres and two real coefficient-work streams. The
existing coefficient stream stays at a single frame for each run and is
cleared before any intervening frame, phase, adapter or recursive event.
Retaining it across these adjacent operations requires grouping them into one
scalar microcircuit; an implementation retaining the old promise “clear after
each individual scalar macro” would need that interface updated explicitly.

The complete local paid-child histogram remains

```text
{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}
```

It contains 3,606 children. Both programs still have 22,693 logical scalar
macros. Keeping the full old adapter allowance gives
`A = 16(22693 + 3606 + 716 + 8) + 64·73 = 437040`, and the unchanged
compiler factor is `K = 64·74^3 = 25934336`. The conservative local finite
bound changes only from `257280 + A K = 11334342462720` to
`181870 + A K = 11334342387310`. The worst orientation switches to forward.
The checker reconstructs the old value against SPEC before calculating this
new local arithmetic. Wrappers, source access outside the fused runs, centre
copies, cleanup, phase work, routing, residuals, ownership and all recursive
children retain their full original charges. There is no new global invoice.

The supplier moment and outer assembly use the unchanged paid histogram and
ownership, so this optimization does **not** improve the accepted κ. Its
deliverable is a cheaper finite scalar circuit and exact integration evidence.

## Correctness and growth argument

Preparation overwrites arbitrary private input and yields `W = q S`.
No destination is `S`, so this equality holds until the final clear, including
when destinations repeat. Each ordered destination update equals its original
scalar operation. The final clear reproduces the original private boundary.
Induction over chunks therefore preserves the full logical program, including
arbitrary correlated helper dirt and both orientations. The separate macro
and primitive interpreters compare every touched row at each chunk
boundary, then check the complete final shear on all input columns.

Binary Horner partial integers lie between zero and `a`, and halving decreases
their magnitude. A retained `q S` is a value already present in the reference
preparation of that run. Logical updates are identical, so retaining `W`
introduces no larger coefficient-work or logical-register l1 envelope. The
checker propagates an independent nonnegative envelope through every primitive
and reproduces the old invoice maxima exactly:

- Forward: `4536094588619580433782972610869617 / 281474976710656`.
- Backward: `16753412757380464429924108070201913461 / 8388608`.

Both remain below the existing `2^192` local payload allowance. The checker
also verifies that all non-scalar events are retained in their original order;
it does not reprove their geometric or analytic meaning.

This finite rational identity is not a formal proof of the full multiplication
theorem. All-size compilation, common-label and mutable-basis realization,
pooled whole-call hosting, normalized residuals, precision/tape/exact recovery,
analytic transfer and the retained bit-supplier assumptions remain inherited.
Production adoption needs an explicit grouped-macro interface and updated
emission/invoice bindings followed by the selected cold/global replay. No
fresh Lean, phase, controller or global assembly verification is claimed here.

## Related work and attribution

@thakrarsagar's PR696, pinned at `5a3f983715027c4fd83f50bc9001d4b18463bed1`, supplies the
credited per-macro idea: copy initialization instead of clear-plus-add, and
direct signed accumulation for unit coefficients. Its reported JP8 counts
are independently reproduced here. No PR696 code is imported. The new
mechanism shares preparation across multiple adjacent macros; it is useful
in addition to that contribution, rather than merely repeating its lowering.
Historical PR411 is credited for explicitly priced dyadic coefficient words.


### Concurrent work checked before publication

While fork access was being arranged, @ellipsi2 published **PR722** at
`a0766ab0fab379e1997fadc3ca157578d57986c1`. It independently uses the same
sharing mechanism in the **forward full-frame cleanup**, covering 999 runs
and 3,022 additions under the original Horner lowering. That overlap is
explicitly credited; this submission does not claim priority for the mechanism.
Its additional coverage is all other eligible scalar phases, the backward
zero-frame precondition, and the verified composition with PR696's lowering.
The existing `chunks` iterator on the pinned programs gives this phase census:

| Orientation / phase | Runs | Additions | Saving beyond per-macro copy lowering |
|---|---:|---:|---:|
| Forward A | 11 | 28 | 102 |
| Forward centres | 8 | 224 | 1,728 |
| Forward B | 69 | 222 | 1,038 |
| Forward full-frame cleanup | 999 | 3,022 | 15,642 |
| Backward zero-frame precondition | 1,088 | 7,336 | 46,400 |

The cleanup's 15,642 savings use the cheaper per-macro baseline, whereas
PR722 reports 19,688 against original Horner; these are different baselines,
not contradictory measurements. Outside cleanup, this package adds 2,868
forward and 46,400 backward saved primitives over per-macro copy lowering.

Jeffrey Cox (@namredips)'s **PR739**, at
`abb9825202dba6f9bc95c7df8d12d86088fdff1a`, extends PR722's forward cleanup
class to coefficient magnitudes related by powers of two. This package does
not implement that extension or claim combined savings with it. Chris Pagolu
(@AllStars101-sudo)'s **PR734**, at
`ba76ba3321d000c8996b0b254bcf0d7260e1bbb6`, and **PR723** supply further
per-macro signed-digit lowerings; those are also outside this composition.
No code or certificate is imported from these concurrent submissions.

PR681 resynthesizes a factory scalar word, and PR698 exhausts fixed-boundary
CK frame choices. This package changes neither object. It does not reopen
the closed CK frame class, delivery rigidity results or K-triangle relocation
neighborhoods. [OVERLAP.json](OVERLAP.json) records the coordination checks.
No pinned sprint issue existed, so the claim is local.

Credit remains with Jeremy Kothe's PR622 construction, Chafik Boukhalfa's
PR626 owner package, DreamingOfClouds' native/emitted cold-helper work,
icekylinx's PR425/433/531 scalar and direct-delivery lineage, eumemic's
call-specific invoice and retained bit supplier, Rohan Arun's corrected
complex recurrence, and the predecessors listed in the
[maintainer review](../../docs/research/community-k492-review.md) and
[retained notice](../complex-k492-owner-repair/NOTICE.md).

Contribution prepared for **@taizaki69** with substantial **OpenAI Codex**
assistance in research, implementation, proof analysis, verification and writing.
No delegated-agent or independent human review is claimed. New material is
Apache-2.0 under the repository [LICENSE](../../LICENSE); existing sources,
licenses, notices and AI disclosures remain intact.
