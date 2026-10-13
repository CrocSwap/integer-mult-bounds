# Complete optimistic recurrence and its limits

Let `d_k` be the literal end-B dimension, `u0_k` the actual old terminal
dimension and `s_k` the entrance dimension. A proposed helper endpoint has
dimension `u_k`, contains its necessary cone, and has width `u_k-s_k`.
Retain all source/target endpoints, the eight ordered centers, A/B frame
assignments, nine calls and 896 live families per replica in ambient rank73.

The exact old local histogram is
`{1:2548,2:338,3:446,4:162,5:72,8:8}`. Its decomposition is:

| Bill | Rank histogram | Rank mass |
| --- | --- | ---: |
| Fixed prefix climbs and center descents | `{1:2048,2:288,3:368,4:160,5:16,8:8}` | 4512 |
| Actual old post-B suffix, all728 registers | `{1:500,2:50,3:78,4:2,5:56}` | 1122 |
| Favorable single jump to each old endpoint | `{1:328,2:80,3:86,4:10,6:56}` | 1122 |

The first two sum to the full old profile of mass5634. The favorable
single-jump relaxation preserves mass, but can reduce its moment. It need
not admit any common-frame cleanup word. This note makes no numerical
exclusion from that relaxation.

In particular, removing an assumed `H(9-d_k)` and adding `H(u_k-d_k)` is
unsafe as a general rejection test. Old endpoints need not be FULL, and
post-B climbs may be split across early cleanup. If other registers' suffix
climbs may change, retaining their entire old bills is also unsafe. Use the
actual old suffix or replace **all** 728 suffix bills by favorable one-jump
costs, including sources and targets.

The fixed source/target/center mass is1856. The old helper widths are
`{4:80,5:32,7:54,8:122,9:216}`, of total3778. The capacity mass for idle
stock per replica is48384. For proposed widths set

```
D(u) = 48384 - 9 * sum_helpers(u_k-s_k)
     = 14382 + 9 * sum_helpers(u0_k-u_k).
```

Require `D(u)>=0` for feasible whole-helper placement. Every idle child has
rank at most48. For `0<z<1`, define `phi_z(r)=r*(73/r)^z`, `phi_z(0)=0`.
Concavity gives `phi_z(a)+phi_z(b)>=phi_z(a+b)`. With P_pre the fixed prefix
histogram, a complete **optimistic moment lower bound** is

```
L_z(u) = [9 * (sum_r P_pre(r)*phi_z(r)
                 + sum_all728 phi_z(u_k-d_k))
           + D(u)*phi_z(48)/48] / (73*896).
```

It includes every required suffix dimension and charges returned helper
mass as idle work. Ignoring bin integrality, shared-gate compatibility,
chronology and new finite scalar work enlarges the candidate class. A
certified minimum `L_z>=1` would exclude an improved complex endpoint beyond
z for this precise family; `L_z<1` is inconclusive. No such outward-rounded
numerical exclusion is asserted here. The endpoint census alone forces
every reductions-only helper proposal back to its old endpoint.

For an actual program and T replicas, the exact recurrence must instead use
the freshly recounted local paid histogram L_new and **literal** idle
histogram I from a valid whole-helper owner map:

```
H(r) = 9*T*L_new(r) + I(r)
M = 896*T, W = 73
sum_r r*I(r) = T*D(u)
M*W - sum_r r*H(r) = 320*T
```

The last identity follows from local mass `1856+sum_helpers(u_k-s_k)`;
width reduction does not erase the inherited rank deficit. The associated
weighted recurrence uses these children plus a separately charged finite
term. That term must recount compensation, scalar/Horner coefficient
access, frames, copies, wrappers, source restoration, routing, bridges,
shifts, moves, private stock, correction streams, precision, tape and rows.
Keep the bit supplier and its surcharge, analytic guards and seven-step
outer recipe. Zero extra finite work is allowed only in the relaxation,
never in a constructed invoice.

A positive nomination therefore still needs a literal cleanup, both exact
arbitrary-dirt orientations, native phases and wrappers, changed residual
adapters, complete whole-helper hosting, the full invoice and rational
moment/outer certificates. This contribution changes none of those inputs
and claims no larger kappa.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
