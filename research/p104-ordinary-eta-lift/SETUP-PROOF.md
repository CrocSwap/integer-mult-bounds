# Fixed installer bound for larger height encodings

This lemma is independent of the ordinary-rate lift. It concerns the same signed binary and Gaussian words, the same finite couplings and floors, **two entry ordinary recipes, three terminal ordinary recipes, and two Gaussian recipes**, with every height satisfying `1024≤H<2^25`. For each of the two supplied profiles, the numerators and denominators of `κ` and `η`, and the positive stop denominator, must have at most 128 bits; the stop denominator is positive. These are encoding bounds, not rate-admission conditions. It carries forward the fixed source's indexed-action and arithmetic hypotheses. It does not certify a new supplier price, native opening, product, activation, precision, or portable execution trace.

## Which source paths depend on a height

The #8072 receipt's old `bit_length()≤20` assertion examines only the final ordinary height of each profile. It does **not** check the Gaussian height. The bound here explicitly checks all seven heights. In the restored fixed compiler, `prepare_native` calls `binary_recipe` for each ordinary height and `numerical_recipe` for each Gaussian height. `transport.Recipe.__init__` and `grades.WeightedRecipe.__init__` record the height and the integer `92H`; they keep the original word, rates, labels, coupling and references. The attributes `width` and `open()` create the large native value/calendar only when an active caller requests them. Fixed `compiler_state.construct` does not call either.

One additional path does construct a large integer: `retimed_supplier.Positive.__init__` passes `1 << rank_log` to its inherited initializer. Its carrier therefore contains `G+1` bits, as tested directly. This is not ignored as a fixed-size parameter. The two fixed profiles and their source arguments have at most seven height records, two explicit Gaussian carriers and the same raw-source graphs, grade cells and role streams. The replay explicitly enforces the 128-bit scalar-encoding guard for both profiles; larger encodings are outside this statement.

For all seven `H<2^25`, `92H<2^32`; a lazily materialized `2^(92H)` would have fewer than `2^32+1` bits. The `1024H` native control exponent is below `2^35`. Each materialized positive carrier `2^G` has at most `2^25` bits. Each is below the source's permitted individual datum bound `w=2^38` bits. This is a width check, not by itself an action-count proof. Active calendars and input-dependent geometry have separate recurring charges.

## Count and charge the changed work

Keep the source's original bound of `2^68` indexed actions on the unchanged graph and raw coupling construction. The only additional profile-dependent work is bounded separately. Use a fixed 25-cell binary countdown and fixed work tapes, as in the source's serial arithmetic model. To produce a carrier and at most 15 extra copies, place the outputs on 16 work tapes, write the leading one, and generate all following zeros while decrementing the shared countdown. One decrement and zero test, including returning the countdown head, fit in four 25-cell passes plus 25 digit writes; allow 512 moves or writes per bit. The 16 output writes and advances need 32 more; allow 256. Rewinding and clearing all 16 streams takes at most 32 moves or writes per position; allow another 256. The remaining 1,024 per bit covers delimiters, copying the initial 25-bit counter, boundary handling and cleanup. Thus 2,048 elementary tape moves or writes per bit is a conservative allowance. This is an explicit fixed-multitape serial construction, not a claim that arbitrary copies on one tape can be made in linear time. Even charging two maximal carriers, plus `2^24` transitions for each of seven recipe parameter constructions and their bounded scalar metadata, gives

```
2·2048·(2^25+1) + 7·2^24 = 137556398080 < 2^40.
```

The per-recipe allowance is conservative for a fixed number of comparisons and assignments on the at-most-32-bit `H` and `92H` integers and the bounded scalar metadata. Charge each of the newly counted elementary steps as an additional indexed action, then apply the full source lookup and rational-arithmetic price to every action; this is conservative even when an action is only a tape move. The fixed-source parsing, charts, coupling, directory traversal and their arbitrary lookups retain their old full charges. The inherited positive initializer stores the carrier by reference; the copies above are an additional conservative allowance, not an observed count. A different constructor that materializes a native calendar, changes the word, grows the stage count, or performs additional height-dependent work needs a new bound. We add `2^40` rather than assuming slack inside the original action census.

Write

```
n = 2^68 + 2^40
w = 2^38,  h = 2w+2
S = 4wn
L = 8S·512·128
E = 2^16(h+4)(7h+9) + 8·2^16(h+4)^2.
```

Using the source's same complete indexed lookup, serial arithmetic and `2^32` parsing/cleanup multiplier, the conservative transition bound is

```
(n+1)(L+E+2^120)2^32
= 217364571993743287866367176320080817069553173293686105666269057384448
< 2^228.
```

The exact arithmetic is in `setup_scaling.py`. The proof uses the source's prior `2^68` action and `w=2^38` datum premises; it does not derive them from a host runtime measurement.

## Finite falsification and source identity

Run `python3.12 -IB setup_scaling.py`. It authenticates and reconstructs the #8072 source, forces both recipe `width` properties and `open()` methods to raise if the fixed constructor touches them, and executes the actual fixed producer and directory serializer on four profiles: #8072; the ordinary η witness; and the 21-bit and 25-bit Gaussian examples. All four created 2,407,819 records, with the same retained raw source objects and 267-bit largest directory integer. The two actual positive carriers contain 1,860,555 and 18,845,937 bits. The direct exact-height guard accepts `2^25-1` and rejects `2^25`. Results and hashes are in `SETUP-RESULT.json`.

The finite replay uses `compiler_state.construct`, `tape_directory.dump` and the source's record census. The two enlarged positive suppliers are separately instantiated to check the carrier bit lengths; the directory census does not serialize those carriers. It is **not** the inherited WASI fuel trace or its `2^113` portable setup certificate. The copied historical portable `producer.py` has literal old-profile assertions and needs a new, separately tested trace before any such claim can be made. The written extension uses the original all-input serial model, not the host elapsed time. Directory hashes in the receipt record the observed CPython execution; they are not required to match across Python builds or object-layout variations.

The recorded source identities are #8072 head `75f7e1c44f48c43983016bcf8878c4d9e5e87c62` and #8057 head `cbe847a953b971f9c6c5a0a6661e2008acd29086`. The principal restored SHA-256 bindings are `transport.py` `9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818`, `grades.py` `6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d`, and `retimed_supplier.py` `2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c`. The bootstrap checks the nested manifests and source overlays; `witness.py` also compares the retained files to the recorded #8072 changed-file Git blobs. This byte check is not by itself a Git-history check. Original notices are retained in `original/` and the peer archive.
