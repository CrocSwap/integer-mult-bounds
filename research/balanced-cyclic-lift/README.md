# One dirty scalar makes a cyclic factor composable in place

Research construction / recursive-interface refinement; **no new κ**.

A real cyclic recurrence with position-dependent rational coefficients of
absolute value at most 1/2 can be enlarged by one scalar and implemented by
reversible rounded shears. The scalar carries the determinant correction.
An ordered factor chain then runs in place, and a two-evaluation adapter restores
one arbitrary dirty array and one arbitrary dirty scalar exactly.

For the retained 55-factor, length-5 fixture the adapter executes 220 stabilized
factors and 2,660 coordinate updates. PR628's original binary dispatcher performs
3,232 **additive** leaf calls with six dirty arrays. The leaf contracts and prices
differ; these figures are not a runtime speedup. Exact coefficient tables can
have O(L)-bit entries, and that expense is explicitly charged.

[PROOF.md](PROOF.md) gives the all-length factorization, the complete precision
and cost recurrences, and remaining interface obligations. [CERTIFICATE.json](CERTIFICATE.json)
retains the exact coverage, hashes, controls, seed-selected fixture and operation
bill. [SOURCES.json](SOURCES.json), [NOTICE.md](NOTICE.md) and [CLAIM.md](CLAIM.md)
record pins, attribution, assignment and overlap.

Reproduce from the repository root with Python 3.9+ and the standard library:

```sh
python3 -I -O -B research/balanced-cyclic-lift/verify.py
```

Expected final line:

```text
PASS_BALANCED_CYCLIC_LIFT: 1560 factors; 7420 full columns; 4680 rounded factors; 315 products; 25 controls; n55: 3232 additive leaves vs 220 stabilized factor executions
```

The same command works on an offline copy of this directory in a path with spaces.
The verifier checks all vendored source hashes and compares a freshly generated
complete evidence object with the frozen certificate. `--write-certificate` is an
explicit developer regeneration mode. Mathematical failures use exceptions and
remain active under optimized Python.

Coverage: exhaustive five-letter coefficients through length four in both
orientations; independent dense rational full-column references; noncommuting
signed eighth-coefficient products through 55 factors and length eight; 220-bit
dirt; exact payload restoration and cancellation; single-instruction omissions,
order/restoration/pivot-collision controls and pre-mutation alias/admission checks.
The pinned predecessor dispatcher is checked through 128 factors with a counting
stub. Its numerical scan/kernel suite is not included in this replay.

The construction handles exact real rational coefficients in the stated range.
The proof's length-independent error bound does not grant constant-size exact
coefficient tables. Extending to complex roots, approximate table preparation,
scaled factors, arbitrary strides and a complete physical transform remains work.
No finite replay is described as a formal proof of the multiplication theorem.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Consumed PR628 head:
`0768f97d06c623b8211e651543c66135796b62bf`. Selected conditional κ at this base:
`51110230636731/31250000000000000`, PR626 with PR543. This package changes no
selected construction or frontier data. Local validation is in [VALIDATION.md](VALIDATION.md).

Prepared for **Wentao Li** ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)), with substantial OpenAI Codex assistance.
Apache-2.0; predecessor notices retained.
