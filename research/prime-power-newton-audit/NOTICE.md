# Attribution, license, and assistance

Prepared for Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance
in research selection, proof derivation, implementation, verification, and
writing. Separate Codex agents derived the valuation proof and implemented
the cyclotomic arithmetic; further review is recorded in VALIDATION.md.
Independent implementations do not imply independent human peer review.

Ali Romman's incorporated PR621, at
`520774462b19b29af41554b74def31f9d01e997e`, supplies the integral kernel,
prime-ideal nonunit lemma, and complex-conditioning context being audited.
Its upstream and classical credits remain: OpenAI's exact-DFT preprint at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, sections `loc:newton` and
`loc:fourier-factorization`, and Alexey Kuznetsov's classical q-calculus
Vandermonde factorization work. No predecessor code is copied or imported.
PR621's source-specific notice remains in place and is source-pinned here.

The Newton polygon theorem and cyclotomic ramification facts are standard;
J. S. Milne and Keith Conrad references are recorded in SOURCE.json. This
package claims no literature priority for the derived specialized formula.
Scott Woolsey Biggart's PR668 CRT-resultant checks, Jason Willems's PR666
composite lifting, Chafik Boukhalfa's PR628 rounded inversion, and Ryan
Pinto's PR692 weighted-stride audit provide related, distinct evidence.
Their pending changes are not imported or certified by this package.

The selected frontier remains Chafik Boukhalfa's PR626 on Jeremy Kothe's
PR622/623 with eumemic's PR543 and their cumulative predecessor work. The
selected construction is context, not the object of this narrow audit.

New code and prose use the repository's Apache-2.0 license. This is not a
formal proof or an independent human verification of integer multiplication.
