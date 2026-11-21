import Nov15.LinP104Base
namespace P104
open P104Data

lemma patChunk4 : (List.range 13).all (fun u => patRow (52 + u)) = true := by decide +kernel

end P104
