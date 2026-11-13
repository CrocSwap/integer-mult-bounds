# Exact tensor fixed spaces of the forward F9 transport

This contribution was produced by Nick Petalas. Apache-2.0.

Claim types: scoped written proof and exact finite signed-cycle certificate.
For the forward full-frame F9 operator-2 monomial T published by unpaidmoon
in [PR #7447](https://github.com/CrocSwap/integer-mult-bounds/pull/7447),
the largest complex payload subspace fixed by its f-column tensor power
has exact dimension

```text
F_f = (512^f + 256^f + 4*32^f + 4*16^f)/10,  for every f>=1.
rank(T^(tensor f)-I) = 512^f-F_f.
```

At one column the fixed space has dimension 96 and the correction rank is
416. At two columns they are 33,280 and 228,864. The predecessor's 16 fixed
computational basis addresses do not exhaust its fixed complex payloads.
The new certificate finds 16, 8, 48 and 24 unsigned-gauge cycles of lengths
1, 2, 5 and 10. Their phase products are all one. Their orbit sums give an
explicit basis at one column, and character averaging proves the all-width
formula. See [PROOF.md](PROOF.md).

If an additive linear repair uses k maps of complex matrix rank at most b,
it must satisfy `k*b >= 512^f-F_f`. This is sharp for unrestricted linear
rank decompositions. That matrix rank is not native axis rank, Fourier
support rank, a recursive child rank or an H8 centre price. No physical
tariff follows without a separate implementation contract.

## Scope and evidence

The monomial and its identification with the source's forward circuit are
cited premises. No predecessor scientific checker is imported or replayed.
Its exact two input files and unchanged credit are retained under `sources/`;
[SOURCE-PINS.json](SOURCE-PINS.json) records their head, origin paths, Git
blob IDs and SHA256 hashes. They are declared inputs in [VERIFY.json](VERIFY.json).
The generic [SOURCES.json](SOURCES.json) binds the task catalogue and selected
record as historical Git provenance; it does not pretend the pending PR is
already an ancestor of main.

The direct verifier checks all 512 signed monomial edges, its complete cycle
partition and diagonal gauge, and all ten power traces. Exact spectral
convolution checks the formula through width 64. A separate literal
two-column pass covers all 262,144 addresses. Sparse Gaussian elimination
of T-I over F257 checks rank 416. Nine domain and semantic controls pass.
The generated stdout receipt hashes every package file; replay writes nothing.
The unbounded quantifier rests on the written projector argument.

The `joint-query-controller` card is explicitly changed to this algebraic
target-debit question. The selected binding-only orientation passed at main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Selected
conditional kappa .00363005817 remains unchanged. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592103)
states the same forward-only scope.

Live overlap covered open PR bodies, active Discussions and handoffs,
recent account PRs, local reservations, distinctive main README searches
and targeted merged-PR searches. The general closed-PR cache refresh timed
out; no complete historical-diff or unpublished-work search is claimed.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/f9-tensor-fixed-space/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/f9-tensor-fixed-space/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f9-tensor-fixed-space
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/f9-tensor-fixed-space --check-source-history
```

Another CPython 3.12 executable may replace that local path. The direct
marker is `PASS_F9_TENSOR_FIXED_SPACE`. Both registered commands use warning
errors and retain every check under optimization. The direct verifier also
runs from a read-only Git-free export, without network or external libraries.

## Limitations

The result is over the complex numbers, for the one published forward
monomial. The actual backward-sign opcode -2 is a different binding.
No physical caller, restored dirty workspace, native implementation,
precision/storage invoice, supplier admission, new kappa or complete
multiplication theorem is established. All five selected framework
assumptions remain. Independent human and formal proof-kernel review are
unclaimed. No selected cold replay, predecessor scientific replay, Lean
or Docker run is included. Code bounds and the managed-allocation deviation
are recorded in the proof.

## Open next questions

1. Can a named legal caller exploit one of these payload spaces after
   paying for its orbit-sum basis, return and restoration? Start with one
   source-compatible space and price both boundary conversions. No native
   tariff for the diagonal gauge is supplied.
2. What is the signed-cycle spectrum of the actual backward-sign opcode
   -2 transport? First obtain its exact source-bound operator. The current
   result does not identify that event with the forward monomial.

## Credit and related work

Credit unpaidmoon for #7447's monomial, circuit identification and
target-debit question, and #6929's earlier fixed-vector distinction.
Ali Romman's #5720/#5745 supply the F9 word and active-mode context,
retaining flyingviper's restoration work and the filtered-native packet of
Cao Yifan, Cinna Davis and Dugongue. Those results are cited, not audited.
Character averaging, diagonal cycle gauges and matrix rank inequalities
are classical. The new step is this transport's complete signed-cycle
certificate, exact all-width payload dimension and correction-rank formula.
No global literature-priority claim is made.

Related open work: #7447 prices the forward monomial at one column; this
package adds its complex fixed-space spectrum and tensor correction rank.
#7301 concerns matrix elements of the canonical K_G operators on basis
addresses, whereas this result concerns the single forward full-frame T
on arbitrary complex subspaces. Neither supplies a physical caller here.
