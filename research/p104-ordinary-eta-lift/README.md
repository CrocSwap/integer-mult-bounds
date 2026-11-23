# An ordinary η lift, with a separate 25-bit setup bound

For the unchanged binary word and finite debit in ToikY's [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`, a three-stage ordinary component with `η=1/256` and heights `(8192,106000,1681001)` books

```
q = 0.003900000000000005 > 0.0039.
```

All three directed stage margins are strict. The previous third height fails with the first two fixed. The old height cap and the old `η=0.0039` also fail. This is a **conditional ordinary-component result**, not a new complete multiplier or a new κ: the unchanged Gaussian trial itself is below `q`, and its priced margin rejects the combined 0.0039 target. The five inherited source premises, complete physical realization, and independent external review retain their prior status. See [the ordinary proof](PROOF.md) and [exact receipt](RESULT.json).

The separately scoped [setup proof](SETUP-PROOF.md) extends the source's indexed-action and serial-arithmetic argument to all seven entry/terminal ordinary and Gaussian heights in `1024 ≤ H < 2^25`, subject to its fixed-word, fixed-stage-count and 128-bit scalar-encoding hypotheses. Charging new carrier/parameter work explicitly still gives an exact fixed-installation bound below `2^228` transitions. This does not price native openings, the recurring caller, activation, precision, or a portable execution trace. The [setup receipt](SETUP-RESULT.json) records finite constructor and directory-census controls; those are supporting tests of the implementation, not a proof for all profiles.

The complete signed price at #8072's **old** κ `0.003898214283192`, using this larger ordinary profile, has `log₂ C ≤ 682472491`; #8072 reported `318292011`. These are different resource classes. The receipt verifies signed arithmetic under the inherited clock premises, but no full astronomical installation or new physical crossover is claimed.

## Reproduce

Use Git and CPython 3.12. From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-ordinary-eta-lift
```

The registered commands independently reconstruct the pinned source in private temporary directories, compare the ordinary receipt, rerun four fixed-constructor/census profiles, and exercise explicit source-corruption, strict-boundary and Gaussian failure controls. The setup pass emits four temporary directory files of about 36 MB each; no physical product, WASI run, or network access is required. Standalone equivalents, run inside this package, are:

```sh
python3.12 -I -B verify.py ordinary
python3.12 -I -B verify.py setup
python3.12 -I -B verify.py controls
```

The saved directory hashes are observations of a CPython run, not cross-environment identities: replay compares the mathematical and profile fields, checks each new census against the stated size bounds, and reports the observed hashes. The compressed predecessor archive is an immutable input and is checked exactly. `original/` is needed to reconstruct the source for these tests; it is not an assertion that the entire predecessor proof has been independently verified.

The offline replay compares the retained source bytes to recorded SHA-256 and Git-blob pins. A stored string naming a commit is not proof that the commit contains those bytes. When a local checkout contains the exact #8072 head, compare its Git objects without replacement refs:

```sh
python3.12 -I -B verify.py source-history /path/to/integer-mult-bounds
```

This optional check requires the head and its trees/blobs to be locally available; it does not fetch or claim source-history completeness. The retained files are also identified at the [exact #8072 source tree](https://github.com/CrocSwap/integer-mult-bounds/tree/75f7e1c44f48c43983016bcf8878c4d9e5e87c62/research/p104-weighted-capped-allocation-490950). A separate checkout can try fetching `refs/pull/8072/head` from the canonical CrocSwap remote; that ref can move, so a fetch is not a substitute for checking the pinned commit and bytes. If the exact object is unavailable, report the gap rather than silently changing the pin. For the recorded file-to-blob mapping and #8057 archive identity, see [source pins](original/source-pins.json), [the peer manifest](original/PEER-SOURCE.json), and [SOURCES.json](SOURCES.json).

## Open next questions

1. Can an independently funded Gaussian supplier cover `q` with the whole signed budget? Start with a source-bound candidate and exact positive-debit and owner-return checks; the unchanged supplier is already a strict negative control.
2. Can the enlarged profile be installed and replayed in the complete physical and precision model? Start by binding its entry/terminal paths, all five inherited premises, supplier openings and costs. The present finite fixtures do not execute the astronomical target geometry.
3. Can a new portable producer trace certify an enlarged profile? Start by replacing the old profile assertions in the inherited WASI producer and measuring the whole bounded trace. The original `2^113` result applies to its own fixed profile.

## Credit

ToikY supplied the exact #8072 retune and the preceding #8066–#8071 price and allocation work. Ali Romman supplied the #8057 signed source and #8055 setup proof; SYLforge supplied the #8052 K7 word. The inherited [notice](original/NOTICE.md), nested archive notices and [Apache-2.0 license](LICENSE) are retained. This ordinary analysis, setup extension, source controls and packaging received substantial OpenAI Codex assistance.
