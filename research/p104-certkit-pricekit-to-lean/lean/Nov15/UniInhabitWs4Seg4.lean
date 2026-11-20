/- UniInhabitWs4Seg (lane UNI-INHABIT): the 26 replay segments of tWs4, each by kernel decide (Par.seg). -/
import Nov15.UniInhabitWs4Tabs
namespace UniInhabitWs4.Tabs
theorem seg8_ok : P.seg ck8 seg8 ck9 = true := by decide +kernel
theorem seg9_ok : P.seg ck9 seg9 ck10 = true := by decide +kernel
end UniInhabitWs4.Tabs
