## Result

The published literal CRT lifecycle package left its arithmetic join unexecuted.
This change builds the explicit 70-role union with the unchanged #7596 numerical
graph and runs one complete pinned current CRT producer invocation with both
providers literal.

The union contains 1,435,098 fixed R/W/M/J/H states. Numerical owners keep
roles 0..63; lifecycle reuses two of the four arithmetic selectors and places
its template/stack on separate roles. Only constant role renaming and state
offsets change the predecessor graphs.

The seven-bit source invocation returns lower 1, product 5 and right record
(3,5). It performs 82 additions, 63 comparisons, 14 divisions and 6
subtractions, including 63 aliased doublings. Its 2,723 literal calls cost
3,515,628 instructions; no old arithmetic or lifecycle provider is called
during the sealed producer/consumer interval.

## Integration and evidence

A real ordering issue is resolved and retained as a negative control:
Entry.close still queries arena.live, so lifecycle CLOSE must come last.
The suite checks exact ordered free stacks, every physical owner and
suspended head, full historical tails, output flags and values, and complete
reservation/setter/body costs.

The primitive domain includes every four-bit operand pair for comparison,
addition and subtraction, every aliased four-bit input, all four-bit
numerators with divisors 1..7, and listed wider cases at seven and nineteen
bits. Together with the source call it executes 18,380 public literal calls
and 31,886,648 literal instructions. Source-byte, physical-alias, sealed
fallback, premature-retirement and returning-carry controls are included.

Reproduce with:

    python3 -B scripts/research_package.py --package research/combined-crt-literal-services

Only a small generator and fourteen authenticated source files are committed.
The million-state graph is recreated in memory. Primary replay used roughly
510 MiB peak RSS and 28 seconds on the recorded CPython 3.12 environment.

## Boundaries and credit

This is one supplied eager Entry. Higher control, Word predicates, record
interfaces, blank grants and changing-Entry attachment remain premises.
Original Entry.close is executed as a separately priced retained service;
the residual native symbol bill is 2,518, including its 468 actions.

No complete controller lowering, common whole-caller tariff, new kappa or
foundational-assumption discharge is claimed. The selected record is unchanged.

Sources: canonical main e54523517; #7596 at ee6005fe241ab947e511fe9f6d86f5f4fa58478b;
published lifecycle at 39c309f1aa72af12669d37ae055da0ece1ae0e7d.
JoyboyBrian's current CRT source and admission, the inherited entry/ownership
lineage, and both predecessor graph packages retain their credit.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.


## Independent review

The separate root review verifies the entire fixed-state relocation, recovering
both immutable predecessor hashes. A newly written raw-cell interpreter runs
348 composed calls at precisions 5, 9 and 17, checks exact combined tariffs and
historical contents, and rejects an omitted template role relocation. It uses
none of the author runtime or oracle classes. The complete source execution
and the original registered normal/optimized receipt remain separate checks.
See REVIEW.md and review/RESULT.json for the precise review scope.
