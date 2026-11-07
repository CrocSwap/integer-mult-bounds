# Exact paid-rank optimum for the fixed four-call clean query problem

For any characteristic-two field K, formal central Q with Q²=1, six public
roles and any finite number of zero-initialized helpers returned zero, the
least total paid rank is **eight** when at most four square-zero paid calls
of whole-matrix rank at most2 are allowed. Free bases are arbitrary constant
invertible matrices. The complete clean columns must satisfy
W(x,0)=(Qx,0) for every x over K[Q]/(Q²−1). Old helper-value columns remain
unspecified; they are not silently restored or erased.

The new contribution is the missing lower-bound implication. Own excluded
[PR6808](https://github.com/CrocSwap/integer-mult-bounds/pull/6808) already
supplies the four-rank-two/two-helper attaining word and the minimum helper
count. Those are cited attainment facts, not reconstructed, replayed or
claimed again. The four-call cap is essential: the credited PR6800/6138 theorem already gives six targets in seven rank-one calls with no helpers, total rank seven. That word also meets the clean contract; it is cited, not replayed.

The method and projection-case inequality are credited to Nick Petalas
[PR6800](https://github.com/CrocSwap/integer-mult-bounds/pull/6800), section3.
That source requires the complete restored-DIRTY endpoint, producing a
projection. We extend only the needed rank argument to a matrix which fixes
the productive subspace. No new rank-factorization invariant is claimed.

## Written argument

The actual paid alphabet is I+Q N with N²=0. Put epsilon=1+Q and prove
I+QN=(I+N)(I+epsilon N), with I+N a legal constant free basis.
After absorbing/conjugating constants, W=C(I+epsilon M), M=sum N_i,
with all ranks/square-zero properties preserved on every role. The exact
clean columns give C|P=I and (CM)|P=I, hence M|P=I. They do not give M²=M
or constrain its other helper columns.

Factor N_i=U_i V_i through its full rank r_i; square-zero gives V_i U_i=0.
Stack U,V, write E=VU on a space of dimension S=sum r_i. The map V is
injective on P and E fixes V(P), so rank(I−E)<=S−dimP. Every call-diagonal
block of I−E is I_(r_i), giving rank(I−E)>=max r_i. Thus
S>=dimP+max r_i. With six targets and at most four calls,
S>=6+S/4, hence S>=8. The caps give S<=8, forcing exactly four rank-two calls.
The field-independent lemma and characteristic-two query application are
separate in [PROOF.md](PROOF.md). The proof retains arbitrary finite helper
dimension and the complete allowed helper-column contract.

## Evidence and reproduction

The first root-controlled diagnostic passed in 0.678 seconds with 21.672MiB maximum RSS under CPython3.12.14. It authenticates four retained exact source prose files before calculating. The finite coverage is all ordered square-zero 2x2 sums over F2 through four slots, F3 through four slots, and F5 through three slots (zero pads, not paid calls); three explicit rank-two block fixtures; 54 newly assembled two-call F2 query-normalization words with all270 instruction steps checked; 81 padded six-target rank profiles; four mathematical premise controls, one zero-call counting-convention check and three parser controls. The RESULT records exact domains, case counts, rank histograms and streamed certificate digests.

No predecessor verifier, constructor or6808 eight-role attainer is imported or run. Small classical fixtures can overlap prior examples; they are not new constructions. These finite checks corroborate the written all-field lemma and separate characteristic-two query application; they do not prove the arbitrary-dimension statement by enumeration. No proof-kernel or human acceptance is claimed.

```
python3.12 -B scripts/research_package.py --package research/clean-query-rank-optimum
python3.12 -B scripts/check_research_commit.py --package research/clean-query-rank-optimum --check-source-history --check-modes
```

SOURCES binds canonical selection/catalogue/legal provenance. SOURCE-PINS
separately binds the four package-local mathematical source copies to their
exact foreign head/path/blob/mode/size/hash, checked against source trees at
acquisition. This is not a generic foreign-ancestry assertion; cached refs
are not publication history. Direct replay needs no Git/network/live external
files. VERIFY.inputs=[] matches that runtime closure. Default normal/O
commands will compare the complete typed retained RESULT; no self-hash cycle.

## Open next questions and limits

The known seven-call, total-rank-seven source boundary above prevents an unrestricted rank-eight claim. No broader classification or follow-on construction is reserved; helper minimality is not reproved.

For physical use, bind one native caller and price zero-helper preparation,
ownership, every free basis and paid map, layout/movement, chronology,
precision, stock and restoration outside this clean endpoint. These are
unknown. All five selected assumptions and the frontier remain unchanged;
no native supplier, new kappa or complete physical/recursive bill is supplied.
The bit-new-register-model card remains explicitly changed/partial, with its
original native conversion gate unmet. The family decision is a narrow
lower-bound audit, not a new construction/search round.

## Credit and exposure

Credit Petalas6800 for normalization, dirty/projection rank method and the
clean/dirty distinction; ToikY/Codex6808 for credited rank8 attainment and
helper minimum; Josie Elliston6138, Petalas6122, Cinna Davis, Ali Romman5617,
Matarener6114 and retained distinct5007/5857/1974/2027 lineage. Rank
factorization, UV/VU fixed-space transport, rank-nullity and dual-number
normalization are classical. [LICENSE](LICENSE) and [NOTICE](NOTICE) retain
Apache-2.0 and source attribution.

Root proposed the clean fixed-space recipe during preclaim orientation,
then source review identified the projection inequality as prior work.
Related source-aware OpenAI Codex proposal, proof, implementation and review
roles see those sources/recipe; this is not blind independence, human or
proof-kernel acceptance. No earlier result or construction is recounted.

Identity calls N=0 are legal source-model padding and can be omitted. The fifth control enforces only the checker's canonical count of nonzero paid calls; it is not a mathematical obstruction or a forbidden source gate. The first successful packet is retained in the external receipts; its zero-control wording was clarified before freeze.
