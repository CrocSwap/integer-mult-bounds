# Two fixed repair cases for the role-275 fusion

Use the exact #7481 native word and signed #7113 caller. The two role-275 MOVEs are 3→93 at 31441 and 93→312 at 31450. They have rank one each. The direct route 3→312 has rank two. The old chart-93 ADD31442 updates role 275 using role 274 after role 274 arrives at MOVE31438 and adds the literal input row of role 100 at ADD31439. That row is exactly \(x_{100}\).

## Source-side repair at 31438

Place the relocated ADD on chart 3 just before MOVE31438. Grant every old live row on chart 3 at that cut and arbitrary rational linear operations. On the unit original input \(x_{100}=1\), all 898 available rows vanish. The required old role-274 contribution before ADD31442 takes value one. The missing contribution therefore cannot be formed from the source bank. The forward literal propagation and separate reverse row extraction establish the same exact separator.

## Delayed repair on chart 312

Grant the direct role-275 arrival its full old value \(A\) before ADD31452 except for \(x_{100}\). Only the old role-77 MOVE31451 may carry an arbitrary additional scalar. The two old values just before ADD31452 are \((A,B)\). The old word then adds \(B\) to role 275 and subtracts half the resulting role-275 value from role 77 at ADD31458. Both old resulting rows are required at this deadline. The fixed arrival \(A-x_{100}\) vanishes on both unit inputs \(x_{100}=1\) and \(x_{77}=1\). Forward replay gives old pairs \((1,0)\), \((0,1)\) before the block and \((1,-1/2)\), \((1,1/2)\) after it. The determinant of the two required output evaluations is one. Thus their classes are independent modulo the granted row. An arbitrary rational form on one additional scalar gives at most one new class. The chart contains only these two original roles at ADD31452, and the literal itinerary has no later old chart-312 arrival through event 31848.

## Directed price

The 17 signed calls would remove 34 rank-one and add 17 rank-two paid positions. With productive ranks fixed, the directed gross is \(17(2-2^{1-C})\) on the exact incumbent crossing bracket. Both endpoints bound it tightly near 0.08584222521755124 raw. One new rank-one recursive position per call costs 17 raw, before any routing, restoration, ownership, precision or tape charges. Each of the two fixed repairs fails even with arbitrary rational correction and free ancillary work. Other cuts or changed arrival encodings require separate evidence.
