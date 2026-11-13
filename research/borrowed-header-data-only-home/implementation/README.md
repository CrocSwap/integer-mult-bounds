# Borrowed HEADER, DATA-only HOME

One literal fixed-rho adapter runs the frozen generic positive core with a
separate supplied immutable Gamma6 HEADER and an already-packed DATA-only
HOME. The body has F_HOME=V, regardless of header length E. On success it
returns only DATA to the identical HOME and restores all private bodies,
guides, guards and heads. Other homes and header/exterior bytes are preserved.

The core is unchanged. Wrapper overhead is at most256(V+1), with64(V+1)
additional historical backing. Complete primitive bounds are

`T <= Setup_rho + 256(V+1) + 2^24(fV+E+1)`,
`K_final <= K_entry + 2112(V+E+1)`.

B1 full-bank delivery/reservation remains separately charged. The graph
starts after HOME reservation; its original reservation prefix is unreachable
from the declared entry and may not use borrowed HEADER3 as scratch.
No header producer, root descriptor conversion, view packing, cutoff policy,
all-MOVE/caller admission, faster nonleaf rate or new kappa is supplied.

Python3.12+, standard library:

```sh
python3 -I -W error -B verify.py
python3 -I -O -W error -B verify.py
sha256sum -c CHECKSUMS
```

Expected marker: PASS_BORROWED_HEADER_DATA_HOME. Two complete f1/rho1 calls
use the same6144-bit DATA home and private banks, with separate headers of
10 and268 bits supplied at entry. The second cutoff has130 bits. C^2 gives
the exact selected-axis swap. Controls cover cutoff, short DATA, late
nonintegrality, returned-length mismatch and wrong/unfinished scatter.
Failure cleanup/retry and universal malformed-input validation are unclaimed.

Read PROOF.md for exact entry and origin rules. Header's first Gamma bit is
at B-relative1; native DATA/private origins are2, keeping private guards away
from permanent^0. A single-header graph uses34 fixed tapes; the two-header
fixture uses35. Constructors expand only fixed offline tables, never runtime
parameters or callbacks. The complete unchanged source closure is retained.
