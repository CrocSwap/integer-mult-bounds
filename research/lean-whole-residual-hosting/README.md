# Lean: whole-residual absorption through a complete invocation window

This independent local contribution proves the **conditional bit hosting
operator lemma** in PR442, `research/idle-axis-hosting/PROOF.md` §2. It moves
whole residuals through a finite window of complete invocation endpoints and
absorbs them into a pending child's exact remainder. It also checks a concrete
rank-28 interval selection from the pinned emitted template. It establishes
no cost, κ, physical compiler instance, or multiplication bound.

The motivating construction is DaysSky's PR442 at
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, against repository main
`12a4934d15006e8c10f9b2264f13f8f341be802b`. See [AUDIT.json](AUDIT.json),+[pinned-window.json](pinned-window.json), and [NOTICE.md](NOTICE.md) for provenance.

## What is proved

The retained state consists of one whole host stream and all other retained
state `R`. A stream is an arbitrary function from paired coordinate addresses
to arbitrary payloads. A bit factor swaps the address halves at selected
coordinates, matching the diagonal-coordinate case of the inherited
`D_U = [[I-P,P],[P,I-P]]` operator. No zero-input, independence-of-payloads,
binary-address, or linearity assumption is imposed on stream contents.

Each **complete endpoint** has the product form
`(host, rest) ↦ (D_idle host, other rest)`. Its relocated form additionally
applies the whole hosted residual to the host. All masks use the same chart.
The theorem proves, for arbitrary finite event lists and arbitrary inputs:

```text
D_(pending \ union residuals) ∘ relocated window
    = D_pending ∘ original window
```

The residual masks must be pairwise disjoint and contained in `pending`.
Intervening idle factors may act on the host: the proof uses their commutation.
Other retained outputs must be independent of the host at the complete
endpoint. Preserving the host alone would not suffice. Internal dirty reads
are permitted when the complete endpoint contract is proved after cleanup.

`PhysicalHosting` extends this result to different old/new auxiliary bank
types. Each endpoint contract holds for every auxiliary input, and actual
bank outputs pass into subsequent invocations. The conclusion compares only
the retained projection. Excluded auxiliary outputs are neither equal nor
restored by this theorem. Every output or scratch component whose equality
matters must be retained in `R` or covered by a separate contract; later use
of excluded banks requires its own scope or independence argument.

| File | Checked obligation |
| --- | --- |
| [CoordinateSwap.lean](CoordinateSwap.lean) | Same-chart bit factors, disjoint union, exact remainder |
| [Hosting.lean](Hosting.lean) | Retiming complete endpoints; window and context identities |
| [PhysicalHosting.lean](PhysicalHosting.lean) | Universal dirty-bank contracts and retained projections |
| [PinnedWindow.lean](PinnedWindow.lean) | Four source-derived masks cover the rank-28 pending child |
| [PinnedHosting.lean](PinnedHosting.lean) | Conditional window instance for that interval list |
| [BoundaryExamples.lean](BoundaryExamples.lean) | Counterexamples to dropping key hypotheses |
| [PhysicalExample.lean](PhysicalExample.lean) | Nonempty toy instance with different changing bank types |
| [Audit.lean](Audit.lean) | Transitive axiom reports for all 47 named theorems |

## Concrete source selection and remaining refinement

Child 2, copy 27, replica 0, family 507 has pending interval `[0,28)` in
64 coordinates. The selected whole residuals are `[24,28)`, `[0,8)`,
`[8,16)`, `[16,24)` at stages 0, 1, 1, 2. Their union is the entire child;
the remainder is empty. Both orders of the two stage-1 factors are checked.

These offsets are in the inherited pending-child chart. Family 507 is a
family of physical streams indexed by cover classes, not one physical
register. Different selectors affect when factors reach a fixed stream.
`PinnedHosting` assumes a complete endpoint list with the selected residual
list; it does not derive that list from every raw gate or cover occurrence.

Application to the physical provider still requires its universal dirty
endpoint, ownership injection and absence of aliasing, physical realization
of the common chart, cover-sweep chronology, remainder implementation, and
any obligations on later use or restoration of excluded banks. These are
explicit premises, not additional axioms in Lean. The finite source checker
does not discharge them. The complex construction is outside this proof.

## Replay

Install the official Lean 4.33.0 toolchain, then run from the repository root:

```sh
python3 -B research/lean-whole-residual-hosting/replay.py \
  --lean /absolute/path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/whole-hosting-replay.json
```

For another working directory, use an absolute script path.
The runner performs no download. It copies all eight modules into an empty
temporary directory, uses only installed `Std` and newly built dependencies,
compiles with `-t 0`, checks source hashes and every named theorem's transitive
axioms, and requires six false mathematical claims to be rejected by Lean.
Only `propext` and `Quot.sound` are permitted; there are no project axioms,
`sorry`, `native_decide`, or prebuilt project proof objects.

To reproduce the separate source binding, first replay the pinned PR442
package with its documented `verify.py OUTPUT` command, then run:

```sh
python3 -B research/lean-whole-residual-hosting/check_source.py \
  --source-root /path/to/pinned-pr442 \
  --template /path/to/OUTPUT/bit/GLOBAL-TEMPLATE.json.gz
```

This Python check binds the literal Lean intervals to source hashes, slots,
owners, and schedule. It is not kernel verification of the JSON parser or
the full template. See [VALIDATION.md](VALIDATION.md) for recorded results.

## Review and relationship to existing work

[REVIEW-PRIOR.md](REVIEW-PRIOR.md) answers whether the earlier single-stream
obstruction faithfully models the disputed interface: its abstract local
statements are correct, but it supplies no full priced-word refinement or
whole-program impossibility theorem. PR448's author acknowledgement remains
the independent reason its advertised gain is unestablished. This proof uses
whole residuals and assumes no unprovided multi-stream register interface.

[REVIEW-POSITIVE.md](REVIEW-POSITIVE.md) records a separate agent's mathematical
and interface review, including the correction needed for different bank
layouts. The reviewer authored the boundary/example modules; those modules
are not independently authored review evidence.

The coordinate algebra and hosting argument are predecessor work. Jacob
Sussman's `pk_union`, `pk_sdiff`, `win_step`, and `win_all` already formalize
related factor/window identities. OpenAI's `WordScheduling.lean` proves
generic scheduling on fixed disjoint supports and substitution given full
matrix equality. Newly inspected PR505 gives a related complete-endpoint
scheduling argument in prose. This package's addition is
a checked conditional bit absorption theorem with explicit retained-state
and dirty-bank contracts, boundary witnesses, and a pinned concrete interval
instance. The bounded audit found no matching Lean hosting implementation;
it makes no global novelty or priority claim.

The subsequent [actual-invocation audit](../lean-source-invocation-audit/README.md)
kernel-checks two trajectories through the literal R747 word and diagnoses
why comparing the full banked and hosted invocation directly requires a
broader contract: additional retained data families also receive residuals.
The physical-provider refinement remains open.
