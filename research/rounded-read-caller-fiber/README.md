# A 120N-bit complete-caller fiber from rounded reads

This contribution was produced by Nick Petalas.

Claim type: scoped written proof with exact finite corroboration. On the
unchanged selected PR6030 word, one explicit legal scalar seed schedule
maps 2^(120N) distinct same-grid public inputs to zero, where N=512^f.
Exact input recovery needs at least 120N additional retained bits. At width
one this is 61,440 bits or 7,680 bytes.

Ali Romman's [PR6547](https://github.com/CrocSwap/integer-mult-bounds/pull/6547)
already supplies an 86N-bit complete-caller family for every seed. It and
his [PR6546](https://github.com/CrocSwap/integer-mult-bounds/pull/6546)
complete same-grid stochastic caller are cited predecessors, not audit
targets. The new construction permits 39 fractional reads of 17 additional
fields before their bits disappear. A coefficient-sign-dependent seed
makes those reads silent. This raises the worst-case floor by 34N bits,
with a weaker seed quantifier. The selected frontier is unchanged.

[PROOF.md](PROOF.md) gives the precise ABI, all 60 witness fields, the
componentwise all-width induction and information-capacity argument.
The runtime input is pinned at main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The predecessor proof is pinned
by citation to `317e4a099488794c372f8a4ad1e70deef3626bbf`.

## Reproduction

From the worktree root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/rounded-read-caller-fiber/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rounded-read-caller-fiber
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rounded-read-caller-fiber --check-source-history
```

The direct command emits a deterministic JSON receipt containing source
and verifier SHA256 hashes, every silent read and erasure event, then
`PASS_ROUNDED_READ_CALLER_FIBER`. It writes no files.

Local validation used CPython 3.12.15. Both registered commands pass with
warnings treated as errors, including the optimized run.

The per-field scan and separate whole-word active-label pass agree on
60 fields and cut 10448. All 3,453 native operands are checked through
the zero contract. There are 129 complete literal integer replays,
including all 120 individual real/imaginary generators and nine simultaneous
patterns at 1, 4 and 512 complex coordinates. Nine actual rejection controls
and two computed boundary witnesses cover source corruption, leaking reads,
native access, copying, wrong scaling, owned access, surviving or duplicate
labels, invalid labels, wrong seeds and outside-family values.

These are checks of the new family. No predecessor scientific suite, native
implementation, full selected replay, Lean or Docker run is required or
claimed. The native zero contract and declared read sets remain hypotheses.

## Scope and limitations

The public domain is arbitrary h-grid data, without an even-coordinate or
actual multiplication-encoding promise. The result applies to the displayed
fixed scalar schedule. It does not improve the predecessor's every-seed
bound, find the global maximum fiber, price physical retained storage, or
discharge any selected assumption. A matching 120N-bit code is supplied only
on the displayed family by its erasing half residues. All five framework
assumptions and the selected kappa remain unchanged.

## Engineering bounds

The verifier authenticates the fixed source before parsing it, with 22,803
events, 770 public and 799 total labels. The largest data replay has 799*1024
integer slots; on these fixtures every slot is zero or one. Loops are bounded
by those dimensions, 129 cases, 60 labels, or the nine rejection controls.
Functions are under 60 lines. Runtime checks use explicit exceptions and
remain enabled under optimized Python. No global framework or predecessor
code is imported.

Power-of-Ten deviations are limited to these offline verification mechanisms.

```text
Rule: 3, fixed memory after initialization
Location: verify.py, JSON parsing and integer data replay
Reason: Python allocates managed objects during arithmetic and parsing.
Scope: The authenticated fixed source and sequential bounded fixtures only.
Compensating control: Fixed dimensions, bounded coefficients and masks,
  799*1024 maximum data slots, and one data replay live at a time.
Verification: Strict normal and optimized registered replays.
Follow-up: Use fixed arrays if ported to a constrained runtime component.

Rule: 9, indirect calls
Location: verify.py, expect_rejection and controls
Reason: Rejection checks must invoke an operation and observe its exception.
Scope: The nine explicit local test callbacks only.
Compensating control: No external callback or dynamic code is accepted.
Verification: Every callback must raise its specific expected exception.
Follow-up: Replace callbacks with explicit variants in a constrained port.
```

## Open next questions

- Can a larger seed-uniform family be found? First inspect whether the 39
  rounded-read constraints have two common integer solutions for arbitrary
  seeds. Conflicting read intervals are the blocker.
- Can correlated input variations enlarge this fixed-schedule family?
  First allow one exact source read and solve its joint cancellation
  constraints. A complete causal proof must prevent leakage into native inputs.
- Which of these inputs are reachable under an actual multiplication entrance
  contract? Bind one concrete encoding before transferring the capacity bound.

The first verified improvement was packaged without extending these questions.
Credit Ali Romman for the caller and fiber predecessors, DreamingOfClouds and
the full retained PR6030 lineage for the word, and zxv for PR6066's residue
interface. No independent human or formal proof-kernel acceptance is claimed.
