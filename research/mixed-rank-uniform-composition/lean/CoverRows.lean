import Std

/-! All rows in a packet retain the full high-matrix range at every ancestor. -/
namespace CoverRows

def pack (radix group digit : Nat) : Nat := group*radix + digit

theorem pack_div {radix group digit : Nat} (h : digit < radix) :
    pack radix group digit / radix = group := by
  unfold pack
  rw [Nat.mul_comm group, Nat.mul_add_div (by omega), Nat.div_eq_of_lt h, Nat.add_zero]

theorem pack_mod {radix group digit : Nat} (h : digit < radix) :
    pack radix group digit % radix = digit := Nat.mul_add_mod_of_lt h

theorem pack_parts (radix i : Nat) :
    pack radix (i/radix) (i%radix) = i := Nat.div_add_mod' _ _

def split (L H A row : Nat) : Nat × Nat :=
  let a := row % A
  let u := row / A
  let h := u % H
  let t := u / H
  (t % L, pack A (pack H (t/L) h) a)

def join (L H A low packetRow : Nat) : Nat :=
  let a := packetRow % A
  let un := packetRow / A
  pack A (pack H (pack L (un/H) low) (un%H)) a

theorem split_number (L H A u l h a : Nat) (hl : l < L) (hh : h < H) (ha : a < A) :
    split L H A (pack A (pack H (pack L u l) h) a) =
    (l, pack A (pack H u h) a) := by
  simp [split, pack_mod ha, pack_div ha, pack_mod hh, pack_div hh, pack_mod hl, pack_div hl]

theorem join_number (L H A u l h a : Nat) (hh : h < H) (ha : a < A) :
    join L H A l (pack A (pack H u h) a) = pack A (pack H (pack L u l) h) a := by
  simp [join, pack_mod ha, pack_div ha, pack_mod hh, pack_div hh]

theorem packet_inverse (L H A : Nat) (hp : 0 < H) (ap : 0 < A)
    (low packetRow : Nat) (hl : low < L) :
    split L H A (join L H A low packetRow) = (low, packetRow) := by
  let a := packetRow % A
  let h := (packetRow / A) % H
  let u := packetRow / A / H
  have rep : pack A (pack H u h) a = packetRow := by
    simp only [u,h,a,pack_parts]
  have ha : a < A := Nat.mod_lt _ ap
  have hh : h < H := Nat.mod_lt _ hp
  rw [← rep, join_number L H A u low h a hh ha, split_number L H A u low h a hl hh ha]

theorem row_inverse (L H A : Nat) (lp : 0 < L) (hp : 0 < H) (ap : 0 < A) (row : Nat) :
    let packet := split L H A row
    join L H A packet.1 packet.2 = row := by
  let a := row % A
  let h := (row / A) % H
  let l := (row / A / H) % L
  let u := row / A / H / L
  have rep : pack A (pack H (pack L u l) h) a = row := by
    simp only [u,l,h,a,pack_parts]
  have ha : a < A := Nat.mod_lt _ ap
  have hh : h < H := Nat.mod_lt _ hp
  have hl : l < L := Nat.mod_lt _ lp
  dsimp only
  rw [← rep, split_number L H A u l h a hl hh ha, join_number L H A u l h a hh ha]

def activeRows (T L H D j : Nat) : Nat := T * (L*H)^(D-j) * H^j

theorem volume (T L H D j : Nat) (depth : j < D) :
    activeRows T L H D j = L * activeRows T L H D (j+1) := by
  have h : D-j = D-(j+1)+1 := by omega
  unfold activeRows
  rw [h, Nat.pow_succ, Nat.pow_succ H]
  ac_rfl

def slabs (rows stock : Nat) : Nat :=
  if rows % stock = 0 then rows/stock else rows/stock+1

theorem one_padding (rows stock : Nat) (hs : 0 < stock) (fits : stock ≤ rows) :
    rows ≤ slabs rows stock * stock ∧ slabs rows stock * stock < 2 * rows := by
  have rem := Nat.mod_lt rows hs
  have eqn := Nat.div_add_mod' rows stock
  by_cases eq : rows % stock = 0
  · simp only [slabs, eq, ite_true]
    omega
  · simp only [slabs, eq, ite_false, Nat.add_mul, Nat.one_mul]
    omega

end CoverRows

#print axioms CoverRows.packet_inverse
#print axioms CoverRows.row_inverse
#print axioms CoverRows.volume
#print axioms CoverRows.one_padding
