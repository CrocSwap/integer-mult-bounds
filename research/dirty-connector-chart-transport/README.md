# Carry a dirty connector through a paid change of chart

A connector-only invertible operation can carry an open dirty connector from
signal B0 x to signal B1 x exactly when the two maps have the same kernel.
The connector dirt changes chart too; the final inverse is compulsory. A
fully explicit three-bit F2 pilot costs **24 scalar XORs versus 32** for two
closed echoes, including both chart operations. All 4096 dirty inputs and
their inverses are checked.

This is a changed-alphabet, fixed-map two-call result. It does not supply a
recursive supplier, native admission, all-size speedup or new kappa. The
inherited universal-connector model forbids connector-only chart operations;
its lower bound is therefore not contradicted.

## Exact contract and proof

Let B0 and B1 map a finite-dimensional vector space X to the same space Z
over a field. An invertible map R on Z with B1=R B0 exists if and only if
ker B0=ker B1. Necessity follows by applying the inverse of R. For sufficiency,
define the map B0 x -> B1 x between the two images. Equal kernels make it
well-defined and injective, and it is onto by construction. Extend bases of
the two images to bases of Z and map the remaining basis vectors bijectively.
This proof includes zero and singular maps. Equal rank alone is insufficient:
over F2 the rank-one functionals x -> x0 and x -> x1 have different kernels.

The implementation below is specifically over F2. Arrays x,z,y1,y2 are
distinct and arbitrarily dirty. The source x is fixed, z is reserved and
hidden throughout, and each output is written only during its own request
interval. All complete calls preserve other arrays and restore their private
scratch and entry heads. The intended final map is

    x'=x; z'=z; y1'=y1+A1 B0 x; y2'=y2+A2 B1 x.

For a chosen, paid R with B1=R B0, execute:

    y1 += A1 z; z += B0 x; y1 += A1 z;
    z <- R z;
    y2 += A2 z; z += B1 x; y2 += A2 z;
    z <- inverse(R) z.

The first echo cancels the initial dirt and contributes A1 B0 x. After
transport, z=R z_initial+B1 x. The second echo cancels R z_initial and
contributes A2 B1 x, leaving z=R z_initial. Only the final inverse restores
the actual connector. Thus arbitrary dirt is preserved without requiring
R z_initial=z_initial. Conversely, a source-independent linear chart
operation R has the prescribed open boundary for every x,z_initial exactly
when B1=R B0. This is a statement about this chart operation, not a lower
bound against other adapter alphabets or direct product calls.

## Paid budget and literal instance

Write c_B0,c_B1,c_A1,c_A2 for complete call costs and c_R,c_Rinv for complete
chart costs, including arithmetic, routing, coefficient access, scratch and
heads. The two closed echoes cost

    I + 2 c_B0 + 2 c_B1 + 2 c_A1 + 2 c_A2.

The transported pair costs

    I' + c_B0 + c_B1 + 2 c_A1 + 2 c_A2 + c_R + c_Rinv.

Preparation, admission, dispatch and reservation belong in I and I'. A saving
requires c_R+c_Rinv+(I'-I)<c_B0+c_B1. An existence proof for R alone supplies
neither its algorithm nor its cost. Dynamic chart synthesis must be charged.

For the fixed pilot, rows are binary bitmasks:

    B0=(7,6,1); B1=(1,6,1); A1=A2=identity;
    R=(3,2,4), namely z0 ^= z1, with R inverse=R.

The maps B0 and B1 are singular of rank two. Each matrix entry 1 is one
scalar source-to-target XOR; the two chart calls each cost one XOR. Hence
the baseline costs 2*6+2*4+2*3+2*3=32 and the candidate costs
6+4+2*3+2*3+1+1=24. No zero-initialized array, free chart, runtime matrix
synthesis or direct A B product is used. Constants are compiled into both
instruction lists. This gate model assumes a complete scalar XOR primitive;
it is not a compilation into the repository's selected recursive machine.

As an additional, explicitly defined fixed-port tariff, number the twelve
bits x,z,y1,y2 from zero and put the home position one cell before bit zero.
Charge each XOR 2*(max(source,target)+1) movement units plus five units for
instruction dispatch, two reads, one write and XOR. The independent totals
are 580 versus 464. These are costs in that stated tariff, not a native
admission certificate or an assertion about hardware instructions.

## Reproduction and controls

    python3 scripts/research_package.py --package research/dirty-connector-chart-transport

Use Python 3.12 for the registered replay. The verifier compares all 262144
ordered pairs of three-by-three binary maps against independently generated
GL(3,2) orbits. Exactly 40916 ordered pairs admit chart transport. It also
checks all 4096 dirty pilot inputs against the direct requested map and the
literal reversed XOR word. Omitting either chart operation or substituting
the wrong closing map produces an explicit counterexample. Exact source
hashes bind the inherited alphabet and mutable-source predecessor.

This result complements `mutable-source-persistent-connector`: that package
changes the source and pays B C u; here the source is fixed and the connector
signal map changes by a paid invertible row operation. It is not another
source-mutation experiment. The task-card first example reproduced the 945
canonical pairings of `universal-connector-boundary` before this extension.
Neither predecessor implementation is imported by the verifier.

## Open next questions

* Find an admitted consecutive pair with equal kernels and cheap chart and
  inverse operations. Start from actual fixed-port source maps and synthesize
  the complete adapter; the missing input is a selected schedule permitting
  the reserved connector lifetime.
* Derive a contracting supplier recurrence only after exhibiting such a
  family and charging chart synthesis, admission and restoration. This pilot
  supplies no all-size recurrence.

Prepared by woklerx with substantial OpenAI Codex assistance. The inherited
connector and mutable-source packages retain their own attribution and scope.
Apache-2.0, following the repository contribution terms.
