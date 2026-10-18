# Full-query source codes require complete endpoint support

PR1862 gives a valid local source encoder that stores the eight-coordinate
centre query in existing source fields. For any invertible full-query encoder
at this interface, the source fields it changes and the target fields it must
correct together cover all 112 ports. Both endpoints cannot be sparse.

The support theorem allows arbitrary finite address-linear encoders. A second,
narrower result rules out a fixed-response logger commuting with the unchanged
line or specified output-frame operator, for every positive tensor power.
Neither result excludes changed operators, monomial conjugacies, carrying the
code through later native work, or paid chart transitions. Endpoint support is
not a universal native-child charge. No new supplier or kappa is claimed.

## Result and evidence

Write J=I-KR, Delta=G-I and H=J Delta. The full-query condition LG=R gives
R Delta=(R-L)G. Since R-L has rank eight and G is invertible, this matrix
has full row rank. If both Delta_i and H_i vanish at a port, then
K_i R Delta=0, contradicting the nonzero K_i. Thus the endpoint supports
cover all 112 ports. Each support also contains at least eight ports.

This supplies a scoped cost control: a model charging one rank-one child per
active endpoint already pays at least 112. Charging a changed source for both
outward and return transfers gives at least 120. Those prices are conditional
rowwise comparators, not a lower bound for all implementations; the old eight
rank-eight centre queries cost 64 in rank mass. A useful implementation must
beat that per-endpoint charging model.

For G=I+ZB and the eight-port query read L in PR1862, there is no solution to
LG=R that commutes with diag(C_q), or with diag(F C_q^-1). Here B may contain
arbitrary complex linear maps, although LZ=I already makes the full-query
logger unique: B=R-L. This is a fixed-frame obstruction, not a lower bound
for every zero-native-cost circuit.

One Fourier output character is enough. At x=1, both excluded-eigenvalue
row sets of Z contain an invertible eight-by-eight minor. Their exact
determinants are -3/512 and -3/1024. Commutation forces the whole output
row of B at that character to vanish, contradicting a nonzero R-L coefficient.
[PROOF.md](PROOF.md) supplies the argument and tensor-power extension.

[EXPECTED.json](EXPECTED.json) is the exact finite certificate. The verifier
derives R directly from the pinned historical scalar program, checks the
source response identities and physical labels, and checks all 512 characters.
There are 494 full-rank cases in both eigenvalue groups. Four actual mutations
fail: a constant character, a zeroed matrix row, a false determinant and a
changed source archive. Three explicit three-port counterexamples show why
invertibility, rank(R-L) and nonzero K rows are needed. A valid toy attains
the support-cover inequality. Checks remain active under Python optimization.

The finite certificate and written argument are separate from a complete
native replay, global routing, precision, hosting or multiplication theorem.
The specified output-frame model is the contract stated in PR1862; this
package does not re-audit all of that predecessor's native events or phases.

## Reproduce

Python 3.11 or newer, standard library only, from the repository root:

```sh
python3 -I -O -B research/sourcecode-commutant/verify.py
```

Expected output:

```text
PASS_SOURCECODE_SUPPORT_AND_FRAME endpoint_support>=112 characters=512 full_rank=494 mutations=4 premise_controls=3 no_new_kappa
```

The runtime reads only its committed certificate and the frozen input archive
declared in [SOURCES.json](SOURCES.json). It needs no network, Git history,
pending PR implementation or generated predecessor receipt. The dedicated
workflow runs the same check under Python 3.11 and 3.14 and retains receipts.
A local replay is separate from hosted CI completion.

## Open next questions

1. **A changed or paid chart transition.** This matters because the local
   encoder is useful only if its source data can be restored or its code can
   be carried onward. First derive the actual conjugated source map between
   two routed charts and price its native transfers. The missing component
   is a complete physical access, restoration and precision invoice.
2. **A different response space.** This matters because the obstruction fixes
   Z and the eight-port read L. First identify a changed target-support or
   query contract and check its excluded-row ranks before searching for a
   circuit. No useful alternative response space is constructed here.

## Credit and review scope

@aliromman's [PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862),
pinned at 7649d9ceecec949541bec4bbde5929344166ba59,
supplies the encoder, fixed-support response space and exact local construction.
Its valid local result is not contradicted. The E8 unit, PR1042 archive,
PR1094 assembly and retained gauge44/native lineage remain credited to their
authors. The source notices credit icekylinx, Hao Yan / FanPUYen, Jeremy Kothe,
Chafik Boukhalfa, rohanarun and NewBArch for the retained frame and supplier work.
No predecessor code is copied into this package.

The new contribution is the endpoint-support tradeoff for arbitrary invertible
full-query encoders, the fixed-frame obstruction and its two-minor witness,
and a separate source-derived exact verifier. Prepared
for Chafik Boukhalfa with substantial OpenAI Codex assistance. No independent
human review or formal proof assistant is claimed. New material is Apache-2.0.
