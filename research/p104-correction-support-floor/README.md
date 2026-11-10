# The sparse P104 correction needs at least 38 ADDs

This contribution was produced by Nick Petalas. Apache-2.0.

The exact correction operator constructed by Ali Romman in
[PR6537](https://github.com/CrocSwap/integer-mult-bounds/pull/6537) needs at least
38 one-target ADDs, even with free nonzero SCALEs, arbitrary rational ADD
coefficients and arbitrary restored dirty workspace. This raises the prior
target-write lower bound from 28 to 38. The credited 74-ADD construction remains
the upper bound. Claim type: scoped written proof with exact finite support
evidence. No new kappa or selected-frontier change is claimed.

[PROOF.md](PROOF.md) gives the general lemma. If B specified outputs each have
support at least s>=2, the first output to receive its final ADD needs at least
s-1 ADDs in its dependency graph; the other B-1 final ADDs come later. Thus
there are at least B+s-2 ADDs. The source operator has 28 changed rows and
minimum support 12. The complete histogram is `{12:3,13:19,25:6}`.

This settles a bounded part of PR6537's open unrestricted circuit gap. It
changes the task card from productive helper splitting to a local correction
obstruction. The result constrains scalar resynthesis after a changed native
boundary; it does not change the recursive moment or provide an actual supplier.

## Reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-correction-support-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-correction-support-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-correction-support-floor --check-source-history
```

Any CPython 3.12 standard-library installation can run the direct verifier.
It writes only stdout. Normal and optimized registered checks extract all
799 rows independently, print every changed support, examine all 9,331 binary
words through length five, check 56 sharp examples and reject six invalid
support declarations and three actual byte corruptions. The success marker is
`PASS_P104_CORRECTION_SUPPORT_FLOOR`. The replay does not run or audit a
predecessor verifier.

The original source RESULT.json and NOTICE are retained byte for byte at the
head named in ORIGIN.json. The original blob and SHA256 are checked directly;
no unmerged Git commit, network access or predecessor executable is required.
SOURCES.json pins the task catalogue and selected record as historical
provenance. The retained source data is authenticated by ORIGIN.json rather
than an unavailable side-branch ancestry pin. Only its `correction` array is
used. Other numbers in the imported result are neither recomputed nor adopted
as new claims here.

## Limitations and verification scope

The exact optimum remains between 38 and the credited 74. The model uses fixed
register names and ADD/SCALE operations. Free permutations, multi-target calls,
native maps, COPY and in-circuit resets need different arguments. The theorem
requires the complete operator on independent coordinates; a restriction to
states reachable from a preceding word is outside the claim. The theorem
is a written proof, not a proof-kernel result. Native/compiler, ownership,
physical scalar and tape costs, rounding, stock and analytic recovery remain
outside the result. All five selected framework assumptions remain.

The verifier uses bounded Python allocations, a managed-runtime deviation from
Power of Ten rule 3. Live symbolic storage is at most 799 rows of 799 rational
entries and one backward row; gate count is fixed at 74. Binary enumeration
uses three integer rows and a word of length at most five. Rational sizes are
bounded by those 74 pinned coefficients. Functions stay below 60 lines, loops
have explicit finite domains, and explicit exceptions preserve checks under
optimization. Warning-strict normal and optimized replay supply the available
Python diagnostics. No shared configuration or historical verifier is changed.

## Open next questions

- Can a cancellation-sensitive circuit invariant raise 38? Start with the
  dependency graph of one of the three support-12 rows. The support lemma
  alone is sharp and cannot settle this operator's optimum.
- Can interleaved synthesis lower 74? Start with a new exact ADD/SCALE word
  and prove its arbitrary-input endpoint, then charge every scalar operation
  and any changed physical boundary. This lower bound supplies no such word.

## Credit and related work

Ali Romman supplied PR6537's correction, factorization and open circuit gap.
Credit PR6529, Rohan Arun's PR6399, Erwan L.'s PR6453 and the retained P104
lineage. The imported NOTICE is unchanged. Arithmetic dependency-graph
counting is classical; the new contribution is its first-final-ADD application
and the 38 floor for this exact operator.

PR6542 gives a rounded implementation of the same correction; it asks a
different precision question. PR6529 is its native-transport predecessor.
Neither is replayed here. Independent human and formal proof-kernel review
are unclaimed.
