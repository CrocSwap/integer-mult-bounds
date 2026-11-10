# Validation and source boundary

The two inert source files were pinned before scientific execution:

- PR6425 head `092dcbd13d1263e691ad29f34fbf286fea1fac2c`.
- `RESULT.json`: Git blob `e18f92e001b8ce9d44287760516bf6ea002bcbcd`,
  22,234 bytes, SHA256
  `f8d15306112914af299acca8720779fbc9f6f07bb1336c51e99304fdea5caf89`.
- `README.md`: Git blob `d9ce3b644cff65dadd88663189638a4bfd52bac3`,
  7,410 bytes, SHA256
  `f35f0a30796e94ced74686bc3614b4478f5460bac0adb7c8d80827991f70ed0c`.
- Two-source manifest SHA256
  `d9d9e3785d6496adf112ccafbe25689057e9a1f28384ca28a536660c9f55f6e9`.

The primary's first scientific run passed. Normal and optimized emissions and
strict defaults passed with identical complete JSON, empty stderr and no source
execution failure. Primary certificate: 31,660 bytes, SHA256
`b477f2a8d144ed884c78ee29ac76fd88c95b076eb2dd290ef2431dd7e4969704`.
It contains 237 retained rows, 43 deleted rows and 237 strict rational separating
points; 2,272 pivots total, at most 49 per target. No floating LP or optional
dependency was used.

The primary and separate checker have distinct code ownership. The latter was
written before reading the new primary code or result, then consumes the sealed
result as untrusted certificate data. This is independently implemented
certificate checking, not blind rediscovery or a second simplex. It authenticates
both source objects independently, verifies every implication using only final
retained premises and checks every separator against all 279 other original
rows. Its corruption controls test actual certificate data and rejection reasons.

The generator's simplex is not trusted for the mathematical conclusion: literal
rational coefficient inequalities establish deletions; explicit rational points
establish nonimplications. Shared `verify_rational_lp.py` from PR5767 is related
certificate tooling, not an optimizer. Its shared 128-variable limit is not
widened and it is not represented as a full-instance replay here.

The independent checker passed on its first run. Normal/optimized emissions were
byte-identical and both strict-default runs passed with empty stderr. Its 71,360
byte receipt SHA256 is
`02c89eed3237e401b4b16563529de77cba8925439f2e67c86021a27846fccc81`.
It checks 43 deletion certificates, 237 full-original-row separators and 14
corruption/schema controls. Of the displayed separators, 134 are integral;
that observation does not establish the smallest integer-only screen.

The original 262,928-clique census and geometric witness validity are predecessor
coverage, not rerun or independently accepted in this session. Composing the
new 280-to-237 equivalence with that larger screen uses PR6425's proof as a
credited premise. Passing either screen does not produce a decoder or a physical
supplier. Fractional separators concern the real polyhedron; they do not prove
integer-only indispensability or minimum over arbitrary replacement inequalities.

Package/runtime, source/commit modes/history, normal/optimized strict replay,
read-only cold export, corruption controls, static review and exact-head hosted
CI are separate obligations recorded in the session receipts and public handoff.
No κ, selected-frontier, compiler/precision/stock/access/restoration/native/outer
admission claim is made. All five selected framework assumptions remain.
