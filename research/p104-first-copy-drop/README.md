# P104's first COPY drop with its complete frame puncture preserved

**Research note / scoped structural threshold. No new kappa.**

Every one of the 7,168 mixed frame-pair decoders retains all eight COPY
terms at rank seven until **22 additional ports are deleted**. The first
drop is therefore **38 total punctures**, when all sixteen original frame
lines remain punctured. This differs from PR1020's unconstrained 26-puncture
root-pair threshold.

The support-label span can fall at 20 additional deletions, but that alone
does not reduce COPY rank. The missing condition is loss of dimension after
quotienting by the partner's radical. The package proves this exact criterion
and exhausts the corresponding 127 hyperplane cuts per side.

The attaining decoder uses **55 copies on 82 ports**, versus P104's **56 on
104**. Its COPY ratio is worse. The result closes this family's first-drop
boundary, without proposing a stronger supplier or claiming an optimum for
the aggregate COPY cost beyond the boundary.

## Reproduce

Python 3.10+ and the standard library, from the repository root:

```sh
python3 -I -O -B research/p104-first-copy-drop/test_package.py
```

Expected markers:

```
PASS_P104_FIRST_COPY_DROP frames=896 decoders=7168 terms=28672 extra_punctures=22 total_punctures=38 span_only=20 copies=55 ports=82 no_new_kappa
PASS_P104_FIRST_COPY_DROP_PACKAGE regeneration=PASS relocation=PASS controls=4
```

The package test replays the independent verifier, regenerates the exact
certificate through the pinned predecessor model in a non-optimized child,
checks read-only relocation, and runs real corruption/occupied-output controls.
The standalone independent verifier also works under optimized Python:

```sh
python3 -I -O -B research/p104-first-copy-drop/verify.py
```

To regenerate, use an unused output path and keep predecessor assertions
enabled:

```sh
python3 -I -B research/p104-first-copy-drop/census.py /tmp/p104-copy-drop-new.json
```

## Evidence and scope

CERTIFICATE.json contains all 896 frame records, the uniform 28,672-term
threshold histogram, the attaining decoder/puncture, and the span-only
counterexample. PROOF.md explains why hyperplane cuts cover arbitrary added
punctures. SOURCES.json pins original source bytes at exact Git commits.

The primary checks 7,282,688 quotient-cut incidences. The independent column-
code implementation constructs the model and all dual decoders from scratch;
it imports neither primary nor predecessor code. It checks 6,724 all-pairs
coefficients and 25 mathematical controls, including all 22 individual port
restorations. Both checkers are by the same AI-assisted contributor; this is
not external human review.

Base: `c0e3631dc24e3c24a861f7d3d79e0608481cccec`; OS-random seed **46**,
structural decoder track. The accepted PR1094 conditional kappa at this base
is `836330098538459/500000000000000000`. This isolated addition changes no
selected record, original package, frozen source or upstream input.

Covered: fixed F0, the complete 896-frame/7,168-decoder family, arbitrary extra
port deletions while retaining the original sixteen-line puncture, and the
exact all-pairs label-pairing cost. Other normal sets, masked/overcomplete
decoders, different COPY endpoints and fully paid hosting remain outside
scope. No physical compiler, full supplier replay, measured runtime, complete
theorem or new kappa is claimed.

PR968 supplies the model and family; PR1020 the distinct unconstrained
threshold; PR1077 extends the generic eight-term floor over complex
coefficients; PR1125 studies asynchronous endpoint delivery. See NOTICE.md
for preserved credit and assistance disclosure. Prepared by **Cinna Davis
(@1337isnot1337)** with substantial **OpenAI Codex assistance**; Apache-2.0.
