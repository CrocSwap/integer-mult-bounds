# What the three omitted #626 digests measure

**Verifier audit; no new kappa.** The [Linux reconciliation](../selected626-linux-reconciliation/README.md)
compares the preserved run `38317651752` with the committed #626 assembly after
removing three digest paths. It already says those differences are not known to
be gzip metadata, because the template, owner audit and invoice were not
uploaded. This note classifies the digests from the producers that wrote them.

```sh
python3 -B research/pr626-omitted-digest-audit/verify.py
```

Expected:

```text
PASS_PR626_OMITTED_DIGEST_AUDIT template=decompressed-payload owner_audit=indented-json-file fresh_invoice=indented-json-file differences=3
```

Python 3.10+ and Git. The sprint base `66849e1475c930fd7732b1a0067ffee7e1e95f60`
must be present; a shallow clone has to fetch it first. No supplier replay.

## Classification

At that base, `research/complex-k492-owner-repair/code/invoice_allcold.py`
defines `filehash` as SHA-256 of the file bytes and `contenthash` as SHA-256
of the decompressed payload when the file ends in `.gz`.

| Omitted assembly path | Producer | What a difference means |
|---|---|---|
| `template_sha256` | `contenthash` of `GLOBAL-TEMPLATE.json.gz`, checked again by decompressing that file in `audit_allcold.py` | The template **payload** differs. Two gzip containers of one payload have the same `contenthash`, so this recorded mismatch is not a compression-header artifact. |
| `input_sha256.owner_audit` | SHA-256 of `OWNERS-AND-PROFILE.json`, written with `json.dumps(..., indent=2)` | The indented owner file differs. That file includes `source_artifacts`, and the invoice binds `CANONICAL-WORD.json.gz` with `filehash`, so the file can change because a nested container changed or because a mathematical field changed. |
| `input_sha256.fresh_invoice` | SHA-256 of `PREFIX-AND-INVOICE.json`, also `indent=2`, via `sha(invoice_path)` in `assemble.py` | Same kind of mixed file receipt for the invoice. |

The recorded Linux and committed values differ on all three paths. They are
copied from the predecessor's `EXPECTED.json`; this package does not recompute
them from missing artifacts.

The fixture shows the distinction directly. One payload compressed twice, at
different level and `mtime`, yields two containers and one payload hash.
Replacing a nested container hash inside an indented owner file changes
`owner_audit` while a projection that keeps only `paid_profile` stays equal.
Changing `paid_profile` still changes that projection. So dropping the file
hash can hide a container-only change, and keeping the reduced assembly
comparison still sees a profile change.

`template_sha256` is the case that cannot be explained that way. Because it is
a payload hash, the recorded disagreement is a real template-content
disagreement. The omitted owner and invoice hashes stay unresolved: without
those files, a container change and a mathematical change are not separable.

## Open next questions

Can the omitted owner and invoice files be recovered from the retained stage
logs, or are they absent from run `38317651752`? That decides whether the two
file-hash disagreements are nested container receipts or changed audit fields.
The first step is to search the preserved logs for `OWNERS-AND-PROFILE.json`
and `PREFIX-AND-INVOICE.json` bytes or their payload hashes. It is blocked by
the reconciliation's own scope: the workflow did not upload those files, and
this audit does not invent them.

## Credit and limits

The reconciliation is Josh Snider's (`jsnider3`), with the selected #626
composition. The gzip-container convention is the existing reproducibility
note. This package only classifies these three digests and adds the fixture
that separates container bytes from payload bytes.

No selected certificate, supplier or kappa changes. The audit does not explain
the numerical template difference and does not rerun `make frontier626-verify`.
All-size, hosting, precision and analytic assumptions of the selected
construction remain open.

Prepared by Riquelme Soares (@hevlyo) with substantial Cursor agent assistance.
Apache-2.0. No independent human peer review is asserted.
