# Executed validation and review

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.

## Evidence completed

- The package metadata/source-pin check passed with all 41 scientific inputs
  and task-catalogue provenance authenticated.
- A full authoring run executed both physical fixtures and wrote the frozen
  receipt. This is a finite source execution, not an all-width proof.
- A separate reviewer found a false `4/3` quadratic geometric coefficient.
  The proof now uses the correct ratio-2 sum and the stronger `32p^2`
  normalized allowance. Exact per-node moment checks and its concrete
  `(ell,d)=(20,16)` counterexample are included as regression controls.

## Registered replay, 2026-11-10

Environment: CPython 3.12.14, Clang 22.1.3, Linux x86_64, glibc 2.41;
standard library only. From repository root:

```sh
python -B scripts/research_package.py --package research/crt-whole-tree-state --check-only
python -B scripts/research_package.py --package research/crt-whole-tree-state
```

Both registered author commands completed within their individual 300-second
limits. Total runner wall time was 237.070 seconds. The normal and
optimized runs each produced:

```text
PASS_CRT_WHOLE_TREE_STATE four_axis_rows=30 producer_calls=28 retained=7176 controls=11
```

The runner then reported:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/crt-whole-tree-state outcome=completed
```

Both runs compared their complete typed receipt with RESULT.json;
neither rewrote it. The same actual numerical and ROM producers executed
in both modes. Explicit failure checks remain active under `-O`.

## Independent mathematical/source review

A separate research worker reviewed the source seam, exact-width entry,
close-before-write ownership, whole-tree state induction and historical
storage, and independently rederived the tariff. It passed the scoped
theorem after the quadratic correction. Its separate executable passed
normal and optimized modes on 744 invoice/moment domains and nine actual
protected-word growth/shrink lifecycles, with three negative controls.
The exact first-use lifecycle is `10P+23` raw actions per word and reuse
is `10P+24`, strictly within the new allowance.

That reviewer did not rerun the large author ROM interpreter. Its
independence is in the separate source/mathematical derivation and exact
smaller controls, not a claim that repeated author execution is an
independent proof. The model-assisted reviewer shares the inherited
provider hypotheses stated in PROOF.md.

The portable [review and implementation](independent-review/REVIEW.md)
are included in this package. After copying them into the package, both
of these read-only commands passed against the frozen independent receipt:

```sh
python -I -B research/crt-whole-tree-state/independent-review/independent.py
python -I -O -B research/crt-whole-tree-state/independent-review/independent.py
```

Each printed `PASS_INDEPENDENT_SCOPED_REVIEW 744 9 3`. The normal command
is also registered as the third VERIFY.json command, with a 30-second
timeout. The two author commands and this third command were all executed;
the 237.070-second figure measures the author runner before that short
independent command was added. Final metadata and pin validation passed.

## Scope of acceptance

Mathematical/source review remains AI-assisted. No independent human
review, proof kernel, full selected-construction replay, binary machine
admission or complete unconditional theorem has been executed or claimed.
The external topology/source producers and payload consumer remain the
explicit open boundaries in PROOF.md.
