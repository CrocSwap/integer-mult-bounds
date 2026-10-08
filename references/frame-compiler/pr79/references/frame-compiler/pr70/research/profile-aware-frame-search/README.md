# Profile-aware frame compilation on frozen PR62

New conditional κ **5.10403292611078e-5**, exact `255201646305539/5000000000000000000`, above the strongest frozen #62
stacked witness `5101691/10^11` by approximately **0.0459048991%**.
The new ideas are complete-profile pricing of retired dependency circuits and
bounded admissible carried-signal exchanges. Coordinate/basis and complement
variants are also explored. The accepted result changes literal compiler words
and actual child profiles; it is not another parameter-only refinement.

The original62 complete profile has exact lower moment >1 at the new bit saving,
and the new complete profile has exact upper moment <1. All47 strict assembly
conditions and seven margins pass. **53 Lean endpoints** pass:34 new universal,
15 concrete,4 reused rational-helper lemmas. No omitted proof, project axiom or
native decision shortcut. The math scope includes dirty-word/complement safety,
coordinate conjugacy, fresh-kernel clearing, actual finite rounding and old-profile
rejection. It does not formalize the Python/C++ compiler or the all-size theorem.

## Reproduce the accepted words

Use an external checkout of frozen PR62 commit
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. No newer sources are consumed.
See `verification/README.md` to compile its exact C++17 profiler, then run:

```
python verification/verify_words.py --upstream UPSTREAM --profiler PROFILER --word23 words/word-23.json.gz --word25 words/word-25.json.gz --output work/recheck
python verification/check_guards.py words/word-23.json.gz
python verification/check_guards.py words/word-25.json.gz
cd math
lake build Frozen62Research
```

The verifier checks immutable sources and its own adapter hashes, full input/dirty
bases in both orientations, exact source/scatter inventory, every literal frame
transition and all fixed-I+J profiles with bounded-minor and CRT checks. It rejects
optimized Python assertion mode. Use the supplied words for authoritative replay;
floating discovery prices propose candidates and have no trusted-proof role.
Discovery source snapshots, exact oracle fixtures (gzip-compressed) and matching
seeds retain original byte hashes. `discovery/SEARCH.md` explains the algorithms,
heuristic boundary and experimental commands. Historical workspace paths in the
source-generation receipts identify the original run; the accepted-word replay
uses the explicit upstream argument and needs no private directory layout.
Portable discovery regeneration:

```
python discovery/regenerate_portable.py --upstream UPSTREAM --work work/regenerate
```

This rewrites workspace paths only and checks both raw words and deterministic
gzip against the accepted words. Floating discovery is outside the trusted
certificate; the independent word/profile verifier establishes acceptance.

The one-hour session froze information through #62. The unchanged data geometry
and its rational recovery are inherited; selected physical words/profile checks
are fresh. All-size analytic, compiler/frame transfer, finite-alphabet tape,
routing, prime selection/recovery and eventual-threshold contracts remain
conditional. No practical runtime or global-optimality claim is made.

Alejandro Zarzuelo Urdiales is the human author/developer, following earlier
Archivara and personal July/October matrix/parity work developed with multiple
AI tools. This synthesis involved substantial OpenAI Codex assistance. Known
linear algebra, matroid exchange, dirty uncomputation and concavity principles
retain prior-work status. The finite construction credits Avi Eisenberg/ikeboy
(#62 interval/core-aware graph), eumemic (#57 frame compiler), Chafik Boukhalfa
(#60 ranking and earlier exact profiling), Rohan Arun and other retained notices.
The prior matrix/parity source is in `../matrix-exponent-synthesis/` and prior
Gaussian work in PR45. Its product counts retain their separate arithmetic scope.
The paper is supplied as LaTeX source; no newly compiled PDF is claimed.
