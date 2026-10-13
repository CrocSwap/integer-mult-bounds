# Validation record

- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Branch: `research/r439-frame521-seed10`.
- Environment: Linux x86_64, Python 3.11.
- GitHub posting access: unavailable; coordination claim retained in `CLAIM.md`.

Commands completed successfully:

```sh
python3 -I -B research/r439-block521-factor/verify.py
python3 -I -B research/r439-block521-factor/search.py --output /tmp/r439-b521-repro.json
cmp /tmp/r439-b521-repro.json research/r439-block521-factor/CANDIDATE.json
```

Verifier result:

```text
PASS_R439_BLOCK521_FACTOR gates=47->31 ADDs=24305->24273 columns=661 controls=7 rank_mass=5129 kappa=unchanged
```

The reproduced candidate SHA-256 was `f27f5a8364cab5cd8ef96d3a92ae673dbe3835d16c0ae47f9ae98717f214c43d`. A fresh exported candidate record stream had SHA-256 `5b27d57516cf6455714ffdb8b5fef2c8478c0bbb134926a1dfedb4abcbd03509`, matching `CERTIFICATE.json`.

Not run: repository-wide `make verify`, C++ five/nine/eleven-stage cohort binaries, hosted-parent rebuild, physical invoice, selected frontier replay, Linux CI, or Lean. The standard-library verifier covers the exact local circuit, full scalar endpoint, owner interface, frame paths, paid profile, exporter bills, payload, and negative controls; the omitted scopes remain explicit obligations rather than implied successes.
