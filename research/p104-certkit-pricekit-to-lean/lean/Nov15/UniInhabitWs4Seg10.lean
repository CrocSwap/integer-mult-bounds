/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg20_ok : P.seg ck20 seg20 ck21 = true := by decide +kernel
theorem seg21_ok : P.seg ck21 seg21 ck22 = true := by decide +kernel
end UniInhabitWs4.Tabs
