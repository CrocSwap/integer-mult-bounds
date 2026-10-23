cd ../E6SLACK2
python3 cnf2.py A0.cand A0.cnf 0 6 6 5 5 5 4; python3 cnf2.py A1.cand A1.cnf 1 6 6 5 5 5 4
python3 cnf2.py B0.cand B0.cnf 0 6 6 6 4 4 4; python3 cnf2.py B1.cand B1.cnf 1 6 6 6 4 4 4; python3 cnf2.py B2.cand B2.cnf 2 6 6 6 4 4 4
cat > runk2.sh <<'EOS'
cd ../E6SLACK2
for f in A0_R* A1_R* A1_free* B0_R* B1_R* B1_free* B2_R* B2_free*; do case $f in *.cnf) n=${f%.cnf}; s=$(date +%s); timeout 600 kissat -q $f $n.drat > $n.kis 2>&1; echo "$n rc=$? $(grep -E '^s ' $n.kis) $(( $(date +%s)-s ))s" >> kissat2.log;; esac; done
EOS
