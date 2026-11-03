# Exact scalar records between rounded P104 native returns

The complete selected PR6030 word can execute every ADD, SCALE and COPY exactly with **five fractional reserve bits** beyond its native return grid. This package supplies the integer executor and the complete source certificate. It includes all 22,803 events, 770 public fields and 29 owned field slots. This changes the precision interface, not the word or its recursive invoice.

Let each public ideal input have Hilbert norm at most a power-of-two B. Let each field have complex dimension 2^n. For target error B times 2^-t, set `p=t+10+floor(n/2)`. Round each real and imaginary input component, and each exact completed native output component, to the nearest multiple of `h=B*2^-p`. Store scalar records in units `h/32`. Then:

- Each scalar instruction is exact, with no rounding defect.
- The final public error is at most `(1323/2048)*B*2^-t`, including input quantization.
- Every ideal-plus-error field norm is less than `1024 B`.
- `p+16` signed bits suffice per stored real component; `p+21` suffice for scalar temporaries.

The executor accepts integer native returns in units h. It does not implement a native child. If a child has internal error, that error and the final quantization must together meet the stated completed-output bound; final rounding alone does not pay for internal errors. Exact COPY and owned reset remain explicit primitives. Their tape placement and cleanup implementation are open. No new kappa or selected-frontier change follows.

The grid checker treats each rounded native return as a fresh arbitrary grid vector. Its five-bit reserve is sharp in this interface model: an explicit basis assignment reaches an odd multiple of h/32. That assignment need not be attainable by the fixed source native operators. Four bits fail the emitted scalar trace; no physical optimum is claimed.

Run `python3.12 -B scripts/research_package.py --package research/p104-exact-scalar-records`. Verification is read-only; only `verify.py --write` replaces RESULT.json. Every symbolic prefix is compared with a separate integer-row calculation. A reverse signed calculation checks all 799 final error rows. Twelve independent native-return fixtures compare all 273,636 scalar-record events with a rational interpreter. The source endpoint, frames, ownership and complete invoice are also checked.

The maximum error amplification is 1323/2 at the final public boundary and 2764 over all prefixes, with unit defects at each input and native return. These are independent-defect coefficients, not errors observed from a particular physical rounding algorithm. The source ideal row-norm bound is 850. PROOF.md gives the grid, range and precision implications.

## Open next questions

Implement one native child with the coarse return grid and the completed absolute-error bound. Price the full internal precision, conversion, record access and cleanup. Bind exact COPY and reset to the physical owner model. The scalar component is ready for that interface test; it does not justify another word search or a changed exponent.

## Credit

Adam Gall supplied the native-only signed-error method in PR2096. Arham Tahir, Nick Petalas and ywz65 supplied the physical dual and whole-word exact-grid precedents. Nick Petalas supplied the rank-seven coefficient-grid method and its model limitations. DreamingOfClouds supplied PR6030; David Arias, Cinna Davis, Gareth Davidson, Ali Romman and all retained P104/native/compiler authors keep their credit. This package applies those principles to a new rounded-return interface on the selected word and supplies its literal integer scalar executor. Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Independent human acceptance and the five framework assumptions remain open.
