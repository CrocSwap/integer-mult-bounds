# RETYPE (Nov 20, Sonnet, Lean)
lean/decoder-duality/Nov15/WordRungPort.lean, kernel-checked 7 s, axioms [propext, Classical.choice, Quot.sound].
- UniPort.rung_port: params n, QR (mains 2n+2QR), h, rhoD, rhoR, S (stay mass), caller (L,T,P), kbar; Cert(cdat T - cdat P - L*PortInv) kbar + per-call rung premise hprice + wall premises + Valid => kappa < kbar.
- portInv_P104: PortInv 104 96 9 (56/104) (56/104) 0 = 400 8^s + 112(9^s-8^s) + 104(1+7^s-8^s).
- rung_port_P104 (= kappa_of_cert_dep recovered), rung_port_7113 (kappa < 93453742/10^10 via UniUniversal.cert7113).
P104-specific beyond parameters: hprice is discharged by BankBanner.price_hsX, which uses HSContract (104/104 rows, heights 0,1,8,9, ht<=9) and eight cut molecules over heights 0..9 (h=9 LP certificate), hbud from UniBud.cert (FceilBank, needs kbar>=.0093453742). Ports7113/DCount/foldBanked7113PD (word fold) not retyped; word-level (Trace) layer remains at P104.
