/-
V2FloorKernelCheck (lane LEAN-KERNEL, Nov 16): the FLAG-cover checker as kernel-evaluable Bool functions, and its
soundness theorem `kernel_intFeasible`: if the data checks return `true`, then `IntFeasible` holds for the pairs
listed in the data. No successor table is needed:
  * edge X<Y with dim X = a ≥ 3: X lies in some hyperplane H = h^⊥ (`exists_hyperplane`); the F-row (h, a, b)
    bounds every such edge (pairs with L ⊆ H, dim L ≤ a);
  * a = 2: X = span{l, w} where l is the first basis mask of a served pair's L; the kernel enumerates every l with a
    table entry and EVERY w < 512 (`planeAll`), and computes the E-row of that plane from the line table `LT`;
  * a = 1: X = span{l} (`lineOK`).
Rows use the τ form of the Gaussian top-M rule (`tau_bound`); τ is free (any value is sound): E rows compute
τ = Mt-th largest weight in the kernel, F rows read it from the certificate.
-/
import Nov15.V2FloorKernelTau

namespace V2Floor
open Finset

/-! ### data formats -/

/-- a pair (record): L basis masks, biorthogonal witnesses, packed cumulative levels (10 fields × 40 bits),
index into the reference pair list. -/
structure KRec where
  lb : List ℕ
  lw : List ℕ
  c : ℕ
  orig : ℕ
deriving Inhabited

/-- a group of pairs sharing the upper space U = Usub uh (uw: biorthogonal witnesses). -/
structure KGrp where
  uh : List ℕ
  uw : List ℕ
  recs : List KRec
deriving Inhabited

/-- line-table entry: a copy of record (g, j) with its group's checks. -/
structure KEnt where
  g : ℕ
  j : ℕ
  uh : List ℕ
  lb : List ℕ
  c : ℕ

inductive BT where
  | lf (l : List KEnt)
  | nd (l r : BT)

def BT.get : BT → ℕ → ℕ → List KEnt
  | .lf l, _, _ => l
  | .nd _ _, 0, _ => []
  | .nd l r, d + 1, v => if v.testBit d then r.get d v else l.get d v

def fld (c k : ℕ) : ℕ := (c >>> (40 * k)) % 1099511627776
def seg (c a b : ℕ) : ℕ := fld c b - fld c a

/-! ### data validity -/

def cumOK (c nlb nuh : ℕ) : Bool :=
  (fld c 0 == 0) && (List.range 9).all (fun k => decide (fld c k ≤ fld c (k + 1)) &&
     (fld c k == fld c (k + 1) || (decide (nlb ≤ k) && decide (k < 9 - nuh))))

def recOK (nuh : ℕ) (r : KRec) : Bool :=
  !r.lb.isEmpty && allLt r.lb && allLt r.lw && biorth r.lb r.lw && cumOK r.c r.lb.length nuh

def grpOK (G : KGrp) : Bool :=
  !G.uh.isEmpty && allLt G.uw && biorth G.uw G.uh && G.recs.all (recOK G.uh.length)

/-- signature of the subspace Usub H on the probe masks P (equal subspaces give equal signatures). -/
def maskOf (P H : List ℕ) : ℕ :=
  P.foldl (fun acc v => if chk H v then 2 * acc + 1 else 2 * acc) 0

def sortedLt : List ℕ → Bool
  | a :: b :: l => decide (a < b) && sortedLt (b :: l)
  | _ => true

def nsOK (NS : List KGrp) (P : List ℕ) : Bool := NS.all grpOK && allLt P && sortedLt (NS.map (fun G => maskOf P G.uh))

def entOK (NS : List KGrp) (v : ℕ) (e : KEnt) : Bool :=
  decide (e.g < NS.length) && decide (e.j < (NS.getD e.g default).recs.length) &&
  decide (e.uh = (NS.getD e.g default).uh) && decide (e.lb = ((NS.getD e.g default).recs.getD e.j default).lb) &&
  decide (e.c = ((NS.getD e.g default).recs.getD e.j default).c) && decide (e.lb.headD 0 = v)

def ltOK (NS : List KGrp) (LT : BT) : Bool := (List.range 512).all (fun v => (LT.get 9 v).all (entOK NS v))

def complOK (NS : List KGrp) (LT : BT) : Bool :=
  (List.range NS.length).all (fun g => (List.range (NS.getD g default).recs.length).all (fun j =>
    !(decide (((NS.getD g default).recs.getD j default).lb.length ≤ 2)) ||
    (LT.get 9 (((NS.getD g default).recs.getD j default).lb.headD 0)).any (fun e => decide (e.g = g) && decide (e.j = j))))

/-! ### rows -/

