# Independent universal certificate for the paired-log ordered inverse

**Independent verification; no new kappa.** Jose Manuel's
[PR1998](https://github.com/CrocSwap/integer-mult-bounds/pull/1998) claims that
its explicit nine-call decoder works over modules over a unital ring, with
noncommuting stage maps. This package checks that precise identity using typed
integer operator polynomials. It corroborates the predecessor proof with a
different method from its rational-matrix fixtures.

The complete symbolic checks pass. The closed decoder equals reverse-event
inversion, and both composition orders are identity on all 17 input blocks.
The separate block-matrix checker independently reconstructs the forward word
and checks both products. The four initial odd-stage logs have identically zero
coefficients in every final X and log block, as claimed by the predecessor.

## Statement and hypotheses

Let V and L be modules over any unital ring. For stages s=0,...,8 let
R_s:V→L and P_s,Z_s:L→V be linear maps satisfying

`R_s P_s = R_s Z_s = I_L`.

There are four X banks, four Y banks and nine independent, arbitrary incoming
log banks. Let W be the chronological map on `V^4 ⊕ V^4 ⊕ L^9` specified by
the pinned PR377 nineteen-event recipe, **before** its terminal signed exchange.
For a forward call, with q=R_s X_j:

```
X_j <- X_j - Z_s q + P_s log_s
Y_j <- Y_j + new X_j
log_s <- q
```

For a backward call, with q=R_s Y_j and the old Y_j used in the first line:

```
X_j <- X_j - old Y_j
Y_j <- Y_j - P_s q + Z_s log_s
log_s <- q
```

The bridge `(dst,src,c)` adds c X_src to X_dst and subtracts c Y_dst from
Y_src. Let D be the closed decoder in the frozen
[PR1998 statement](references/PR1998-README.md), section “Explicit decoder”.
The certificate establishes `D W = W D = I`. Operator order is retained;
there is no field, division, dimension or cross-stage commutation assumption.

This statement concerns the fixed nine-call controller. It does not extend to
controllers with shared incoming logs or changed event order. The query-rank
and observation-row-space theorem from PR1998 is outside this certificate.

## Why the symbolic certificate is sound

A block entry is a finite Z-linear combination of typed operator words. Words
act rightmost first. The only reductions delete adjacent `R_s P_s` or `R_s Z_s`
at the same stage; the resulting empty word is identity on L. Each deletion
is justified by a stated hypothesis, and combining integer coefficients uses
only additivity. Thus reducing every entry of a product to its identity entry
certifies that product for every instance of these module maps.

The rewrite system terminates because each rule shortens a word by two. Its
left sides have no overlaps: they start with R and end with P or Z. Reductions
at disjoint sites commute. Consequently the reductions are confluent and give
unique irreducible words. This argument covers every word length and all nine
stages. The finite normalizer tests below are additional implementation checks.

[verify.py](verify.py) propagates block expressions through the literal events,
independently transcribes the closed decoder, and constructs a reference inverse
by undoing each event. It checks 578 block identities in the two composition
orders and 289 block identities comparing the two inverse descriptions.

[check_certificate.py](check_certificate.py) imports neither that implementation
nor PR1998's code. It builds sparse elementary 17-by-17 block matrices, multiplies
them chronologically, and uses whole-word rightmost reduction instead of a
stack. It compares the resulting W with the certificate and checks both inverse
products. This forward binding also rejects replacing W and D by two fake
identity matrices.

The binding of the closed formulas to the pinned prose is an explicit manual
transcription, available for review in `closed_decoder`. This is a checked
algebraic certificate and a written soundness argument. No proof-assistant
kernel build or full multiplication-theorem formalization was performed.

## Exact evidence and controls

[CERTIFICATE.json.gz](CERTIFICATE.json.gz) contains every coefficient and ordered
word: 541 forward monomials and 2,070 decoder monomials, with maximum word
length ten. A normal replay regenerates and compares every proof-relevant field
without writing files. Equality uses decompressed canonical JSON; compression
container bytes are not mathematical acceptance criteria.

The main checker rejects all 53 prescribed faults:

- 18 individually disabled right-inverse relations;
- all 18 omitted nonterminal events;
- all nine changed bridge signs;
- all eight omitted Y-reader queries.

Disabling a relation is a certificate failure under fewer hypotheses; these
controls are not counterexamples to the legal predecessor construction. No
optimization search or impossibility claim is made.

Seed 83 selects stages 8 and 3 for a complete comparison of stack, leftmost and
rightmost reduction on all **12,872** well-typed words of lengths zero through
eight in that six-symbol alphabet. Cross-stage cancellation, operator-order and
ill-typed-action controls are included. The controller identities use all 27
stage symbols. [test_certificate.py](test_certificate.py) has five test groups,
including eight rejected receipt corruptions: coefficient sign, reader stage,
two fake identity maps, Boolean/float/zero coefficients, Boolean input index and
truncated matrix. Its checks remain active under `-O`.

## Reproduce and source pins

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/paired-log-universal-identity-seed83
```

Expected: all three registered commands pass, including

```
PASS_PAIRED_LOG_UNIVERSAL_IDENTITY blocks=17 stages=9 two_sided_identities=578 normalizer_words=12872 controls=53 no_new_kappa
PASS_PAIRED_LOG_BLOCK_CERTIFICATE two_sided_block_identities=578 forward_monomials=541 decoder_monomials=2070 maximum_word_length=10
```

The final command reports five passing test groups. Metadata-only validation is
`python3 scripts/research_package.py --package research/paired-log-universal-identity-seed83 --check-only`.
To regenerate only this certificate, run its `verify.py --write-certificate`.

Base commit: `c676548106012571fefa1dce0ec16f1bcfe11dce`.
[SOURCES.json](SOURCES.json) pins the retained PR377 recipe, selected-record
provenance and actual selected review/assembly. The recipe SHA256 is
`910fffd7b8980f1130d8bbec56d5ac34f92986c2a2c480b6aea40754b4b832ac`.
[PENDING-SOURCE.json](PENDING-SOURCE.json) pins PR1998 head
`9a3a967693055eba38ee4a5f5d311295fc4c224c`, its frozen statement and the inspected
predecessor verifier. The latter is neither copied nor imported.

At this base the selected conditional kappa remains
`836330098538459/500000000000000000 = 0.001672660197076918`, from PR1094, with
PR589/PR555 on the bit side. Native chart realization, routed Y-reader
acquisition, injections, owners, log normalization, precision/tape costs, a
complete paid recurrence and the inherited all-size/analytic interfaces remain
outside this audit. No selected cold replay is required for these new files.

## Open next questions

Transport this exact ordered identity and its source binding into a proof
assistant. First define the two module sorts and 27 maps, prove the local
two-sided swap identity from the two right-inverse equations, and compose the
pinned recipe before comparing the explicit decoder. This would replace trust
in the Python checkers with a checked proof term for this one interface. The
source-to-proof-assistant adapter and build remain absent. The structured
question, relevance and blocker are in [TASK.json](TASK.json).

## Coordination and credit

[CLAIM.md](CLAIM.md) records track 75–84, OS assignment seed 83, the three narrow
candidates, scope, base and finish estimate. No pinned sprint issue existed, so
the claim is local. [OVERLAP.json](OVERLAP.json) records the entry scan's complete
PR/Discussion pagination and its limits. [FINAL-OVERLAP.json](FINAL-OVERLAP.json)
records the final scan: all 337 open PRs and the latest 25 updated Discussions.
A connection reset prevented a full final Discussion refresh; its coverage is
explicitly partial. PR1998 was merged during this session at the unchanged
pinned head. The newer phase-query rank claim and native common-hub query/cost
work are separate investigations; this certificate adds algebraic corroboration
to the incorporated predecessor.

Jose Manuel (@jmbarrancoml), PR1998, supplies the explicit decoder and proof being
checked. Zhihao Chen (@jacklightChen), PR377, supplies the retained controller
recipe. Ali Romman (@aliromman), PR1862/PR1969, and Rohan Arun (@rohanarun),
PR1931, supply its local paired-query lineage. Their predecessor attribution is
retained in the frozen statement. Query swaps and ordered inversion use standard
linear algebra; this package claims the independent symbolic certificate.

Sricharan Vagvala (@theon199) prepared the new work with substantial OpenAI Codex
assistance in research, mathematics, implementation, verification and prose.
No subagents or independent human review were used. New work and the retained
PR1998 statement are Apache-2.0; upstream and frozen predecessor packages remain
unchanged.
