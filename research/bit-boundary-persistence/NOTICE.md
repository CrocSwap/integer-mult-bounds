# Notice

New material is prepared for Ali Romman (@aliromman), with substantial
OpenAI Codex assistance. It is supplied under Apache-2.0, the repository
license. No independent human review is implied.

The candidate starts from DreamingOfClouds's PR589 tuning of eumemic's PR555
punctured word. The construction retains eumemic's PR543 L3 skeleton and
interleaved scalar interface, DreamingOfClouds's PR545 punctured-star geometry,
and the prior work identified in their source notices.

The native exporter and legality checks come from Dylan Crow's PR370 lineage.
The multi-stage column checker comes from DaysSky's PR381. The parent and
pricing engines come from DreamingOfClouds's PR463/510 and PR315 lineage.
Whole-residual idle hosting comes from DaysSky's PR442, with the owner and
replica checks from chafreaky's PR443/472 lineage. The scalar interface also
uses Zhihao Chen's PR425 work. Jacob Sussman introduced the E8 unit.

These tools are used from the two unchanged packages pinned in `SOURCES.json`.
Their source notices and licenses remain in those packages. The new builder
and independent record replay were written for this candidate. The new driver
uses the existing adapters and their existing supported parameters; it does
not change the pinned exporters, checkers or pricing engines.

Source inlining and early helper retirement are prior ideas. The related
PR429/515 and PR433/437 work is acknowledged. PR953, PR980, PR997, PR1001 and PR1015
were checked for overlap. This package claims one verified boundary and its
complete hosted invoice, not priority for a general circuit method.
