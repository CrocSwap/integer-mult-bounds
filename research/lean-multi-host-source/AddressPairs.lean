import FramedReplay
import CoordinateSwap

/-! Explicit conversion between the source's pair of address vectors and
the hosting framework's vector of coordinate pairs. -/
namespace AddressPairs

abbrev Vectors (ι : Type) (K : Type) := (ι → K) × (ι → K)

def join (p : Vectors ι K) : WholeHosting.Address ι K := fun i => (p.1 i, p.2 i)
def split (a : WholeHosting.Address ι K) : Vectors ι K :=
  (fun i => (a i).1, fun i => (a i).2)

theorem split_join (p : Vectors ι K) : split (join p) = p := rfl
theorem join_split (a : WholeHosting.Address ι K) : join (split a) = a := rfl

def gauge (g : FramedReplay.Gauge (Vectors ι K)) :
    FramedReplay.Gauge (WholeHosting.Address ι K) where
  forward a := join (g.forward (split a))
  inverse a := join (g.inverse (split a))
  inverse_forward a := by simp only [split_join, g.inverse_forward, join_split]
  forward_inverse a := by simp only [split_join, g.forward_inverse, join_split]

theorem relative_gauge (g h : FramedReplay.Gauge (Vectors ι K))
    (a : WholeHosting.Address ι K) :
    (gauge g).forward ((gauge h).inverse a) = join (g.forward (h.inverse (split a))) := by
  simp only [gauge, split_join]

def swapVectors (mask : WholeHosting.Mask ι) (p : Vectors ι K) : Vectors ι K :=
  (fun i => if mask i then p.2 i else p.1 i,
   fun i => if mask i then p.1 i else p.2 i)

theorem join_swap (mask : WholeHosting.Mask ι) (p : Vectors ι K) :
    join (swapVectors mask p) = WholeHosting.swapAddress mask (join p) := by
  funext i
  cases hm : mask i <;> simp [join, swapVectors, WholeHosting.swapAddress, hm]

theorem relative_coordinate (g h : FramedReplay.Gauge (Vectors ι K))
    (mask : WholeHosting.Mask ι)
    (hrel : ∀ p, g.forward (h.inverse p) = swapVectors mask p)
    (a : WholeHosting.Address ι K) :
    (gauge g).forward ((gauge h).inverse a) = WholeHosting.swapAddress mask a := by
  rw [relative_gauge, hrel, join_swap, join_split]

end AddressPairs
