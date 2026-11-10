# Scoped preservation of the digest-search seam

This is a source-bound tooling result. It changes neither the shared scanner nor
the selected multiplication frontier. Nick Petalas's PR6428 asks whether the
remaining tree-wide digest search can reuse reads across repeated objects. Its
unchanged-head reuse and historical measurements remain predecessor results.

## Domain

The intercepted call is exactly `git grep -I -l -z -F (-e digest)+ COMMIT --`,
with lowercase ASCII 64-hex digests and a full object ID, issued with
`check=False` and no input payload from the authenticated source. Objects are
readable and immutable during the call; repository configuration, index and
attributes are stable. The statement concerns successful classification and
resulting source reports. It does not assert identical arbitrary diagnostics,
resource failures, races, side effects, or timing on every possible Git state.

Unsupported invocations retain the original implementation. The adapter also
falls back on gitlinks, enabled or unrecognized recursive settings, unsupported
tree rows, reader failures, oversized path arguments, empty candidate sets and
restricted-grep errors. Empty candidates do not manufacture a no-match return:
the original command still decides whether configuration or other state fails.

## Necessary raw-byte condition

Without text conversion, a positive fixed-string match for a digest requires
that exact byte string somewhere in the unconverted regular blob. The condition
is necessary, not sufficient: Git can reject a raw-hit path as binary. A match
inside a longer hexadecimal string is still a match; no token boundaries are
introduced. No case folding or expression inversion is admitted.

For every regular tree entry `(path, object ID)`, group by object ID and read each
distinct blob once. Scan its payload in bounded chunks, retaining the preceding
63 bytes. Every 64-byte occurrence either fits in one chunk or crosses a boundary
within that suffix. Reset the suffix for each object; object framing is never
searched as content. Reader header, size, delimiter and completion checks must
all pass. Thus no regular blob containing a needle is omitted.

## All aliases and final classification

Expand **every** path alias of a raw-hit object ID. Identical bytes can have
different `.gitattributes` classifications: a text alias may match while a
binary alias does not. Caching one alias's `git grep -I` verdict for the whole
object is therefore unsound in either direction. Raw-hit membership is the only
property reused across paths.

Delegate the retained paths to the original Git grep with global
`--literal-pathspecs`, the original revision/options/environment and `--`.
NUL-framed tree parsing preserves newlines and carriage returns; literal
pathspecs preserve punctuation and pathspec-looking names. Every originally
reported path is retained by the necessary raw-byte condition. The final command
uses Git's original path policy, so it introduces no newly reported paths. Git
traversal order is retained. The original source then constructs and sorts its
complete report, including duplicate target-digest multiplicity, without changes.

This proves equality of the successful search results, and hence the source
reports, under the stated eligibility and stability conditions. Executable
fixtures corroborate the specific supported call/CLI behavior; they are not a
proof for all Git versions or configurations.

## Work accounting and limits

The prefilter transfers each distinct regular blob once, stream/discard, even
after finding a hit. Final Git grep reads candidate paths again. Changed-target
reads, unchanged-head reuse and pinner-before/head reads remain separate source
work. Tree/path/pattern metadata scales with the query. Each search window has
at most one chunk plus 63 bytes; multiple temporary buffers coexist, so the
payload-memory statement is only O(chunk size), excluding Git/process buffers.
Python-received payload bytes are not
physical disk I/O, decompression counts, CPU cost, or a runtime guarantee.

Controlled same-history timings and exact logical counts are reported separately.
The canonical PR6428 154-row historical replay was not performed here. Complete
historical object closure and a fair repeated end-to-end benchmark remain open.

## Credit

Armin Pourshafeie/apoursh and the retained Anthropic Claude attribution own the
original scanner (PR6319). ToikY's PR6357 supplied the repository selection and
literal CR/LF path repairs. Nick Petalas supplied PR6428's unchanged-head reuse,
benchmark and explicit next question. The canonical `git_source_env` policy and
its retained authors are used exactly after authentication. Git's developers
provide the path-aware final matcher. The new adapter and corroboration were
prepared by ToikY with OpenAI Codex assistance; independent AI checks do not
constitute human acceptance or mathematical supplier admission.

Primary Git references: [v2.50.1 tree traversal/configuration](https://github.com/git/git/blob/v2.50.1/builtin/grep.c),
[binary/path-driver matching](https://github.com/git/git/blob/v2.50.1/grep.c), and
[command semantics](https://github.com/git/git/blob/v2.50.1/Documentation/git-grep.adoc).
