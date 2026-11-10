# A uniformly shrinking 28-bit Gaussian residue child

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped constructive written proof with exact finite corroboration.
No new kappa or selected-frontier change is claimed.

Centering the residues and decoding through an asymmetric signed interval
saves one bit in every Kronecker slot of the paid Gaussian residue lane:

```diff
- unsigned slot: 2k + ceil(log2 L)
+ centered slot: 2k - 1 + ceil(log2 L)
```

For declared parent width n, digit width b, length L=ceil(n/b) and top digit
width t=n-b(L-1), the sharp maximum child magnitude-bit length is

```text
D_center = min(k,t) + (L-1)(2k-1+ceil(log2 L)).
```

Both child operands are nonnegative magnitudes. Exactly one paid exact
multiplication supplies their product; sign handling and extraction remain
additional work. The new bound saves exactly L-1 operand bits relative to
the cited unsigned formula.

In the retained 455-point Gaussian box with 64-bit digits:

| Quantity | Result for the new layout |
|---|---|
| Largest fixed residue width shrinking throughout its supported tail | k=28, at every n=29..14592 |
| Prior unsigned uniform choice | k=27 |
| Full-width k28 child at n=14592 | 14329 bits, saving 227 bits |
| New k28 boundary at n=8193 | 8065 bits |
| k29 obstruction for this new layout at n=8193 | 8321 bits |

The credited fixed numerical certificate permits p=208-k. The new uniform
tail therefore permits rounded payload precision p=180 rather than p=181.
Working enclosure precision Q=448 is unchanged. This is a precision and
child-size improvement, without a total-runtime or physical-cost claim.
[PROOF.md](PROOF.md) gives the all-length construction, attained size theorem,
uniform-tail proof and exact limits. The executable reference bounds arrays
to 228 entries and digits/residue widths to 64 bits.

## Evidence and reproduction

The standalone exact checker enumerates 13,140 array pairs and 50,628
convolution coefficients. The domains include unequal lengths, zeros,
negative packed values and both signed endpoints. It checks 100 exact
small size maxima across 20,460 original inputs, five large attaining
inputs, all 933,888 supported width/residue pairs and every one of the
14,564 new k28 tail widths. The new layout admits 417,584 pairs versus
410,725 under the cited unsigned formula, adding 6,859 pairs. Fourteen
invalid-input/decoder cases reject. Four semantic controls include the
positive half-base endpoint, an undersized-slot collision and a failure
of unsigned extraction on a negative packed product.

The changed-caller replay authenticates eight existing input files, loads
the retained PR3881 caller, and substitutes only its exact lane dependency
inside that private process. A finally block restores the dependency.
It executes complete p180 Gaussian products at n=8193 and n=14592,
checks all 455 recovered coefficients in each execution, and reaches the
new sharp child bounds in both. Each execution performs 573 Gaussian line
calls. The numerical backend, preparation, transforms, CRT order, lifting
and carry are inherited inputs, not results re-audited by this package.
Reference products and schoolbook coefficients are used only as postchecks.

From the repository root, with the standard-library CPython 3.12 interpreter:

```sh
PY=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$PY" -W error -X dev -I -B research/centered-gaussian-residue/verify.py
"$PY" -W error -X dev -I -B research/centered-gaussian-residue/boundary.py
"$PY" -B scripts/research_package.py --package research/centered-gaussian-residue
"$PY" -B scripts/check_research_commit.py --package research/centered-gaussian-residue --check-source-history
```

Substitute another CPython 3.12 path on another machine. The last command
requires committed package bytes. The registered replay runs both direct
checks normally and with optimization enabled. Expected markers are
`PASS_CENTERED_GAUSSIAN_RESIDUE`, `PASS_CENTERED_GAUSSIAN_BOUNDARY`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Each direct invocation generates a stdout receipt bound to SHA256 hashes
of the package files. No receipt is handwritten or frozen. Outputs belong
outside the checkout. The official package export includes the declared
inputs; the two direct scripts require no Git or network in that export.

## Scope, credit and overlap

ToikY's [PR3926](https://github.com/CrocSwap/integer-mult-bounds/pull/3926),
Open next question 2, asks for a changed packing or numerical certificate.
Credit its attained unsigned size law, strict-child window and inherited
fixed-certificate precision law. David Ganz / Dugongue's
[PR3881](https://github.com/CrocSwap/integer-mult-bounds/pull/3881), head
`75e098dc12a2567e73a2858137408e08d31dbf84`, supplies the paid residue lane
and its Gaussian recovery theorem. Mason Hale supplies the numerical backend,
normalization, FFT/CRT ordering and carry path. Their source-specific notices
retain the Harvey-van der Hoeven and earlier contributor lineage. Signed
Kronecker substitution and modular lifting are classical. No general
literature-priority claim is made. Predecessor bytes and credit are unchanged.

[SOURCES.json](SOURCES.json) pins live runtime inputs and historical provenance
at main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) records the explicit change from invoice verification
to this new packing construction. The selected-binding first command passed;
it was orientation, not a selected scientific replay.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363350)
preceded construction and execution. Live PRs, recent account PRs, claims,
merged searches and distinctive all-main README/PROOF searches were checked.
The cached remote snapshot covered 430 open PRs and 6,401 Discussion records.
Only 113 of 8,917 local note paths were materialized for that scan; targeted
Git searches supplemented it. Unpublished work and arbitrary diffs remain
outside this bounded overlap check.

No new Gaussian error theorem, minimal packing theorem, complete caller
invoice, all-size recursion/base-case policy, physical implementation,
stock/tape bound, supplier admission or multiplication theorem is supplied.
All five selected framework assumptions remain. Lean, Docker, a selected
cold replay and independent human or formal proof-kernel review are unrun.

## Open next questions

- Does the new lane reduce the complete cost of one physical caller? Price
  the k27/p181 and centered k28/p180 programs, including signs, extraction,
  numerical transforms, preparation, movement and restoration. The missing
  physical composition and complete invoice block a total-cost conclusion.
- Can another packing admit k29 uniformly? Begin at n=8193 with a different
  pack/extract contract and its attained magnitude-bit maximum. The 8321-bit
  exclusion here concerns this constant-slot scheme only. No further search
  or follow-up construction is included.

## Verification constraints

Build the Lever supplies the explicit lane and deterministic checker.
Prove It Works requires two complete executions through the actual retained
caller, with the new lane reached and every recovered coefficient checked.
New functions are below 60 physical lines. There is no recursion or process
launch. All new arithmetic loops have bounds from 228 entries, 64-bit digits,
the fixed finite domains above, at most 455 coefficients or eight source
files. Acceptance checks use explicit exceptions and survive optimization.
Warning-strict normal/optimized execution and in-memory syntax compilation
provide the available diagnostics; no separate static analyzer was run.

Power of Ten rule 3 deviation: CPython and Fraction allocate dynamically.
The bounded command uses fixed small lists and bounded operand sizes, with
at most 228 digits and packed operands below 31,000 bits. Receipt reads
are bounded to eight package files of at most one MiB each. No fixed-memory
or allocator-internals claim is made. Rule 9 deviation: one authenticated
fixed-path module import and one named lane substitution bind the actual
caller; their targets are fixed and restoration runs on every exit.
Inherited backend code and its runtime are unchanged dependencies, with
their existing contracts, rather than newly certified Power of Ten code.
