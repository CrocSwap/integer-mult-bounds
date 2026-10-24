# Exact interface for a coarse centre reset

An exact coarse-component reset at the backward centre cut gives the
original unit shear and restores all 480 arbitrary helper inputs. The
same cut has no effect on either forward data output. This is an exact
operator statement with an oracle reset. It is not a rounding circuit
or a precision certificate.

## Literal cut and carrier values

Use the pinned raw `FULL-MODE-PROGRAMS.json.gz`, decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
Execute events 0 through 12994. Event 12995 is the centre phase marker.
Events 12996 through 13003 negate the eight centre registers. Omit those
eight signs for the reset experiment. Resume the suffix at event 13004,
the phase B marker.

The centre registers are 92, 57, 81, 224, 11, 240, 9, and 256. Their
native frames are 415 through 422, each of rank eight. In the mode input
basis, their complete input rows are

```
forward:  w = u + R x;
backward: w = u + R y/4.
```

Each row has exactly 56 source coefficients and one mode coefficient.
It has no initial target coefficient and no other helper coefficient.
The corresponding mode input roles are 225, 226, 229, 232, 241, 242,
257, and 258. All statements include the inherited native frame views.

Both data banks can therefore be scaled by a common delta without
changing the coarse part of a centre row. In physical centre frame H_k,
the backward carrier is H_k(u_k+delta R_k y/4). An exact coarse reset
would replace it by H_k u_k. A grid and error proof must show that a
permitted rounding operation makes this replacement.

## The two suffix maps

Let w_old be the incoming centre value and replace it by an arbitrary
w_new before the retained suffix. No centre sign is applied. The exact
maps are

```
F: Xout=x;
   Yout=y+x-K w_old;
   uout=w_new-Rx.

B: Yout=y;
   Xout=x-y+R^T(w_new-u);
   uout=w_new.
```

Here K=R^T/4. All 472 other helpers return to their input contents.
These formulas follow from the complete suffix impulse responses. A
forward centre increment d changes only the mode output by d. A backward
increment d changes the mode output by d and the X output by R^T d.
The same identities were proved in `CROSS-CUT-PROOF.md` and
`CROSS-CUT.json`; the new checker replays them directly.

For B choose w_new=u. Then the output is (x-y,y,u), with all 480 helper
contents restored. The retained native rank is 5522. There is no new
native child in this oracle interface. The eight removed complex signs
reduce the retained scalar bound from 204418 to 204402. This figure
excludes all reset, data-scaling, precision, and address costs.

For F the data output is independent of w_new. This remains true when
w_new is a nonlinear function of the cut values. A coarse reset, a fine
reflection, or a negative coarse value cannot remove the term -KRx.
An input correction Y+=Ku cancels only the old helper term. An output
mode correction cannot change Y. A forward improvement needs an edit
at another carrier or an additional target access.

## Exact checks and precision boundary

`check_centre_reset_interface.py` checks all 704 initial columns, the
full eight-column suffix response, all 480 backward helper outputs,
and the exact eight sign locations. A control that erases the arbitrary
coarse input fails. Forward reset and reflection have equal data outputs;
neither gives the required unit shear.

The result is `CENTRE-RESET-INTERFACE.json.gz`, with decompressed SHA-256
`fa0b2c75f8fdcbe75aa2f35f77559a06477d99adcf0d69040cba075743108868`.

```
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_centre_reset_interface.py
```

Expected status:

```
PASS_EXACT_CENTRE_RESET_ORACLE_INTERFACE
```

The separate frozen source packet is `INTERNAL-MODE-SOURCE-ROWS.json.gz`,
decompressed SHA-256
`ff1ae64f2c81d3192ef1f2f0cf0c5d984eed9215b200bbe9d4d54bf630925d38`.
Its exact reverse scalar cones contain 132 native events of total rank
156 for the backward centres, and 616 events of total rank 784 for the
forward centres. Every listed input has an initial-helper component,
even if both data banks are scaled. The packet lists endpoint views
separately. These counts describe the centre read cones. They are not
the full final-data error cones after a reset.

The digit study must prove the coarse lattice, the separation margin,
the effect of each approximate native job, the output decoding error,
and the complete finite cost. In particular, errors on paths outside
the reset carriers can remain in the final data. This note makes no
precision, supplier, or kappa claim.

OpenAI Codex performed this exact interface check under the user's
direction. A separate backward error-cone review is in progress.
