# Attribution and license

This contribution is by Jerry Chen (@CubeJerry), with substantial OpenAI
Codex assistance in research, implementation, verification and writing.
It is offered under the repository's Apache-2.0 license (../../LICENSE).

The baseline word and its exact interface checker are from DreamingOfClouds'
PR589 on eumemic's PR555, retaining the PR543, PR545, PR510 and earlier
supplier lineage. Their existing notices and licenses remain unchanged.
Dylan Crow authored the record exporter and generalized native checker
interfaces with Anthropic Claude assistance. DaysSky supplied the bridged
stage schedule generalized in columns_k.cpp; the earlier native checker
and source527 credits remain in their pinned repository files.

The new search and verifier were written for this experiment. Positive
integer row-subtraction factorization and the source-bound block verification
pattern also appear in concurrent PR857 (@zeusinsight), PR873/PR891
(@navinor), PR880 (@Deftsalt-debug) and PR884 (@martinxxx9). Their circuits
and code are not imported. PR891's single-write obstruction for frame 522
motivated allowing repeated writes and intermediate donors here.

Gareth Davidson (@bitplane), PR904 at
`33b9175c345bcd0f21b95d29f37cb95fffd5a134`, independently shortens one
four-register interval inside this block by one ADD, as part of a broader
prefix-resynthesis package. That concurrent result is credited and its
partial overlap is detailed in README.md; no combined saving is claimed.

The Python positive-prefix replay follows the contract and exact payload
formula of the pinned native checkers, with attribution above; the C++
checkers are compiled unmodified. These checks are independent of the search
but reuse the inherited geometry/interface and native checker implementation.
No literature-priority claim or full independent theorem audit is made.
