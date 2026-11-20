# Reviewed snapshot and portability record

The package preserves the exact author science reviewed by the
independent classification worker and the root analytic reviewer.
The proof hash is unchanged:

```
85f820586326b51b41b73feea2edfe5426a39659440d2b04431ec9c6e24a795a
```

The classifier, complete certificate, primary receipts, source
witnesses and controls are also byte-identical. Both review texts,
their original receipts and the classification replay log are retained
verbatim. Their historical run-directory locators remain as review
provenance; current portable commands are in README and VERIFY.

[REVIEW-BINDINGS.json](REVIEW-BINDINGS.json) binds every retained
file's original and packaged hash. `verify_package.py` checks
the independent review's source hashes against the current science
and repeats these bindings after the full registered replay.

## Only adapted file

`review/classification/verify_independent.py` has three documented
text changes:

1. Resolve its source at the package root rather than an adjacent
   run directory.
2. Add an optional `--receipt PATH` argument.
3. Write a fresh receipt only when that argument is supplied.

The determinant, decoding, Taylor, orbit, mutation and analytic
calculations are unchanged. [PORTABILITY.patch](review/classification/PORTABILITY.patch)
shows the exact delta. The binding verifier reverses the three
replacements and checks the original script hash, so the adaptation
is reconstructible without relying on this prose.

The packaged script hash is:

```
d5fc7fcebc8731ace15a80d52bf32865abcd2d5ccde072f957aee753ebe0d761
```

The stored independent receipt is the accepted historical run,
including its elapsed time. A fresh replay prints its own elapsed
time but leaves that receipt unchanged by default. Time is not a
mathematical equality criterion. All deterministic author-generated
certificates and receipts reproduce their original bytes.

## Packaging-only additions

README, the task/replay/source manifests, input authentication,
the explicit optimized-suite wrapper, this integration record,
overlap notes and the concise PR description
were added for review and replay. They do not alter the scientific
statement, source guards, coefficient certificate or proof constants.

The source-history preflight is not claimed: the pinned #7599 head
is an external pending source object, with its exact cold-fetch
command documented. Offline arithmetic replay uses only the retained
package bytes. Local review and verification do not change the
selected frontier or constitute publication.
