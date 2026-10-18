# Strict payload comparison with large JSON integers

This opt-in successor fixes one portability failure in commdata2338's [PR2040 strict comparator](../strict-replay-payload-comparison/README.md): valid JSON integers exceed Python's process-wide decimal conversion limit. It preserves the frozen predecessor and its other comparison rules. No supplier execution or new kappa is claimed.

With `PYTHONINTMAXSTRDIGITS=4300`, comparing `{"n":<4301 digits>}` to a whitespace-only reformat returns `invalid` in the predecessor. With limit `0`, it returns `json-format`. Limit `640` reproduces the same problem at 641 digits. These are synthetic exact-number fixtures; this contribution does not claim the retained 105-file corpus contains such an integer or that a supplier certificate is invalid.

## Change and evidence

[compare.py](compare.py) authenticates and compiles the exact retained comparator source, then replaces only its JSON parser and diagnostic hook in a private module. Integer tokens pass through `int(Decimal(token))`: the JSON lexer still enforces integer grammar, the value remains an `int`, and decimal arithmetic precision does not round it. Duplicate-key checks, exact decimal parsing and nonfinite rejection remain in place. The code never changes `sys.set_int_max_str_digits` or the decimal context.

A second occurrence of the same limit affects `repr` when an unequal large integer is reported. The diagnostic hook preserves the typed difference path and uses a bounded sign/bit-length/binary-SHA256 summary when that conversion fails. **Equality still compares complete exact values; these summaries never decide acceptance.** Integer/decimal/Boolean distinctions, unknown fields, array order, root mapping and explicit timing validation retain the predecessor's rules.

[verify.py](verify.py) runs the retained complete audit twice, with the original comparator and this successor. Both full receipts must equal the committed predecessor receipt: all 105 corpus files, 39 adverse mutations and 22 deleted-timing controls. It also runs the nine unchanged predecessor test groups against the successor API (their small CLI test still launches the retained CLI), plus eight new control groups:

- Exact signed integers at 1, 639, 640, 641, 4,299, 4,300, 4,301 and 10,000 digits, checked by independent digit accumulation with decimal precision 2 and rounding traps.
- Identical, reformatted and recompressed payloads; complete one-digit, sign, type and container changes with typed diagnostics.
- Duplicate keys, malformed integer grammar, nonfinite constants, declared timing paths, relocation and pinned-source mutation.
- Real CLI processes under limits 0, 640 and 4,300, with assertions enabled and optimized, from an unrelated directory containing spaces. A changed digit must exit 1; an equivalent reformat must exit 0.

All external inputs have exact Git blob and SHA256 pins in [SOURCES.json](SOURCES.json). Compiled predecessor/audit bytes are the same bytes authenticated; cached bytecode is not used for them. Immutable source/container checks remain byte-exact. The package replay needs no network and writes no tracked outputs.

## Reproduce

From the repository root, Python 3.12 standard library:

```sh
python3.12 -B scripts/research_package.py --package research/strict-payload-large-integers
```

For direct controls or the standalone comparator:

```sh
python3.12 -I -B research/strict-payload-large-integers/verify.py
python3.12 -I -O -B research/strict-payload-large-integers/test_compare.py
python3.12 -B research/strict-payload-large-integers/compare.py REF_DIR RUN_DIR
```

The CLI retains the predecessor's root/timing/output options. Exit 0 means equivalent generated payloads under the explicit policy; exit 1 means a difference/invalid payload; configuration errors exit 2. Source authentication failures also fail before comparison. Use generated-payload equivalence only for generated evidence, never to relax immutable source pins.

## Validation

On macOS arm64, the registered CPython 3.12.14 replay passed the complete retained audit, **17 test groups**, and the separate **eight optimized groups**. The new eight groups also passed on CPython 3.11.15, 3.13.12 and optimized 3.14.7. Three deliberately broken successors (default integer parser, integer-to-decimal retagging, and unrepaired diagnostics) failed the same controls. An optimized 3.14.7 Git-free read-only export passed the complete audit and 17 tests, with every exported file unchanged. The selected baseline source-binding check passed.

Before submission, canonical main still matched the task base. The overlap refresh covered 728 open PRs at 22:20 UTC on October 15, 2026. Discussion refresh hit an API rate limit and retained the complete 1,440-record snapshot from 22:15 UTC. No matching repair was identified; these searches do not prove novelty. Exact freshness and limitations are in TASK.json.

## Scope and credit

Base canonical main `df801f6da7b9aa8e01bd35decde7b1b1d45eec08`, priority revision 5. Task `portable-replay`, refined to the integer-limit defect; chooser nonce `28c18deb21d7b93b8314fb2d7044018f`. The precise task, overlap and stop rule are in [TASK.json](TASK.json). Canonical investigation: [Discussion 2800](https://github.com/CrocSwap/integer-mult-bounds/discussions/2800).

PR2040 at `d31c1418c0c23994d1444dbd9d356b9a8238fd5e` retains credit for the strict comparator, corpus and 39-case audit. Josie Elliston's PR1824 supplied the portability predecessor; Maxime Fleury and Antoine Olivier established the gzip convention. Rohan Arun, Jeremy Kothe, Douglas Colkitt and the retained supplier/archive lineage keep their original attribution. PR2693's paired traversal optimization and PR2344's Windows roots are separate pending work; neither is imported here.

This is a portability repair, not a performance claim, mathematical verification, source-authentication replacement or supplier replay. Integers are limited by available resources; untrusted-input resource hardening and arbitrary nesting are outside scope. The added Decimal conversion may cost more for ordinary integer tokens. No Linux/Windows execution, hosted CI or independent human review is claimed. Existing all-size, physical, hosting, precision and analytic obligations remain open.

Prepared for Arham Tahir with substantial OpenAI Codex assistance in design, implementation, testing and writing. Self-reviewed only. Apache-2.0; predecessor bytes and notices remain unchanged.

## Open next questions

Should a future generated-payload wrapper adopt this parser? First review that caller's input-size/resource policy and run its existing controls through this explicit successor. Adoption is outside this scoped contribution; there is no new mathematical blocker. Structured details are in TASK.json.
