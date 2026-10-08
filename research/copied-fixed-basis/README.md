# Copied retained centers with fixed local bases

The conditional witness is **κ = 242889/6250000000 = 3.886224e-5**.
Its bit saving is `19432631/500000000000`; the inherited complex saving
is `717/10^7`. Both exact moments, all 47 strict assembly conditions and
seven margins pass. The bit moment gap exceeds `6.3667e-15`, and the final
assembly gap exceeds `5.1804e-14`. This is not formal verification.

The bit graph is PR36's actual base-two `(25,23)` graph, with original
envelopes and original oriented matching. Both local bases are `I+J`.
The data profile is **26 singletons +21+481**: the generic second 15-block
is not used. Actual controlled permutations and both 47-edge incidence
trees prove compatibility with the complete local transition profiles.
PR36's copied schedule, paid endpoint correction, complete role volumes,
arbitrary scratch restoration, semantic guard and `p^2000` stock remain.

```sh
make copied-fixed-check
make copied-fixed-producer
make verify
```

The producer rebuilds both scalar DAGs, original label dependencies,
matching and every local profile in temporary storage. C++17 and Python's
standard library suffice. Exact rank-two minors use one prime; source
growth and core changes use three Lucas–Lehmer-certified primes with
strict dimension-specific bounds. No sampled-zero claim is used.
The arithmetic checker checks pinned sources, both trees, every physical
class, both moments, semantic row stock, assembly and four negative controls.
The complete inherited `make verify` run is separate from these focused checks.

[Proof](../../notes/copied-fixed-basis.tex), [certificate](certificate.json),
and [source manifest](SOURCE.json). The generated patch replaces the pinned
PR36 `notes/copied-centers-note.tex`; apply independently of historical
replacement patches. No PDF is generated. Analytic, recovery, prime-existence,
fixed-tape and constructive-setup thresholds remain eventual dependencies.

Credit icekylinx PR36/32 for copied centers, fixed projectors, local profiler,
complex graph and assembly; Dominik Scholz PR35/33 for exact fixed-basis and
dimension adaptations; Zhihao Chen PR29/21/23; Rohan Arun PR31; Paureel/Aurel
Prosz; Swapnil Jain; RaD/hipotures and all authors in NOTICE. The new composition
is by Dominik Scholz with substantial OpenAI GPT-6 Astra/Codex assistance.
Inherited Apache-2.0 and CC0 notices and historical AI disclosures remain.
