# A sharper plateau divisor for chronological widths

**Scoped written proof with exact finite corroboration. No new κ.**
This contribution was produced by Nick Petalas.

For the separated fixed-rule numerical compiler of Jerry Chen / CubeJerry's
[#7424](https://github.com/CrocSwap/integer-mult-bounds/pull/7424), replace its
common plateau exponent `tau=A*ceil(log2 k_min)` by

```
nu_gamma = 1 + floor((min(N,A*gamma_next-1)-A*gamma)/delta_gamma),
delta_gamma = smallest positive fresh-source rank on the plateau.

B_n divides product_gamma S(gamma)^nu_gamma, for every 1 <= n <= N.
```

Every new exponent is at most `A-1`, strictly below the previous `tau`.
The new divisor divides the old one, strictly whenever an observed plateau
has source count greater than one. It also gives a smaller explicit bit
upper bound. It changes neither the width sequence nor its proved
asymptotic degree. [PROOF.md](PROOF.md) states all hypotheses and proves
that the visit exponent is the exact maximum on the numerical child graph.

The reason is specific: every paid exit leaves its parent's plateau, while
every complement step inside it subtracts at least `delta_gamma`. Applying
that count to every prime-valuation chain proves the divisor, including
primes absent from the rank alphabet.

For targets `(2,3)`, one paid rank-1 site, `A=64` and `N=127`, the upper
divisor decreases from `2^64` to `2^32`. The new divisor attains the width
already established by #7424. That width formula is credited prior work;
the new result is the general divisor refinement. No physical supplier for
this toy rule is asserted.

## Exact evidence

The independently written standard-library checker imports no predecessor
program. It constructs 670 distinct bounded rule/maximum fixtures, totaling
11,926 width rows and 851 plateau rows. All 851 literal graph maxima equal
the new visit bound. The divisor decreases strictly on 448 fixtures; 222
have only base ranks. A further 294 first-plateau/truncation fixtures attain
the divisor exactly. Sixteen domain and semantic controls pass, including
lowering the exponent, dropping its final `+1`, allowing a same-plateau exit,
and pooling repeated chronological cuts.

Normal and optimized runs print identical computed results and fixture digest:

```
PASS_ADDITIVE_PLATEAU_WIDTH
computed_library_sha256=39175e152722a32239563041f1ee5c4669c8aca9b5212d3bc96a0ccb98dd8365
```

Counts refer to the stated finite fixtures. The universal statement rests
on the written proof and the cited numerical-flow premises. No predecessor
scientific suite or selected cold replay was run.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/additive-plateau-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/additive-plateau-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/additive-plateau-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/additive-plateau-width --check-source-history --check-modes
```

Substitute another CPython 3.12 path on another machine. The two registered
commands have 120-second timeouts. Direct verification writes nothing.
Adding `--record /absolute/external/new.json` generates a receipt with the
computed results, interpreter version and SHA256 hashes of all seven package
files. It refuses existing paths. A receipt is never hand-written.

[SOURCES.json](SOURCES.json) pins main's historical task/selected/width documents
as provenance. It separately identifies the exact public #7424 proof and its
SHA256 as cited mathematical provenance. No external executable/data inputs,
network access or unmerged Git objects are needed by the direct verifier.
The citation hash is not a claim of runtime authentication or theorem review.

## Limits and implementation bounds

The theorem concerns the exact least-replication recurrence for finite fixed
separated histograms with `r_max<k_min` and `m<=A`. It supplies no evaluated
selected manifest or new batching policy. Native semantics, owned erasure,
complete instruction generation, tape/precision and analytic recovery remain
separate. All five selected assumptions remain. No complete multiplication
theorem, physical runtime/memory gain or frontier change follows.
Independent human and formal proof-kernel review are unclaimed.

The executable checker restricts `A,N<=256` and each explicit role list to
four entries. All loops have finite bounds; word/path depths are at most
eight. Each census has at most 131,072 visited units and 65,536 exits. It
retains fewer than 17 million child entries in the most permissive allowed
case; actual fixtures are smaller. Python's managed allocation is a stated
Power of Ten rule-3 deviation: the enforced caps bound collections, and no
persistent process or cache is retained. A fixed-capacity implementation
would be needed before increasing these limits. Functions stay below 60
physical lines, checks use explicit exceptions under `-O`, and warning-strict
source compilation and execution are the applicable diagnostics. No external
linter or type checker is required by this standard-library package.
The invalid-input table has eleven fixed local callbacks, a bounded rule-9
deviation used only to exercise rejection paths. They run synchronously and
hold no external state; direct dispatch would replace them before that table
accepted externally supplied cases.

## Open next questions

1. Retain actual source multiplicities and gcd discounts for one evaluated
   selected histogram. Start from its exact chronological source manifest
   and derive a prime-valuation bound. That manifest and analysis are absent
   here; a smaller visit count does not prove additional cancellation.
2. Specify a compact width representation and its exact divisibility-query
   contract when A varies. The cited quadratic explicit-output obstruction
   survives this refinement; changing the representation needs a new proof.

## Credit and scope

Jerry Chen / CubeJerry #7424 at
`d622d8c62defa9defeb95741e88b33a120044866` supplies the independent-ambient
recurrence and explicit open question about ambient constants; #7345 supplies
its quantitative library framework. codyw912 #4638 supplies the original
plateau-product divisor. Mihir Srivastava #4507/#5071 supplies chronological
gcd/LCM batching; zxv and Jacob Alan Sussman supply the compiler/flow, with
Ryanson Jonathan, Cinna Davis and the retained native lineage credited by
those sources. Their results are premises, not audit deliverables.

The new minimum-decrement argument, divisor proof and checker were produced
by Nick Petalas. New work is Apache-2.0. The formal-interface-lemma card is
explicitly changed to this written compiler-size side result. The selected
orientation passed at main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8, selected #7000. [Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19571833).
