# Validation record

Publication base: `cef4b52f2a59009865bf8eabde1be3f159063703`.
Historical native source: `624de9dc66858af0945e5f8a0942488d62280d43`.
Producer source: `361f5d4100640177d6a983dd2f336021c75bfd5e` (#4929).
Both source commits are raw Git ancestors of the publication base.

Environment: Ubuntu Linux, CPython 3.12.3, Git 2.55.0, standard library only.
The direct normal and optimized checks each pass in about four seconds.

```sh
python3 -I -W error -B research/coded-port-adapter-ceiling/verify.py
python3 -I -O -W error -B research/coded-port-adapter-ceiling/verify.py
python3 -B scripts/research_package.py --package research/coded-port-adapter-ceiling --check-only
python3 -B scripts/research_package.py --package research/coded-port-adapter-ceiling
```

Expected direct output starts `PASS_CODED_PORT_ADAPTER_CEILING` and records
5,824 supported grade-two pairs, at least 112 grade-two bank channels,
four semantic rejection controls, exact intervals and no new kappa.
The metadata-only check prints `PASS_PACKAGE_METADATA_AND_PINS`;
the registered runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
These commands passed locally in both normal and optimized modes.

The four semantic controls independently reject a nonzero code diagonal,
a wrong inverse entry, replacement of a supported transport by grade zero,
and a sign change violating the exact inverse polynomial. Checks execute
authenticated source bytes directly and authenticate science bytes before
and after the run. They regenerate the scientific result in memory and do
not write or repair frozen artifacts.

The written all-width phase-quotient/rank argument was derived by the parent
agent and reviewed by the source/interface agent. These related AI-agent
checks are not independent human review or formal-kernel verification.
The source producer's complete 632-input endpoint is inherited from #4929;
it is not freshly replayed by this package.

Before publication, compare committed bytes and require declared source
ancestry with `scripts/check_research_commit.py --check-source-history`.
Use `scripts/export_research_package.py` to export the committed package,
check its inventory, and run the direct verifier after extraction into a
fresh directory with Git absent from PATH. Operational receipts name the
actual contribution head and export hash; they do not authenticate themselves.
Hosted CI is pending until publication. No complete caller, uniform compiler,
outer recursion, selected frontier, or new kappa is validated here.
