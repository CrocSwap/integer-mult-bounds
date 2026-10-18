# Eisenstein E8: a bound for nonlinear fixed-support messages

**Research note; no new kappa or physical supplier.** On the 40 Eisenstein
E8 lines, zero-error messages with b independent bits demanded per port
cost at least **22b Eisenstein pairing-rank units / 44b rational units**,
provided each q-bit message is charged q times its source/reader pairing
rank and charges add. Encoding and decoding may be nonlinear. Unequal
demands satisfy

    C >= max(ceil(11 sum_t b_t / 20), max_clique sum_(t in clique) b_t).

The abstract equal-width optimum remains between 22b and 40b. The bound
does not exclude three stages. Nonlinear physical per-bit pricing remains
an explicit assumption, not a consequence proved here.

This composes Jonathan Lam's concurrent [#798](https://github.com/CrocSwap/integer-mult-bounds/pull/798)
scalar Eisenstein certificate with Alexander Templeton's
[#785](https://github.com/CrocSwap/integer-mult-bounds/pull/785) nonlinear
transcript method for the different Hurwitz geometry. The new coverage is
nonlinear/block messages on Eisenstein E8, arbitrary unequal demands, a
concentration bound and concrete assumption controls. Our initial scalar
experiment was superseded by #798 and is credited accordingly.

## Reproduce

From the repository root, Python 3.10+ with its standard library:

```sh
python3 -B research/eisenstein-message-copy-bound/verify.py
```

Expected:

```text
PASS_EISENSTEIN_MESSAGE_BOUND: 22b; unequal demands 11/20 plus clique bounds; 298378 flat pairs; 12 rejection controls; no new kappa
```

The replay verifies pinned sources, the exact geometry, all 772 flats,
298,378 flat pairs, 30,880 one-line extensions and all 2,970 maximal
cliques. It exhausts the nonlinear 12-port example on 4,096 inputs, the
unequal-width example on 64 inputs and an intentionally excluded
side-information example on 128 inputs. Twelve rejection controls run by
default, including underpriced width and incorrect nonlinear decoding.
The generated result must equal [certificate.json](certificate.json).
`--output NEW_FILE` writes a receipt only after successful verification and
refuses to overwrite existing files.

An arithmetic implementation that imports neither checker module verifies
every geometric inequality using modular rank witnesses, and exact
Fraction ranks for all flat bases and the 241 tight positive-rank witnesses:

```sh
python3 -B research/eisenstein-message-copy-bound/crosscheck.py
```

See [PROOF.md](PROOF.md) for the all-width argument, model and remaining
obligations; [VALIDATION.md](VALIDATION.md) for executed checks; and
[CLAIM.md](CLAIM.md) for selection, coverage and the single pivot.

## Pins and scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. OS-random assignment seed
**41**, structural decoder research. Runtime dependencies: Python standard
library only; source pins and upstream contribution heads are recorded in
[SOURCES.json](SOURCES.json). Two predecessor proofs are retained verbatim
under `sources/`, with their original attribution.

The result assumes fixed supports and widths, independent inputs, exact
deterministic decoding and only orthogonal free side information. It does
not cover adaptive relays, average-cost coding, cheaper physical sharing
across bits or rational sub-line supports. Finite checks are not a formal
proof of the full multiplication theorem.

Prepared by **Michael Fischler (@shiftybitshiftr)** with substantial
**OpenAI Codex assistance**. No independent human review is claimed.
Apache-2.0; see [NOTICE.md](NOTICE.md).
