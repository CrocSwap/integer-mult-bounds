# Literal tariff conversion audit

**Result:** an all-width mandatory cost vector for the actual compact
rounded ADD kernel, its exact sum over the proposed QUERY-only source,
and a necessary numeric conversion condition. **No new kappa and no
unconditional physical tariff obstruction.**

For coefficient a/b, put L=max(bitlength(|a|),bitlength(b)) and let delta
indicate an odd denominator. On B public numeric data bits, every
successful retained compact ADD must perform at least

    B * (250 + 73L + 28 delta)

physical reads/writes/unit moves. Including fetched flat table rows gives
B*(288+86L+33 delta). The proof counts mandatory initialization, L Horner
passes and their rewinds, offset and residue scans, quotient staging,
installation, head returns and two current-body retirements. Zero inputs
provide valid witnesses at every positive width. Extra width, delimiters,
setup, contexts and old backing add nonnegative omitted work.

The exact local source has 61,052 ADDs, sum L=167,955 and 4,079 odd ADDs,
used at 18 joint contacts. A direct full ADD substitution therefore has a
lower bill of **497,482,686 B raw actions**, or **578,910,834 B including
flat rows**, when the per-field comparison volumes agree. A separate COPY
is excluded. No new full source registry is installed here.

The frozen precision model totals 843,431,488. Removing ALL the existing
ADD charges releases 47,484,288, so retaining the rest of that invoice
leaves 204,052,800 for replacement ADD work. If a proposed converter says
one tariff unit pays rho raw actions per comparison data bit, it necessarily
requires

    rho >= 82913781 / 34008800.

The corresponding raw-plus-flat-row requirement is 96485139/34008800.
Equal units (rho=1) cannot support this specific replacement ledger. This
does not prove the full program exceeds the cap: other retained entries
are model/upper charges, and the source does not assert rho=1. A different
converter, implementation, volume convention or repricing needs its own
proof. The original source's warning about the missing converter is
credited; the universal forced-pass vector and exact replacement condition
are the new contribution.

## Reproduction

```bash
python3 -I -B research/literal-tariff-conversion-audit/verify.py --suite all
python3 -I -O -B research/literal-tariff-conversion-audit/verify.py --suite all
```

Expected: `PASS_LITERAL_TARIFF_SOURCE`, `PASS_LITERAL_TARIFF_LOWER_VECTOR`,
and `PASS_LITERAL_TARIFF_CONTROLS`. Standard library only; runtime needs
no Git, network or solver. The 36 small literal cases use the unchanged
executor, independent hardware counters, heterogeneous widths, the three
actual maximal coefficient witnesses, dirty scratch and exact source
preservation/cleanup. Nine width-increment checks isolate the proved
coefficient. No complete numerical word is run.

See [PROOF.md](PROOF.md) for the vector proof, units, exact provenance,
limitations and necessary conversion inequality; [SOURCE.json](SOURCE.json)
for the full census; and [LITERAL.json](LITERAL.json) for the bounded
physical evidence. All 19 unchanged dependencies are authenticated.

## Open next questions

Supply the exact caller volume and machine-clock conversion, then a
complete upper bill for all arithmetic, native routing, owned banks,
setup/metadata, history and recursive ancestors. This audit leaves the
global five foundational assumptions and selected certificate unchanged.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI assistance**.
Credit DreamingOfClouds' CrocSwap/integer-mult-bounds#6936 and
CrocSwap/integer-mult-bounds#6937; the canonical stream and finite
precompilation authors; and CubeJerry's compact ADD, lifecycle, QUERY-only,
precision, rounded SCALE and global LAMBDA packages. This is an explicitly
complementary cost audit, not another arithmetic implementation.
