# Sequential integration after the accepted precision supplement

This directory adds the reviewed supplied-grid arithmetic result to
[#8093](https://github.com/CrocSwap/integer-mult-bounds/pull/8093)
at expected head `ea0274f8e6b6add282a63c11c5b8c4420ed3bc7e`, whose tree is
`c09b52f711358be141d4403f449c57dd89fb68b3`. It preserves all earlier scientific
files. Only the parent README, TASK and VERIFY metadata are extended.

The accepted proof is SHA256
`05e85b54fd4b8f834f1790ff18ca53f5cd05aaf58e316aef4ba72aabe2b7fa9a`;
the new program is SHA256
`cce97fcc515e3240224cada0a25c666fbac13454135b4fd71589f30bf67b3184`.
`FROZEN.json` authenticates the complete author/reviewer package. The separate
review accepts the universal argument and includes its own exact oracle,
39,220 cases, 18,716 ties, 8,628 zero-multiplier cases, 1,020 literal odometer
calls, 28 API bindings and four adverse source mutations. Its normal and
optimized receipts agree byte for byte.

Two execution-boundary clarifications in `review/REVIEW.md` apply to the
unchanged proof. The extracted Grid fixture supplies `operator.mul` as an
exact-integer helper; it does not execute or price the retained
`word_product` machine implementation. The new local shift/add implementation
is separately proved and charged quadratically. The example sides=(2,),
digit_bits=5 is an admissible explicit constructor geometry; no claim is made
that `multiply_uniform` selects that particular instance.

The original seven verification registrations are unchanged. The eighth
registration now calls `run_registered.py`: it runs the exact previous eighth
command first, then the new author and independent reviewer checks in normal
and optimized modes. All four new receipts are generated in a private
temporary directory and compared byte for byte with frozen evidence. The
author's original sibling-import invocation is retained; independent review
uses isolated interpreter mode. No predecessor guards, proof APIs, source
coefficients, arithmetic chronology or published receipt are rewritten.

The result covers supplied scalar arithmetic at the actual external calls.
Coefficient preparation, global transport and ownership, native private
storage, reversible cleanup and the accelerated outer tariff remain open.
All five selected assumptions and the selected kappa remain unchanged.
