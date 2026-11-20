/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg22_ok : P.seg ck22 seg22 ck23 = true := by decide +kernel
theorem seg23_ok : P.seg ck23 seg23 ck24 = true := by decide +kernel
end UniInhabitWs4.Tabs
