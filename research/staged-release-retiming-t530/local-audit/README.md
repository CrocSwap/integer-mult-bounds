# Independent local audit of the two release retimings

Run from this directory, or invoke `verify.py` by its absolute path from anywhere:

```sh
python3 -B verify.py
```

Python 3.10 or later and the standard library suffice. No network, repository checkout or third-party packages are needed. All input paths are relative to `__file__`; output is written to a fresh temporary directory, or the external directory supplied with `--out /fresh/output`. The expected final line is `PASS_PORTABLE_LOCAL_RETIMING_AUDIT`.

The verifier authenticates all packaged inputs, runs the separately written minimal scalar/frame proof, freshly replays both complete free-operator words on all 632 arbitrary input columns in both orientations, checks all 91 private zero buffers, and exercises four semantic rejection controls. It also authenticates retained receipts of two complete native replays performed during this research session. The full native implementation is not bundled or rerun by this command.

## Exact change and proof

Parent words: [PR3605](https://github.com/CrocSwap/integer-mult-bounds/pull/3605), pinned at `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. In both variants, only B, cleanup and `report.local_profile` change.

At zero-based B indices 591–592, replace

```text
640 += 2 * 644   at P
496 -= 2 * 644   at P
```

with

```text
496 -= 2 * 644   at P
640 += 2 * 644   at Q
```

Here `P = span(429,30)` and `Q = span(423,65,20,10)`. At indices 641–642, similarly exchange `656 -= 660` and `520 -= 2*660`, raising the delayed first gate to `Q' = span(427,96,24,6)`.

Each pair contains two rational elementary shears with the same source and different targets. The shears commute exactly. No warp intervenes, and none of the six involved registers has a warp. The delayed donor originally traverses the nested frames `span(30) < P < Q`, of dimensions 1, 2, 4; Q is already the next frame used by donor and pivot. Retiming allows a direct donor jump from dimension 1 to dimension 4. The same argument applies to Q'. Cleanup follows canonical inverse-reverse order at FULL.

Each block replaces `H₁ + H₂` with `H₃`. The total delta is `−2H₁ − 2H₂ + 2H₃`, yielding profile `{1:2437,2:724,3:226,4:102,5:20,8:8}`. For every `0 < a < 1`, `3^(1−a) < 2^(1−a) + 1`, so the recursive moment strictly decreases. This is a structural improvement, rather than decimal rounding. Rank mass remains 5135. Helper identities, entrance/final frames, interfaces, 408 live helpers, 91 private zero buffers and width inventory `{4:26,5:2,6:18,7:52,8:97,9:213}` all remain unchanged.

## Native evidence and scope

`receipts/native-{base,extra}/RESULT.json` records two fresh successful five-stage native runs: native, ledgers, local replay, wrappers and phases, including the separate warp-recipe checker. Their independent replay reports cover all 632 live columns, all 91 zero buffers and all 512 warp columns in both orientations. Exact local prefix bounds are:

| Orientation | Bound | Bits |
| --- | --- | ---: |
| Forward | `202390250292205836324211411723 / 512` | 89 |
| Backward | `4091250694836343058381993950001 / 128` | 95 |

Both lie below the inherited 128-bit local reserve and 192-bit charged payload. Native events decrease from 22768 to 22766; scalar macros and primitive counts remain unchanged. Public `COMMANDS.json` files replace this session's private user/workspace prefixes with `$RESEARCH_WORKSPACE`. They are publication derivatives, not the original command bytes. `PUBLICATION-PROVENANCE.json` records the original and public SHA256 for every changed copied file. Scientific native result, source and local replay receipts remain byte-identical. The portable verifier does not execute historical commands.

To rerun the full native implementation, obtain repository commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, use Python 3.12 with NumPy, and substitute actual checkout/capsule paths below. Each destination must not already exist:

```sh
python3 -B /path/to/repository/research/t74-native-fast/run_native.py /path/to/local-audit/words/RETIMED644-660-base.json.gz /path/to/fresh-native-base
python3 -B /path/to/repository/research/t74-native-fast/run_native.py /path/to/local-audit/words/RETIMED644-660-extra.json.gz /path/to/fresh-native-extra
```

The driver SHA is in `SOURCE-PINS.json`; each native result retains its full native source manifest. These independent local native runs used Python 3.12.14 and NumPy 2.3.5. The separate integrated admission used Python 3.12.14 and NumPy 2.5.4.

This capsule proves the local replacement and its strict moment reduction. It does not rerun the global owner/controller/physical/outer release or establish an unconditional integer-multiplication bound. A higher κ still requires source-bound assembly and transfer checks and the source's declared theorem hypotheses. Pending source claims are not promoted here to the repository's selected reviewed baseline.

## Negative controls

The inherited checker rejects: (1) raising the first gate while retaining old order, at frame monotonicity; (2) omitting the frame jump while claiming the new invoice, at paid profile; (3) coefficient 2 to 3 with a consistent inverse, at target map; (4) old literal cleanup, at canonical inverse-reverse ordering. The fourth is structural: the old inverse shears also commute, so their old order remains operator-equivalent.

Mutation words, logs and JSON results are generated under `<output>/negative/`. The minimal proof additionally rejects coefficient, frame and interface mutations.

## Provenance and license

The staged suppliers are Ross Richardson's PR3605 contribution, based on dcharb78's PR3133 lineage. The commuting retiming was found by the joint-circuit agent in this session; the minimal proof and packaging were written separately by the fresh-math review agent. No priority is claimed over predecessor suppliers or their mathematics.

`vendor/audit_local.py` is an unchanged SHA-pinned copy of `research/rank7-coupled-586-588-carrier-fold/vendor/audit_local.py` at the repository commit above; its notice credits icekylinx with OpenAI GPT-6 Astra assistance. The reused native implementation is credited in `NATIVE-LINEAGE-NOTICE`. Inherited notices and credits remain in `vendor/SOURCE-NOTICE` and `vendor/SOURCE-CREDITS.md`. The retained source and this derivative capsule are Apache-2.0 licensed; see `LICENSE`.

## Publication adapter

This directory is a public derivative of the preserved local capsule. Only execution-path metadata, output routing and publication documentation were adapted; source words and inherited checkers remain unchanged. No full native replay was repeated by this adapter. The default command writes outside the package; an explicit `--out` must name a new directory outside it. There are no external repository inputs; see `PUBLIC-INPUTS.json`.
