# Four exact modes and sharp geometric convergence of projection ratios

For the unstrengthened projection recurrence with block-four seed
`(0,27456,48576,68320,86592)`, this package proves

```
L = 439277/149175,
2^(-m) < T_m-L < 2^(1-m)             for every m >= 5.
```

Here `T_m=a_m(m)/a_m(1)`. The exact limit L is Nick Petalas's
[#5151](https://github.com/CrocSwap/integer-mult-bounds/pull/5151) theorem.
The **new results** are an exact four-mode representation of the entire
normalized profile and the two-sided geometric error bound. They improve the
conservative O(1/m) convergence rate explicitly left open there. This is a
scoped arithmetic proof with an exact finite certificate, not a new kappa or supplier.

The proof also yields strict decrease for every m>=4 and the exact unattained
infimum L. JoyboyBrian's concurrent
[#5184](https://github.com/CrocSwap/integer-mult-bounds/pull/5184) already proves
those shared conclusions by a different weighted-order method. They are
credited, independently obtained corollaries here; the submission is focused
on the additional geometric rate and finite-mode representation.

## Proof and evidence

[PROOF.md](PROOF.md) gives the complete argument. Normalizing the recurrence
reveals a single triangular operator and four exact modes. Each mode's scaled
increment has a two-dimensional transfer approaching an involution. The
two-step error is summable; exact states at blocks 32 and 33 therefore certify
the whole infinite tail. A finite prefix completes the monotonicity theorem.
This explains why checking more decimal values alone would not suffice.

[verify.py](verify.py) uses only integers and `fractions.Fraction`, reads no
external files, and writes nothing. Its deterministic output is retained in
[RESULT.json](RESULT.json). The check covers:

- 1,215 normalized profile equalities against a separately written literal
  integer recurrence, over blocks 4 through 48;
- 172 scalar recurrence and 172 scaled-state transfer identities;
- a bivariate polynomial identity for the uniform remainder, its rational
  bound constants, and 49 separately labelled finite lemma fixtures;
- both infinite-tail certificates, exact finite-prefix inequalities, and ten
  rejection controls (wrong recurrence, seed, domain, perturbation bound,
  involution sign, summability premise, parity, limit, or seed universality).

The universal inequalities are proved in writing. Executing the finite
certificate does not independently audit the written proof or the inherited
limit theorem. Normal and optimized Python runs use explicit checks, not
disableable assertions.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/projection-geometric-tail
python3.12 -I -X dev -W error -B research/projection-geometric-tail/verify.py
python3.12 -I -O -X dev -W error -B research/projection-geometric-tail/verify.py
python3.12 -B scripts/check_research_commit.py --package research/projection-geometric-tail --check-source-history
```

Expected markers: `PASS_PROJECTION_GEOMETRIC_TAIL`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
Direct verification takes less than a second on the author's macOS arm64 host
with CPython 3.12.12; this is an observation, not a performance claim. The direct
commands also work from a read-only, Git-free package export. The registered
runner needs Git history for provenance. No third-party dependencies are used.

## Sources, overlap, and limits

Fresh base: `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
The selected source/metadata baseline passed; no selected scientific replay was
needed or run. [TASK.json](TASK.json) records the handoff-first scope change from
`independent-moment`; [claim #5169](https://github.com/CrocSwap/integer-mult-bounds/discussions/5169)
is the canonical investigation record.

- Jacob Alan Sussman [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
  supplies the hook seed, recurrence, and engine interpretation; head inspected:
  `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`.
- Maximilian Lutz / lm1909 [#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643)
  independently derived the counts, checked the finite prefix, and proved the
  earlier conservative all-block bound. Its retained README is pinned as
  provenance in [SOURCES.json](SOURCES.json). Its unresolved hook-rank inputs
  remain unresolved here. The central ledger marks #4628/#4643 partially reviewed.
- Nick Petalas's [exact limit proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e6c8e945a47dcc4a6f08974682090fc7f5e221a3/research/projection-recursion-limit/PROOF.md)
  at `e6c8e945a47dcc4a6f08974682090fc7f5e221a3` is a **cited mathematical
  dependency**, not an imported executable or an independently replayed result.
  Its exact proof hash and specialized theorem are recorded in PROOF.md and
  SOURCES.json. Publication and passing CI do not imply scientific acceptance;
  #5151 was merged during this investigation, without changing its cited head.

The pre-claim search covered 331 open PRs, 4,339 Discussion records, and 6,918
main-tree notes, followed by live recent-claim/PR and closed-PR term checks.
The nearby same-account Gram and R437 claims and all earlier excluded topics
were left alone. Search coverage excludes unpublished work and arbitrary diffs.
The final live overlap refresh found #5184, head
`b8aa60d489ff067c5b994a54e5ebd3c2bdc09503`. Its claim was posted at 11:39:28 UTC,
between the last pre-claim live query and creation of #5169. Its proof was read
and credited before publication; no peer verifier was rerun. The scope was
narrowed in [the canonical update](https://github.com/CrocSwap/integer-mult-bounds/discussions/5169#discussioncomment-19145289)
to the additional results above. The PR records the latest coverage snapshot.

The result is about this seed and this recurrence. It does not provide an
elementary closed form for the mode sequences or classify every seed. The
optional triangle/max strengthening is outside scope. Hook ranks, engine
premises, physical realization, dirty restoration, complete recursive pricing,
native/outer admission, Lean, and independent human review remain unverified.
No selected frontier is changed.

## Open next questions

1. Which other seed profiles have monotone top ratios? This would make the
   projection method's best all-block bound decidable for new hook data.
   Start by applying the four-mode tail certificate to adjacent-difference
   linear functionals of a general block-four seed. An exact characterization
   must handle equality on the limiting parity boundaries; finite tests do not.
2. Can the mode sequences admit elementary or q-series closed forms? This
   could give exact parity-sensitive leading error constants. Start from
   (2.1) and the fixed triangular operator. This package proves neither such a
   form nor the optimal constants in its geometric enclosure.

## Credit

Prepared by Krzysztof Wojt with substantial OpenAI Codex assistance. A Luna
worker assisted with a read-only claim inventory, bounded exact coefficient
fixtures, and an arithmetic/indexing review; final decisions and integration
remained with the primary agent. SymPy was used for exploratory algebra only;
the published certificate uses the standard library. No independent human or
proof-kernel acceptance is claimed.

Credit Sussman, Lutz, Petalas, JoyboyBrian, eumemic (#288), Swapnil Jain, and the retained
certificate-method/engine lineage. This new work is Apache-2.0. Frozen
predecessor files, shared tooling, and the selected record remain unchanged.
