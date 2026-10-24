# A sharp P112 floor for exceptional-hull cross forms

The new [scoped proof](PROOF.md) gives exact two-call COPY cost **128** when
`beta01 = r_i v^T` and the reverse form's row space lies in the binary span
of the eight exceptional source annihilators. The reverse form may have
rank greater than one. Every double term then costs at least 16, because
its Schur feedback vanishes.

The explicit rank-(1,2) fixture has minimum pure cross prices `(0,0)`.
Thus commdata2338's [PR2395](https://github.com/CrocSwap/integer-mult-bounds/pull/2395)
sufficient test abstains, while this theorem proves the sharp floor.
The new result excludes this exceptional-hull subfamily of PR2395's open
rank-(1,2) cases. It does not settle that entire rank pair.

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Reproduction and evidence

From the repository root, use CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/p112-exceptional-hull-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p112-exceptional-hull-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/check_research_commit.py --package research/p112-exceptional-hull-floor --check-source-history
```

The portable interpreter spelling is `python3.12 -W error -B`. Run the
publication preflight after committing. The registered normal and optimized
commands print a generated JSON receipt bound to the package and live-source
hashes, followed by

```text
PASS_P112_EXCEPTIONAL_HULL transfer=8192 doubles=6561 floor=128 controls=2
```

Local replay used CPython 3.12.15 on macOS arm64. Both registered commands
passed. Hosted CI is recorded in the PR body when available.

The 8,192 transfer checks cover all eight forward exceptional choices,
eight reader restrictions, eight source restrictions and sixteen elements
of the source-normal span. The 6,561 double cases cover all nine possible
support spans in each of four positions for the explicit fixture. They
have minimum price 16. The sixteen coordinate terms attain 128.

Two hypothesis-removal controls exhibit actual price-15 doubles. They
show why the new double-price argument needs its geometric hypotheses;
they do not exhibit a sub-128 exact decoder. The written proof supplies
the universal implication for arbitrary complex factors. No solver, Lean,
native operator replay or multiplier replay is required or claimed.

## Sources and related work

The base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the actual geometry and PR2395 proof.
PR2395, head `361de309e5fc05f83862f0b6c611210eda9837a1`, supplies the support
classification, within-call floor and coefficient incidence count. Sagar
Thakrar's [PR2294](https://github.com/CrocSwap/integer-mult-bounds/pull/2294)
supplies the arbitrary directed cross-form model, following alephnan's
PR1714 and the support work of Mihir Srivastava and Adam Gall.

JoyboyBrian's [PR5141](https://github.com/CrocSwap/integer-mult-bounds/pull/5141),
head `b75399c455aa24f21ec9c78c337c3c277efd177d`, settles rank-(1,1). Its
mixed-orientation calculation is the adjacent rank-one predecessor. The
new step closes the reverse functional under linear span and thereby
allows higher reverse rank. Its proof and verifier are not imported.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144293)
is the canonical investigation record. The catalogue card
`formal-interface-lemma` is changed to this written interface proof, with
no claim of proof-assistant formalization.

## Limitations

The inherited support theorem is a cited premise. This package computes
only the geometry needed for the new transfer and fixture, rather than
rechecking that theorem. The union rank price is the separate-total
two-call root-code model. Physical chart realization, dirty restoration,
hosting, precision, rank-power costs, recursive admission and integer
multiplication remain outside scope. The selected frontier is unchanged.

## Open next questions

1. Settle the rank-(1,2) cases outside this exceptional-hull family. First
   classify which coordinate restrictions give nonzero Schur feedback;
   then couple those discounts to the paid pure terms. Arbitrary complex
   coefficient cancellation remains the obstacle.
2. Can a legal physical cross-form interface realize any surviving
   discounted pairing? Start with one explicit form and charge its chart
   conversions and cleanup. A binary form alone supplies no implementation.

## Verifier bounds

The verifier uses structured control flow, fixed finite domains and no
recursion or code generation. Every function is shorter than 60 lines.
Checks use explicit exceptions and remain active under optimization.
The diagnostics command is Python's warning-strict replay in both modes.

Power-of-ten rule 3 has a CPython runtime deviation in `verify.py`.
Integers, JSON parsing and lists allocate dynamically. Input files are capped
at 2 MiB; the root table is 112-by-8, and the largest pairing is 18-by-18
binary. The 6,561-case enumeration retains one pairing at a time. The
normal and optimized replays exercise this bound. A fixed-memory port
would be needed only if this finite offline verifier becomes an embedded
runtime requirement. No shared library or predecessor file is changed.
