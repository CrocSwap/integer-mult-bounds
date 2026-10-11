# Attribution and scope of new work

Jacob Sussman supplied the E8 label family, circuit, scatter, frame scheduler,
checkers, price routines, and general proof framework in
`jacobalansussman/wht-power-saving-lean`, commit
`9c94857bbaee886f8649edee0bc2d3c738f9555e`.

The files in `vendor/` are unchanged copies from that commit. Its Apache-2.0
license and notices are included. `data/original.json.gz` is also unchanged.
The new certificate derives from that file. Sussman's upstream notice retains
the attribution for earlier contributions to the construction.

DaysSky's CrocSwap PR352 supplies the connection to the complex branch and the
exact coarse-moment convention used here. Its commit
`04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2`, source paths, and hashes are
recorded in `sources.json`. Prior frame-retiming contributions
include CrocSwap PR328 and PR350. No claim of priority for the general method is
made.

The new work consists of four explicit frame changes, a deterministic
generator, independent scalar and frame checks, exact rational cost bounds,
and the short cost proof. OpenAI Codex and its research agents supplied
substantial assistance. New contributions are
offered under the repository's Apache-2.0 license.

Attribution does not imply review or endorsement by the credited authors.
