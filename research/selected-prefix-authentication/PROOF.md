# Path-prefix reuse preserves complete source authentication

This scoped implementation-equivalence proof was produced by Nick Petalas.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

## Contract

Fix a stable POSIX filesystem tree and a root R already resolved to a physical
absolute directory. Each explicit manifest name is a canonical nonempty
relative POSIX path, has no backslash or `..` component, and has at most 128
components. There are at most 4,096 names. The captured PR6030 manifest has
1,405 names, all within these capacities.

The original source checker and report projection are Douglas Colkitt's and
Mihir Srivastava's work. Their source hashes are pinned in SOURCES.json. This
proof concerns replacement of `explicit_file` only. Underlying scientific and
source-binding claims are cited inputs, not new audit results.

## Original acceptance predicate

For components p1 through pk, the original `explicit_file` checks canonical
spelling, rejects every symlink among the k successive prefixes, resolves
the complete path, requires containment in R and requires a regular file.
On the stable tree, this is equivalent to:

1. Every proper prefix is a non-symlink directory.
2. The complete path is a non-symlink regular file.

A regular leaf reached without symlinks has directory ancestors. Conversely,
append the canonical components to physical R. None is `..` or a symlink,
so resolving the result cannot leave R. The leaf predicate gives a regular
contained file. Missing components, nondirectory ancestors, directory leaves
and symlinks fail both predicates. Invalid names fail before this equivalence
is used. We claim equality of acceptance and returned paths, not identical
error messages or failure timing.

## Cached-directory invariant

The new validator initially maps only the empty prefix to R. At each proper
prefix it either uses a stored directory or checks a fresh candidate for
`not is_symlink()` and `is_dir()` before storing it. By induction, each
stored entry is the same physical non-symlink directory that the original
traversal reaches. The stable-tree premise keeps that fact valid during the
invocation.

Leaves never use cached leaf facts. Each call checks its own leaf for symlink
and regular-file status. The predicate equivalence proves that each permitted
name returns the same Path as before, or both versions reject it. Prefix
reuse cannot admit a rejected file under this premise.

On Windows every name delegates to the original validator. Its alias and
junction behavior is retained without an optimized Windows traversal. The
finite fallback control exercises delegation, not native Windows execution.

## Complete check and invocation boundary

The checker executes from its pinned source. Only its global `explicit_file`
reference changes, in a fresh namespace created for that call to `report`.
Every manifest iteration, read, SHA256, inventory equality, certificate check,
supplement check, primary-proof check and other publication-pointer check
remains in the original function. Corresponding returned paths agree, so
their reads see identical bytes on the stable tree. The unchanged projection
receives the same record and certificate. JSON serialization is identical.

No directory map or digest enters the next invocation. Later file-byte changes
are re-read; later directory and leaf symlinks are rechecked. The controls
exercise both changes. Neither checker supplies an atomic snapshot, and
mutation during a call is outside this theorem.

The captured selected record has SHA256
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.
It is the exact official record at the pinned main. The benchmark requires
those record bytes still to match before comparing official and adapter
commands. It never substitutes a later frontier silently.

## Exact work reduction and limits

Enumerating the manifest gives 7,759 components, 1,405 leaves and 441 distinct
proper prefixes. Original explicit-name traversals perform 7,759 component
symlink checks. New traversals perform 441 directory symlink checks, 441
directory-type checks and 1,405 leaf symlink and type checks. They eliminate
5,913 repeated directory symlink checks. Two resolutions in the original
`path` call per explicit file also disappear from this traversal. Other path
resolution in the unchanged checker remains. The cache has 442 entries with R.

The finite verifier corroborates this predicate and complete report on its
declared cases. The source argument explains retained checker coverage. The
benchmark measures a local implementation improvement. None verifies the
scientific theorems represented by those files, admits a supplier, changes
a physical tape bill or discharges a selected framework assumption.
