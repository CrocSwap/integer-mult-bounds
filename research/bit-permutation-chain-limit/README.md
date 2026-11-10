# Six-piece rank chains cannot exclude two arrays in seven calls

This finite certificate was produced by Nick Petalas. Apache-2.0.

The six plane-orbit blocks preserved by free permutations of four address bits
leave a limitation in the rank-chain approach proposed in Jacob Sussman's
[PR #6706, open question 5](https://github.com/CrocSwap/integer-mult-bounds/pull/6706).
For seven single-bit calls, the minimum of

```text
sum_t rank M_1[U_t, U_(t-1)^c] / rank K[U_s, U_0^c]
```

over every shrinking chain of unions of these six blocks, with positive
denominator, is exactly **27/10**. Thus every such inequality passes for two
target arrays. Six single-bit calls also pass, with minimum **23/10**.
These formal schedules are not transform constructions. The stronger
kept-subspace bound cited in #6706 already excludes two arrays in six actual calls.

Even every chain together cannot exclude the seven-call schedule. A search
that uses only this relaxation needs a stronger invariant. This does not limit
other time-dependent cuts, representations or additional program constraints.

## Evidence and scope

`PROOF.md` defines the model and proves the dynamic program's completeness.
`model.py` constructs the exterior-power matrices with Gaussian integers.
`CERTIFICATE.json` contains every new rectangular cut rank and every minimum
endpoint cost for lengths five, six and seven. The five-call capacity is 19/10,
so that schedule fails for two arrays and supplies a negative control.

`verify.py` regenerates the certificate. A separate enumeration covers all
262,144 six-call chains and 531,441 seven-call chains and agrees with the dynamic
program. It counts positive-demand chains separately and rejects three false
conclusions. These coverage algorithms share the exact cut tables.

Claim type: finite certificate with a written proof of its finite interpretation.
The relationship to the engine game uses Sussman's exterior-power and
character-block premises as cited inputs. Their validity, his original
35-plane exclusions and his other numerical results are not rechecked here.
No physical supplier, full invoice, new kappa or selected-frontier update is
claimed. All five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed.

## Reproduce

Run from the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-permutation-chain-limit/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/bit-permutation-chain-limit/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-permutation-chain-limit
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-permutation-chain-limit --check-source-history
```

Any CPython 3.12 installation can replace that local interpreter path. Each
direct run prints a generated JSON receipt bound to all package file hashes.
`--emit` prints the regenerated mathematical certificate. The verifier writes
no files and needs neither Git nor network access. Hosted checks are pending
at initial publication; the PR body records their later status.

## Credit and source status

Jacob Sussman, `jacobalansussman`, posed this question in PR #6706 at
`71ba6fe3b88a6b54f7aa1e40a179cdb389e1113f`. His exterior-power model,
character-block equivalences and chain-cut argument are cited premises.
The new result is the exact six-orbit rectangular rank table and complete
chain-relaxation limitation. No predecessor executable is a replay dependency.
`SOURCES.json` records the exact predecessor URL and text hash. That pending
PR is an external scientific reference, not an ancestor asserted to be
available in a clean clone.

Credit eumemic for the register/network-code viewpoint, Ahlswede, Cai, Li and
Yeung for network cut bounds, Avestimehr, Diggavi and Tse for rank capacities,
and David Arias, Adam Gall and Michael Yee for the retained temporal-cut
lineage. Sussman's #4628 and Maximilian Lutz's #4643 retain their earlier
bound and review credit. Exterior powers, exact elimination, symmetry orbits
and finite dynamic programming are classical. Global literature priority is
unclaimed.

## Open next questions

- Find an invariant under bit permutations that excludes the displayed
  seven-call schedule. The complete six-piece chain family accepts it. Start
  with target-specific information subspaces or a different representation.
- Couple these chains to actual delivered information. Start with one alleged
  two-array seven-call program and its exact intermediate subspaces. A passing
  rank table alone does not supply such a program.

## Implementation bounds

There is no recursion or background process. There are 35 planes, 24 bit
permutations, 64 orbit unions and 729 nested endpoint pairs. Matrix dimensions
are at most 35. Chain loops have the explicit bounds above; registered commands
have 120-second timeouts. Functions are under 60 physical lines.

Power-of-ten rule 3 has a managed-runtime deviation in both Python files.
Python allocates integers and finite containers during replay. Fixed dimensions
and chain lengths bound live state; enumeration streams chains. Warning-strict
normal and optimized execution checks this implementation. A fixed-memory
backend is a separate task if required. No external static analyzer is required
by this package; its registered checks use warning-strict Python execution.
