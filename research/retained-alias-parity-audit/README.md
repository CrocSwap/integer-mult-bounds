# Scatter parity with repeated retained helpers

**Mathematical boundary audit; no new κ.** The odd-multiplicity condition in
[Kumagi's PR3004](https://github.com/CrocSwap/integer-mult-bounds/pull/3004)
is an exact equality of coefficients of independent retained slots. It also
characterizes semantic equality for the pinned selected word, whose nine
retained helpers are distinct. Applying its unqualified “whole word iff”
statement to every JSON word accepted by the scalar checker needs that
independence premise: the checker permits repeated helper addresses in `ret`.

This package supplies the exact criterion with aliases and a full-size
counterexample to necessity **outside the selected producer's fixed retained
list**. It does not identify a wrong selected operator or a complete supplier
acceptance bug. The selected result remains
`κ = 836330098538459/500000000000000000 = 0.001672660197076918`.

## Exact criterion and proof

Work over F2. Let slot `k` name physical helper `q_k`, and let `m_tk` be the
multiplicity of slot `k` in scatter row `t`. Define

```text
e_tk = (m_tk mod 2) XOR [m_tk > 0].
```

Thus `e_tk=1` precisely for a positive even multiplicity. The symbolic checker
XORs once per occurrence; the exporter emits once per slot membership. Both
read the same helper value, and scatter writes only targets. Their difference
at target `t` is therefore

```text
XOR_q ( XOR_{k: q_k=q} e_tk ) value(q).
```

The prefix D/A is invertible on all arbitrary input registers: each admitted
gate adds a sum of distinct other registers to its destination, and applying
that gate twice is the identity. Hence the rows giving the values of distinct
physical helpers after the prefix are linearly independent. The difference
vanishes for every input exactly when

> For every target `t` and physical helper `q`, the number of slots naming `q`
> with positive even multiplicity in row `t` is even.

The suffix B/C is also a composition of invertible gates, so equality at this
cut is equivalent to equality of the full scalar operators. Frame MOVEs have
no scalar action in this projection. No claim about their physical cost follows.

If `ret` is injective, every alias class is a singleton and the criterion
reduces to PR3004's odd-positive-multiplicity condition. Simple scatter rows
remain sufficient with or without aliases. Distinct helper addresses would
not establish independence for an irreversible prefix or a restricted input
space; the proof uses the actual reversible gates and arbitrary dirty inputs.

The smallest cancellation of a coefficient discrepancy across aliases needs
four row entries. At least two discrepant slots must name the same helper,
and each needs positive even multiplicity at least two. It is attained by
`ret=[q,q]`, `row=[0,0,1,1]`: the symbolic contribution is zero and the export
adds the same value twice. This is an exact algebraic observation, with a
bounded exhaustive check below; it is not a new impossibility theorem for
suppliers.

## Selected-source fixture and controls

The OS assignment seed **62** selects retained index `62 mod 9 = 8`, helper
**480**, and the first cyclic target at or after row 62 omitting that index,
**row 64**, originally `[2,4,6]`. Append helper 480 to `ret` as slot 9 and
append `[8,8,9,9]` to that row. Both new positive multiplicities are even.
The full unchanged checker accepts all 661 arbitrary source, target and dirty
helper input columns, H1–H5 and all four conclusion flags. The unchanged
exporter also implements the original endpoint on every column.

Two controls retain the same successful symbolic endpoint but export the wrong
operator: omit the two occurrences of slot 9, or let slot 9 name helper 479
instead. In each case only output register 175 differs. The full exact input
column supports are committed in [EXPECTED.json](EXPECTED.json); input column
480 is a one-bit witness in both controls. An omitted exported ADD is detected,
and appending one occurrence to the original row is rejected by the actual
symbolic checker with `targets not y + x`.

| Fixture | Symbolic terms | Exported scatter ADDs | COPY rank sum | Records | Export equals symbolic |
|---|---:|---:|---:|---:|---|
| Original selected word | 527 | 527 | 63 | 27,234 | yes |
| Balanced alias | 531 | 529 | 70 | 27,238 | yes |
| Unpaired even slot | 529 | 528 | 70 | 27,237 | no |
| Distinct helpers | 531 | 529 | 70 | 27,238 | no |

The alias fixture pays for an additional rank-seven COPY and its ERASE, and
two additional scatter ADDs. It is outside the selected nine-total producer
and adds cost. Neither alias cancellation nor a correct scalar endpoint
licenses refunding those operations or changing a recursive profile. The
opt-in simple-support guard from Arham Tahir's PR2992 rejects its repeated row,
as designed; no change to that sufficient guard is proposed.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3 -I -O -B research/retained-alias-parity-audit/verify.py
```

Expected (about seven seconds on the contributor's Linux environment):

```text
PASS_RETAINED_ALIAS_PARITY_AUDIT columns=661 cases=87641 balanced_alias=agrees controls=4 no_new_kappa
```

The verifier authenticates source bytes before execution, compiles the actual
checker with its checks enabled, invokes the unchanged exporter in temporary
directories, and independently interprets both JSON gates and packed records
with 661 simultaneous F2 basis bits. Its record interpreter checks COPY/ERASE
lifetimes; it deliberately makes no native frame/geometry claim.

The finite domain is **every one of the 23 alias patterns on 1–4 slots**, up
to renaming physical helpers, and **all ordered rows of length 0–6** over
those slots: 87,641 cases. Direct occurrence/membership evaluation and the
grouped criterion agree throughout. Of the 25,319 agreeing cases, 8,712 have
positive even multiplicities. There is no randomized or unfinished search.

Additional checks and separate receipt regeneration:

```sh
python3 -I -O -B research/retained-alias-parity-audit/test_verify.py
python3 -B scripts/research_package.py --package research/retained-alias-parity-audit
python3 -I -O -B research/retained-alias-parity-audit/verify.py --write-receipt /tmp/alias-receipt.json
cmp research/retained-alias-parity-audit/EXPECTED.json /tmp/alias-receipt.json
```

Six behavioral test groups cover alias cancellation, the injective corollary,
the independence premise, the minimal four-entry length, changed source bytes,
and broken/truncated record lifetimes. Explicit primary checks remain active
under `-O`; the authenticated original checker is compiled with `optimize=0`.

Local verification used CPython 3.12.14 on Linux x86_64. The registered replay,
six groups, package metadata/pins, baseline source-binding check and strict
selected-record check pass. The initial probe created an ignored checker `.pyc`
that the closed source inventory rejected; removing that generated file restored
the exact inventory, with no changed source bytes. Hosted CI and the complete
selected cold replay were not run for this isolated audit.

## Pins, scope and credit

Exact base: **997e6a9ca7b4f95d50e366f61412fd640d72a88a**.
[SOURCES.json](SOURCES.json) records Git blobs and SHA-256 hashes, including the
selected source manifest. PR3004's inspected head was
`ce08d19f6e43bbc6f552858d93154efe3aa98916`; its frozen README is pinned here.
[CLAIM.json](CLAIM.json) records track selection, three candidates, overlap
coverage and the stopping rule. No pinned sprint issue existed, so the claim
was recorded locally. [TASK.json](TASK.json) supplies the catalogue context and
[VERIFY.json](VERIFY.json) registers only this scoped replay.

Credit Kumagi/PR3004 for the coefficient-space characterization and exhaustive
row census; Nick Petalas/PR2977 for the original paired-scatter mismatch,
full-column/native controls and handoff; Arham Tahir/PR2992 for the versioned
simple-support boundary; and PR3099's duplicate-boundary corroboration. Dylan
Crow wrote the exporter; eumemic and DreamingOfClouds supply the retained bit
word/checker lineage. Douglas Colkitt supplies the selected source bindings and
review. This contribution adds the retained-alias premise audit, corrected
semantic criterion, minimality proof and full-size cancellation/control evidence.

No predecessor verifier is imported. The original checker and exporter execute
as explicitly identified audit subjects. Their source notices remain unchanged.
All new work is Apache-2.0, by **theon199**, with substantial **OpenAI Codex**
assistance in research, code, verification and writing. No independent human
or proof-assistant review is claimed. No native compilation, complete cold
replay, source acquisition, hosting, precision/tape, all-size compiler or
analytic-transfer obligation is discharged; no selected record is edited.

## Open next questions

A separately versioned successor should state whether `ret` denotes distinct
physical helpers or permits aliases. If it requires independent slot semantics,
enforce injectivity or prove it from that producer before using the per-slot
necessity statement. If aliases are intentional, the grouped criterion above
is the scalar contract, while every COPY/ERASE and emitted ADD still needs its
own charge. The first step is adding this fixture to the successor schema
review; supplier adoption additionally requires new manifests and the full
symbolic/export/native replay. This audit does not justify another search.
