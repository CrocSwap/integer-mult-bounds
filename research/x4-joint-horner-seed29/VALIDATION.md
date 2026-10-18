# Validation and handoff

Executed on 2026-10-13 UTC (2026-10-14 in Melbourne), macOS arm64
Darwin 25.5.0, CPython 3.14.6. No additional Python packages are required.

## Verified result

- Full normal and isolated optimized replay: 6,112 eligible pairs, 2,764
  arithmetic-saving candidates, 1,586 selected pairs, 13,072 real primitives
  saved backward, all 737 formal input columns, every group boundary, complete
  endpoint, arbitrary helper restoration and private erasure.
- Both full scalar executions agree on prefix row-l1 5,338,828, fractional
  depth 19, the inherited positive envelope, and all 5,202 non-scalar events.
- The separate integer implementation checks all 6,112 local matrices (97,792
  entries), obtains the same optimum by forward path DP, and independently
  rebuilds the complete 130,602-primitive stream and its SHA256.
- Twelve main adverse controls and four independent integer circuit controls
  pass. Identity and pricing are separate checks: an endpoint-equivalent
  inflated circuit is rejected by its cost check.
- Seven focused tests pass normally and under isolated optimized execution.
  They cover 144 varied signed/denominator microcircuits, alias/type/dyadic
  rejection, physical event boundaries, exhaustive small matching comparisons,
  independent full certificate reconstruction and package controls.
- The minimal relocated tree has spaces in its path, no Git metadata and only
  declared source inputs. Its optimized full replay passes from another working
  directory. Source corruption, overlapping pairs, a suboptimal matching and a
  corrupted #799 checkpoint fail. A different active selection with an intact
  #799 checkpoint is accepted.
- `make selected-record-check` passes at the original base and after rebase;
  the latter verifies the newly selected PR890 kappa, not the older X4 value.

Reproduce the contribution with:

```sh
python3 -I -B research/x4-joint-horner-seed29/verify.py
python3 -I -O -B research/x4-joint-horner-seed29/independent.py
python3 -I -O -B research/x4-joint-horner-seed29/test_package.py
```

The first command prints:

```
PASS_X4_JOINT_HORNER candidates=6112 pairs=1586 saved=13072 columns=737 no_new_kappa
```

The complete deterministic receipt is EXPECTED.json. Search code, certificate
checks and full scalar replay use exact arithmetic. The all-candidate census
and complete primitive stream have independent reconstruction, not just a check
of a nominated winner. Two implementations by the same AI agent are not
independent human review.

## Current-main reconciliation

Starting base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Submission integration base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.

The branch was rebased onto that refreshed main. Six non-context source files,
including the original committed replay archive, remained byte-identical.
The prior selected-record bytes moved unchanged to
`certificates/checkpoints/frontier799.json`, SHA256
`9873519224e2db72d6a8c926f51e3e75129671e467948c6f6b03744f8bcfc699`.
Both readers require this exact hash at the original or official checkpoint
path. They do not silently repin the older witness to the active PR890 record.

The current accepted record and its maintainer review were read after refresh:
PR890/U8/T21, conditional kappa **0.001661957774647029**. This package retains
the completed X4 contribution and makes no U8 compatibility or transfer claim.
The accepted frontier and `upstream/` have no changes from this contribution.

The overlap refresh covered 710 open PRs through #939. No pinned sprint issue
existed, so the claim stayed local. New #937 changes a historical central
factor; #932 changes a frame-zero target basis. No same-scope joint two-source
nonzero-frame Horner construction was found. Their work is neither imported
nor silently included in these savings. Exact inspected heads are in
OVERLAP.json. CLAIM.json records the submission result and link.

## Remaining work and limits

The exact class optimum is only for disjoint adjacent eligible pairs, the
specific binary circuit, and strictly more than one saved primitive per pair.
It does not exclude signed-digit circuits, longer accumulations, changed order,
or new frames. No new kappa, runtime gain or general circuit optimum is claimed.

The primitive work register clears at pair boundaries rather than at both old
macro boundaries. A production emitter must represent and admit that interface,
rebind the evidence and rerun the relevant physical and global checks. Scalar
interpreters do not execute physical frame/phase/Clifford events. A local
192-bit magnitude check is not a complete recursive precision/tape proof.

All original macro adapter charges remain: 380,784 adapters at compiler factor
25,934,336. Because the unchanged forward orientation binds, the complete
conservative local arithmetic recount improves by only **16**, despite the
13,072 backward primitive saving. No global invoice is represented as run.

Not run: full `make verify`, any selected-supplier cold rebuild, fresh global
owner/hosting/invoice/outer assembly, Lean, another Python version or hosted CI.
The change is an isolated research package and leaves existing generators and
artifacts unchanged. All-size/compiler, realization, hosting, bit-supplier,
precision/tape/recovery and analytic assumptions remain inherited.
