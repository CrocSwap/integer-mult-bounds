# Attribution and license

Prepared for **woklerx** with substantial **OpenAI Codex AI assistance**,
including implementation, experiment execution and a separate agent review.
This is not independent human peer review. New work is Apache-2.0 under the
repository license.

**Aaron Wang / navinor, PR946**, identified the locale/newline reproducibility
problem and authored the proposed encoding changes. Files under `inputs/pr946/`
are eight byte-identical proposed inputs from commit
`b6e22dbf548d72f18b722ccb6c2ea8e3d9df6ac1`; their original comments and notices
are preserved. These are test inputs, not adopted production code.

**Ross Richardson, PR950**, supplied the unchanged exact packed verifier and
its complete historical source manifest. **Douglas R. Colkitt** authored the
historical central-factor implementation and repository sources it checks.
The existing package notices retain further predecessor credit.

The **batch952 maintainer review** first identified the eight-input PR950
conflict and deferred PR946. This contribution credits that finding and adds
a reproducible wider inventory, isolated per-input rejection controls and a
complete source-preserving restoration replay. The batch970 review and
**woklerx's PR970** provide an additional accepted package with five matching
source references; no fresh PR970 mathematical replay is claimed here.

The exact-byte/payload distinction follows the repository's reproducibility
policy and **Maxime Fleury's gzip-container reproducibility audit**, following
**Antoine Olivier's** replay findings. Here the conflicting inputs are plain
files: no gzip normalization or digest relaxation is used.
