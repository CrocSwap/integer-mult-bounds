/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg12_ok : P.seg ck12 seg12 ck13 = true := by decide +kernel
theorem seg13_ok : P.seg ck13 seg13 ck14 = true := by decide +kernel
end UniInhabitWs4.Tabs
