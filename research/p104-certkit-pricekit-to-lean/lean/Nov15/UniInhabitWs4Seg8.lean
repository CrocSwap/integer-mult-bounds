/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg16_ok : P.seg ck16 seg16 ck17 = true := by decide +kernel
theorem seg17_ok : P.seg ck17 seg17 ck18 = true := by decide +kernel
end UniInhabitWs4.Tabs
