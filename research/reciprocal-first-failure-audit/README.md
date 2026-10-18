# First real-input failure of the seeded two-guard reciprocal

**Independent finite verification; no new kappa.** For the fixed reciprocal
routine below, every real input `1 <= c < 2` satisfies the strict residual
contract at every integer target `p=1,...,14`. The first failing target is
**p=15**, where the complete failure set is the union of the **seven closed
intervals** below. This is complete real-input coverage, including nondyadic
inputs and equality endpoints, not a search over a sample of rationals.

Charles Bethin's [PR1655](https://github.com/CrocSwap/integer-mult-bounds/pull/1655)
provides the first interval's reachable witness and explicitly does not claim
minimal failing precision. This package adds the complete earlier-precision
exclusion and all seven failure intervals, using a new integer census and a
separately implemented inverse-floor interval partition. It independently
corroborates that credited witness; it does not claim priority for the failure
or the sharp uniform guard count. @ToikY's
[PR1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638) supplies the
three-guard all-precision upper proof.

## Fixed routine and exact result

Write `R_t(z)=floor(2^t*z)/2^t`. Start with `x=5/8`, perform one step at
`t=6`, and set `m=1`. While `m<p`, set `m=min(2*m,p)` and `t=m+2`. Each step is

```
c_t = R_t(c)
u = R_t(c_t*x)
x = R_t(x*(2-u))
```

Every product is exact before its indicated floor. The incoming iterate is
preserved even when the first post-warm-up precision decreases from six to
four bits. The contract is `|1-c*x| < 2^(-p-1)`, measured against the true c.

At p=15 the working precisions are `[6,4,6,10,17]`. Put `K=131072`.
For each row, the exact failing interval is **[j/K, 131070/A]**, with both
endpoints included, and the routine returns `x=A/K` throughout that interval.

| j | A |
|---:|---:|
| 254758 | 67435 |
| 255744 | 67175 |
| 256822 | 66893 |
| 256826 | 66892 |
| 256922 | 66867 |
| 257863 | 66623 |
| 259860 | 66111 |

Each right endpoint is strictly inside its own prefix cell
`[j/K,(j+1)/K)`. Its residual is exactly `1/65536`, so excluding it would
incorrectly omit a strict-contract failure. The residual is larger to its
left and smaller immediately to its right. All seven failures have positive
residual. The largest residual is `137569/8589934592`, exceeding the bound by
`6497/8589934592`. The negative-residual side has positive margin `1/8388608`.

The first interval reduces to PR1655's `[127379/65536,26214/13487]`;
its left-end residual excess is the credited `655/8589934592`.
[The certificate](CERTIFICATE.json) records all exact slacks, per-target
output-stream digests, output-run counts and endpoint membership.

## Why the finite checks cover every real input

**Prefix reduction.** At fixed p, let T be the maximum precision read,
including the six-bit warm-up. On each half-open interval
`[j/2^T,(j+1)/2^T)`, every prefix read is constant. Induction over the fixed
schedule makes every stored iterate constant too. There are exactly `2^T`
such intervals covering `[1,2)`. This is a finite partition argument, not a
floating-point approximation of a continuum.

For a constant positive output x on `[l,r)`, the residual `e(c)=1-c*x` is
strictly decreasing. Every input in that interval passes exactly when

```
e(l) < B and e(r) >= -B, where B=2^(-p-1).
```

The different inequalities are intentional: l is included and r is excluded.
If the positive side fails, its set is `[l,min(r,(1-B)/x)]`, excluding r
when that endpoint is the cell boundary. The negative failure set starts at
`max(l,(1+B)/x)` when this is strictly below r, and excludes r. A positive
failure may be a singleton; the one-guard control actually contains three.

**Independent inverse-floor partition.** The second implementation starts with
`[1,2)` and its constant seed. For any incoming interval with exact value x,
write `S=2^t`, `C=floor(S*c)` and `q=floor(C*x)`. The exact equivalence

```
q <= C*x < q+1
iff ceil(q/x) <= C < ceil((q+1)/x)
```

shows that q is constant precisely on
`[ceil(q/x)/S,ceil((q+1)/x)/S)`, intersected with the incoming interval.
The next iterate there is `floor(x*(2*S-q))/S`. The evaluator enumerates these
integer q values, checks adjacency and both coverage endpoints at every stage,
and merges adjacent equal-output intervals. It derives the capped schedule
from powers of two below p, rather than sharing the first evaluator's loop.
It uses Fraction arithmetic and imports no census or predecessor functions.

