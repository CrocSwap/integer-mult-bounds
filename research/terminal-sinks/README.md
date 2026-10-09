# Terminal sinks on the paired-cube complex word

This applies the terminal-sink lemma of PR #166 by jamesyc (closed by its author) to the complex word and checks it
independently here. `sinks_gate.py`'s own frame scans, replay and controls carry the soundness argument; they do
not use #166's checker. Gate, audit and integration by eumemic with Anthropic Claude assistance.

## The substitution

A sink is an auxiliary role `z` with these properties:

- it starts at frame 0 with no gauge: no source injection, not a donor or recipient;
- it is written only as a destination, `z <- z + b*a`, never as a control, and never in phase one;
- its write frames are nested, `0 <= F_1 <= ... <= F_k <= U`, where `U` is the frame of its single side root
  `y_t += c*z` (`t` in `T`);
- it has a pivot `p` in `T` with no deferred old-value read of `p` between the phase cut and `z`'s last write.

The sink is deleted and replaced by three steps:

1. at the phase cut, after the copied-centre scatter: `y_t -= y_p` for `t` in `T - p`, at frame 0;
2. at each original write time: `y_p += c*b*a`, at frame `F_i`;
3. right after the last write: `y_t += y_p` for `t` in `T - p`, at frame `U`.

Each sink removes one physical register and, per core, one child `r = rank U` and one child `h - r`. The deficit is
unchanged.

## Checks (`sinks_gate.py`)

1. The frozen layer passes #161's checker (`scripts/paired_cube_physical.py`, unchanged) and matches its frozen
   record.
2. Every condition above is recomputed for every sink from the regenerated word, the layer and the read schedule.
   Target groups of different sinks are disjoint.
3. The literal stage word has every frame step nested, forward and literally reflected. This covers X ports,
   Y ports and physical slots: time-0 and deferred reads, injections, ops, the centre scatter, side-root reads,
   K on the sources and full-frame inverses.
4. The unsubstituted word's literal per-stage histogram equals #161's record over three stages. The substituted
   word's histogram is that minus `[r]` and `[h - r]` per sink.
5. A dirty-scratch replay mod 2^61-1 gives `(X, Y + X, Z)` forward and `(X - Y, Y, Z)` reflected.
6. Four controls are rejected:
   - a sandwich raised before the centre scatter;
   - an omitted post-shear;
   - an uncomplemented reflected pivot write;
   - a post-shear moved after its pivot's first correction.

## Results (p11N1b_TB31: TMOD TB31 triple module, the depth-4 maximum-weight layer)

| | W | complex AC |
|---|---|---|
| layer | 13,936 | 6479443/1e10 = 6.479443e-4 |
| + 42 sinks | 13,894 | 6493335/1e10 = 6.493335e-4 (+0.214%) |

On p11N1_Qb01 the same rule gives 42 sinks and 6466544/1e10 -> 6480380/1e10.

**Why only 42.** Only all-eight (disjoint) roots are sinks here. Of the 165 roots, 123 have retained producer
consumers, 15 are source-injection roles, and 15 are written in phase one; some roots fail more than one test.
The face0 sinks that meet the conditions fail the frame scan: the post-shear at their rank-19 `U` raises target
registers above later rank-18 reads, so the target chains stop nesting.

## Use

    python3 research/terminal-sinks/sinks_gate.py           # check against certificates/paired-cube-sinks-input.json
    python3 research/terminal-sinks/sinks_gate.py --write   # refreeze
    python3 research/terminal-sinks/sinks_gate.py --tree=T --work=W --layer=L --sinks=S.json [--out=X.json]

`sinks.json` is `{"sinks": [[role, pivot], ...]}`. When it is present, `scripts/paired_cube_network.py` prices the
complex profile from `checked_sinks_record()` instead of #161's record.
