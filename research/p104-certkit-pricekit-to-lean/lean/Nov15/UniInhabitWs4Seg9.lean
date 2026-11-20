/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg18_ok : P.seg ck18 seg18 ck19 = true := by decide +kernel
theorem seg19_ok : P.seg ck19 seg19 ck20 = true := by decide +kernel
end UniInhabitWs4.Tabs
