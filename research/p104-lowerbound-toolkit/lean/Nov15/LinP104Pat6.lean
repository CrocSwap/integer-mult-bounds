import Nov15.LinP104Base
namespace P104
open P104Data

lemma patChunk6 : (List.range 13).all (fun u => patRow (78 + u)) = true := by decide +kernel

end P104
