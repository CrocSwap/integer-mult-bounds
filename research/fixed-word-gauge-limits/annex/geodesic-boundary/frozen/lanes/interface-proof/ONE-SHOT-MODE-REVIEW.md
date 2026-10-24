# A complete native endpoint for one mode cohort

The one-shot mode endpoint proposed by the history-encoding and
encoded-controller lanes passes independent review. It works on arbitrary
initial mode contents. It gives legal monomial access to the mode decoder
both before native processing and after the full 73-axis transform. It
does not restore the contents changed by the coupled active call.

The source adapters and their exact phases are pinned in
`WALSH-MODE-ADAPTERS-SOURCE.json`. Their payload and the underlying raw
mode primitive are specified in `WALSH-MODE-REVIEW.md`. This proof uses
that independently checked mixed interface.

## Preparation, active call, and completion

At stage s, let `N=9+8s` and `m=1+8s`. Let Z_s be the quadratic sign
`(-1)^sum_(i<j<=N) x_i x_j`. It acts only on the completed U_s. It is
the identity on the remaining `64-8s` axes.

For an arbitrary initial mode h, apply Z_s and then G_m. The input to
the type-zero active word is therefore `G_m u`, where `u=Z_s h`.
After the active word and its base output adapter B_s, the mode is

    C_omega_N G_N u' = Z_s F_N Z_s u'.

Apply Z_s on the left, then the native transform on the untouched future
axes. The final value is exactly

    F_73 z',       z'=Z_s u'.

Thus the initial standardized content is h and the final standardized
content is z'. No assumption that h is zero occurs.

The complete native rank count per mode is

    8s + 9 + (64-8s) = 73.

The preparation G_m is one rank-8s child with explicit monomial wrappers.
Its even-space Gram matrix is `B=I_(8s)+11^T`, with `B^2=I`. In the old
even-space address chart, its kernel is `P_B H_(8s)`. The identity
`H_(8s)=S F_(8s) S`, where S has phase `i^wt`, is exact because 8s is a
multiple of eight. The future completion is the native transform on an
actual coordinate block. Rank-zero preparation or completion is omitted.
These are strict smaller-rank children at every stage.

The retained selected native admission also checks the stronger inequality
`73^2>2*r_max^2`. The unsplit rank-56 and rank-64 jobs do not meet it.
There is an exact rank-count repair: split the coordinate F_56 in each
preparation or tail into disjoint F_48 and F_8 children, and split F_64
into disjoint F_48 and F_16 children. The enclosing monomial maps stay the same.
The new maximum rank is 48, so the displayed inequality then holds. This
factorization preserves the endpoints and the rank sum, but adds recursive
calls. Their routing, admission, and changed recurrence moment must be
charged. The native rank sum alone does not price this repair.
These splits minimize the concave moment among coordinate splits with
maximum rank 48: for fixed total rank, a concave power sum is least when
the parts are as unequal as the upper bound permits.

## The exact contents and their access maps

Put `N_s=M_s Z_s`. Its inverse is `Z_s M_s^-1`. In the notation of the
reviewed mixed map, set

    A_s=D_p^-1 K N_s,
    B_s^content=N_s^-1 R D_p,
    P_s=D_p^-1 P D_p.

Here B_s without the superscript remains the native output adapter.
The forward contents are

    x'=x,
    y'=y+(I-P_s)x-A_s h,
    z'=-h-2 B_s^content x.

The backward contents are

    x'=x-(I+P_s)y-8 A_s h,
    y'=y,
    z'=-h-B_s^content y/4.

The order of N_s is required: its Z_s acts first. All 472 ordinary helpers
are restored by the unchanged active primitive. The preparation and
completion operate only on this mode cohort.

The already checked adapter identity is

    B_s F_N M_s=Z_s F_N Z_s.

It gives

    F_73 N_s F_73^-1=B_s^-1 Z_s,
    F_73 N_s^-1 F_73^-1=Z_s B_s.

The extension from N to 73 is valid because every factor is the identity
on the future axes. These are exact monomial maps, including their
phases. Thus both N_s and its inverse can be used at the empty frame and
the final full frame without a recursive conversion child. The result
does not make every old-data source query monomial.

There is also a simple complex transpose correction if a controller
needs it. In the one-shot coordinates, `N_s^T N_s=Z_ell`, where
`ell=(1<<(8s))-1`. Its two physical repairs are Z_ell at the empty frame
and `X_ell Z_ell` at the full frame. The scalar phase in the latter is
one because ell has weight 8s. This follows from the more general repair
in `WALSH-MODE-REVIEW.md`; it changes no recursive rank count.

## Independent checks and conditional invoice

Run:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/review_one_shot_modes.py
```

The expected output is `PASS_INDEPENDENT_ONE_SHOT_MODE_ENDPOINT`. For
each of the nine stages, it reconstructs both kernels of
`F_73 N_s=(B_s^-1 Z_s) F_73` from the literal address columns and native
Gaussian coefficients. It checks all 10,732 coefficients in a complete
quadratic phase witness on the two 73-bit kernel coordinates. It also
checks the literal inverse monomials, the preparation's global phase,
and the complete native rank count. No producer phase expressions are
imported. All requirements remain active under `-O`.

For a new eight-mode cohort at every call, there are 72 new mode families
per replica and 1,152 over the 16 replicas. Add the independently checked
old width-nine owner backfill. The conditional child profile change is

    {8:-896, 9:1152, 16:256, 24:256, 32:256,
     40:256, 48:256, 56:256, 64:256}.

Its paid rank change is 74,880. If every new mode is a valid full output,
its productive rank change is 84,096. The difference is 9,216, or 576
per replica. The resulting physical stock would be 15,978. These counts
include all displayed preparations, completions, and displaced old jobs.

With the optional split just described, replace the 256 jobs of rank 56
by 256 jobs each of ranks 48 and 8, and replace the 256 jobs of rank 64
by 256 jobs each of ranks 48 and 16. The resulting profile change is

    {8:-640, 9:1152, 16:512, 24:256,
     32:256, 40:256, 48:768}.

It has the same paid rank change and stock. Its concave recursive moment
is larger than that of the unsplit profile.

The rank count alone is not a recurrence improvement. The new child
jobs require admission, the larger stock must be charged, and every
finite scalar and address operation must be counted. Most directly,
the coupled content controller must restore z'=h and its required data
outputs, or prove another exact productive content contract. No such
controller, complete supplier, or kappa result is certified here.

The identities hold for all positive tensor powers, since the base
operator and scalar phase are exact. Prepared with substantial OpenAI
Codex assistance and independent agent review. No independent human
review is claimed.
