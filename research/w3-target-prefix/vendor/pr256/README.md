# gcert-program-233

**The source-assisted complex word of PR #233 as one explicit numbered program (no new κ).** PR #194's contract
notes that "a literal globally renumbered operation program is not exported" for its flow word. This package
exports it, for PR #194's word and for PR #233's, in Jacob Sussman's certificate format gcert/1
(jacobalansussman/wht-power-saving-lean): 12,052 numbered registers, 18,248 frames, every addition explicit, the
star scatter as a rule. His reference checker `gx.check1` (vendored unchanged) accepts both files: nested frames
of every register, block histogram, N = 262,944 unit moves, and the exact scalar identity (every target receives
exactly its source, every source is restored).

| program | blocks per invocation | N | checker | five-stage saving |
|---|---|---|---|---|
| PR #194 word (control; the circuit of #193) | 70,169 = Sussman's published histogram, class by class | 262,944 | accepted | 7474547/10¹⁰ (his Lean figure; `gxdry.py` reproduces it on this file) |
| **PR #233 word** | 69,683 | 262,944 | accepted | **7547/10⁷ exact bounds here; 7547361/10¹⁰ by Sussman's mirror** |

The PR #233 program's ledger 3(x + y + s + c) + 2v·e₂ is PR #233's certified child histogram, so this is the word
PR #233 certifies (complex saving 3549537/5·10⁹), now as a transcript a third-party checker reads. In the
Lean-checked five-stage layout (m = 110, W = 14,692) it is 0.97% above the circuit of #193. κ does not change: the
bit supplier binds in every current assembly. [PROOF.md](PROOF.md) states the claim, the checks and the emitter.

## Verify

    python -m pip install numpy==2.3.5 scipy==1.17.0        # only for the pinned regeneration of PR #202's word
    python3 -B research/gcert-program-233/verify.py          # about 4 minutes; -O is refused

The script checks every pin of `SOURCE.json`, rebuilds the 308 pinned files of PR #202 from the vendored PR #233
package and regenerates the source-aligned word (PR #194's pipeline), then for each of the two physical layers runs
PR #184's flow (`--witness`) and exact lift, emits the gcert/1 program with `gcert_emit.py`, runs `gx.check1`,
compares the block histogram (control: Sussman's `references/sussman/pr193-blocks.json`; result: PR #233's child
histogram), certifies the five-stage moment at 7547/10⁷ (7548/10⁷ rejected) and compares the regenerated
certificates byte for byte (uncompressed JSON) with `certificates/` and the run with `certificate/expected.json`.
`--write` regenerates the committed files; `--temp-root` chooses scratch storage.

To check a certificate with Sussman's tools directly:

    python3 -B tools/gx/refcheck.py <this package>/certificates/gcert1-p11-pr233-flow.json.gz   # in his repository
    python3 -B tools/gx/gxdry.py    <this package>/certificates/gcert1-p11-pr233-flow.json.gz   # mirror and price

## Files

`verify.py`, `gcert_emit.py` (the lowering), `gx/gx.py` (Jacob Sussman's reference checker, unchanged),
`scripts/moment.py` (exact moment bounds, from PR #225), `certificates/gcert1-p11-pr194-flow.json.gz` and
`certificates/gcert1-p11-pr233-flow.json.gz` (the programs, 0.5 MB each), `certificate/expected.json`,
`references/pr233-layer/` (PR #233's package at `109a857`: baseline tarball, witness, verify helpers, certificate),
`references/sussman/pr193-blocks.json` (the histogram and counts of his certificate of #193), `SOURCE.json`,
`PROOF.md`, `NOTICE`. `.github/workflows/gcert-program-233.yml` runs the verifier on Python 3.11 and 3.13.
