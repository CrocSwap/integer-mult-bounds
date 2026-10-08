import Std

/-!
Bookkeeping behind the all-cardinality fixed-target assignment objective.
The geometric/profile contracts supplying these quantities are separate.
This identity is valid for exact integer-scaled quantities; the replay uses
rigorous rational enclosures for the true characteristic weights.
-/
namespace MatrixMatchingDual

theorem feasibility_slack_normal_form (m W repetitions K A edgeSum small large : Int) :
    (A+repetitions*(edgeSum-K*(small+large)))-m*(W-repetitions*K) =
      A-m*W+repetitions*(edgeSum+K*(m-small-large)) := by
  grind

end MatrixMatchingDual
