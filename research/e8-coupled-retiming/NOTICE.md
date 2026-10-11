# Attribution and scope of new work

Jacob Sussman supplied the E8 label family, circuit, scatter, frame scheduler,
checkers, price routines, and general proof framework in
`jacobalansussman/wht-power-saving-lean`, commit
`9c94857bbaee886f8649edee0bc2d3c738f9555e`.

`data/original.json.gz` is an unchanged copy from that commit. The new
certificate derives from that file. This package uses the repository's
[Apache-2.0 license](../../LICENSE). The source notices that apply to the
retained certificate are copied below.

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

## Upstream notice excerpts

The following text is copied from the copyright header and sections 4 and 8
of the [upstream NOTICE](https://github.com/jacobalansussman/wht-power-saving-lean/blob/9c94857bbaee886f8649edee0bc2d3c738f9555e/NOTICE).
References within these excerpts refer to that source repository.

```text
Walsh-Hadamard power saving (wht-power-saving-lean)
Copyright 2026 Jacob Sussman

Repository: https://github.com/jacobalansussman/wht-power-saving-lean

4. How the new files were made.
   Jacob Sussman made the new files on 2026-10-08, 2026-10-09 and 2026-10-10
   by directing a team of AI agents (Claude). The agents wrote the new Lean
   files, the certificate data and the generator scripts. They made the
   rebuild scripts under tools/rebuild/, in part by adapting programs of
   CrocSwap/integer-mult-bounds (section 6): ten of the thirteen on
   2026-10-09, tidied for this repository on 2026-10-10, and three on
   2026-10-10. On 2026-10-10 they also wrote the search programs under
   tools/e8/ and found with them the certificate of the fourth result
   (section 8). See README.md, section 4.

8. The certificate of the fourth result and the search programs.
   tools/certificate/gcert1-e8-r783.json.gz, the Lean data modules
   generated from it (Work/GCert/Data/Gen/E8*.lean, Work/GCert/Data/Gen/E8/
   and the modules of Work/GCert/Data/ with E8 or B2Ge8 in their names) and
   the Python programs under tools/e8/ were made by the agents for this
   repository on 2026-10-10 (section 4). The circuit in that certificate
   is not the circuit of section 6, and no data file of
   CrocSwap/integer-mult-bounds was loaded to make it. It uses three
   devices that were published by others in pull requests to that
   repository:
   - the in-place pair, a + b and a - b formed on the two arrays that held
     a and b: icekylinx (#184), carried in #191 and #193 (ikeboy);
   - the re-use of a finished helper with a compensating read: jamesyc
     (#124) and eumemic (#143);
   - the late pairing rule, the choice of which finished helper a new
     value takes: Chafik Boukhalfa (the account chafreaky), #200 and #233,
     and pull request #2 of this repository. The search programs apply the
     idea with a greedy rule of their own; his program, his pairs and his
     certificate were not used.
   No program of that repository is included in tools/e8/, imported or
   run by it. The programs of tools/e8/ have not been compared statement
   by statement with the programs of that repository, as those of
   tools/rebuild/ were (section 6). The integer programme of
   tools/e8/ is solved with the open-source solver HiGHS, called through
   SciPy (scipy.optimize.milp), with NumPy; none of the three is included
   here. The credits, with links, are in README.md ("Whose ideas the new
   unit uses") and in RELATED-WORK.md, section 8.
```
