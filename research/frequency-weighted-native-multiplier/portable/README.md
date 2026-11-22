# Portable fixed installation

The frequency-weighted signed multiplier has an alternative fixed installer with $S<2^{113}$ individual tape reads, writes and moves on the complete fixed trace. The full-store price for the same tape computation gives $2^{142}$, with a coarse $2^{146}$ ceiling for both invocations. The smaller price uses the actual standalone interpreter head positions and the longest sequence of zero-fuel instructions. It generates the 106 runtime files and a 36,094,602-byte directory from the pinned source. A fresh interpreter receives those exact outputs, initializes both Gaussian suppliers and all five binary recipes across the two tiers, and writes the linked multiplier. Its stages have heights (3,000, 3,080, 1,024) and (8,192, 129,414, 524,288, 483,871). The equations for $\kappa$, the active-data bill and the five inherited research premises are those of the parent construction. [Local stack and control proof](STACK-LOCALITY.md) · [Complete tape-machine proof](TRACE-CLOCK.md) · [Whole multiplication construction](../README.md)

The fixed phase has no operand input. Its two deterministic executions cover every installation of this specified machine. The multiplier receives its signed integer tapes afterwards. The setup bound applies to the same installation at every operand length. The two portable interpreter runs, explicit file services, archive recovery, complete directory transfer, final startup, copying and cleanup are charged. After setup the original algorithms read the restored typed records. The setup reduction is a certified ceiling for a different fixed installer. The comparison with the prior $2^{228}$ ceiling gives no measured speedup. The additional public interpreter is 26,267,204 bytes, even before library and output storage. [Resource proof](TRACE-CLOCK.md) · [Reproducible clock calculation](run.py)

| Complete fixed operation | Guest fuel | Guest linear memory | Virtual file bytes transferred |
| --- | ---: | ---: | ---: |
| Produce both profiles and their whole directory | 802,083,502,514 | 331,808,768 | 51,780,723 |
| Open the emitted source and directory, bind both receivers | 132,344,680,603 | 153,878,528 | 44,886,562 |

The output directory contains 2,407,819 records and 5,174,419 references. The 110-file linked installation occupies 38,671,319 bytes, including this directory. The conservative tape model permits up to $2^{64}$ scratch cells during lowering. These are explicit construction costs. Host measurements and the mathematical tape allowance price different operations. [Complete recorded evidence](EVIDENCE.json)

## Replay

Use CPython 3.12, Git and Wasmtime for Python version 38.0.0. From the repository root run these commands in a shell. The driver requires an empty output directory. Both downloads are public fixed inputs. The driver checks their SHA-256 digests before using them.

```sh
work=$(mktemp -d)
python3.12 -m venv "$work/venv"
"$work/venv/bin/python" -m pip install wasmtime==38.0.0
release='https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/python/3.12.0%2B20231211-040d5a6'
curl -fL "$release/python-3.12.0.wasm" -o "$work/python.wasm"
curl -fL "$release/python-3.12.0-wasi-sdk-20.0.tar.gz" -o "$work/library.tar.gz"
portable=research/frequency-weighted-native-multiplier/portable
"$work/venv/bin/python" -B "$portable/run.py" --wasm "$work/python.wasm" \
    --archive "$work/library.tar.gz" --work "$work/output"
"$work/venv/bin/python" -B "$portable/compare.py" . "$work/output/installed-native.dag"
```

The separately downloaded module has SHA-256 `e5dc5a398b07b54ea8fdb503bf68fb583d533f10ec3f930963e02b9505f7a763`. The library archive has SHA-256 `6c1cddbb69ae09e87eee2906bdc70539bff5f2969818a6f8457d4e6a6eb67d4d`. The driver takes its three library members. The archive also contains a different interpreter binary. The release links and original licenses are listed in the component notice. [External components](NOTICE.md)

For the arithmetic replay alone, run `python3 -B research/frequency-weighted-native-multiplier/portable/verify_receipt.py`. It checks the archived invoices and identities through standard-library integer operations.

The driver writes `clock.json`, `signed.json`, the complete typed directory and the linked `machine/` tree. The machine executes $(-741503)\cdot466013=-345550037539$ at a finite tensor geometry. The independent check starts a clean instance through the usual Git-based installer. It compares each variant's chronological grades and histogram, both type descriptors, every typed transport share, and the full emitted byte stream. Production positive and ordinary ranks exceed the size of these finite product tests. [Fixed receipts](EVIDENCE.json) · [Finite signed test](signed.py) · [Independent original compiler](compare.py)

## What is trusted

The bit-level tape simulation and clock are written mathematics. The finite witness uses the byte-pinned guest, the Wasmtime 38 Cranelift meter with canonical NaN handling, the listed Python host reader and the specified preview1 file service. The checker parses every instruction in the guest. It checks the control depth, signatures, operand and record bounds, archive and directory identity, fuel cap and the total using Python integers. The portable setup proof has no Lean component. The regenerated executable and typed directory are checked independently of the tape simulation. [Opcode parser](guest_opcodes.py) · [Archive reconstruction](source_image.py) · [Directory and key checker](record_census.py)

## Open next questions

Can a smaller self-contained compiler remove the 26 MB CPython image while keeping the same verified output? A comparison against an alternative would need its own complete file, arithmetic, movement and receiving clock. The current physical product test leaves the first production-scale execution and performance crossover open.
