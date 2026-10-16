# Exact Windows input roles for the selected final-output comparator

**Scoped verifier engineering; constructed relocation fixtures, no supplier
execution and no new kappa.** This adds an opt-in adapter for the six input
roles in Adam Gall's [PR2101](https://github.com/CrocSwap/integer-mult-bounds/pull/2101)
complete output comparison. All five required predecessor files are retained
byte-for-byte at `a247ef876e50bf3a7d890c7c1f9b409576674d7d` and authenticated
before import.

PR2101's `compare_outputs.prepare` requires absolute POSIX roots and constructs
input keys with `/`. A correctly bound constructed Windows receipt therefore
fails with `root must be an absolute POSIX path`. Its output inventory already
uses POSIX relative names; the failure is confined to the six absolute input
keys. PR2101 explicitly did not claim a Windows execution result.

## Contract and implementation

`compare_roles.py` accepts a typed root `{style, path}` for each of `work` and
`local`. Supported styles are `posix` and `windows-drive`. A Windows root must
use its exact ordinary absolute drive spelling and backslashes. UNC, device,
extended-length, mixed-separator, relative, dot-component, trailing-dot/space,
reserved-device and alternate-data-stream spellings reject. These restrictions
are a bounded lexical input contract, not a Windows filesystem equivalence
algorithm. POSIX backslashes remain literal filename characters.

For each side, the adapter:

1. Requires the unchanged complete 105-file inventory and three external input
   byte strings. It parses the independent receipt with the predecessor's
   duplicate-key-aware, exact-number parser.
2. Builds the six expected native paths from the pinned role suffixes. Each
   exact key must name its correct actual same-side input digest. Missing,
   extra, stale, swapped and alternatively spelled keys reject. Windows keys
   which collide under `casefold` reject conservatively; case is never folded
   to accept a receipt.
3. Rewrites **only** those six authenticated keys in a copy of
   `INDEPENDENT-T16.json` to fixed synthetic POSIX roots. No other string, key,
   digest or field is rewritten. Receipt paths are never followed for I/O.
4. Delegates to PR2101's unchanged complete comparator, which authenticates the
   six edges again, both invoice edges and all 22 log references; it compares
   all 105 outputs with its original exact typed policy. The only inherited
   quotients are the two authenticated invoice links, six role keys and 22
   fresh timing fields. All other fields, including historical times, remain
   covered. The coupled outer-log validator is exposed unchanged.

For a fixed validated context, construction gives six distinct expected keys.
Exact dictionary equality binds each key to its input digest before the
injective six-key translation. Thus the translation cannot erase a difference
in role assignment or any field outside that dictionary. This is the narrow
reason for the adapter; replacing every backslash in a receipt would not have
this property. The proof argument is source-level and the tests are finite,
not a formal verification of either comparator.

Example use after loading this module:

```python
reference_context = {
    "work": {"style": "posix", "path": "/reviewed/run"},
    "local": {"style": "posix", "path": "/reviewed/local"},
    "external": reference_input_bytes,
}
candidate_context = {
    "work": {"style": "windows-drive", "path": r"C:\replay\candidate"},
    "local": {"style": "windows-drive", "path": r"C:\replay\local"},
    "external": candidate_input_bytes,
}
report = compare_roles.compare(reference_files, candidate_files,
                               reference_context, candidate_context)
if not report["equivalent"]:
    raise ValueError("complete output differs")
if (compare_roles.outer_log(reference_log, reference_files) !=
        compare_roles.outer_log(candidate_log, candidate_files)):
    raise ValueError("coupled outer log differs")
```

`*_files` must contain the entire strict output directory, including all eleven
inner logs. The caller must authenticate its reference and supply the actual
three byte strings under `local-word`, `local-replay`, and `owners`. Merely
passing a trusted-looking root does not authenticate a supplier run. The test
fixture demonstrates the required archive and receipt bindings.

## Verification and evidence

```sh
python3.12 -I -B research/selected-windows-role-adapter/verify.py
python3.12 scripts/research_package.py --package research/selected-windows-role-adapter --check-only
python3.12 scripts/research_package.py --package research/selected-windows-role-adapter
```

The registered replay passed normally and under `-O` in 63.81 seconds total:
**6 positive controls and 176 rejected faults per execution**. All new guards
use explicit exceptions. `RESULT.json` lists every control. The fixture
authenticates both immutable archives, the ten PR1042 local provider inputs,
the PR1094 result/assembly/replay receipts and the selected owners. Its 105
strict outputs and thirteen-line outer log are the reviewed archived run.

Six constructed positives cover unchanged POSIX inputs, Windows drive paths
with Japanese characters and spaces, literal POSIX backslashes, an identical
Windows pair, Windows relocation composed with invoice reformatting and all
22 fresh timing changes, and its coupled outer log. Failure controls cover
all six digest/key omissions and aliases, all fifteen distinct role swaps,
all 105 output omissions, an extra output, fourteen unsupported root forms,
a six-key/five-Windows-identity collision, duplicate JSON keys, identical stale
inputs, scientific/type and raw-link changes, an unlisted path-like string,
an uncoupled log, and five immutable predecessor source mutations.

Executed locally on native Windows with CPython 3.12.11. Native `Path` spelling
also agrees for the six constructed Windows keys. This observation is path
construction evidence, **not fresh Windows supplier output**. A separate Codex
agent reviewed the adapter, independently checked unchanged POSIX report
equality, non-mutation and the case-collision fixture, and identified a test
gap that was fixed: malformed roots are now tested directly instead of being
rejected incidentally by a stale receipt key. No independent human review or
hosted-CI pass is claimed.

## Open next questions

Apply this adapter to the separate fresh Windows successor replay coordinated
in [Discussion2333](https://github.com/CrocSwap/integer-mult-bounds/discussions/2333)
and published as [PR2336](https://github.com/CrocSwap/integer-mult-bounds/pull/2336).
Supply its exact roots and three actual external inputs, compare every output,
and validate the outer log. Stop on an unclassified scientific/log mismatch;
do not broaden normalization just to make a run pass. PR2336 reports eleven
CRLF-only inner-log differences. This adapter retains PR2101's byte-exact inner
log policy, so a full Windows comparison needs a separately reviewed log
policy if those differences are present. PR2336's execution is credited as a
concurrent reported result, not reproduced here. The structured question is in
`TASK.json`. UNC/extended-length paths, filesystem alias equivalence, full cold
ancestry, supplier mathematics and inherited all-size obligations are outside
this package.

## Attribution and coordination

Current main base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision4. The one-shot picker chose verifier engineering, nonce
`4727282e9476c909011340ff0b783e8c`. Live overlap found #2333 already taking
PR2316's supplier-wrapper handoff, so this scope was narrowed before substantive
implementation. The canonical claim is in
[Discussion1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-18941855).

Credit Adam Gall (PR2101 full comparison and PR2059 invoice binding),
commdata2338 (PR2040 strict typed comparison), Josie Elliston (PR1824 selected
final-stage portability), josecarlosgonzalezroque-design (PR2316 Windows
manifest audit), and Maxime Fleury/Antoine Olivier (payload/container rule).
The supplier and selected evidence retain Rohan Arun, Jeremy Kothe, Hao Yan,
Douglas Colkitt and their credited predecessor lineage. The unchanged vendor
files retain their original authorship and license notices.

Prepared for AAAmirinu with substantial OpenAI Codex assistance in design,
implementation, testing and writing, including a separate AI review. New work
Apache-2.0. No selected source, manifest, frontier, maintainer decision or
existing PR is modified.
