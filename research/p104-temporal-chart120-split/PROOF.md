# A second fully charged causal-history split, at chart 120

This is one source-bound instance of Ali Romman's causal-history owned-buffer
mechanism. It uses the byte-identical constructor and timed-certificate checker
from #7140, with a new source, witness, path, inventory and complete application.
It is a conditional finite construction, not a complete multiplication theorem.

## Exact source and coefficient identities

`INPUTS.json` retains all 30 files from #7140 at
`a95783a8c861248a759136d4285ea725499cf231`, package
`research/p104-causal-buffer-split`, including its full nested closure and notices.
The exact source word has SHA256
`81f9b2e0a170aa3ab0cd4bb1056c834ebe0b98eaf37abe5986c6e53abd1257ea`.
The new word has SHA256
`c38b79279f665d46d795501de6645a8a16d9324c22199fa615313b6abfdc3e2f`.

Let P(t,r) be the complete normalized-coordinate source row immediately before
original event t, and S(t,r) the complete final response to adding one unit to
role r there. Owned initialization, erasure and COPY are included in these
linear maps. The independently reconstructed certificate is

```
P(39225,649) + P(39224,1449) = e1449 = c
```

and

```
−S(39280,650)/2 − S(39298,1305)/2 − S(40403,1488)/2
+ S(41465,1449) − S(41470,651)/2 + S(41668,198) = e1449 = d.
```

These are equalities in every source public input/output coordinate, not just
the displayed coordinate. In particular, all main inputs, old #7140 added
public input, retired helper and other boundary groups cancel. Thus `c d = 1`.
The common helper group has boundaries U=3 (zero space), V=127 (full space).
Frame F=120 has basis [7,25,75,160,288] and dimension five.

## Legal temporal access and the paid change

`PATHS.json` gives seven original MOVE paths. They are retimed only between
adjacent scalar contacts: the constructor checks that every role event in each
interval is one of the declared MOVEs and that no other operation reads it.
Their paths and paid ranks are retained. This brings the two collection roles
to F before their respective gathers and leaves each delivery role there until
its injection. Pivot p=648 already resides at F at retirement cut 39225.

The one changed paid path is main role 198 in interval [41607,41668]. Original
MOVE 41667 goes from frame 597, basis [82], to frame 207, basis
[2,5,8,17,33,65,129,257], rank seven. Replace it by 597→120 at cut 41607 and
120→207 at cut 41668. The exact inclusions are checked; these ranks are four
and three. The injection at 41668 occurs before departure. No other source
contact moves across a read or write.

The seven neutral paths and this one paid path are all source-bound. Each
gather/injection is checked against its actual frame after retiming. Scalar
coefficients and roles outside the explicit split remain those of the source,
with the required successor and owned-label relabeling.

## The two-buffer identity

Take p=648 and the fresh arbitrary public input n=1493 at F, value z. The helper
boundary matrix G is simply the swap of roles 648 and 1449: its row p is c and
`G d=e_p`. The credited elementary basis algorithm emits four instructions for
G, with only unit coefficients. Apply G inverse at U. The gathered functional
c then equals the original independent input x_p.

Initialize owned A at F before the first gather. At cut 39225, A=x_p and the
current value of p is some v. Initialize owned B=0 and execute

```
B += n;  B -= A;
n += p;  n -= A;  n -= B;
p += A;  p -= n.
```

The result is B=z−x_p, n=v and p=x_p. Clear A under the inherited owned-erasure
contract; retire p at F. Continue every old p occurrence on n instead, shifting
all old owned labels by one. At the six declared later cuts, add the listed
coefficient times B to the designated role in F. Their full final response is
`d(z−x_p)`. Clear B after the last injection.

Finish with G at V, using n as the successor of p. The source helper map is the
identity, and G maps the added response to `e_p(z−x_p)`. Thus n returns z; retired
p already holds x_p; all other public outputs and the full main operator are
unchanged. All owned rows are cleared. Both complete operator directions are
also checked by separate exact executions.

The two buffers are explicit owned storage. Neither arbitrary public input is
initialized or discarded. This argument does not require an invertible local
map on public cut coordinates, a simultaneous middle pairing, or an additional
opcode. It does not claim that two buffers are minimal.

## Accounting and scope

The new native delta is ΔP={3:+1,4:+1,7:−1} and ΔT={4:+1,5:+1,9:−1}. Both rank
masses are unchanged. There are 1,494 public fields and 1,094 helpers, 55 owned
labels and 58 owned lifetimes. Peak owned stock stays 44; owned rise mass stays
56. The 74,655 instructions add 21 ADDs, two SCALEs, one MOVE, two INITs and two
CLEARs. All extra lifetimes and scalar services are charged.

The unchanged 17-stage caller has 110,434 paid positions, 22,342 productive
fields, surplus 1,424 and zero empty-root credit. Both directed price engines
nominate κ=.003643180671645, an increase of .000000221652614 over #7140.
`APPLICATION.md` and `VALIDATION.md` record the actual full replay and its
status; the coefficient identity alone does not establish those checks.

The freshly derived grid remains 1125/F25. Exact lifecycle adapters bind
(lifetimes, peak, labels) to (58,44,55) in both precision paths. They retain the
lifecycle assertion and reject an extra uncharged lifetime. No frozen source
bytes are edited. All caller storage, grid, envelopes, ordinary and compiler
costs are recomputed for this word.

The search stopped at its first positive after 715 of 7,667 individually
affordable paths. This is not a temporal optimum or an exclusion of remaining
paths. Earlier ToikY chart-120 work is retained through the predecessor chain;
this package does not claim discovery of the chart. Credit Ali Romman,
CubeJerry, Matarener, Rohan Arun, ToikY and all retained authors.

## Open next questions

1. Independently replay the two simple boundary-vector equations, all typed
   observation times, and the complete new storage/caller application.
2. After a fresh upstream/overlap checkpoint, test an uncovered causal domain
   on this changed source, with every path and owned cost included.

The five inherited framework assumptions remain: native_all_columns,
owned_erasure, compiler, precision_tape and analytic_recovery. Human/formal
acceptance, maintainer admission and compiled top-level execution remain open.
Prepared for dillona with substantial OpenAI Codex assistance; no subagents.
Apache-2.0.
