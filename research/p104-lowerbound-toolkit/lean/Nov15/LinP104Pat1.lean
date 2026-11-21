import Nov15.LinP104Base
namespace P104
open P104Data

lemma patChunk1 : (List.range 13).all (fun u => patRow (13 + u)) = true := by decide +kernel

end P104
