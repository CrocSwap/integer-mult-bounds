import Nov15.LinP104Base
namespace P104
open P104Data

lemma patChunk0 : (List.range 13).all (fun u => patRow (0 + u)) = true := by decide +kernel

end P104
