/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg0_ok : P.seg ck0 seg0 ck1 = true := by decide +kernel
theorem seg1_ok : P.seg ck1 seg1 ck2 = true := by decide +kernel
end UniInhabitWs4.Tabs
