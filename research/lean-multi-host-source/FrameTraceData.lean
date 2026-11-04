import FrameTraceCheckpoints
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace SourceFrameTrace
open FrameTrace
open TreeReplay (Tree)
theorem scalar_word : forward.map Entry.scalar = SourceMatrix.forwardWord := by
  simp only [forward, chunks, List.flatten_cons, List.flatten_nil, List.map_append, List.map_nil, project0, project1, project2, project3, project4, project5, project6, project7, project8, project9, project10, project11, project12, project13, project14, project15, project16, project17, project18, project19, project20, project21, project22, project23, project24, project25, project26, project27, project28, project29, project30, project31, project32, project33, project34, project35, project36, project37, project38, project39, project40, project41, project42, project43, project44, project45, project46, project47, project48, project49, project50, project51, project52, project53, project54, project55, project56, project57, project58, project59, project60, project61, project62, project63, project64, project65, project66, project67, project68, project69, project70, project71, project72, project73, project74, project75, project76, project77, project78, project79, project80, project81, project82, project83, project84, project85, project86, project87, project88, project89, project90, project91, project92, project93, project94, project95, SourceMatrix.forwardWord, SourceMatrix.forwardChunks]
theorem forward_checked : runChecked forward (state0,true) = (state96,true) := finish0
theorem forward_valid : Valid forward state0 := checked_valid forward (state0,true) (congrArg Prod.snd forward_checked)
#print axioms scalar_word
#print axioms forward_checked
#print axioms forward_valid
end SourceFrameTrace
