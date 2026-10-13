# Attribution and license

New audit, oracle, controls and explanatory note: Ryan Pinto (GitHub
Ambassators), with substantial AI assistance from OpenAI ChatGPT / GPT-6
Astra Pro in task selection, mathematical reasoning, implementation, tests
and documentation. This is AI-assisted independent implementation, not an
independent human peer review or a proof-assistant certification.

The verbatim `vendor/branchfree.py` is from Chafik Boukhalfa (chafreaky),
PR #489, head `8922e3b3f0fd7772b0fb42028eb2532984c3ab42`, originally at
`research/branchfree-gaussian-inverse/code/branchfree.py`. Its signed packing,
five-factor Gaussian program and existing checks are predecessor work, not
new inventions of this audit. The source PR credits the retained
RaD/hipotures phase-cell work, its PR #481 batched Gaussian boundary work,
and Alexey Kuznetsov for the classical q-calculus identity. This audit does
not reproduce or claim a new proof of those larger constructions.

Concurrent local `gaussian-polynomial-identity`, `gaussian-symbolic-audit`,
`gaussian-symbolic-independent` and `q-gaussian-symbolic-audit` claims motivated
the single pivot to a distinct packing obligation. No code or result from
those concurrent packages is imported or used as an oracle.

New material is Apache-2.0 under the repository's CONTRIBUTING.md.
`vendor/LICENSE` is the unchanged source repository license at the pinned
commit. No inherited source or notice has been edited.
