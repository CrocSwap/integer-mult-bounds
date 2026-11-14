# Attribution and scope

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. No independent human or formal-kernel acceptance is claimed.

Nick Petalas, CrocSwap/integer-mult-bounds#7504 at
4eece58f5cebdb70a92d65447974f1c02383f60b, supplied the direct canonical
padded-rotation predicate, endpoint formulas and exact child closure.
His unmodified proof, source manifest and evaluator are retained. These
mathematical results and arithmetic complexity are credited prior work.

Cinna Davis / 1337isnot1337 #4100 supplied the original deterministic Beneš
compiler and padded rotation. Its canonical check_batched_crt.py and NOTICE
remain unmodified. ToikY #4192 supplied generic arena lowering; JoyboyBrian
#5092/#5496 and successors supplied the encoded ROM/current-row context.
#7388's live CRT caller and #7390's sort fusion remain separate work.

The new contribution is the2096-location,14-tape graph, its format/domain
validation, owned-Boolean/cleanup/guard contracts, complete scan costs and
historical-backing bound. No predecessor formula is claimed anew. No full
caller or selected assumption is discharged and no new kappa is claimed.