For comparison only, the resulting intervals are expanded to their finest
prefix-cell multiplicities. The verifier compares the full ordered output
streams **byte for byte**, plus run counts, exact extreme residuals and every
failure interval at every target. The certificate retains a SHA256 fingerprint
for reproducibility; exact agreement during replay does not rely on that hash.

There are **262,272** two-guard prefix cells across p=1..15. Both engines also
check all **262,144** cells of the three-guard p=15 positive control. This
finite positive control corroborates PR1638; its all-precision theorem is not
proved by our enumeration. The independent implementations were written in
one Codex-assisted session; no independent human or proof-kernel review is
claimed.

## Reproduce and failure controls

Python 3.12+ and the standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/reciprocal-first-failure-audit
```

Expected: `PASS_RECIPROCAL_FIRST_FAILURE first_p=15 intervals=7
two_guard_cells=262272 independent_partition=PASS no_new_kappa`, six passing
test groups, then `PASS_REGISTERED_RESEARCH_PACKAGE`.

The default replay writes nothing. Direct source-export replay is also supported:

```sh
python3 -I -O -B research/reciprocal-first-failure-audit/verify.py
python3 -I -O -B research/reciprocal-first-failure-audit/test_audit.py
```

To regenerate a certificate, pass `--write /path/to/new.json` to verify.py.
An occupied output is refused. Preserve the package and its one declared
repository input at the same relative path when making a minimal source export.

Controls cover all seven rational equality endpoints and interior/exterior
points; the credited witness; lower-guard failures and equality-only
singletons; truncated incoming precision, stale prefixes, omitted inner
rounding, ceiling output, omitted warm-up, omitted final cap and the wrong
final precision; invalid/gapped/overlapping partitions; and invalid domains.
Actual optimized subprocesses reject a missing failure interval, an incorrectly
open equality endpoint, a changed manuscript input, and a changed predecessor
copy. The tests run the complete verifier from an offline, read-only export
in a path containing spaces and preserve an occupied output file.

## Pins, scope and credit

Base: `5668c25a9331334e939d538540c69d69a16a3420`.
[SOURCES.json](SOURCES.json) binds the unchanged Section09 input and byte-exact
predecessor notes at PR1638 `394b90ee7fdaedd1f666a78a442127be3da17810` and
PR1655 `4880c3ea0401927a5fc0215dce99feefe092d9e9`. Their notices and AI disclosures
are preserved. No predecessor executable is imported. The selected record,
manifest, actual PR1094 construction and review were inspected at this base:
conditional kappa remains `836330098538459/500000000000000000`.

[TASK.json](TASK.json) records seed83, the three considered tasks, exact local
claim, scope change from the generic moment card, stopping rule, completed
coverage and overlap. There was no pinned coordination issue; the donor's
local-claim fallback was used. Full entry overlap covered 458 open PRs and
319 discussion records with complete pagination and no warnings. Text searches
are leads, not a priority or novelty guarantee. The review ledger supplied no
accepted disposition for these later reciprocal PRs.

This is a downstream Section09 side result, not a supplier or multiplication
bottleneck improvement. No upper bound on failing precision beyond the first
failure is searched; no changed schedule, absolute-error-only optimum, kernel
proof, root/recovery integration, physical tape admission, performance claim,
selected cold replay or complete multiplication theorem follows. The inherited
all-size/compiler, source, hosting, precision/tape and analytic obligations are
unchanged. Hosted CI is separate from the local checks in VALIDATION.json.

Credit Charles Bethin (@cbethin), @ToikY, Hanson Sun (@bbMisk)/PR1528, the
retained OpenAI manuscript/classical Brent reduction, and the repository's
maintainers. New work is Apache-2.0, prepared for **Ross Richardson with
substantial OpenAI Codex assistance** in derivation, implementation,
verification and writing. No subagents were used. See the original notices in
vendor/ and the repository LICENSE.

## Open next questions

Can a precisely specified change confined to the final capped step retain two
guards and satisfy the residual contract? The seven intervals provide exact
regression fixtures. First derive a reachable-state bound and the full cost of
any extra rounding precision or iteration; passing these finite fixtures alone
would not establish a uniform theorem. This does not reopen the excluded
unchanged schedule.

Can the inverse-floor partition lemma and its half-open endpoint rules be
formalized, then linked to an authenticated execution certificate? Start with
the two floor inequalities above. A proof-kernel environment and a reviewed
source-to-formal-routine binding remain prerequisites.
