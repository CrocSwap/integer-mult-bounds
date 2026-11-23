# Fixed-role byte envelopes for the direct scalar and ordinary roots

Source: Ali Romman's retimed runtime, PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. Canonical research base:
`e54523517d0f03e58352e647c403a5af3e525a57`. Exact resolved modules are
retained in `sources/` and bound by `SOURCE-BINDINGS.json`.

This supplements the source-local byte census in PR #8091. Its purpose is
to replace three remaining function-level volume assertions with explicit
fixed-role historical bounds. It does not certify the global native/outer
census, nesting count, movement tariff, control storage or activation
threshold. No new kappa and no complete foundational-assumption removal.

## 1. Direct scalar: a uniform envelope across differing siblings

Consider the actual `direct_body.scale_atom`. Each component width is a
positive integer, the external prefix and suffix are positive, and the
factor is an admitted nonzero rational unit whose reduced numerator and
denominator have absolute value at most 20 and are prime to three. Put
`W=sum(component_widths)` and `V=prefix*3^W*suffix`, the actual incoming
byte volume. The source has two whole-word roles and twenty bucket roles.

For **any finite sequence of calls** with these premises, reusing their
fixed tuple positions and with every incoming volume at most `V*`, the
sum of all 22 role-wise historical maximum endpoints is at most

\[
 \left(2+1+\frac12+12\frac13+4\frac19+\frac1{19}+\frac1{20}\right)V_*
 =\frac{27521}{3420}V_* < 9V_*.                         \tag{1}
\]

The two full-word roles each have endpoint at most `V*`. The twenty
bucket coefficients are:

| Zero-based bucket position | Uniform fraction of `V*` |
|---|---:|
| 0 | 1 |
| 1 | 1/2 |
| 2 through 13 | 1/3 each |
| 14 through 17 | 1/9 each |
| 18 | 1/19 |
| 19 | 1/20 |

The fractions `1/2`, `1/19` and `1/20` can be limiting suprema; attainment
is not required for an upper bound. Named matcher pages, the already-owned
input bank and the caller's output owner are outside these 22 new roles
and remain separately charged.

### Exact bucket counts

For one component, let `q=3^s`, let `b` be the total width of earlier
components, and let `u=suffix*3^(W-b-s)` be an opaque block in bytes. One
prefix processes `q*u=V/(prefix*3^b)` bytes. Every prefix erases its buckets
before the next prefix; there is no multiplier from the number of prefixes.

For integer scale `k`, only positions `0<=j<k` are used, and their exact
record counts in either direction are

\[
 C_j(q,k)=\left\lceil\frac{(j+1)q}{k}\right\rceil
          -\left\lceil\frac{jq}{k}\right\rceil.          \tag{2}
\]

This is the literal division used by the forward path. In the inverse
path a record index `v` enters bucket `j` precisely when
`v=-q*j mod k`. The integers `0<=v<q` of that residue correspond to
`jq/k<=h<(j+1)q/k`, giving the same count. This uses the native unit
condition `gcd(q,k)=1`. The role endpoint is therefore
`C_j(q,k)*u`, at most `(C_j(q,k)/q)*V`.

The admissible integer factors are the thirteen integers `2<=k<=20`
coprime to three. For any one of them, write `q=kh+r`. Equation (2) gives
`C_j=h+delta_j(r)`, where `delta_j(r)` is zero or one. Hence

\[
 \frac{C_j(q,k)}q=\frac1k+\frac{k\delta_j(r)-r}{kq}.       \tag{3}
\]

The residues `3^s mod k` repeat with a finite period. The certificate
explicitly checks the first return to one for each of these thirteen
fixed integers; the largest period is 18. In a fixed residue class, a
positive correction in (3) decreases as `q` grows, and a nonpositive
correction is bounded above by `1/k`. Thus it suffices to compare the
first occurrence of every residue and the limit `1/k`. Exact rational
comparison gives the table above for all positive component widths.
This finite certificate plus (3) is an all-size argument, not a finite
width search extrapolation.

Negation uses only bucket zero, and its endpoint is `(q-1)u<V`. This is
why bucket zero receives coefficient one. Both numerator and denominator
passes, every component, and different sibling calls reuse these same
positions. Taking each position's maximum preserves its uniform table
entry, proving (1). The full source `work_tapes` cleanup clears and
truncates all positions at return; no sibling retains another copy.

### Why a smaller single-call estimate cannot be substituted

