# Contract the idle role-379 stop on #7636 and #7658

Role 379 can go directly from chart 748 to chart 1072 on both pinned
words. The removed stop at chart 1065 has no use of role 379. The direct
rank-3 MOVE replaces ranks 2 and 1 with the same absolute operator,
public outputs, owned observations and productive targets.

The directed crossing on the #7658 parent is **[0.0037170835568,
0.0037170835569]** with its declared 17-call invoice residual. The lower
endpoint is 0.00000031655895 above the parent's published upper endpoint.
The crossing for the #7636 parent is **[0.0036810345257, 0.0036810345258]**
under its own declared residual and 180-CLEAR contract.

| Pinned parent | Source events → candidate | Ordered CLEARs | Paid positions → candidate | Productive targets | Directed parent bracket | Directed candidate bracket |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) | 202,668 → 202,667 | 180 | 109,652 → 109,635 | 22,461 | [0.0036807241001, 0.0036807241002] | [0.0036810345257, 0.0036810345258] |
| [#7658](https://github.com/CrocSwap/integer-mult-bounds/pull/7658) | 150,010 → 150,009 | 234 | 108,598 → 108,581 | 22,461 | [0.00371676699784, 0.00371676699785] | [0.0037170835568, 0.0037170835569] |

For each comparison the paid delta is `{1: -17, 2: -17, 3: +17}`, the
targets are unchanged, and rank surplus stays at 1,424. The declared
signed invoices are retained in [the source bundle](retained/). The
replays recount native ranks from the two literal words in each case.
[The proof](PROOF.md) gives the transition identity and source clocks.
[The discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19695810)
records the original bounded investigation.

## Verification

Both exact replays compare all 1,501 arbitrary-input public rows and
their end charts. They verify each original live-donor certificate in
both tapes. #7636 retains 1,049 ordered owned or COPY observations and
#7658 retains 1,317. For both cases the exact Gaussian checker compares
the two old transitions and the direct transition against their
canonical operators, then compares the two-step composition against the
direct transition. Each comparison covers 512 forward and 512 adjoint
columns with absolute phase. The wrong-phase control preserves the
signed Pauli tableau and is rejected by the column test.

The mutation checker also rejects a valid intervening SCALE, an
incorrect MOVE source, an omitted direct MOVE and a changed scalar.
The separate replay rejects an illegal chart, a legal sign change with
the same recursive invoice, and a self-referential CLEAR certificate.
It independently derives the full invoices using the declared caller
residuals and encloses their price crossings with rational logarithm and
exponential bounds. The construction uses the pinned 256-bit directed
invoice evaluator. On #7658 the published exact upper at 14 decimal
places is checked by the independent replay. The construction first
refused that upper at its 13-decimal grid guard and then used the
conservative upward tick 0.0037167669979.

| Case | Mutation and phase in original run | Separate exact replay in original run |
| --- | ---: | ---: |
| #7636 | 9.11 s / 103,088 KiB RSS | 104.30 s / 261,188 KiB RSS |
| #7658 | 14.44 s / 85,128 KiB RSS | 56.45 s / 244,204 KiB RSS |

The separate replay applies one CPU, 2 GiB address space and 240-second
CPU and wall limits per case. Each registered combined command is
capped at 320 seconds.

From the repository root on Linux with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-role379-idle-stop
```

To replay an offline copy directly, run from this package's directory:

```sh
python3.12 -I -B verify.py 7636
python3.12 -I -B verify.py 7658
```

The commands check the source bytes, reconstruct the mutated words in
private temporary directories, run both checkers, and compare their new
results with the [retained receipts](evidence/). Generated gzip encoding
may vary across Python and zlib builds. Candidate comparisons authenticate
the exact decompressed bytes, while the independent replay binds the
actual gzip bytes it read on that run.

## Source and assumption boundary

The catalogue is provenance at base
`e54523517d0f03e58352e647c403a5af3e525a57`. The external parent sources
are vendored at the exact commits, paths, Git blob IDs and SHA-256
values in [SOURCE-PINS.json](SOURCE-PINS.json), so the replay requires
only these bytes. Git history verification for the catalogue belongs to
the registered launcher. The package keeps the original notices and
only the inputs used by the replay.

| Parent | Exact head | SHA-256 of original decoded word | SHA-256 of candidate decoded word |
| --- | --- | --- | --- |
| #7636 | `7e68d8dd62d9a38c0f3c942262a7a85ca7125b75` | `98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2` | `9b5b66e93f91c9538525d8d7b1278e0f203058d5cd4e1351fa06f8315fdaa555` |
| #7658 | `0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82` | `fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6` | `f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669` |

Both brackets are conditional on the corresponding parent word's native
all-column provider, owned erasure, compiler, precision/tape and analytic
recovery assumptions, and on its unchanged #7113 signed caller residual.
The #7658 comparison preserves role 457's initial chart 281 and all 234
CLEARs, with 52 of 68 allocated labels used. The #7636 comparison preserves
its 180 CLEARs and 68 used labels. The paid result measures the recursive
invoice. A complete application additionally requires the physical
caller, native provider, conversion and tape/precision obligations.

For #7636 the unchanged literal ADD at old clock 150836 has coefficient
`23184221/921600`. Its numerator exceeds the historical 24-bit fixed-tape
guard. A charged legal lowering and fresh resource check would be needed
to use that retained tape contract.

## Credit

DreamingOfClouds supplied both exact parent words and the initial
main-176 contact changes. #7630 E6 and #7658 E2 exposed the silent stop
on their respective lineages. The #7658 base also credits SYLforge's
#7637, Ali Romman's #7605 and Rohan Arun's signed #7113 caller. The full
lineage and retained code credits are in [NOTICE](NOTICE). Clear1nsight
prepared this package with substantial OpenAI Codex assistance. The
task scope is changed from a joint helper-basis/channel split to a
single paid native transition contraction on two exact words.

## Open next questions

- Verify the full #7658 candidate against the actual #7113 caller,
  using the same 234 CLEAR witnesses and role-457 entrance. The
  decisive check is the retained caller under matched native, signed,
  precision and charged tape bounds.
- For #7636, qualify a legal, charged same-frame lowering of the
  overwide literal before any claim under that fixed-tape model. The
  lowered tape would need a new hash and comparison against this
  scalar and ownership transcript.
