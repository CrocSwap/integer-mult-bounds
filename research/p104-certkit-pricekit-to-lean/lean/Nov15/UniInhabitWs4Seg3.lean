/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg6_ok : P.seg ck6 seg6 ck7 = true := by decide +kernel
theorem seg7_ok : P.seg ck7 seg7 ck8 = true := by decide +kernel
end UniInhabitWs4.Tabs
