# Conditional κ = 7.93469326753735·10⁻⁴: #348 with a frame-retimed complex program (+7.65·10⁻⁸ over #348)

**κ = 158693865350747/(2·10¹⁷) ≈ 7.93469326753735·10⁻⁴** — complex coarse b = 794099421460999/10¹⁸ (was
794022782431403/10¹⁸ in #348). The only change to chafreaky's #348 package is the complex gcert/1
(`certificates/gcert1-p10-b325-c2.json.gz`), replaced by a concave-frame-descent retiming of it
(`retime/retime_gcert.py`, 21 gate moves; same gates, same R = 6,253, same registers). #346's complex guard
(gx.check1 + gxcore, labels, scalar words, splice, precision guard) passes on the retimed program and b is certified by
both rational moment engines with the 10⁻¹⁶ fallback; the outer assembly (47 strict constraints) gives the κ above.
Full replay (`verify.py`, including #348's complete regeneration followed by the deterministic retiming, byte-for-byte equal to the committed program): PASS, κ = 158693865350747/(2·10¹⁷).
Everything else below is #348's README (credit: chafreaky, LJH-217 #346 and upstream).

---

κ = 7.93392809291691e-4

# PR #346's w3 bit word with a per-point p = 10 complex supplier

A conditional finite construction with **κ = 793392809291691/10¹⁸ ≈ 7.93392809291691 × 10⁻⁴**. That is
+8.127·10⁻⁷ (+0.1025 %) over PR #346 (κ = 396290046684973/(5·10¹⁷) ≈ 7.92580093369946·10⁻⁴).

PR #346 (LJH-217) put PR #310's w3 Design T and twin condensation on PR #325's p10b bit word. That word's bit
coarse saving lies above every known complex cap, so κ is set by the complex supplier. This package keeps PR
#346's bit word unchanged and replaces its complex supplier with a stronger p = 10 program of the same recipe. In
that program each point i has its own pair module, shared by both bits.

| side | supplier | coarse saving (10⁻¹⁶ fallback) |
| --- | --- | ---: |
| bit | PR #346's final w3 word on PR #325's p10b word (vendored) | c = 32069035133443/(4·10¹⁶) ≈ 8.01725878336075·10⁻⁴ |
| complex, PR #346 | p = 10 gcert/1 program, PR #325's pair module, flow R 6,265 | 396604388013523/(5·10¹⁷) ≈ 7.93208776027046·10⁻⁴ |
| **complex, this package** | **p = 10 gcert/1 program, pointwise pair modules, R 6,253** | **b = 794022782431403/10¹⁸ ≈ 7.94022782431403·10⁻⁴** |

Both suppliers make the complex side bind. Here the bit saving is capped one 10⁻¹⁸ grid point below the leaf cap
(1 − 10⁻⁹)·b and fed through PR #315's outer assembly, which checks 47 strict constraints and the finite bridge.
`verify.py` first reproduces PR #346's κ exactly from PR #346's b, then computes κ from this package's b. In both
cases the next 10⁻¹⁸ κ and the cap itself are rejected.

## Complex supplier

The word, recipe and chain are PR #327's (at `40ed045`): the source-assisted complex word of PR #184/#194 at
p = 10, with the centre-sharing graph, HK carrier arcs plus PR #162's extension, PR #200's frame descent, PR #233's
maximum-weight pairs, PR #184's flow and exact lift, PR #194's contract and PR #256's emitter. The query modules
come from `spec/c2.json`:

- triple module: PR #327's `tmod_t2_p10.json`;
- all-but-one module: PR #325's `qmod_p10.json` (PR #315's), the same for all 90 invocations;
- pair module of point i (both bits): `modules/pointwise/pmod_i{i}.json`. These six distinct files were found by a
  greedy climb that started from PR #325's `pm_p10.json` (`discovery/README.md`). Each has 36 inputs plus the
  star-centre root, and `centre46.load_pmod46` checks its contract.

| program | R | W | N | blocks | a | rejected | coarse b (/10¹⁸) | Lean |
|---|---|---|---|---|---|---|---|---|
| PR #327 centre-mw | 6,455 | 10,295 | 165,940 | 47,979 | 7795/10⁷ | 7796/10⁷ | 779597612622781 | 1 − 7795973/10¹⁰ |
| shared #325 modules (`spec/uniform.json`; same b as PR #346's supplier) | 6,265 | 10,105 | 162,140 | 47,619 | 7932/10⁷ | 7933/10⁷ | 793208776027046 | 1 − 7932084/10¹⁰ |
| **pointwise pair modules (`spec/c2.json`, this package)** | **6,253** | **10,093** | **161,900** | **47,599** | **7940/10⁷** | **7941/10⁷** | **794022782431403** | **pending** |

**Status of the 7940/10⁷ program.** Sussman's reference checker `gx.check1` (exact scalar identity) and his
`gxcore` mirror of the two Lean checks accept it, and both reject a flipped sign. It also passes the rest of the
chain: `paircheck.py`, PR #200's checker, the exact flow lift and PR #194's contract (13/13). `verify.py`
regenerates it byte for byte. **Its Lean run is pending**: the host with the Lean toolchain needs an interactive
re-authentication. The companion program with one shared pair module (7932/10⁷) went through the same pipeline and
was built in Lean (`lean/companion-7932-evidence.txt`). The per-point program uses the same generator path, with
only its module files changed.

## Bit side

PR #346's final word is vendored unchanged (`bit/pr346/`). It consists of:

- its final records (`FINAL-RECORDS.bin.gz`, checked against its `RECORD-SHA256SUMS`);
- its κ receipt (the normalized five-stage histogram, the stock W = 125,712 and c);
- its LICENSE and NOTICE.

`verify.py` decodes the records with its own reader and recounts the paid children (MOVE and COPY ranks). It then
requires PR #346's normalized histogram to equal 60·H + 12·2v·(e₃₈ + e₁₉ + e₄₂ + e₄), and certifies c from it with
both rational engines. The stock W is taken from PR #346's receipt and is not re-derived. PR #346's own bit checks
are not re-run here: the Design T verifier, PR #266's legality and five-stage column checkers, primes and bank
tiling. Since the complex side binds, κ depends on the bit word only through c > (1 − 10⁻⁹)·b, and c is 0.97 %
above that cap.

## Verify

    python -m pip install numpy==2.3.5 scipy==1.17.0
    python3 -B research/w3-p10b-pointwise-complex/verify.py --quick   # about 30 s: pins, bit side, program, kappa
    python3 -B research/w3-p10b-pointwise-complex/verify.py           # about 6 min: also regenerates the program

Nothing is fetched; `-O` is refused. `--quick` covers:

1. `MANIFEST.json`;
2. `SOURCE.json`: git blob and sha256 of every vendored file at PR #327 `40ed045`, PR #325 `c4f1b74`, PR #346
   `11b4de5` and PR #329 `c6b1a28`;
3. the bit side;
4. the committed program: canonical sha256 `ff2d7307…`, `gx.check1`, `gxcore`, the E5 controls, and the exact
   price (7940/10⁷ with and without the fallback, 7941/10⁷ rejected, b by both engines);
5. κ for PR #346 (reproduced) and for this package.

The full run also regenerates the program:

1. it rebuilds PR #202's 308 files from the vendored PR #233 package;
2. it runs PR #327's anchors (a) and (b), then anchors (d) and (e) on `spec/uniform.json`;
3. it runs anchor (f): on the companion's frozen layer, `aligned_word_spec.py --spec` writes the same seven files as
   PR #327's `aligned_word_p.py --centre46`;
4. it builds the per-point word with `aligned_word_spec.py --spec spec/c2.json` and runs the whole chain;
5. it requires the committed program byte for byte, and compares the run with `certificate/expected.json`.

`.github/workflows/w3-p10b-pointwise-complex.yml` runs both modes on Python 3.12 and 3.14.

## Open obligations

- The Lean build of the 7940/10⁷ program (pending; see above).
- Everything PR #346 lists as open for its bit word: PR #310's native downstream chain is not ported to p = 10,
  PR #315's scalar/prime/finite stages cannot take an edited word, and the complex guard keeps PR #315's p = 11
  additive row constants.
- PR #346 also ran PR #315's portable complex checks, ported to p = 10 (labels, scalar words, splice, precision
  guard); they are not run on this program here. This package's complex checks are PR #327's chain plus
  `gx.check1`/`gxcore`.
- All inherited interfaces of PR #315/#325/#346 remain assumptions. This is a conditional finite construction,
  not a formal verification of the multiplication theorem.

## Files

| path | origin | content |
|---|---|---|
| `verify.py` | new (from PR #327's verify.py and PR #329's math_check.py) | the checks above |
| `spec_graph.py`, `aligned_word_spec.py` | new | per-invocation spec and word builder |
| `spec/c2.json`, `spec/uniform.json` | new | the program's spec, and the companion spec used for anchors |
| `modules/pointwise/` | new | the ten per-point pair modules |
| `modules/pm_p10.json`, `modules/qmod_p10.json` | PR #325 `c4f1b74` | default pair module and the all-but-one module |
| `modules/tmod_t2_p10.json` | PR #327 `40ed045` | triple module |
| `layers/c2/`, `layers/uniform/` | new | frozen layers of the program and of the companion |
| `certificates/gcert1-p10-b325-c2.json.gz` | new | the program, star form |
| `certificate/expected.json` | new | the full run's record |
| `bit/pr346/` | PR #346 `11b4de5` | bit word records, hash list, κ receipt, LICENSE, NOTICE |
| `pricing/outer.py` | PR #329 `c6b1a28` (= PR #315's) | the 47-constraint outer assembly |
| `lean/companion-7932-evidence.txt` | new | Lean console output of the companion program |
| chain, checkers, engines, `references/`, `discovery/pr327/` | PR #327 `40ed045` | vendored byte for byte |
| `discovery/` | new | how the modules and layer were found |
| `SOURCE.json`, `MANIFEST.json`, `PROOF.md`, `NOTICE` | new | provenance, pins, claim, credits |
