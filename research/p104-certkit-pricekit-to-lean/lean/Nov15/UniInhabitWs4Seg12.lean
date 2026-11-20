/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg24_ok : P.seg ck24 seg24 ck25 = true := by decide +kernel
theorem seg25_ok : P.seg ck25 seg25 ck26 = true := by decide +kernel
end UniInhabitWs4.Tabs
