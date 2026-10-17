cd ../E6SLACK2
for f in A0_R* A1_R* A1_free* B0_R* B1_R* B1_free* B2_R* B2_free*; do case $f in *.cnf) n=${f%.cnf}; s=$(date +%s); timeout 600 kissat -q $f $n.drat > $n.kis 2>&1; echo "$n rc=$? $(grep -E '^s ' $n.kis) $(( $(date +%s)-s ))s" >> kissat2.log;; esac; done
