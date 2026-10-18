# Inverse-column frame labels close the R439 source-19 exception

**Scoped all-length obstruction; no new kappa or supplier.** In a reversible
XOR circuit with retained monotone frames and both operands raised to a common
containing frame, wire `i` contains not only its forward-row entry labels but
also every entry label selected by column `i` of the inverse current matrix.
The induction in [audit.md, Section 3](audit.md#3-general-all-length-inverse-column-frame-invariant)
allows temporary writes, cancellation and arbitrary finite circuit length.

For the fixed eleven-wire F508 map left open in
[PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368), the inverse
column of source 19 includes wire 466, whose entry label is already F508.
Therefore source 19 must exit on F508. Combined with the predecessor's forward
bounds, all eleven exits equal F508, and the original single-climb profile
`{2:6, 3:2}` is minimal for `0<a<1`. The fixed continuation and literal inverse
cleanup cannot turn a replacement into a paid-frame improvement.

The inverse-column support and source-star calculation were already present in
Arham Tahir's PR1368. The contribution is the general invariant and its use for
arbitrary legal circuits, beyond that prefix form. The longer fully charged
first-contact relaxation in Section 2 is a secondary argument. No synthesis
search was needed. This follows [claim 1470](https://github.com/CrocSwap/integer-mult-bounds/discussions/1470)
and the [source-19 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18911407).

## Exact evidence and replay

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/r439-source19-dual-frame-obstruction
```

The registered command runs the verifier under `-I -O -B`, including its
read-only `--word` adapter against the existing pinned PR589 gzip. No packages
are installed and no files are written. Standalone replay is also available:

```sh
python3 -I -O -B research/r439-source19-dual-frame-obstruction/verify.py
```

Expected: `PASS_R439_F508_SOURCE19_DUAL_BARRIER`, thirteen rejected failure
controls and exit status zero. The checker covers exact rational spans and
binary inversion, all 2,048 dirty assignments for the 45-ADD positive fixture
and its inverse, a 47-ADD fixture that temporarily writes source 19, all 1,008
oriented updates on `GL(3,F2)`, and synthetic cleanup frames of ranks 4 through 8.
The longer fixtures are controls, not shorter-word or lower-cost candidates.

Local Python 3.12.14/macOS arm64 normal and optimized runs passed, as did the
pinned-word adapter. Certificates and fixtures matched between modes. Against
the Pro research-session output, only the Python-version field/line changed;
the fixture matched byte-for-byte. [certificate.json](certificate.json) records
the local source-bound run; [positive-fixture.json](positive-fixture.json) gives
the deterministic gates and individual climbs. These are recorded outputs,
not required checker inputs. `--json PATH --fixture PATH` writes fresh outputs;
include the registered `--word` argument to reproduce the source-bound
certificate. The certificate records the executing Python version.

The adapter verified both byte pins, the actual roots/entries, `B[205:242]`,
its 37 ADDs and `{2:6,3:2}` invoice, and the cleanup shape. Source 19 next visits
`C[372]`, frame 1, rank eight. It does not replay the full 661-wire dirty word.
Finite checks support the written universal argument; they are not a proof
assistant or an independent human mathematical review.

## Scope, provenance and credit

The consequence is restricted to the original eleven wires, exact dirty map,
reversible XORs, common-operand monotone frames inside F508, and the fixed
surrounding interface. It does not settle block 509, enlarged seams, new wires,
nonmonotone reuse, different gate rules or continuation compilers. H2/K,
native/hosting, precision/tape, all-size realization and analytic-transfer
obligations remain separate. The selected frontier is unchanged.

[SOURCES.json](SOURCES.json) pins historical main `410026dc` and the live gzip;
its `external_predecessors` pins PR1368 head `6ae784908c57f3aa5a2165d382b21a40accdf7a6`
for attribution, outside generic pin validation. No predecessor implementation
or large input is copied. [TASK.json](TASK.json) records the change from the
original complex-decoder assignment to the concrete scalar-to-moment handoff.

Credit Arham Tahir with OpenAI Codex assistance for PR1368, its forward argument,
data and prefix calculation; retain the lineage listed in [NOTICE.txt](NOTICE.txt).
Prepared by Andrey Mas with substantial GPT-6 Pro assistance through ChatGPT for
the mathematics and unchanged checker. Codex coordinated sources, packaged the
result and ran separate local checks. Apache-2.0.

## Open next questions

Does the same inverse-column invariant close source 22 in block 509? First
refresh overlap, pin that block's matrix and entry labels, and compute its
inverse-column label. A full paid-frame conclusion also needs its remaining
wire and continuation obligations. That separate block has not been checked
here; closing it would resolve the predecessor's other exceptional source.
The structured question is in [TASK.json](TASK.json).
