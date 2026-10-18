/- Syntax and negative-control fixture only. This is not an HPE theorem.
   The explicit extra axiom below is deliberately forbidden by the audit.
   Apache-2.0. Hanson Sun, with OpenAI Codex assistance. -/
namespace HPEInventoryFixture
theorem clean : True := True.intro
theorem ext (p q : Prop) (h : p ↔ q) : p = q := propext h
axiom extra : False
theorem bad : False := extra
end HPEInventoryFixture

#print axioms HPEInventoryFixture.clean
#print axioms HPEInventoryFixture.ext
  #print axioms HPEInventoryFixture.bad
