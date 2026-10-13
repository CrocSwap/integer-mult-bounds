# PR565 and worst-case indexing

PR565 is a useful physical copy lemma. It does **not** establish worst-case
constant-time indexing, and it does not change the multiplication parameter.
This review uses commit `890b2906ebb76b3c9392a08d64e933630c06b1ac`; the Lean
addition is its parent `b5766e1`. The final commit only repairs an unrelated
certificate's source hash. Exact source hashes are in `SOURCE-REVIEW.json`.

## What the theorem supplies

`BinaryCounterCompactCopy.lean` defines an explicit machine with nine states
and two tapes. Tape 0 contains a finite little-endian Boolean list `bits` at a
marked home position. Tape 1 must be pristine. Let `n = bits.length` and let
`p` delete the high trailing zero bits, with `m = p.length`.

`compact_run_exact` (line 409) proves the exact physical endpoint: tape 0
retains the original represented footprint and blanks its high zero cells;
tape 1 contains the canonical finite word `p`. Empty and all-zero inputs
produce an exactly blank output tape. `final_halted` proves the endpoint is
halted. There is no arbitrary spectator-tape parameter in the public theorem.

The supplied run index is

\[
 T(n,m)=\begin{cases}2n+3,&m=0,\\2n+2m+4,&m>0,\end{cases}
 \qquad T(n,m)\leq 4n+4.
\]

The theorem provides this index and halted endpoint, not a first-halting-time
claim. The transition program explicitly scans to the far end of the input;
this routine therefore does not perform arbitrary-width copies in a bounded
number of physical steps.

The new source has nine axiom probes. The package's retained evidence reports
41 probes across the six-source dependency closure, with standard Lean axioms
only. This session inspected the exact source, manifest binding and checker;
it did not perform a fresh Lean kernel replay. The supported checker requires
Linux `/proc`, the exact hashed official Lean 4.21.0 installation, and five
pinned sources from PR488/PR511. Its command is recorded below.

## Consequence for the indexing approach

A physically materialized `w`-bit label cannot in general be written to a
pristine bounded-alphabet tape in constant time: the copy must write its
nonblank output cells. If an independent representation theorem gives
`w = O(log V)`, this helper provides an `O(log V)` conversion. That logarithmic
representation theorem and numeric-value preservation are explicitly outside
this package; they must not be silently inferred as existing Lean results.

The promising interface remains a maintained local state that exposes only
the digits or routing decisions required by the next elementary stream step.
Such an interface can aim for a fixed worst-case transition budget without
materializing a complete binary address on each request. A redundant counter,
scheduled carry propagation or an explicit stream clock needs its own proof
that every request is ready on time. The compact-copy theorem supplies none
of those scheduling or ready-state invariants.

This helper can instead serve a boundary conversion: initialize a caller,
produce a final canonical result, or perform an infrequent checkpoint. A
complete integration must establish:

1. The maintained counter's numeric value agrees with the emitted stream
   position, including the empty-word representation of zero.
2. Each next-step request has a constant physical transition bound and needs
   only the state exposed by that step's contract.
3. Copy boundaries have explicit schedules and invoices. A linear copy cannot
   be inserted into every request while still claiming constant worst-case
   latency.
4. The two-tape theorem composes with the actual caller, including available
   pristine output, spectator preservation, heads and tape footprint.

These are distinct from a rank-profile improvement. Faster indexing changes
the implementation cost of stream traversal. A larger certified κ still
requires a changed paid profile or another justified change to the complete
recurrence/invoice. PR565 supplies neither.

## Reproduction

Read the exact added source without changing the active branch:

```sh
git show 890b2906ebb76b3c9392a08d64e933630c06b1ac:research/lean-compact-counter-copy/BinaryCounterCompactCopy.lean
```

The package's supported fresh Linux kernel replay, after obtaining its exact
pinned dependencies and official Lean distribution, is:

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --input-foundation-root /path/to/PR488/research/lean-binary-input-preparation \
  --dispatcher-foundation-root /path/to/PR511/research/lean-binary-count-dispatcher \
  --build-dir /absolute/path/to/new-empty-build
```

The full multiplication result continues to depend on the separate all-size
compiler, common-label/mutable-source, hosting, precision/tape and analytic
transfer assumptions. A finite tape helper does not discharge those interfaces.
