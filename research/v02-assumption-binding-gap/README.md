# V02 assumption values are not bound by the public replay

**No κ change.** The selected frontier stays
`363005817/100000000000`. This package does not justify the 56 recorded
frontend facts, and it does not prove that any recorded value is false.

## Scope and evidence

This is item 1 of the open-request list taken from
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19530668):
the 56 `original_source_condition_assumptions` in the V02 export, against the
two-role contract. The parent-origin handoff on the same thread is a different
request and is not done here.

Catalogue card `formal-interface-lemma` asked for one uncovered interface
binding. The scope is **changed**: the live handoff is the #7136 export and the
frozen `pyinit_failure` / `exec_failure` commands, not a Lean lemma and not one
of the five selected-frontier assumptions. The connection to the bottleneck is
indirect. These assumptions are a prerequisite named by the V02 archive; they
are not a selected-invoice term. A side result is still the requested audit.

Pinned public export: Clear1nsight commit
`1998ae8ee6d46bafac647329e5b41a85941bb2e7`, the commit named in that handoff.
That commit is not an ancestor of this branch. The seven archive files are
vendored in `pinned-export/` and checked by Git blob id. Caller contract on
this branch: `research/h25-c05-criterion-consumer-contract/ROLE-PROOF.json` and
`snapshot/original/variant/variant_driver_v1.py.txt` from PR #6397.

### What is proved

The public `verify.py` mentions `original_source_condition_assumptions` once,
and that occurrence is

```text
need(len(fixture['original_source_condition_assumptions']) == 56, 'assumption count differs')
```

So the public PASS authenticates the key count only. Replaying the vendored
checker on the unmodified archive returns PASS with
`original_commands_executed = 0`. Replacing `__GNUC_MINOR__` with `4` and
rewriting the manifest hash leaves that PASS object unchanged. Deleting
`HAVE_IEEEFP_H` makes the same checker fail with `assumption count differs`.
That is a proof about this finite program, plus one positive replay, one
value-changed replay, and one rejection control. It is not a search.

### Exhaustive census of the 56 names

The object has 20 integers and 36 nulls. Neither role's argv contains any of
the 56 names as an element. The only token agreements are:

| Name | Recorded | Agreement visible in the frozen argv |
|---|---:|---|
| `__GNUC__` | 13 | `argv[0]` ends with `x86_64-linux-gnu-gcc-13` |
| `__STDC_VERSION__` | 201112 | the element `-std=c11` is present |

Those two agreements are spellings in the driver. They are not an installed
`-dM` dump, and the public replay does not read them. Every other recorded
integer is absent from the argv. That includes `__GNUC_MINOR__ = 3` and
`__GNUC_PATCHLEVEL__ = 0`: the basename `gcc-13` does not state the minor or
the patch.

Recorded integers with no argv element: `_LP64 = 1`, `__CHAR_BIT__ = 8`,
`__ELF__ = 1`, `__GNUC_MINOR__ = 3`, `__GNUC_PATCHLEVEL__ = 0`, `__LP64__ = 1`,
`__SIZEOF_LONG__ = 8`, `__SIZEOF_POINTER__ = 8`, `__STDC_HOSTED__ = 1`,
`__STDC__ = 1`, `__amd64 = 1`, `__amd64__ = 1`, `__gnu_linux__ = 1`,
`__linux = 1`, `__linux__ = 1`, `__unix__ = 1`, `__x86_64 = 1`,
`__x86_64__ = 1`.

Recorded nulls, also not argv elements: `HAVE_IEEEFP_H`, `HAVE_STAT_H`,
`HAVE_SYS_TERMIO_H`, `MS_WINDOWS`, `MS_WINDOWS_DESKTOP`, `MS_WINDOWS_GAMES`,
`NT_THREADS`, `_AIX`, `_MSC_VER`, `_WIN32`, `_WIN64`, `__ANDROID__`,
`__APPLE__`, `__CYGWIN__`, `__DragonFly__`, `__FreeBSD__`,
`__FreeBSD_kernel__`, `__GNU__`, `__HAIKU__`, `__ILP32__`, `__MACH__`,
`__NetBSD__`, `__OpenBSD__`, `__VMS`, `__VXWORKS__`, `__cplusplus`, `__hpux`,
`__hpux__`, `__i386`, `__i386__`, `__rtems__`, `__sgi`, `__sun`, `__sun__`,
`__vxworks`, `__wasi__`.

