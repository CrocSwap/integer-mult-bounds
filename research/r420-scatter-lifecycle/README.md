# R420 COPY/scatter lifecycle

This proves the Boolean behavior of the **661-register** retained-major scatter
slice of eumemic's PR543 R420 word: **9 COPY, 568 ADD and 9 ERASE** operations.
It fills the scalar lifecycle obligation left open by PR612. The R420 word is a
historical component; this package does not certify the complete current selected
construction or improve κ.
The repository source pins use main `f567884aeb8851b6e794af1184119a3bfbe1e631`.

For every input state, including arbitrary source, helper and temporary bits:

- Each of the 660 original coordinates equals direct retained-centre XOR scatter.
- Original source/helper coordinates are preserved.
- Temporary register 660 ends false, independently of its incoming value.
- Its incoming value is restored only under the explicit premise that it was false.

`R420ScatterData.lean` contains current retained centres, scatter rows and the exact
ordered windows obtained from the record exporter. `check.py` regenerates those
literals from the pinned JSON before compiling. The kernel proves the Lean
membership loop equals every exported centre/destination in order; aggregate
counts alone are insufficient. Fresh finite bounds then instantiate PR590's
generic COPY/scatter theorem on `Fin 661`. All four modules compile from source;
no historical `Fin 730` object is retained or renamed.

The exporter is pinned at
`research/e8-bit-carrier-skeleton/code/bit/export_records.py`, lines 59–63, which
R420 reuses. COPY is modeled as overwrite, ADD as Boolean XOR, and ERASE as writing
false. This is a scalar projection: frame transport, physical allocation and
ERASE legality, A/C cleanup, D compensation, the complete multiplier and all-size
transfer remain separate. No equality with a reordered row-major circuit is claimed.

## Reproduce

Use Python 3 and the official **Lean 4.21.0 Linux** distribution, with no Mathlib
or network access. The existing PR612 official-core manifest pins the Lean binary
and all 317 `Init` source/object pairs; the checker checks these before and after
the build. The supplied compiler and shared-library runtime remain trusted;
these manifest checks do not pin the complete executable runtime.
Repository supplier scripts are never executed.

From the repository root:

```sh
python3 research/r420-scatter-lifecycle/check.py \
  --lean /opt/lean-4.21.0-linux/bin/lean --build-dir /tmp/r420-lifecycle-build
```

The build directory must not exist. Each module gets a fresh object, a 60-second
wall/CPU budget, a 4 GiB address-space limit and one compiler thread. The checker
requires all **28** printed probes, in order, to use only standard Lean axioms.
Objects, raw logs and `RESULT.json` are written outside the package. For only
source correspondence, use `--bind-only`; that mode does not claim a Lean build.

`MANIFEST.json` records repository inputs, source hashes, imports and probes.
The source-binding boundary is external to Lean; the literal theorem itself is
kernel checked. The official runtime manifest is reused from
`research/lean-current-r420-boundary-interfaces/OFFICIAL_CORE_MANIFEST.json`.

The eleven source-binding controls run with either normal or optimized Python:

```sh
cd research/r420-scatter-lifecycle
python3 -m unittest -v test_binding
python3 -O -m unittest -v test_binding
```

Three controls alter retained order, a scatter index or exported destination
order while preserving the shapes and refreshing the local data hash; source
regeneration must still reject them. Other controls change proof, exporter or
generic semantics, and one checks a valid relocated set of inputs.
Omitted modules, lifecycle probes or exporter inputs and redirected source paths
must also be rejected.

An optional compiler acceptance control copies the package to a new directory,
replaces only the lifecycle proof with `sorry`, refreshes its source hash, and
requires rejection of the resulting `sorryAx` probe after compilation:

```sh
python3 test_kernel_rejection.py --lean /opt/lean-4.21.0-linux/bin/lean \
  --output-dir /tmp/r420-lifecycle-negative
```

The accepted package remains unchanged. Recorded results are in `VALIDATION.md`.

## Attribution

Apache-2.0. Prepared by Chinmay (@chinmayarvind23), with substantial OpenAI Codex
assistance. `BitXorTargetTranslation.lean` and `BitCopyScatterWindow.lean` are
byte-identical to James Chang's PR590 at
`58690bdbb587f482569ba1bdf7bf61a5396b4768`; the lifecycle proof adapts its explicitly
historical instance. PR612 identified the remaining R420 obligation; PR834 audits
that package's source expressions but does not establish this lifecycle theorem.
The R420 supplier is eumemic's work with substantial Anthropic Claude assistance;
the inherited record exporter credits Dylan Crow / utcorvusvolat-dotcom.
Original notices are preserved in `SUPPLIER_NOTICE.md` and `R420_NOTICE.md`.
