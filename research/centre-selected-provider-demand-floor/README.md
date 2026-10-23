# Exact information floor for the selected gauge44 centre decoder

## Question and result

For one invocation of the currently selected `gauge44` local provider, how many
independent scalar channels must an exact linear replacement deliver to
preserve the centre phase's updates to consumer rows 112 through 223?

The answer is exactly eight. The selected provider copies eight distinct source
rows into private centres, and its 112-by-8 consumer-demand matrix has rational
rank eight in both forward and backward orientations. Any exact linear
factorization through `m` scalar channels has rank at most `m`; therefore
`m >= 8`. The selected provider attains this information bound with eight
totals. Each total is carried by a rank-8 centre macro, so the selected profile
spends 64 rank units per invocation.

In matrix form, if a replacement uses an encoder `E` with `m` scalar outputs
and a linear decoder `F` to preserve this endpoint, then `D = F E`, whence
`8 = rank(D) <= rank(E) <= m`.

The 64-unit statement is an observed profile and a conditional floor for
replacements that retain the selected rank-8-per-channel carrier contract. The
rank computation alone does not prove that every changed decoder graph or
outside-code factorization must pay 64. The P112 copy-rank theorem has an
explicit root-code factorization interface; applying it to a changed decoder
requires proving that decoder meets that interface. This package claims the
unconditional information floor of eight channels for the stated linear
contract.

## Contract and source binding

The contract is the `centers` phase in
`research/gauge44-slots-t16/evidence/local/LOCAL-PROGRAMS.json.gz`, dispatched
by all calls in the selected global template to provider `gauge44`. The source
manifest named by `certificates/selected-result.json` hashes both the global
template and local program. The verifier checks those hashes, checks that the
inline provider program equals the separately pinned local program, and checks
each call's provider and orientation hash.

Forward totals use source rows `(92, 57, 81, 224, 11, 240, 9, 256)` and private
centres `C_0` through `C_7`, mapped by the selected global template to the
physical private range `[7168, 7176)`. The eight rank-8 centre events have
frames 413 through 420. Each total contributes to 28 distinct consumer rows with
coefficient `+1/4` or `-1/4`; the union of the consumer rows is exactly 112
through 223. The backward gather matrix is entrywise equal to the forward
fanout matrix and restores the same eight source rows.

An exact nonzero minor uses rows `(112, 117, 118, 120, 113, 116, 115, 123)`;
its determinant is `-1/16384`, so the matrix has rank eight. Multiplying that
determinant by `4^8` gives `-4`.

This is source-current work complementary to PR #3120 (head
`6e36982ccc888bdb4dc15982322d8fe1aed392b4`): that PR computed the same kind of
demand rank from a frozen archived template. Its archived local program is a
different input from the local program bound by the current selected source, so
this verifier re-derives the claim from the current provider rather than
importing that archive's binding.

## Verification

From the repository root:

~~~sh
python3 -B research/centre-selected-provider-demand-floor/verify.py
python3 scripts/research_package.py --package research/centre-selected-provider-demand-floor --check-only
~~~

The verifier uses only the Python standard library and exact rational
arithmetic. It checks the selected-record and source-manifest pins, provider
dispatch, source and restore rows, all 224 fanout/gather terms, the exact rank
and minor, and two rank-dropping mutations. It does not run the selected cold
replay or any k-call cost calculation.

## Scope and limitations

- The lower bound is for linear scalar-copy interfaces that preserve this
  exact 112-row endpoint and allow the eight named source-row values as
  independent inputs.
- It proves at least eight independent channels. A 64-unit lower bound for a
  changed implementation additionally needs a proof that its factors satisfy
  the fixed rank-8 root-code charge model.
- No physical cross-call sharing eligibility, restoration bill, hosting,
  precision, tape cost, supplier admission, or new kappa is established.
- The selected-source local check records 716 columns; this package does not
  independently rerun that source check or the full selected replay.

## Open next questions

Can the exact selected 112-by-8 demand be represented by a changed decoder whose
copy channels fall outside the fixed rank-8 root-code factor model while
preserving the endpoint and all source/restoration obligations? This decides
whether the observed 64-unit charge extends beyond the retained carrier
contract. First derive the full factor interface for one concrete replacement
and price its exact matrix. The blocker is that no changed decoder is supplied
by this per-call audit.

## Credit

Selected construction and source line: PR #1094 and the review bound by the
selected record. Demand-rank predecessor: Aaron Wang's PR #3120, which this
package rebinds to the current selected provider. The conditional root-code
cost model is from `research/p112-batch-centre-floor/PROOF.md`; its credit chain
remains with PR #845, PR #1098, PR #968, and PR #1180. Prepared by OpenAI Codex
laptop-07 for Cinna Davis; substantial AI assistance, no human or proof-assistant
review claimed. Apache-2.0.
