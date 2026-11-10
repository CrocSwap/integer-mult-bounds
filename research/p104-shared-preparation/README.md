# Share the actual P104 opening preparation with a zero-restored slot

This contribution was produced by Nick Petalas. Claim type: scoped exact
construction, with finite corroboration. No new kappa.

The first 18 events of DreamingOfClouds's [PR6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621)
add `r471 + r525/2 + 2*r704` separately to six rows. The replacement computes
that expression once in inactive owned slot 770, adds it to the six rows,
and uncomputes the slot to zero before clearing it.

```text
old: 18 ADDs
new: INIT, 3 ADDs to compute, 6 ADDs to deliver, 3 ADDs to uncompute, CLEAR
```

The new prefix has 12 ADDs and 14 events. The complete emitted word has
18,557 events instead of 18,561. It uses the same 29 owned labels and does
not increase the peak number of active owned slots. Every instruction is
in existing empty frame 3. The suffix, every MOVE, public boundary and frame
declaration are unchanged. Paid and productive recursive profiles have zero
delta. The new CLEAR erases zero; it needs no nonzero-erasure rule.

For inputs bounded componentwise by A, the temporary is at most `7*A/2`
and the public prefix states are at most `9*A/2`, the same public bound as
the old prefix. No additional fractional bit is needed in exact dyadic
arithmetic. [PROOF.md](PROOF.md) states the identity and scope.

This saves six logical ADD instructions. If ADD, INIT and CLEAR have prices
`a`, `i`, `c`, the ordinary-work gain is `6*a-i-c`. With unit event prices
it is four. Physical allocation, movement and rounding costs have not been
established here, so there is no claimed tape runtime improvement.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-shared-preparation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-shared-preparation --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-shared-preparation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-shared-preparation/verify.py
```

Replace the interpreter path with a local CPython 3.12 path on another machine.
The verifier prints `PASS_P104_SHARED_PREPARATION` in a generated JSON receipt
bound to the package files. It checks nine basis columns, all 512 vertices of
the nine-input unit box, 17 signed dyadic cases, and seven rejection controls.
Both programs are linear on the public inputs. The written identity covers
arbitrary public data, beyond the finite fixtures.

Emit the revised word into a new external output path:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-shared-preparation/rewrite.py /absolute/external/WORD.json.gz
```

The emitter refuses an existing destination or a path within the checkout.
No predecessor verifier or complete native/caller replay is run. The local
identity and literal untouched suffix establish the substitution without
rechecking the predecessor's construction or numerical invoice.

## Sources and scope

The exact source is PR6621 at `c51a142bb94c6d46ebee9a48c3f71cde8022da91`.
[NATIVE-SOURCE.json](NATIVE-SOURCE.json) records the two archive layers,
their hashes and the exact retained WORD and NOTICE members. These members
are copied unchanged into `inputs/`; the verifier authenticates their SHA256
and Git blob hashes. The source head is not claimed to be an ancestor of this
contribution. A clean checkout has the retained bytes and needs no unmerged
Git object, network request or predecessor import.

Credit DreamingOfClouds for PR6621's compensated paid-job merge, the expression
and its six recipients. Credit Ali Romman for PR6551/6545/6529 and the retained
native construction, Rohan Arun for the donor-transport work, Erwan L. for the
anchor work, and all predecessors named in the unchanged [source notice](inputs/NOTICE).
Common-subexpression factoring and compute/uncompute are classical. The new
contribution is this exact source-bound zero-restored substitution and its
resource ledger.

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected record resolves to PR6030. Scope changed from a paid-transition
fusion attempt to this first smaller ordinary-work improvement. No further
construction search is included. Full supplier correctness, physical hosting,
rounded arithmetic, caller/compiler admission and all five framework assumptions
remain inherited and unproved here. Independent human and formal proof-kernel
review are unclaimed.

## Related open work

- [PR6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621) supplies
  the exact source word. This contribution factors its opening scalar block;
  it makes no new claim about that PR's kappa or complete invoice.
- [PR6638](https://github.com/CrocSwap/integer-mult-bounds/pull/6638) audits a
  predecessor comparison gate. That question is separate from this equivalence.
- [PR6674](https://github.com/CrocSwap/integer-mult-bounds/pull/6674) concerns
  seven main-signal bypasses. This word retains every paid hop and reader map.

## Open next questions

1. Price the new early lifetime on one physical caller. Start with its actual
   zero-init and zero-clear costs and test `6*a > i+c`, including allocation
   and cleanup. Instruction counts alone do not settle this comparison.
2. Integrate the substitution with a rounded backend. Start with the nine-input
   prefix and charge changed rounding correlations. The exact dyadic bound
   does not by itself preserve an approximate caller contract.
