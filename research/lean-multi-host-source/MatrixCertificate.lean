import MatrixCheckpoints
namespace SourceMatrix
open TreeReplay

theorem literal_word_checked : runCheckedRows forwardWord (initial,true) = (expected,true) :=
  (chunks_flatten forwardChunks (initial,true)).symm.trans runFull_checked

theorem literal_word_rows : runRows forwardWord initial = expected :=
  (checked_projection forwardWord (initial,true)).symm.trans
    (congrArg Prod.fst literal_word_checked)

#print axioms literal_word_checked
#print axioms literal_word_rows
end SourceMatrix
