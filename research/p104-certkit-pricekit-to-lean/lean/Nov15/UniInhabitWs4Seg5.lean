/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg10_ok : P.seg ck10 seg10 ck11 = true := by decide +kernel
theorem seg11_ok : P.seg ck11 seg11 ck12 = true := by decide +kernel
end UniInhabitWs4.Tabs