For a **single** call, both integer passes together have bucket high sum
at most twice the sum of one-prefix component volumes. The earlier widths
form an increasing subsequence of `0,...,W-1`, so that sum is at most
`(3/2)(1-3^-W)V/prefix`. Negation contributes at most `V/prefix` to
bucket zero. Adding the two full-word buffers proves a strict `<6V`
bound per call (and the no-component identity case is cheaper).

That scalar total must not be applied after taking independent role maxima
across differing calls. Different factors make different buckets large.
The actual executed sequence in `evidence/RESULT.json` records a sum above
`6V*`, while each individual call is below `6V*`. The table in (1), rather
than the single-call inequality, is the reusable historical envelope.

## 2. Five root-body roles: fewer than seven incoming volumes

For `triangular_ordinary.root_body`, let the incoming ternary field be
`V=prefix*3^(2e)*gap*suffix`. Retain the actual `rows`,
`k=least_power(3,rows)`, `extent=3^k`, and
`padded=ceil(extent/rows)*rows`. For positive rows,

\[
 rows\le extent,\qquad extent\le padded<extent+rows\le2extent.
\]

The `expanded` and `body` roles each hold
`V'=prefix*padded*3^(2e-k)*gap*suffix<2V`. This explicitly retains the
zero row padding as bytes.

Write `e-k=c*width+r`, exactly as the source. The call to `body_ordinary`
passes `c`, `prefix*padded`, the gap `3^r*gap*extent`, and suffix
`3^r*suffix`. The complete declared child volume is therefore

\[
 prefix\,padded\,3^{2c\,width}\,3^{2r}\,extent\,gap\,suffix=V'.
\]

Thus the child interface is volume-preserving; its internal owners and
scratch retain separate charges. The `genuine` role has exactly `V`
bytes after padding removal. The high and trailing cold corrections
each have declared volume `V`, when present, and otherwise remain empty.
The five fixed roles consequently total at most `2V'+3V<7V`.

For varying source parameters, each of the two padded roles has its own
uniform `<2V*` cap and each other role has cap `V*`. This also gives a
`<=7V*` envelope across any finite sequence with incoming volumes `<=V*`;
strictness holds for a nonempty finite sequence by taking its attained
maxima. Earlier-stage scratch and same-stage named pages are not part of
the five roles. The at-most-one-live-root-per-stage fence is retained from
the preceding source audit, not proved from this byte inequality.

## 3. The public binary rectangle is a single, serial enlargement

The actual `ordinary_carrier.ordinary_swap` uses two work files for the
public rectangle. For positive binary width, let `a=2^bits`, let `b=3^d`
be the least ternary power at least `a`, and let one incoming prefix slab
have `V_s=a^2*gap*suffix` bytes. Since `a<=b<3a`, its full two-axis padded
volume is `V'_s=b^2*gap*suffix<9V_s`.

`fiscal_scans.rectangle_slab` writes exactly that padded length, including
both holes within each row and the final padded-row tail. The caller
erases its opened file before returning the completed slab and erases the
completed file before the next prefix slab. Each of the two roles has
historical endpoint at most `V'_s`, so their sum is `<18V_s`, independent
of the prefix count. Relative to the full incoming call of `p` slabs this
is `<18V/p`. In the reverse rectangle the same true and padded extents
are consumed; no second enlargement is introduced.

This theorem is conditional only on the complete ternary service's
declared input/output volume at that interface; it does not replace the
service's own native correctness or cost proof. The width-zero and cold
branches do not open these rectangle files. Descending ordinary stages
use the ternary service directly, so this particular rectangle is not
charged once per ordinary stage.

## Verification and open next question

The checker authenticates the resolved sources, proves the thirteen exact
residue-period certificates, executes actual scalar calls with an
independent componentwise permutation oracle, and records historical
maxima across a varying-factor sequence. Failure controls reject missing
bucket erasure and a deliberately undersized table entry.

Root-body checks execute its original control arithmetic with byte-count
streams and a volume-checked child interface; they are not payload
executions at astronomical ranks. The public rectangle checks execute
actual bytes with a separately implemented complete ternary transpose in
place of the native service. Their stated scope is the wrapper, padding,
serial cleanup and interface size. An omitted residual-factor mutation
fails the child-volume check.

These envelopes close local portions of the retained `256`-volume
allowance. A remaining next question is the complete owner-bank byte
cover across the other raw helpers and its interaction with the proved
Gaussian census. The immediate-adapter count, full static call-graph
coverage, outer CRT/control allocation and movement tariffs remain open.

Credit Ali Romman for the runtime, root envelopes and stage-space
architecture; retained predecessor authors keep their attribution.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance
and separate model-assisted review pending. No human or formal-kernel
verification is claimed.
