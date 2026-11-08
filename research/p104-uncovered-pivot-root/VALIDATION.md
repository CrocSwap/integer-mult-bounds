# Integrated validation

Base commit: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Environment: CPython 3.12.14 with standard library only.

Executed:

```
python3 -B scripts/research_package.py --package research/p104-uncovered-pivot-root
```

The registered command ran both independent checkers with `-I -B` and
`-I -O -B`. All four checks passed, ending in
`PASS_REGISTERED_RESEARCH_PACKAGE`. Root checks cover 110 parameter roots,
220 exact polynomial operator identities, 3,300 transported-carrier nullspaces,
seven retained source hashes and five rejection controls. Accounting checks
cover 4,298 top-k identities, 840 independently coded transport systems, four
retained source hashes, complete native/root histograms and exact rational
crossing/derivative signs. Both checkers reproduce their stored results.

The source sign-Gram lemma and transport argument were independently reviewed
by the team lead; the accounting derivation was independently reviewed against
the root geometry. This is not formal proof-kernel verification or a native
word/compiler replay. See `accounting/VALIDATION.md` for the independent
accounting worker's fresh-copy verification record.
