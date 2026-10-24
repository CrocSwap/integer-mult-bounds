# One modular inversion prepares the fixed CRT cache

**Scoped algebraic construction, no new kappa.** One modular-inverse
provider call prepares all the fixed cofactor inverses and the target
inverse in Hiroki KUMAZAKI's [PR #4716](https://github.com/CrocSwap/integer-mult-bounds/pull/4716)
cache. The cited construction uses `m+1` calls for a left group of size `m`.
The new construction uses one call modulo the full left-and-target product.
For the first source fixture, this changes three inverse calls modulo
`11,13,17` to one inverse call modulo `2431`.

The inversion modulus is wider. **No bit-cost or runtime improvement is
claimed.** Current-state reconstruction, padded invalidity and the target
offset remain the same mathematical contract. Every subsequent evaluation
uses no inverse call. The three current-state query sites established by
#4716 are unchanged; the cache stores none of their evaluated values.

## Fixed data and construction

Let `m>=1`, with pairwise coprime integers `n_0,...,n_(m-1),s>=2` and
positive integer `Q` satisfying `gcd(Q,s)=1`. These include #4716's
left-group moduli, target modulus and preceding right-child product.
Define

\[
S=\prod_j n_j,\quad C_j=S/n_j,\quad T=Ss,\quad
A=\left(\sum_j C_j\right)\bmod S,\quad v=SQ\bmod s,
\]

\[
U=(sA+Sv)\bmod T,\qquad r=U^{-1}\bmod T.\tag{1}
\]

This is the sole inverse call. Extract

\[
\alpha_j=sr\bmod n_j,\qquad \mu=Sr\bmod s.\tag{2}
\]

**Theorem.** The unit `U` in (1) is invertible modulo `T`, and (2) gives
`alpha_j=C_j^-1 mod n_j` and `mu=(SQ)^-1 mod s` simultaneously. The claim
holds for composite moduli too; primality is not required.

For each left modulus, `C_k` is divisible by `n_j` when `k!=j`, so
`U=sC_j mod n_j`. This is a unit. At the target, `U=Sv=S^2Q mod s`,
also a unit. The moduli are pairwise coprime, so `gcd(U,T)=1`.
Reducing `Ur=1` modulo `n_j` gives `C_j(sr)=1`; reducing it modulo `s`
gives `(SQ)(Sr)=1`. These are exactly (2).

The same packed inverse supplies a domain check. For positive moduli at
least two and positive `Q`, `gcd(U,T)=1` holds **if and only if** the left
and target moduli are pairwise coprime and `gcd(Q,s)=1`. If a prime divides
two left moduli, it divides every `C_j`, hence `A`, `S` and `U`. If it
divides a left modulus and `s`, it divides both summands of `U`. If it
divides `s` and `Q`, then `U=S^2Q=0` modulo that prime. These exhaust the
ways the stated coprimality conditions can fail. The constructive argument
above proves the converse. [cache.py](cache.py) verifies the returned
canonical inverse by `Ur mod T == 1`, so an incorrect provider cannot
silently produce a cache.

## Preserve the current-state contract

Let `P_j=product_(k<j) n_k`. Prepare
`w_j=P_j C_j alpha_j mod S`. For a current vector with `0<=a_j<n_j`, set

\[
k(a)=\sum_j a_j w_j\bmod S,\qquad c(a)=k(a)\mu\bmod s.\tag{3}
\]

By (2), these are exactly #4716's fixed-weight reconstruction and target
offset. Equivalently, `k(a)` is the unique integer in `[0,S)` such that
`k(a)=a_j P_j mod n_j` for every `j`, and
`SQ c(a)=k(a) mod s`. If any supplied nonnegative current coordinate
satisfies `a_j>=n_j`, the evaluator returns invalid with `k=c=0`, retaining
the predecessor's disabling rule on padded coordinates. Each call reads
its supplied current vector afresh. Setup depends on no address or payload.

The new contribution is the packed setup (1), extraction (2), domain
criterion and executable cache construction. The CRT reconstruction
contract, three-epoch distinction and exceptional repair correctness are
credited premises from #4716 and its predecessors. No predecessor
executable, word census or physical caller is replayed here.

## Exact first fixture and operand bounds

For `(n_0,n_1;s;Q)=(11,13;17;1)`, the verifier emits

```text
S=143, C=(13,11), A=24, v=7, T=2431
U=1409, r=892, alpha=(6,6), mu=5
```

All extraction identities are checked directly as integer congruences.
The artifact makes exactly one provider invocation in setup; its spy
rejects a second invocation, and is retained through all current-vector
evaluations.

