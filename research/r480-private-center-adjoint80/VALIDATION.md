# Validation and handoff

Test environment: Linux x86_64 / WSL2 and CPython **3.12.3**.
Exact base: `c0e3631dc24e3c24a861f7d3d79e0608481cccec`.
OS assignment seed: **80**, independent-verification track.
The 50-minute work window started at 19:18:52 UTC on 2026-10-13.
The mathematical implementation completed before 19:38 UTC.
The remaining work covers focused verification, source inspection and handoff.

## Result and executed checks

Both intact programs pass on all 712 inputs and outputs.
The complete domain contains 40 private-center CLEAR/COPY omissions.
Eight omissions are scalar-redundant, 24 affect ordinary inputs, and eight affect only private inputs.
All 32 nonzero defects have exact rank one and explicit basis-vector witnesses.
No error was found in the intact word, and no new kappa is claimed.

```sh
python3 -I -O -B research/r480-private-center-adjoint80/check.py
python3 -I -O -B research/r480-private-center-adjoint80/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
git diff --cached --check
```

The complete command prints:

```text
PASS_R480_PRIVATE_CENTER_PACKAGE coordinates=712 matrices=42 omissions=40 private_only=8 no_new_kappa
```

Four package tests pass. They cover singular COPY/CLEAR pullback laws,
rank-one factors, 2,000 integer-dyadic arithmetic comparisons and all eight private-only witnesses.
An optimized minimal offline relocation passes with only the package and three pinned repository inputs.
Forged rank, forged response, omitted site, omitted orientation and changed archive controls fail.
The selected-record check and **25 selected-record regressions** pass at the base.

The reverse-mode checker uses exact rational covectors.
The forward checker independently recomputes all 42 full matrices with integer-dyadic rows.
It verifies every defect factor, site, classification and witness against the certificate.
Certificate formatting changed only the layout of sparse-vector entries.
Every canonical JSON field remained identical, and the complete command passed afterward.

## Scope and source evidence

The model is the literal scalar macro projection on 704 persistent and eight private-center coordinates.
Non-scalar events, coefficient-work primitives, physical frames, Clifford phases and recursive child execution remain outside its scope.
Native replay, global hosting/invoice/assembly, precision/tape, full cold replay, hosted CI and Lean were not run.
The retained native receipt authenticates the original input, not a new physical replay.

The input archive SHA256 is
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The source is `slots/local/LOCAL-PROGRAMS.json.gz`, the R480 seven-slot word retained by PR1094.
The R492 historical evidence directory is not used.
The source receipt binds the members to the PR1042 checkpoint.
The PR1094 review and reproduction script establish the unchanged local-word dependency.
All three repository-input pins match refreshed main
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
The selected result remains PR1094, conditional kappa **0.001672660197076918**.

A restricted contract can require zero incoming centers.
This result distinguishes that interface from arbitrary incoming private state.
It does not allege acceptance of mutants by full production admission or a multiplication-theorem defect.

## Overlap and attribution

The full refresh inspected **789 open PRs through #1177**.
Sagar Thakrar's PR745 supplies the historical JP8 adjoint/private-input precedent.
Its inspected head is `fc6ebccca3bd61a6eaf6ec3fcbf2e99d2888c35c`.
This contribution adds the actual R480 word, a complete 40-site atlas,
all eight private-only response vectors and exact prefix/suffix factorizations.
PR835's modular SW4 endpoint audit uses a distinct method and object.
PR1049/1149 check local cells and frame ranks. PR1153 checks primitive sign substitutions.
No predecessor code or pending patch is imported by either implementation.
The final refresh found woklerx's PR1174, head
`5d2d0472a4843bf4b0858453d3eb5931ac19fbbb`.
It audits paid cleanup COPY transposition on 705 coordinates and excludes center lifetimes.
This 712-coordinate macro atlas includes all private-center clears and copies,
and makes no transposed-primitive accounting claim.
The immediate pre-submit refresh reached **PR1184** and found no pinned issue.
PR1184 (`2f1c9e0e671bb10aecd452e18449130b0601932d`) preserves the emitted
auditor's existing 704-column coverage while accelerating its full native checks.
This audit independently adds the eight private input coordinates and the complete
CLEAR/COPY omission atlas. It claims neither that acceleration nor a full native replay.

Construction credit remains with Jeremy Kothe, Rohan Arun, Hao Yan, Chafik Boukhalfa,
icekylinx, DreamingOfClouds, eumemic and the retained community lineage.
The local claim records the rejected candidates and complete stopping rule.
No pinned coordination issue existed.

New files are Apache-2.0. @Scratch-net contributes with substantial OpenAI Codex assistance
in research, implementation, proof, verification and writing.
The two implementations are AI-assisted, not independent human peer review.

## Final handoff

Submitted as [PR1198](https://github.com/CrocSwap/integer-mult-bounds/pull/1198).
Exact implementation commit: `8c6178044a0fd46b4a10e99f1c99ba208ba82b46`.
The handoff commit changes only this document and the local claim.
Executable code, source pins and the mathematical certificate remain identical.
No PR was merged or closed, and the selected frontier remains untouched.
