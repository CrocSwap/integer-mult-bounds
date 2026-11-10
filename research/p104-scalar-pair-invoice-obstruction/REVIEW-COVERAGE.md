# Review coverage

The final `PROOF.md` combines two separately developed checks. These are
independent AI implementations and author-side reviews, not external human
acceptance or proof-kernel verification.

* `reviews/A-INDEPENDENT-REVIEW.md` covers the universal forced-E and kernel
  geometry, complete rank-five classification, endpoint incidence, and
  rank-five pointwise invoice. Its exact reviewed text is preserved as
  `reviews/GEOMETRY-REVIEWED-PROOF.md`, SHA256
  `982f486ddbc997ccb9f2c5fb6ade88578ac92dd56ad5deed12a2ca2549694bac`.
  Sections 1–5 are unchanged in substance in the final proof. The independent
  modular implementation is `reviews/a_matrix_review.py`; its retained receipt
  records all 6,561 F3 parameter choices and all six rank-five F3 cases.
* `INDEPENDENT-INVOICE-REVIEW.md` covers the complete source/candidate invoices,
  all 16 allocation/orientation fixtures, the exact eight-inventory census,
  the four rank-six concavity comparisons, and each rank-seven deletion.
  Its portable independent implementation and receipt are
  `independent_invoice.py` and `INDEPENDENT-INVOICE.json`. This is the separate
  coverage for final proof section 6; the geometry review is not silently
  extended to that added section.

The primary replay is `verify.py`, with `RESULT.json`. Physical paid fragments,
native supplier scientific replay, compiler qualification, and the five
inherited all-size assumptions are outside these checks.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
