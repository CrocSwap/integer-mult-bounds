/* Independent scalar reconstruction, enabled only in verification builds.
 * Tekalign / substantial OpenAI Codex assistance, Apache-2.0. */
static void check_state(void) {
    uint64_t e=0,o=0,a=0,b=0,c=0;
    unsigned __int128 visited=0;
    for(int i=0;i<es;i++) {
        e|=UINT64_C(1)<<((E[i]^q)>>1); visited|=bit(E[i]);
        for(int j=0;j<i;j++) a|=UINT64_C(1)<<((E[i]^E[j])>>1);
        for(int j=0;j<os;j++) c|=UINT64_C(1)<<((E[i]^O[j])>>1);
    }
    for(int i=0;i<os;i++) {
        o|=UINT64_C(1)<<((O[i]^q)>>1); visited|=bit(O[i]);
        for(int j=0;j<i;j++) b|=UINT64_C(1)<<((O[i]^O[j])>>1);
    }
    int ac=0,bc=0,cc=0;
    for(int i=0;i<(1<<(N-1));i++) {
        ac+=(int)((a>>i)&1); bc+=(int)((b>>i)&1); cc+=(int)((c>>i)&1);
    }
    if(e!=epoints || o!=opoints || a!=ee || b!=oo || c!=eo || visited!=seen ||
       even_excess!=es*(es-1)/2+os*(os-1)/2-ac-bc || odd_excess!=es*os-cc) {
        fputs("STATE_ORACLE_MISMATCH\n",stderr); exit(3);
    }
}
