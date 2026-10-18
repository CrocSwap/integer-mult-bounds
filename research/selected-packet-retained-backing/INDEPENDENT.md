# Independent audit of the prefix-return cut

This audit was derived from the exported source before reading the primary proof
or `verify.py`. The independently written checker does not import either. Source:
PR #2697, commit `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, specifically
`packet_engine.py`, `consumer.py`, `vendor/packet.py`, `vendor/records.py`,
`vendor/bitstream.py`, and `vendor/stream_runner.py`. The checker authenticates
all 23 exported files against both SHA-256 and Git blob IDs in `SNAPSHOTS.json`.
It first requires the manifest's raw SHA-256 to equal the fixed digest
`a9f623f4971232daccb39091b51294d9cd09fe07af054184edc4f3bd7a51008e`.
That verifies agreement with the pinned manifest; upstream provenance is the
package's separately recorded source-export obligation.

The question is a source-level cut, not an execution maximum: a new
`read_prefix(directory, field_count)` return value is available, but its caller
has not yet overwritten `packet_engine.run`'s `fields` binding. Count distinct
`Tape.cells` arrays reachable from the named payload and field roots. A length
includes its LEFT cell. Repeated roots of the same array contribute once.

## Assumptions and notation

* There are `N >= 1` complete prefixes, each with `F > 0` payload symbols. Set
  `V = NF`. The borrowed source has retained array length `K >= V + 1`; any
  additional cells are blank history.
* The directory has retained length `D`, and every returned field-prefix tape
  has the same minimal length `Q`, including LEFT. Thus its encoded prefix has
  `Q - 1` symbols. For a fresh unpadded directory, `D = N(Q - 1) + 1`; the cut
  identity also permits longer blank directory history. The producer's exact
  directory size is not proved here.
* `factory()` produces a fresh ordinary `Tape`, initially of length one. All
  newly copied payload tapes of one prefix have length `F + 1`, and actions
  preserve that retained length of `local`. At each completed action,
  `changed` is either `local` itself or a separate tape with
  backing length `F + 1`. No other cross-root aliases occur.
* The actual caller `Consumer.apply` is suspended inside `packet_engine.run`.
  Its `first` preflight prefix was freshly read and subsequently cleared. The
  local `first`, and any `prefix.tape`/closed-frame aliases of it, retain exactly
  one array of length `Q`.
* `t >= 0` is the number of previously completed primitive events; boundary
  enter/return events do not increment it. Within primitive `t`, exactly
  `j` prefixes have completed, with `0 <= j < N`. Execution has reached this
  cut without an exception. The roots considered are `source`, `current`,
  `output`, stale `local` and `changed`, `directory`, preflight `first`, stale
  `fields`, and the fresh return value.

The action contract is explicit. Merely returning a tape with `F` nonblank
symbols does not prove its retained length is `F + 1`; an action with padded
history requires its actual returned backing length in the sum. The alias case
below is an interface witness, not a claim that the selected native primitive
trace can return an alias.

## Identity-aware root ledger and derivation

`Tape.clear()` rewrites symbols to BLANK and rewinds; it never shortens
`cells`. `Tape.write()` can extend the array; it never contracts it. Copying
exactly `m` symbols into a fresh tape therefore produces retained length `m+1`.

Before the first primitive, `current is source`. At each completed primitive,
`current = output` installs a newly allocated whole-packet array of length
`V + 1`. The subsequent primitive allocates another fresh `output`, leaving
`source`, `current`, and this new `output` distinct. This remains true for any
number of primitives: a previous whole-packet array that is no longer named is
outside the root set. No sum over all historical whole packets is justified.

At the cut, exactly `jF` symbols have been appended to the current `output`;
its length is `jF + 1`. In the initial cut, neither `local`, `changed`, nor
`fields` has yet been assigned. At every other cut, the previous iteration's
`finally` cleared them without deleting their bindings. They remain present
across the outer primitive-loop boundary as well as the inner prefix loop.
The new `fields` assignment has not happened, so the previous and fresh field
arrays coexist.

For a noninitial cut, let `delta = 1` when the last completed action returned a
separate `changed` tape, and `delta = 0` when `changed is local`. When `j > 0`,
this is prefix `j-1` of primitive `t`. When `j = 0` and `t > 0`, this is prefix
`N-1` of primitive `t-1`. It is the previous action's alias relation, not the
not-yet-run current prefix action's relation.

| Category | Initial `t = j = 0` | Other cuts |
| --- | ---: | ---: |
| Borrowed source; current deduplicated when `t=0` | `K` | `K + 1[t>0](V+1)` |
| Current output | `1` | `jF+1` |
| Cleared stale local and changed | absent | `(1+delta)(F+1)` |
| Directory | `D` | `D` |
| Cleared caller preflight first | `Q` | `Q` |
| Cleared stale fields | absent | `Q` |
| Fresh returned fields | `Q` | `Q` |

