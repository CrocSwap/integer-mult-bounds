# Actual convolution owners and one returned native window

This source-bound lemma joins the original #7849 direct-circulant caller's
complete-field lifetimes to the native requested-grid interface published
in #8093 at `780e96d8c149690df0f06661e2b9f94eb91737fe`.

The literal convolution needs at most seven complete outer field slots.
Its three transforms retain respectively three, four and six fields at
native calls, including both operands still held by `multiply`. Opposite
conjugation and final public conversion reach seven. One serial conversion
window suffices; it is cleared across its full historical extent between
calls. The conditional historical join adds seven field extents, that
window, and the separate historical maximum of each native private tape.

[PROOF.md](PROOF.md) gives the universal source-reference argument, marked
field layout, full-scan invoice, exact native return contract and remaining
obligations. The native service must return into the held complete window,
restore dirty borrowed owners, retire private frames and leave no escaping
mutable owner. Those requirements remain explicit assumptions.

The contribution closes the **outer caller lifetime and window-composition
implication**. It does not implement or admit the accelerated native service,
prove its private extent bounds, discharge canonical owned-erasure, or cover
the later integer recovery arrays/accumulator in `multiply`. The returned
outer result remains owned by the caller; another public call needs a paid
transfer/retirement rule before reusing those slots. There is no new kappa.

## Evidence and reproduction

Standard-library CPython 3.12, from this directory:

```sh
python3 -B check.py
python3 -O -B check.py
```

The 22 literal-method executions cover 528 native calls, 483,696 complete
native record visits, 4,868 total field records, sizes through 2,048 records,
and pack widths 1,2,3,4,5,8. Every input component is nonzero, including
physical holes. Numeric endpoints match the unmodified source. The tables
are diagnostic legal programs, not a Fourier-coefficient compiler replay.
Normal and optimized receipts are byte-identical.

Ten controls address too few slots, root aliasing, omitted caller roots,
reusing a returned outer result, an expired native window, an unowned native
return, an incomplete field, separate historical maxima, old dirty tails
and source corruption. The historical/tail cases are explicit accounting
counterexamples; other ownership controls execute the instrumented caller
or window interface. `__del__` only observes diagnostic reference death;
the proof constructs explicit physical retirement at the source's last use.
The exact sequential normalized-H oracle is not an accelerated supplier.

## Overlap, credit and open next question

Prior numerical-arena work already proves per-arena historical maxima and
qualifies capacity replay noncircularly. Mixed-rank FRAMES already provides
adjacent physical frames and complete owner returns. The full-native-domain
adapter already binds a local Full word to a rounded Gaussian service.
These results are credited rather than recast as new.

The new component is the actual #7849 convolution's simultaneous owners,
its source-specific seven-slot construction, and its join to the new
complete requested-grid window. #8091's retimed binary/ordinary storage
closures concern a different caller. Live #8093 and focused PR searches
were refreshed on 2026-11-23; coverage is partial and is not a global novelty
claim. Sources and scope are recorded in TASK.md and SOURCES.json.

The next useful question is to establish native return contract N and the
per-tape extent vector for one actual accelerated global invocation. Start
at argument transfer, final held-result installation and full private-frame
retirement. Internal realization, genuine stock and physical bounds are
still needed. No complete multiplier-space theorem follows from this alone.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Ali Romman, Ross Richardson, the retained mixed-rank/native owners,
earlier #8093 contributors and the common-grid authors. Apache-2.0; source
notices remain unchanged. Independent human or kernel acceptance is unclaimed.
