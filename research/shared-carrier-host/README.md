# P111 gather obstruction for the fixed U8 word

This package gives a **scoped negative result**. It tests a P111 query at the
end of the U8 A section. It retains the old rows, helper contracts, and later
word. Each new carrier follows a monotone frame path. New carriers do not
combine with each other before they reach the query hyperplane.

All 112 choices of the removed root fail a favorable complete moment bound.
The least lower bound is

```text
1.00000864736369386816835926810620863001514 > 1
```

at the PR942 complex exponent `b = 0.001664727258740678855772`. The bound gives
the new gather free entrance frames, no separate centre charge, free dirty
compensation and cleanup, free scalar and adapter work, and ideal residual
packing. A real implementation in this class cannot have a smaller moment.
The proof applies to every positive replica count. It also permits a different
puncture in each call.

This does not give a new kappa. It closes one way to reuse U8 for the paid
P111 decoder in PR1060. It does not rule out a changed A or B word, mixing new
carriers before the query frame, paid frame descents, or a different owner
geometry. It does not apply to the local word in PR1042.

## Reproduce

From the repository root, run:

```sh
python3 -I -B research/shared-carrier-host/verify.py --out /tmp/shared-carrier-host-result.json
```

Expected last line:

```text
PASS_SCOPED_FROZEN_U8_GATHER_OBSTRUCTION
```

The command uses only the Python standard library. It takes about one second
on the development machine. It reads the retained source archive, rebuilds
only the local U8 word in a temporary directory, and removes that directory.
It does not use the stored result as an oracle. `RESULT.json` is the finite
certificate from this command. It records all 112 exact row expressions,
required frames, data-path credits, and moment intervals.

The exact arithmetic is checked against the retained interval engine with
80 logarithm terms and 16 exponential terms. The new calculation uses 24
and 12 terms. The controls check a wrong query coefficient, an invalid
coalesced frame path, an invalid old-row frame advance, and a mixed label
chart. A free-query control passes the moment test in all 112 cases. Thus the
new transport charge is decisive.

## Sources and result status

The exact base is `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. PR942 was selected
at that base. The source word is the PR799 X4 archive plus the PR869/870 U8
recipe. Its decompressed SHA-256 is
`090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a`.
`SOURCES.json` pins every local dependency used by the command.

The later main commit `ba82555c64e1879e4b7decce28186f208fcb8262` selects PR1042:
`kappa = 0.001672188119205421`, with
`b = 0.001674989015937672328468`. That b is larger than the test value. The
moment for each fixed profile is strictly increasing in b. This fixed-U8
integration class therefore cannot reach that later b either. This comparison
does not extend the obstruction to the PR1042 word.

Read `PROOF.md` for the class and the all-replica argument. Read `RESEARCH.md`
for the failed approaches and the source-receipt issue. Read `NOTICE.md` for
credit and the inherited limits. No full multiplication theorem or independent
human review is claimed.