Consequently the exact retained-length sum on this specified root set is

```
B(0,0) = K + 1 + D + 2Q,

B(t,j) = K + 1[t>0](NF+1) + (jF+1)
         + (1+delta)(F+1) + D + 3Q       otherwise.
```

In the fresh-result case `delta=1`, the noninitial payload contribution is
`K + 1[t>0](NF+1) + (jF+1) + 2(F+1)`. In the alias case it is smaller by exactly
`F+1`. The initial cut is independent of the eventual first action's result.
For `N=1`, the first primitive has only the initial cut, while every subsequent
primitive has the `t>0,j=0` case with stale prefix roots. The derivation applies
to all integer parameters satisfying the assumptions, not only the checker grid.

This is a simultaneous-root result. It neither adds unrelated phase maxima nor
infers retained backing from a nonblank payload measure. In particular PR #2731's
`3v+3R` nonblank payload statement excludes this category. The previously
identified field-only `D+3Q` cut is retained as a component; the present audit
adds its simultaneous payload roots, first-cut exception, whole-packet aliases,
and the cross-primitive stale-binding case.

## Independent executable check

Run from any working directory:

```
python3 -I -O -B research/selected-packet-retained-backing/independent.py
```

(The displayed relative path assumes the repository root.) The script writes
only deterministic JSON to stdout and disables bytecode writes. Its acceptance
conditions use explicit `require`/`ValueError` checks, so interpreter optimization
does not remove them. A private meta-path loader compiles the authenticated
in-memory source bytes directly, with `optimize=0`, bypassing `.pyc` files and
temporarily replacing preloaded modules of the same names. The loader restores
the previous module state on exit; each fixture also restores patched engine
methods in `finally`. It executes the
literal authenticated `packet_engine.run`, `Tape`, `read_prefix`, `copy_bits`,
and native binary `Counter`. A wrapper around the imported `read_prefix`
inspects the caller's local roots after the literal reader returns and before
the caller assigns the returned tape to `fields`. It deduplicates by array
identity, without using the primary verifier or its formulas.

The layout, event stream, and action are fixtures. The layout supplies the
requested fibre count. Events select either a fresh copied result or the same
local tape. The cleared preflight `first` is built with the literal reader and
retained by the harness, reproducing the source-visible caller root. This does
not execute the numeric `Consumer.apply` callback, establish selected geometry
admission, or verify selected arithmetic. Those are separate primary-source
witness obligations.

The finite exhaustive grid is:

* `N in {1,2,3}`, `F in {1,2,7}`, encoded prefix symbol length in `{1,2,5}`;
* source blank padding in `{0,9}` and directory blank padding in `{0,5}`;
* all eight fresh/alias action-mode words of length three.

Observed result: **864 fixture runs, 5,184 cuts**, including 864 initial cuts,
1,728 first-prefix cuts of later primitives, and 2,160 each of fresh and alias
stale-result cuts. All source authentication and identity/length checks passed
under `-I -O -B`. Additional in-memory hardening controls rejected an altered
manifest and altered `records.py` bytes, completed the same grid despite preloaded
replacement modules for `packet_engine`, `records`, and `packet`, verified
restoration of those prior modules, and verified that failed explicit acceptance
still raises under `-O`. These checks created no scratch files.

Nine deliberately incorrect accounting rules were rejected wherever applicable:
counting source/current twice; dropping cleared payload roots; dropping previous
fields; dropping the caller's preflight first; treating clear as shrinking;
forgetting stale roots at a new primitive; always counting changed separately;
always aliasing changed/local; and omitting LEFT markers. Each rejection uses a
changed estimate against the measured literal-root sum. These are
**defect-sensitive accounting controls**, not source-mutation tests.

## Covered domain and limits

The written induction and identity argument cover every `N >= 1`, `F > 0`,
`t >= 0`, `0 <= j < N`, and permitted `K,D,Q` under the stated freshness,
length, successful-execution, and alias contracts. The executable evidence is
finite and restricted to the explicit grid and interface fixtures. Neither is a
formal-kernel proof.

This exact cut omits numerical words, counters, program tables, event objects,
closed callback internals other than aliases to `first`, Python object headers,
bytearray overallocation, garbage-collector retention, and all unnamed or
external roots. It proves no global peak, allocator byte count, physical tape
reserve, recursive closure, or new multiplication exponent. Any such extension
must provide the missing resident categories and lifetimes separately.