/-- Σ_{d=b}^{8} Mt b d · τ d. -/
def mtau (b : ℕ) (τ : ℕ → ℕ) : ℕ := ((List.range' b (9 - b)).map (fun d => Mt b d * τ d)).sum

def kth (m : ℕ) (l : List ℕ) : ℕ := (l.insertionSort (fun x y => decide (y ≤ x))).getD (m - 1) 0

def wE (ms : List KEnt) (a b g : ℕ) : ℕ := ((ms.filter (fun e => decide (e.g = g))).map (fun e => seg e.c a b)).sum

def keysE (ms : List KEnt) : List (ℕ × ℕ) := (ms.map (fun e => (e.g, 9 - e.uh.length))).dedup

def tauE (ms : List KEnt) (a b d : ℕ) : ℕ :=
  kth (Mt b d) (((keysE ms).filter (fun k => decide (k.2 = d))).map (fun k => wE ms a b k.1))

def rowE (ms : List KEnt) (a b : ℕ) : ℕ :=
  ((keysE ms).map (fun k => if b ≤ k.2 then wE ms a b k.1 - tauE ms a b k.2 else 0)).sum + mtau b (tauE ms a b)

def inPlane (l w v : ℕ) : Bool := v == l || v == w || v == (l ^^^ w)

def memE (l w : ℕ) (e : KEnt) : Bool := e.lb.all (inPlane l w) && chk e.uh l && chk e.uh w
def memE1 (l : ℕ) (e : KEnt) : Bool := e.lb.all (fun v => v == l) && chk e.uh l

def planeMs (LT : BT) (l w : ℕ) : List KEnt :=
  ((LT.get 9 l) ++ (LT.get 9 w) ++ (LT.get 9 (l ^^^ w))).filter (memE l w)

def planeOK (LT : BT) (T : ℕ → ℕ → ℕ) (l w : ℕ) : Bool :=
  (List.range' 3 6).all (fun b => decide (rowE (planeMs LT l w) 2 b ≤ T 2 b))

def planeR (LT : BT) (T : ℕ → ℕ → ℕ) (l lo n : ℕ) : Bool :=
  (List.range' lo n).all (fun w => w == 0 || w == l || !(decide (w < w ^^^ l)) || planeOK LT T l w)

def planeAll (LT : BT) (T : ℕ → ℕ → ℕ) (l : ℕ) : Bool :=
  (LT.get 9 l).isEmpty || (List.range 16).all (fun i => planeR LT T l (32 * i) 32)

def lineOK (LT : BT) (T : ℕ → ℕ → ℕ) (l : ℕ) : Bool :=
  (List.range' 2 7).all (fun b => decide (rowE ((LT.get 9 l).filter (memE1 l)) 1 b ≤ T 1 b))

def memF (h a : ℕ) (r : KRec) : Bool := decide (r.lb.length ≤ a) && r.lb.all (fun v => par9 (h &&& v) == 0)

def wF (h a b : ℕ) (G : KGrp) : ℕ := ((G.recs.filter (memF h a)).map (fun r => seg r.c a b)).sum

def rowF (NS : List KGrp) (h a b : ℕ) (τ : ℕ → ℕ) : ℕ :=
  (NS.map (fun G => if b ≤ 9 - G.uh.length then wF h a b G - τ (9 - G.uh.length) else 0)).sum + mtau b τ

def slotF (a b d : ℕ) : ℕ := ((a - 3) * 5 + (b - 4)) * 5 + (d - 4)

def rowsF : List (ℕ × ℕ) :=
  [(3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, 5), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8), (6, 7), (6, 8), (7, 8)]

def hypOK (NS : List KGrp) (T : ℕ → ℕ → ℕ) (td h : ℕ) : Bool :=
  rowsF.all (fun ab => decide (rowF NS h ab.1 ab.2 (fun d => fld td (slotF ab.1 ab.2 d)) ≤ T ab.1 ab.2))

/-! ### the abstract pairs -/

section abstract
variable (NS : List KGrp)

def grp (g : ℕ) : KGrp := NS.getD g default
def rcd (q : ℕ × ℕ) : KRec := (grp NS q.1).recs.getD q.2 default

def POS : Finset (ℕ × ℕ) :=
  (range NS.length).biUnion (fun g => (range (grp NS g).recs.length).image (fun j => (g, j)))

abbrev PS := {q // q ∈ POS NS}

def LBK (p : PS NS) : List ℕ := (rcd NS p.1).lb
def UHK (p : PS NS) : List ℕ := (grp NS p.1.1).uh
def numK (p : PS NS) (k : ℕ) : ℕ := if k < 9 then fld (rcd NS p.1).c (k + 1) - fld (rcd NS p.1).c k else 0

theorem mem_POS {q : ℕ × ℕ} : q ∈ POS NS ↔ q.1 < NS.length ∧ q.2 < (grp NS q.1).recs.length := by
  unfold POS; simp only [mem_biUnion, mem_range, mem_image]
  constructor
  · rintro ⟨g, hg, j, hj, rfl⟩; exact ⟨hg, hj⟩
  · intro h; exact ⟨q.1, h.1, q.2, h.2, rfl⟩

end abstract

end V2Floor
