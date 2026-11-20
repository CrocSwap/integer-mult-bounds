/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg14_ok : P.seg ck14 seg14 ck15 = true := by decide +kernel
theorem seg15_ok : P.seg ck15 seg15 ck16 = true := by decide +kernel
end UniInhabitWs4.Tabs
