# Exact joint T29 bin-count spectrum

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive proof with exact finite corroboration. In the
historical fixed U8 whole-helper packing model at T=29, let x count
capacity-16 `{9,7}` bins and y count capacity-8 `{4,4}` bins. The exact joint
projection is the full integer rectangle

```text
4824 <= x <= 12992,       0 <= y <= 8286.
```

Every pair in this rectangle occurs. There is no additional coupling or
parity restriction between these two counts. This answers the explicit Open
next question in woklerx's [PR1844](https://github.com/CrocSwap/integer-mult-bounds/pull/1844).
The new result is the joint projection and its inventory-preserving exchange.
The predecessor's one-dimensional x range and starting construction are cited
premises, not new results or audit targets. No kappa improvement is claimed.

## Model and cited premises

The capacity quotas at `(8,16,32,48)` are `(19488,12992,12992,12992)`.
The helper demands at widths `(4,5,7,8,9)` are
`(20880,8352,14094,31842,56376)`. The required remainder profile is
`{0:49770,1:4,2:1,48:8689}`. Helpers remain whole. No chronological,
geometric, chart or physical owner constraint is imposed.

Hanhong Zhao's [PR1160 proof](../t29-capacity-audit/PROOF.md), Lemmas 1-2,
shows that every realization uses tight patterns. Its four remainder-one
bins each contain one four, its remainder-two bin contains at least one
four, and each of its 4,303 full capacity-48 bins contains at least one four.
It also proves the necessary x range. We use these statements as published
premises, without rerunning their pattern census.

Woklerx's [PR1844 construction](../t29-capacity-projection-spectrum/README.md)
gives a realization for every integer x in that range with y=8286. Write
`x=4824+2t+e`, where e is zero or one. Its groups outside capacity eight
that contain eights are exactly:

| Capacity | Pattern | Number of bins | Eights per bin |
|---:|---|---:|---:|
| 16 | `{8,8}` | `8168-2t-e` | 2 |
| 32 | `{9,9,8,4}` | 1 | 1 |
| 32 | `{9,8,8,7}` | e | 2 |
| 32 | `{8,8,8,8}` | t | 4 |
| 48 | `{9,9,9,9,8,4}` | 4303 | 1 |

All other groups are retained unchanged. Exact proof and construction bytes
are pinned as historical provenance in [SOURCES.json](SOURCES.json).

## Proof of the joint range

Necessity of the x interval is PR1160's result. Nonnegative counts give
`y>=0`. The forced bins cited above consume at least `4+1+4303=4308`
fours outside capacity eight. The y distinguished bins consume another 2y,
so `2y+4308<=20880`, giving `y<=8286`. This is a new necessary bound on y.

For sufficiency, start with PR1844's realization for the desired x. The table
contains exactly

```text
2(8168-2t-e) + 1 + 2e + 4t + 4303 = 20640
```

eights outside capacity eight, independently of x. Replacing an eight in any
one bin by two fours preserves its total width, capacity tag and remainder.
It also preserves its signed price since an eight and two fours both cost
-2 in the inherited price system. Any subset of these 20,640 occurrences
can be replaced, including several occurrences within a bin.

Choose any desired integer `0<=y<=8286` and put `k=8286-y`. In exactly k
of the starting capacity-8 `{4,4}` bins, replace the two fours by one eight.
In exactly k of the listed external eight occurrences, make the reverse
replacement. There are enough occurrences because `k<=8286<20640`.
The two changes cancel in the four and eight inventories. They leave all
other helper demands, all bin quotas and the entire remainder profile fixed.

The external move cannot change the number of capacity-16 `{9,7}` bins:
those bins contain no eights, and replacing eights creates only fours.
The capacity-eight move reduces y by exactly k. Thus the result has the
prescribed pair `(x,y)`. This proves sufficiency for every integer pair,
without interpolation or an integral-relaxation assumption.

The verifier implements the construction using counts of equal patterns.
For each group with n bins and s eights per bin, spending a replacements
converts `floor(a/s)` complete bins, at most one partial bin, and leaves the
rest unchanged. This realizes every integer budget a between zero and ns.
No individual-helper splitting is used.

## Verification and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/t29-joint-bin-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/t29-joint-bin-spectrum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/t29-joint-bin-spectrum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/t29-joint-bin-spectrum --check-source-history
```

The direct commands emit `PASS_T29_JOINT_BIN_SPECTRUM` in a generated JSON
receipt bound to every package file's SHA256. They write no files and import
no predecessor executable. The finite checks construct new joint witnesses
and check every capacity, every helper width, every remainder and both named
projections. They test the external pool at every x, every y on four x slices,
and six boundary/interior y values at each remaining x. Local exchange checks
cover every convertible starting shape. Malformed coordinates, missing
compensation, an extra bin and a false projection must reject under normal
and optimized Python. Universal coverage follows from the written exchange
proof; the sampled interior grid is corroboration, not exhaustive pair coverage.

Local normal and optimized runs each pass 82,138 joint constructions, 8,169
pool identities, 15 local exchange checks and 11 rejection controls. The two
registered commands took 1.65 and 1.65 seconds on CPython 3.12.15/macOS arm64.
These are check durations, not performance improvement measurements.

The selected source-binding orientation also passes with
`scripts/research_selected_baseline.py`. No selected operator replay,
predecessor census, Lean or Docker build is run. Independent human and formal
proof-kernel review are unclaimed.

## Scope and implementation bounds

The selected-packing card changes to this historical arithmetic side question.
The joint range describes assembly freedom within a known sharp remainder
profile. It supplies no additional recursive saving and makes no claim about
the changed selected #4470 supplier. Physical matching, owner geometry,
chronology, charts, storage, precision and a complete caller remain unpriced.
No further construction expansion follows from this result.

The verifier has no recursion, subprocesses, network access or generated code.
It retains one construction at a time, with at most 36 pattern groups and
12 widths per group. Its outer loops range over 8,169 fixed x coordinates and
at most 8,287 y coordinates. Each replacement loop has at most four steps.
Functions remain below 60 physical lines; explicit exceptions retain all
contracts under optimization. Warning-strict execution supplies diagnostics.
AST syntax and function-size inspection pass. No standalone linter or static
type checker is installed in the execution environment.
CPython's dynamic objects and integer arithmetic are a managed-runtime
deviation from Power of Ten allocation constraints, bounded here by these
fixed domains. No speed or memory benchmark claim is made.

## Open next questions

1. What is the joint projection after also fixing the number of full
   capacity-48 `{9,9,9,9,8,4}` bins? This would distinguish the remaining
   exchange freedom from a genuinely coupled constraint. Start by retaining
   that coordinate in the same four/eight ledger. The present move changes it,
   so the rectangle theorem does not settle the three-coordinate problem.
2. Can any realization in this rectangle satisfy one literal historical owner
   and chronological constraint? Start with one named owner fixture and its
   legal windows. These constraints and their physical prices are absent here.

## Credit

Woklerx supplies PR1844's affine family and the explicit joint-projection
question. Hanhong Zhao supplies PR1160's capacity model, tight-pattern theorem
and capacity-tagged realizations. Chafik Boukhalfa supplies the PR795/PR890
prices and family; Jonathan Capalbo supplies PR942's all-replica relaxation;
woklerx supplies PR992's sharp T29 profile; Hao Yan supplies the PR858 owner
lineage. The new joint-range proof and verifier were produced by Nick Petalas.
All predecessor files and credit lines remain unchanged.
