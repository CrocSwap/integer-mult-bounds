# Executed bounded verification

Environment: Python3.12.14, Linux, standard library only. No source or
scientific input outside the package is needed by the direct commands.

```sh
python3 -I -W error -B verify.py --write
python3 -O -I -W error -B verify.py
```

The ordinary run generated `RESULT.json`; the optimized run checks its
exact normalized JSON contents. Expected marker:
`PASS_OLD_SOURCE_OWNED_ZERO`. Input and source schema authentication is
included. No Python assertion supplies a necessary acceptance gate.

| Old body bits | Old context bits | HOME body bits | Producer steps | Entry |
|---:|---:|---:|---:|---|
|9216|127|2056|993891|Fresh blank owned window|
|18432|131|5130|1956674|Inactive contents correlated with source|
|36864|131|8204|3952983|Fresh; nontrivial prefix and spectators|
|49152|533|12700|2873984|Fresh; two rows, r=2, long cutoff|
|70656|2187|22542|7454551|Inactive; b=22, long ignored descriptor field|

The graph has4803 locations and43 tapes. Its actual-hardware table SHA256 is
`d3de6dd3ff8ec98822356c2aa9709e9e9ebf6f53c86c7b6a4a6b21c9c6ad4727`.
The source/abstract table SHA256 is
`22f44ff9799be701b6e9199529412decf23dc375e9ff7a979ba7918100b15d66`.

The separate nonzero live CLEAR entry has F=3080, with3072 DATA1 bits,
and completes in24650 transitions with the whole body raw0. This is a
supplied valid CLEAR boundary, not an uncharged native operation inserted
between producer and retirement.

The receipt records15 malformed-format, geometry, target-extent, alias and
mutation controls. Every complete success checks all old source/context
contents, output, heads, private bodies, markers, exteriors and retained
earlier history. All complete packets have f=1. No full f>1 packet, complete
selected caller, real native child or recursive multiplication run is claimed.

Independent orchestrator verification is recorded separately when available;
the author's optimized rerun is regression, not an independent proof.
