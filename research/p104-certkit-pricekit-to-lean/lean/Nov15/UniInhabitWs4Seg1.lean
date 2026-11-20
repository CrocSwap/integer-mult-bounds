/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg2_ok : P.seg ck2 seg2 ck3 = true := by decide +kernel
theorem seg3_ok : P.seg ck3 seg3 ck4 = true := by decide +kernel
end UniInhabitWs4.Tabs
