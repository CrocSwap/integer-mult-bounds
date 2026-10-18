# A strict integral packing improvement for PR2979

A 103-row journal moves 44 helper roles in PR2979's literal T74 allocation.
It reduces six exceptional full capacity-48 bins to two and strictly lowers the
complete conditional recursive moment. Both an independent geometry checker and
the retained owner checker accept all 271,728 roles. The scalar words, 666-call
order, provider dispatch and helper widths are identical to the source.

The certified moment endpoint increases from
`[0.0017290339826465135177175, 0.0017290339826465135177176]` to
`[0.0017290342130642563095108, 0.0017290342130642563095109]`.
The gain is between `2.304177427917932e-10` and `2.304177427917934e-10`.
This closes about 12.93% of the predecessor's remaining fractional-packing gap.
It is a finite allocation and moment improvement, conditional on the inherited
supplier model. It is not a new admitted multiplication exponent or a change
to the selected result.

The scientific source is Marius-Paul Dumitrean's
[PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979), head
`be191346391661f4d35fc0d1508d0a6029572576`. The base is canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
[Sources and exact blobs](SOURCES.json), [task and overlap](TASK.json),
[exchange journal](EXCHANGE.json), and [deterministic receipt](RESULT.json)
make the result independently replayable. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18979056)
records coordination.

## The exchange

The only changes to the bin-pattern histogram are the following eleven-bin
identity. The suffix is the bin capacity. Each number inside brackets is one
helper width.

```text
old                                      new
1 [7,9]@16                               1 [8,8]@16
6 [9,9,9]@32                             1 [7,8,8,9]@32
4 [4,8,9,9,9,9]@48                       1 [9,9]@32
                                         4 [4,9,9,9]@32
                                         4 [9,9,9,9,9]@48
```

The capacity counts and every width count agree exactly. Other bins can exchange
roles of equal width while retaining their pattern. Thirteen homogeneous-width
relay paths place the displaced roles in legal windows. The journal records
44 location changes and 59 additional offset changes for compaction. Its
preimages bind every edit to the literal source fill. The geometry checker
reconstructs windows from source events and checks complete helper coverage,
physical-family exclusions, capacities, disjoint masks and compact prefixes.
No solver is needed for replay.

With `H_r(b)=r(73/r)^b`, the complete profile changes by

`Delta(b) = 4 H_1(b) + 4 H_3(b) - 6 H_5(b) + H_14(b)`.

The source profile and new profile have the same rank mass, `4,816,512`.
The latter is

```text
{1:1645684, 2:470196, 3:159472, 4:71928,
 5:13710, 8:5328, 14:1, 48:28190}.
```

It includes every local child at every call and every idle remainder. The
physical inventory remains `66,304 + 408 + 8 + 91 + 2 = 66,813`.
Both literal words' cleanup namespaces contain precisely the same 91 private
buffers. The older generic owner engine reports `66,794` using its historical
fixed `+490` term, which corresponds to 72 buffers. Its raw field is retained
as a diagnostic. The exposed physical total charges the actual 91 buffers,
as PR2979 already does.

## Exact sign proof

For every `0 < b <= 1/100`, this exchange strictly improves the moment.
Factor `Delta(b)=73^b f(b)`, where

`f(b)=4+12*3^(-b)-30*5^(-b)+14*14^(-b)` and `f(0)=0`.

The elementary bound `exp(-x) >= 1-x` and the rational logarithm bounds

```text
109/100 < log(3) < 11/10
log(5) < 161/100
263/100 < log(14) < 66/25
```

give, throughout this interval,

```text
f'(b) <= 30*(161/100)
         - 12*(109/100)*(989/1000)
         - 14*(263/100)*(1217/1250)
       = -60509/125000 < 0.
```

Thus `Delta(b)<0`. To certify the logarithm bounds with rational arithmetic,
put `z=(y-1)/(y+1)` for `1<=y<=2` and
`L(y)=2*(z+z^3/3+z^5/5)`. The positive atanh series gives

`L(y) <= log(y) <= L(y)+2*z^7/[7*(1-z^2)]`.

Use `3=2*(3/2)`, `5=2^2*(5/4)` and `14=2^3*(7/4)`.
[The executable certificate](moment.py) checks these inequalities exactly.
A separate directed integer-interval implementation with 64 logarithm terms,
24 exponential terms and explicit tails encloses both roots of
`sum_r n_r H_r(b)/(73*896*74)=1`. Both roots lie inside the proved sign interval.

