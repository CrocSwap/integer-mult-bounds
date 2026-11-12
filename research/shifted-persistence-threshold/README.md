# A shifted persistence threshold that includes the missing seven-step case

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For
positive integers `d0,a,b`, set `D=d0*b` and

```text
T = 1                              if a>D,
    max(2,ceil((3D-a)/(2a)))        otherwise.
```

For every integer `m>=T`, `(m+1)^D < 2^a m^D`. The new `T` is never larger
than `ceil(27D/(17a))`, the sufficient threshold in unpaidmoon's
[PR #7450](https://github.com/CrocSwap/integer-mult-bounds/pull/7450).
At `(d0,a,b)=(1,1,5)` it lowers eight to the sharp seven. At `(1,2,5)`
the sharp four is preserved. The proof uses the classical decreasing
function `(2x+1) log(1+1/x)`. The threshold application is the new result.

[PROOF.md](PROOF.md) gives the complete argument, the exact endpoint
exception at `m=1`, and the persistence implication. The general sufficient
threshold is not an exact minimum. For example it gives fifteen at
`D=10,a=1`, where fourteen already works.

## Source and scope

This answers Open next question 1 of unpaidmoon #7450 at
`f9b9057f9befe744df7f6b58b61b53e77001af1f` using an `m`-dependent inequality,
instead of refining another pair `3^p<2^q` under its uniform bound. Its
power-pair census and persistence construction are cited, not audited or
replayed. The question is the source; the classical convexity argument is
self-contained. No predecessor code or data is needed to run this verifier.

The retained comparison is section 6 of
[the #7000 application review](../../docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md).
[SOURCES.json](SOURCES.json) pins that historical context, the selected
record and the originating card at canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`. These are provenance, not live
mathematical inputs. The source PR is external context with its exact head
and URL recorded in [TASK.json](TASK.json).

Card `uniform-transfer-audit` has changed scope to this auxiliary lemma.
It reduces a sufficient persistence region relevant to the effective
cutoff discussion. It neither constructs the initial successful index nor
discharges `precision_tape` or another framework assumption. Selected
`kappa=363005817/100000000000` is unchanged.

## Reproduce

Use CPython 3.12 and the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/shifted-persistence-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/shifted-persistence-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shifted-persistence-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shifted-persistence-threshold --check-source-history
```

On another machine, substitute its CPython 3.12 executable. The direct
verifier emits `PASS_SHIFTED_PERSISTENCE_THRESHOLD` in a JSON receipt
containing all six package-file SHA256 hashes and the exact enumerated
counts. Redirect it outside the checkout to retain a generated receipt.
No handwritten receipt or generated replay output is committed.

The bounded checks cover 255 shifted-power cases, 255 consecutive decreases,
9,216 parameter pairs and 27,648 one-step evaluations. In that parameter
rectangle, 4,753 threshold pairs strictly improve. Nine semantic controls
cover both sharp examples, strict equality, the `m=1` branch, a
sufficient-versus-necessary distinction and an overstrong slope. Eight
invalid parameter pairs must fail with the exact declared reason. Optimized
execution keeps every check active because checks do not rely on `assert`.

No selected cold replay, predecessor scientific suite, Lean or Docker run
is needed for this local theorem. No hosted CI success is claimed here.

## Verification design

`verify.py` has a fixed finite workload, no recursion, subprocesses,
network calls, file writes or dynamic dispatch. All functions are shorter
than sixty lines. Positive-integer arguments are validated at the threshold
boundary; all result checks raise explicit errors even under `-O`.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`: CPython
allocates arbitrary-precision integers during execution. The finite ranges
bound each power-product operand below `2^10240`, and the verifier retains
only one case at a time plus six source hashes. The registered commands
exercise that complete bounded workload. If these ranges become configurable,
the change must introduce explicit input and memory caps. Python has no
compiler warning mode; both registered commands use `-W error`. The package
does not alter shared diagnostics or repository CI configuration. Ruff and
Mypy are unavailable on the local PATH; in-memory compilation and the
warning-strict registered replays are the available Python diagnostics.

## Related open work

- [#7450](https://github.com/CrocSwap/integer-mult-bounds/pull/7450), unpaidmoon,
  supplies the `27/17` bound and explicitly asks about the missing `m=7`
  case. This proof includes that case and retains the same sharp four.
- [#7286](https://github.com/CrocSwap/integer-mult-bounds/pull/7286), unpaidmoon,
  tightens a monomial record count used elsewhere in the same review.
  Its count and elimination model are independent of this one-step inequality.

## Open next questions

The final section of [PROOF.md](PROOF.md) asks for a sharper elementary
correction where this sufficient bound exceeds the true threshold. Its
first example is `D=10,a=1`; no external blocker is required to begin.
Physical implementation, complete cutoffs, supplier admission and all five
framework assumptions remain separate obligations.

## Credit

Credit unpaidmoon #7450 for the source question, the prior `27/17` threshold
and its retained persistence-note lineage at
`8e0124415604b89a1cfc842cb6dc6da96ea87ac5`. Credit Douglas Colkitt's retained
#7000 application review for the effective-cutoff comparison. The convexity,
logarithm and induction arguments are classical. The shifted
threshold, its application and its exact verifier were produced by Nick
Petalas. Independent human and formal proof-kernel review are unclaimed.
