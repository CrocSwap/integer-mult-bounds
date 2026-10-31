# Full fixed-height direct-flow exponent

**No new κ.** For the historical raw-p7 flow of #4436, with its original
height `floor(log_5(N/121))`, this package determines the exponent of the
complete scalar leaf recurrence:

\[
L(N)=N^{s_*+o(1)},\qquad
0.99738855928<s_*<0.99738855931.
\]

In particular, `L(N)=O(N^0.99739)`, a scalar saving of `0.00261`. This is a
scoped theorem about the exact recurrence, including every complement,
leaf exit and boundary exit. It supplies neither an effective onset rank
nor a physical supplier admission or multiplication bound.

## What is new

[PROOF.md](PROOF.md) sums all mixed target/paid layers with uniform local-limit
and geometric-tail bounds. The resulting source, boundary and leaf constants
resolve the full-flow normalization left open after the leaf saturation of
#6118 and leaf tariff of #6125. The exact complete-complement coefficient
then has a unique crossing; eventual upper **and lower** induction identify
the scalar recurrence exponent.

The same analysis yields a limiting leaf fraction of approximately
`0.898921196171` and a full-flow log gap of approximately `120.370030517`
at the raw root. It also locates the older, more conservative sufficient-test
crossing in `(0.99743801995, 0.99743801998)`. That sufficient-test crossing
is **not** the recurrence exponent; exact complement accounting gives the
stronger result above.

The proof extends #4459's exact mirror windows and #6118's nonlattice
paid-law limit rather than assuming stable normalized shares. #4456 checked
finite flows and recurrences. #4467's random-walk heuristic and #6128's finite
tails do not settle this all-family limit. The later changed-height compiler
of #4483 already removes tensor padding and approaches the better raw root;
our theorem concerns the original fixed height and does not replace that
construction. No source file or selected record is changed.

## Sources and proof boundary

The exact base is `a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`.
[SOURCES.json](SOURCES.json) pins every live dependency by Git blob and SHA256:

- `research/direct-mixed-flow/flow.py`: exact flow of #4436.
- `research/direct-flow-leaf-walk/verify.py`: literal historical raw-p7 inventories.
- `research/direct-flow-boundary-share/README.md`: complete mirror decomposition.
- `research/direct-flow-leaf-saturation/PROOF.md`: Stone interval theorem
  specialization, nonlattice law and weighted paid limit.

The originating #4436 head was `56003680aee2871773de408e5f01cc5dd46b144c`;
#4456's independent finite check was `bbef80cd12c66afa31cb347c7393fafc873a0c88`.
The replay uses the explicitly pinned files at the canonical base, not a
moving PR head. The catalogue and selected record are historical provenance.
The selected κ `0.003125804`, admitted bit value `0.0034`, and all five inherited
framework assumptions remain unchanged. The historical p7 inventory is not
asserted to be the currently selected complex supplier.

The analytic proof depends on Stone's nonlattice interval local-limit theorem
as precisely stated in the pinned #6118 proof. The new uniform summation and
both-sided induction are written arguments; finite checks do not establish
an all-size limit. This is not a proof-assistant formalization or independent
human acceptance. Current archive and targeted later-reference searches found
no full fixed-height exponent theorem; that bounded survey is not exhaustive.

## Reproduce

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-exponent-gate
```

Expected: `PASS_DIRECT_FLOW_FULL_LIMIT`, a certificate containing
`PASS_EXACT_COMPLEMENT_SIGNS`, then
`PASS_REGISTERED_RESEARCH_PACKAGE research/direct-flow-exponent-gate outcome=completed`.
The replay authenticates its inputs before executing the frozen flow source
in memory. It writes no source or generated artifacts. The registered runner
provides a fresh private bytecode namespace. Full Git history is required for
the optional publication-ancestry check, which is separate from source-byte
and mathematical checks.

The bounded check covers 26 complete histogram fixtures at depths 0–3,
104 exact power identities, nine coefficient identities, exact tilt/root
brackets, the full limiting shares/log gap, 27 derivative intervals, and the
complete-complement root bracket. Every numerical acceptance gate uses
outward-rounded rational intervals. The complement integral uses 512 positive
binomial terms and a proved tail bound, including its endpoint at one.

Negative controls reject five different histogram errors (extra terminal
truncation, missing mixed layers, missing multiplicities, reversed windows,
missing root sources), invalid interval and series domains, and omitted
positive binomial tails on exact square-root fixtures. Ordinary and optimized
Python runs preserve these explicit checks. No random search, seed-dependent
claim, large-rank recurrence scan or empirical convergence fit is used.

Four independently modified source copies also fail their authentication
gates, and a clean source-only copy passes the full verifier. Optional
independent numerical corroboration is preserved in
`python3.12 -I -B research/direct-flow-exponent-gate/independent_diagnostics.py`.
It uses separate Decimal moment and libm beta/series methods, imports none
of the exact engine, and is explicitly outside the acceptance gate.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

- Make the convergence effective: obtain a quantitative nonlattice interval
  bound for the paid law, then propagate its constants through the mixed-layer
  and leaf tails. This would materialize the induction onset and constants;
  the present Stone argument establishes existence only.
- Determine whether the fixed-height flow's all-size physical realization
  can fund its complete native, recursive and restoration work. Begin with
  an explicit source-bound implementation and bill. The scalar exponent
  alone does not discharge any of these obligations.
- Compare explicit finite-rank cost against #4483's changed-height compiler
  after an effective onset is known. Its better asymptotic raw-root target
  does not by itself decide the finite-rank comparison.

## Credit

Prepared for **@CubeJerry with substantial OpenAI Codex assistance**, including
parallel mathematical derivation, code, prose and adversarial cross-review.
An independent Codex reviewer derived the mixed-layer constants and complete
complement coefficient, audited the interval engine, and used a separate
high-precision/beta-series numerical implementation for corroboration. Those
floating diagnostics are not acceptance gates. All source-bound exact gates
are included here. No independent human review is claimed.

Credit zxv (#4436/#4483), the independent finite review in #4456,
Ryanson Jonathan / pinterbanget (#4459/#4465/#4467), DLamdata (#6118),
Nick Petalas (#6125/#6128), Cinna Davis / 1337isnot1337 (#4405 and p7),
Jacob Alan Sussman (lockstep compiler), Charles Stone, and the retained
native/precision/analytic predecessors. New work is Apache-2.0.