The unchanged local profile's inherited fractional cap is bracketed by
`[0.001729035764875516181444, 0.0017290357648755161814441]`.
The new endpoint realizes at least `0.9999991024990394` of that cap, leaving
about `1.551811259871933e-9`. This package compares to the source's pinned cap;
it does not independently recertify the fractional optimum or prove integral
optimality.

The sign inequality is independent of the common local profile. It therefore
also applies when another valid supplier has the same ordered widths, chronology
and unchanged background bill. The final overlap check found Jeremy Kothe's
[PR3015](https://github.com/CrocSwap/integer-mult-bounds/pull/3015), head
`e244296debb45fe6f4da84d29e4d64fbab55fda0`, which reports a restore-word edit
with the same fill, widths and buffers. Its edit and any composed admission
are not validated here.

## Reproduction and coverage

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-integrality-exchange
```

On a machine using uv, the equivalent command is
`uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/rank7-integrality-exchange`.
The registered replay checks source SHA256 bindings, the literal journal, full
old and new owner geometry, exact moments, the sign proof, the retained checker
comparison and eleven rejecting controls. Four behavioral test groups cover
literal journal/preimage behavior, changed source bytes, exact root/sign values,
and identical normal/optimized CLI results. All conditions remain active under
`-O`. [VERIFY.json](VERIFY.json) declares every external replay input.

Discovery used one SciPy 1.16.1 integer-pattern proposal. A 50-second broad local
placement solve found no incumbent; a restricted fixed-pattern model was
infeasible. A deterministic augmenting-path construction then found the retained
relay journal. Those failures are limited to their models. They are not packing
obstructions. The decision log records the attempts. Discovery dependencies are
unnecessary for the certificate or registered replay.

The finite model still assumes the source words' native width and paid-local
contracts. This package binds their endpoint lengths, reports and private
namespaces, but does not reprove their scalar/native arithmetic. Arbitrary dirty
restoration, native/warp dependencies, complete physical backing and movement,
precision/prefix/tape, complete supplier/outer release and all-size/compiler
obligations have not been replayed for this changed allocation. None of their
unknown costs is assigned zero by this result.

## Open next questions

1. Run the existing fresh-native/admission/outer chain on the journal-derived
   fill. This is the next test that can turn the finite gain into a conditional
   supplier improvement. Start by applying `EXCHANGE.json` with `verify.apply`
   to the pinned source fill and using the resulting complete profile. The
   source chain's environment and inherited admission obligations remain the
   blockers; old receipts do not bind this new fill.
2. Can a larger replica count remove the remaining two exceptional bins without
   losing chronology? First derive an exact pattern relation and a fully charged
   candidate, then apply source-window/family checks. The unchanged fractional
   cap bounds the possible gain. This session stops after one strict legal
   improvement and does not claim that another search is justified or optimal.

## Credit and implementation choices

Nick Petalas contributes the relay journal, exact improvement proof and new
checks. Source credit remains with Marius-Paul Dumitrean for PR2979, Mason Hale,
Jeremy Kothe and Jeremy Diviney for the word/frame/extraction lineage, Yiyang Lu
for chronological flow and realization, Tekalign for owner-window conventions,
Ross Richardson for PR2987/3010's complementary packing audits, Dugongue,
icekylinx, themilkman216 and the retained geometry/native/owner contributors.
No source archive or pinned predecessor is modified. Apache-2.0.
Substantial automated assistance was used; no independent human or formal-kernel
review is claimed.

The Build the Lever principle led to the replayable journal and checker rather
than a numerical search receipt. Prove It Works required checking every literal
role and the complete moment before retaining the candidate. Power of Ten led
to explicit finite bounds, checks active under optimization and scoped state.
Python's managed allocation is a documented deviation from fixed allocation;
the maximum working domain is 74 replicas, 666 calls, 271,728 roles and 149,184
bins. Only the pinned retained comparison module is executed dynamically, after
its source digest passes. The independent geometry and moment code import no
predecessor Python modules. Rejection callbacks execute synchronously with
bounded targets. Python warnings are errors in validation. Ruff correctness,
binding, import and modernization rules are checked; repository-wide typing and
pedantic documentation/style enforcement are not introduced by this package.