If every fixed modulus has at most `ell` bits, then
`T<2^((m+1)ell)`. Thus the new inverse accepts at most `(m+1)ell` bits,
whereas the old inverses each use at most `ell` bits. This is an explicit
operand-width tradeoff. For `L=bit_length(T)`, `0<=A<S`, `0<=v<s`, and
both summands forming `U` are below `T`; their unreduced sum is below `2T`.
Compute `v` using `Q mod s` before multiplication. Extracting the left
inverses uses the common value `sr mod S`; all other fixed extraction
products are below `T^2`. Prefix-weight products are below `S^2`, since
`P_j<=C_j` and `C_j alpha_j<S`. Forming `sum C_j` is also below `S^2`,
because `m<S` and each `C_j<S`. Reading/reducing the original `Q` still
depends on its supplied bit length.

The code uses exact divisions by known factors, modular additions,
multiplications and reductions in addition to the single inversion.
Their cost is not zero. Without a specified inversion and tape tariff,
one call at width `L` cannot be compared with the `m+1` smaller calls.
No inverse-count minimality is claimed; other arithmetic models may
compute inverses without an inverse-provider operation.

## Evidence and reproduction

Run from the worktree root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/crt-one-inverse-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/crt-one-inverse-cache --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/crt-one-inverse-cache/verify.py
```

The verifier checks 209 cache setups and 8,871 current vectors, with
inverse moduli up to 188 bits. Its complete small family uses ordered
pairwise-coprime triples from `(2,3,4,5,7,8,9)` and right prefix `1` or
`11`. Every pair of padded coordinates through its first invalid value
is evaluated. A separate bounded oracle enumerates `[0,S)` and tests
all defining congruences, rather than importing a predecessor decoder.
Additional fixtures include three/four-modulus groups, composite moduli,
one left modulus, the source fixture and a 521-bit right prefix.

Sixteen inputs/providers are rejected: malformed domains, noncoprime data,
nonunit prefixes, corrupted inverse-provider outputs and invalid residue
types. Three mathematical omission controls detect dropping the target
summand or either extraction multiplier. Both registered normal and
optimized commands use explicit exceptions and `-W error`. The generated
stdout report includes hashes of both executable sources. No handwritten
receipt is committed.

## Scope and implementation limits

This is a source-specific algebraic cache module, not physical integration
into #4716, #5053 or a selected caller. Their files remain unchanged.
No setup/erasure tape program, complete-key service, arithmetic tariff,
compiler-size bound, supplier admission, complete multiplication theorem,
independent human review or formal proof-kernel acceptance is supplied.
The selected conditional kappa remains `60403/20000000`.

The algorithm's loops have the explicit input bound `m`; the verifier's
outer family has at most 210 ordered triples, two prefixes and five
additional fixtures. Small coordinate enumeration has at most 100 vectors
per setup and its direct oracle has at most 72 candidates. No recursion,
network activity or file writes occur. Functions stay below 60 lines.
The runtime validates public domains and authenticates the provider result.

Power of Ten rule 3 deviation: Python allocates managed integers and
collections during execution. Scope is this finite algebraic module and
bounded verifier. Live cache storage is `O(m log T)` bits plus the supplied
input `Q`, with fixed verifier families; no unbounded queue or retained
query cache exists. Normal and optimized warning-strict replay checks the
same predicates. A future fixed-tape integration must replace these managed
objects with a charged arena and prove allocation/cleanup bounds. Rule 9's
inverse callback is restricted by the declared two-integer provider
contract, with one call and a checked postcondition; the verifier uses
only its bounded spy, corruption providers and rejection callbacks.

## Open next questions

1. Under one specified binary-arithmetic tariff, when does the larger
   inversion save total setup work? First compare `I(bit_length(T))` plus
   all packed setup operations with the separate inverse calls. No such
   cost comparison is established here.
2. Can the packed constants be prepared in the actual encoded-current CRT
   arena and erased with its physical owner/head contract? Start with the
   `(11,13;17;1)` setup and bind every arithmetic operand to that arena.
   The missing physical implementation and complete bit-cost ledger block
   supplier substitution.

## Credit and coordination

This contribution is produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

Hiroki KUMAZAKI / kumagi supplied #4716's fixed cache contract and
#4169/#4174's inverse/placement lineage. Cinna Davis supplied #4100's CRT
construction; unpaidmoon supplied #4377's arithmetic tariffs; Ryanson
Jonathan supplied #4409's current-state query handoff; ToikY supplied the
retained Beneš work. Douglas Colkitt, John-Michael Smith and #763 retain
their compact/exceptional-repair credit. JoyboyBrian's #5053 supplies the
separate encoded current-child producer, not an inverse-count premise.
The cofactor congruences used here are elementary CRT identities.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142347)
names the new inverse-count target. [TASK.json](TASK.json) records its scope
change from the all-size implication card, and [SOURCES.json](SOURCES.json)
pins the predecessor contract as provenance. This family decision is narrow:
ship the first setup improvement and leave physical expansion to the named
open questions.