The frozen commands, reconstructed from the driver and matched to #6397's
`ROLE-PROOF.json`, are the same in both Python modes:

```text
/usr/bin/x86_64-linux-gnu-gcc-13 -nostartfiles -shared -fPIC -O3 -std=c11
  -Wall -Wextra -Werror -I/usr/include/python3.12
  {S}/areas/field-negative-variants-v1/<role>/dict_probe_fields_v1.c
  -o {O}/<role>/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so
```

`<role>` is `pyinit_failure`, then `exec_failure`. There is no `-dM`, `-D`,
`-U`, `-undef`, or `-include`.

### Hosted implicit include

`/usr/include/stdc-predef.h` is a regular baseline node of 2,462 bytes, mode
420, sha256
`8db4f65e62cade8ae4d9b77960ee6aee093255acc1b637e3fb37d79179733b15`. The pinned
walker resolves that literal path to itself. The public verifier never names
`stdc-predef`, and none of the 56 keys names it. Presence of the node is not
a binding of the hosted implicit-include policy. The export's first remaining
obligation still asks for that binding. The earlier rule model in
`research/h25-c05-v03-input-constructors/implementation/c05_gcc_rules_v1.py`
already records `automatic_preinclude.effective = False`; this package does
not rerun that derivation.

### What this does not show

A null record is not a proof that a header macro is absent after inclusion.
Both `pyconfig.h` rows are in the graph as regular files with hashes only.
`SOURCE_MAP.json` excludes original host file contents, so `HAVE_STAT_H = null`
cannot be compared with those headers here. No installed compiler was run.
The census is exhaustive for this 56-key object and these two argvs. It is
not a statement about every GCC invocation. The public graph replay's PASS is
left intact; only its silence on assumption values is established.

## Reproduce

From the repository root, Python 3.12:

```sh
python3 -B research/v02-assumption-binding-gap/verify.py
```

Expected stdout status: `PASS_V02_ASSUMPTION_VALUES_UNBOUND`. The command
reruns the vendored public checker three times in a temporary directory. It
does not write the package, open a network connection, or invoke GCC. Pins
and hashes are in [SOURCES.json](SOURCES.json). The selected-record and
catalogue rows there are provenance for the card, not inputs of the census.

## Open next questions

1. Can a transcript of these two frozen argvs, with the sample phase named,
   bind each of the 56 values?
   *Why:* the public PASS does not. A predefine dump, a dump after
   `stdc-predef.h`, and a dump after `pyconfig.h` are different claims.
   *First step:* archive one stdout whose argv equals the frozen command and
   whose phase is stated, then compare each name.
   *Blocked by:* the export has no such transcript, host file contents are
   excluded, and this package does not run a compiler.

2. Do the two hashed `pyconfig.h` rows define `HAVE_STAT_H`, `HAVE_IEEEFP_H`,
   `HAVE_SYS_TERMIO_H`, `MS_WINDOWS`, `MS_WINDOWS_DESKTOP`,
   `MS_WINDOWS_GAMES`, or `NT_THREADS`?
   *Why:* the recorded nulls are compatible both with a predefine-phase sample
   and with those names never being set. The hashes are
   `dcda0cfa3f4971db195817881c58025db6c76f19ae45f26d3dda0a43001253e8` and
   `23931f53bc7ee512c6bd3162828747494eaa5e21f23dd63b31170ec1adfbe65e`.
   *First step:* compare those hashes to file text that defines or does not
   define each name.
   *Blocked by:* the fixture stores the hashes and not the text.

## Credit

The export and the handoff are Chris R / Clear1nsight, PR #7136, with the
assistance disclosed there. The two-command contract is PR #6397. The
implicit-include rule left open by the v03 constructor model is that earlier
package's. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
