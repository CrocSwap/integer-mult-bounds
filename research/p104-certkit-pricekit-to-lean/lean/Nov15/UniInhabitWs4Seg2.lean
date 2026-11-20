/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg4_ok : P.seg ck4 seg4 ck5 = true := by decide +kernel
theorem seg5_ok : P.seg ck5 seg5 ck6 = true := by decide +kernel
end UniInhabitWs4.Tabs
