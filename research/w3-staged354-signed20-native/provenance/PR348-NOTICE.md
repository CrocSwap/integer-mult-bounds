Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance. Apache-2.0.
Inherited files keep their original notices and assistance disclosures. This package claims no exclusive priority
over concurrent work.

What this package contributes:
- the per-point p = 10 complex program (claim 7940/10^7, coarse b = 794022782431403/10^18), together with its
  pointwise pair modules, its frozen layer and its spec;
- the per-invocation module spec and builder (spec_graph.py, aligned_word_spec.py, and anchors (e) and (f));
- the composition of that program with PR #346's bit word, an independent recount of that word's paid children,
  and the reproduction of PR #346's kappa;
- verify.py, MANIFEST.json and the git-blob pins of SOURCE.json.

Everything else is retained and credited:

- LJH-217 / Louis Harrison (Anthropic Claude assistance), PR #346 (research/w3-p10b-complex-p10 at 11b4de5): the
  final w3 bit word on PR #325's p10b word. It is vendored unchanged in bit/pr346/, with its records, hash list,
  kappa receipt, LICENSE and NOTICE.md. PR #346 also composed it with a p = 10 complex supplier and computed the
  complex-bound kappa that this package reproduces. Its bit word's own checks (Design T verifier, PR #266
  checkers, primes, bank tiling) are PR #346's and are not re-run here.
- utcorvusvolat-dotcom: PR #310, the w3 Design T and twin condensation, with their builders and cost model, which
  PR #346 ported to h = 20.
- PR #266's official cohort legality and five-stage column checkers, as run by PR #346.
- DreamingOfClouds (Anthropic Claude assistance):
  - PR #325 (c4f1b74): the p10b bit word under PR #346's, the re-annealed pair module pm_p10.json (the default pair
    module of the spec and the start of the pointwise climb) and the all-but-one module qmod_p10.json;
  - PR #315: the p = 10 five-stage package, qmod_p10.json, the centre-sharing Graph.finish patch, and the outer
    assembly convention (complex-bound path) used for kappa;
  - PR #327 (40ed045): the p = 10 complex supplier, its recipe and chain (aligned_word_p.py, centre46.py,
    paircheck.py, normalize_scatter.py, module_cut.py, discovery/pr327/), the triple module tmod_t2_p10.json, and
    verify.py, which this verify.py generalises; all vendored byte for byte;
  - PR #304: the p = 11 recipe.
- Jacob Sussman (Anthropic Claude assistance): gcert/1, gx.py and gxcore.py (vendored unchanged in gx/,
  Apache-2.0, Copyright 2026 Jacob Sussman, jacobalansussman/wht-power-saving-lean at f010392c), the bridged
  five-stage layout B_2, and the Lean generator and Compare.lean used for the companion program.
- chafreaky / Chafik Boukhalfa (Anthropic Claude and OpenAI Codex assistance):
  - PR #233: the maximum-weight pairing, and the layer package vendored in references/pr233-layer/;
  - PR #200: the frame descent and the complete complex checker;
  - PR #256: the gcert emitter gcert_emit.py;
  - PR #225: scripts/moment.py;
  - PR #329: pricing/outer.py, which is PR #315's unchanged.
- icekylinx (OpenAI GPT-6 Astra and Codex assistance): PR #144 paired cubes and Graph.finish; PR #184 the
  source-assisted construction, frame flow, exact lift and contract.
- Avi Eisenberg (ikeboy): PR #191/193/194/202, the source-aligned pipeline and the PR #202 baseline.
- eumemic (Anthropic Claude and OpenAI Codex assistance):
  - PR #168 modules and frames;
  - the source527 rational moment engines (scripts/source527/, see its NOTICE);
  - outer.py, the 47-constraint outer assembly of PR #315 (from icekylinx's PR #144 and Zhihao Chen's PR #23,
    with hipotures' balanced prefix).
- DaysSky: PR #162, the extended carrier closure.
- hcg890: PR #234, the five-stage architecture and the 10^-16 fallback envelope.
- SovereignSteak: PR #250.
- Evan McKinney: the completed banks of the five-stage packages.
- Rohan Arun: the joint-dual re-pin in PR #327's head.
- The PR #202 baseline lineage, as credited in references/pr233-layer/NOTICE.
- OpenAI: the original complex phase network of "Integer multiplication below n log n".

The credits above do not imply review or endorsement by the credited authors.
