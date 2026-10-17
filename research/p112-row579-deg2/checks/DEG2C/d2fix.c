// DEG2C impl: mask-level model. own E8 (Bourbaki, same construction as R579/b.c), reuse b.c slot-cover oracle.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64; typedef struct{u64 a,b;} M2;
static int adjm[8][8],R[240][8],nR,pos[120][8],lab[120],perm[8][120];
static int ip(int*c,int*d){int s=0;for(int i=0;i<8;i++)s+=2*c[i]*d[i];for(int i=0;i<8;i++)for(int j=0;j<8;j++)if(adjm[i][j])s-=c[i]*d[j];return s;}
static inline int popc(M2 m){return __builtin_popcountll(m.a)+__builtin_popcountll(m.b);}
static inline M2 AND(M2 x,M2 y){M2 r={x.a&y.a,x.b&y.b};return r;}
static inline M2 OR(M2 x,M2 y){M2 r={x.a|y.a,x.b|y.b};return r;}
static inline M2 XOR(M2 x,M2 y){M2 r={x.a^y.a,x.b^y.b};return r;}
static inline M2 ANDN(M2 x,M2 y){M2 r={x.a&~y.a,x.b&~y.b};return r;}
static inline int isz(M2 x){return !(x.a|x.b);}
static inline int eq(M2 x,M2 y){return x.a==y.a&&x.b==y.b;}
static inline int sub(M2 x,M2 y){return isz(ANDN(x,y));}
static int cmp(const void*x,const void*y){const M2*p=x,*q=y;return p->a<q->a?-1:p->a>q->a?1:p->b<q->b?-1:p->b>q->b?1:0;}
// hash M2->int
#define HS (1<<20)
typedef struct{M2 k;int v;}HE; 
static HE*newh(){HE*h=calloc(HS,sizeof(HE));for(int i=0;i<HS;i++)h[i].v=-1;return h;}
static unsigned hf(M2 m){u64 x=m.a*0x9E3779B97F4A7C15ULL^(m.b+0x1234567)*0xC2B2AE3D27D4EB4FULL;x^=x>>29;return (unsigned)x&(HS-1);}
static int hget(HE*h,M2 m){unsigned i=hf(m);while(h[i].v>=0){if(eq(h[i].k,m))return h[i].v;i=(i+1)&(HS-1);}return -1;}
static void hput(HE*h,M2 m,int v){unsigned i=hf(m);while(h[i].v>=0)i=(i+1)&(HS-1);h[i].k=m;h[i].v=v;}
static inline int getb(M2 m,int t){return (t<64?m.a>>t:m.b>>(t-64))&1;}
static inline void setb(M2*m,int t){if(t<64)m->a|=1ULL<<t;else m->b|=1ULL<<(t-64);}
static M2 applyp(M2 m,int g){M2 r={0,0};for(int t=0;t<120;t++)if(getb(m,t))setb(&r,perm[g][t]);return r;}
// ---- cover oracle (b.c)
static int nd,dims[8],ns,sl[128];
typedef struct{int cnt,anchor,b[8],r;} Slot;
static int reduce(Slot*s,int x){for(int t=7;t>=0&&x;t--)if((x>>t&1)&&s->b[t])x^=s->b[t];return x;}
static int dfs(int i,Slot*S){
  if(i==ns)return 1;int seen_empty[8]={0};
  for(int k=0;k<nd;k++){Slot c=S[k];
    if(c.cnt==0){if(seen_empty[dims[k]])continue;seen_empty[dims[k]]=1;c.cnt=1;c.anchor=sl[i];Slot T[8];memcpy(T,S,sizeof(Slot)*nd);T[k]=c;if(dfs(i+1,T))return 1;continue;}
    int x=(sl[i]^c.anchor)&255;int y=reduce(&c,x);
    if(y){ if(c.r>=dims[k]-1)continue; int t=7;while(!(y>>t&1))t--; c.b[t]=y;c.r++; }
    c.cnt++;Slot T[8];memcpy(T,S,sizeof(Slot)*nd);T[k]=c;if(dfs(i+1,T))return 1;}
  return 0;}
static HE*cch;static int ccn=0;
static int coverable(M2 q){ if(popc(q)>28)return 0; int c=hget(cch,q);if(c>=0)return c;
  ns=0;for(int t=0;t<120;t++)if(getb(q,t))sl[ns++]=lab[t];
  Slot S[8];memset(S,0,sizeof S);int r=dfs(0,S);hput(cch,q,r);return r;}
// ---- data
static M2*LM;static int nL;static M2*AL;static int nA;static char*atype;static int cntT[8];
static const char*tn[]={"root","D7","A7","E6A1","E6","D6"};
static int USECOV=1,K,MODE; // 1: skip cover (size only)

static int Ln[8],Mx[8][8],nStack;static long cs[9],cc[9],bytyp[8];static int curty;
static int tri(int i,int j,int k){M2 a=AL[i],b=AL[j],c=AL[k];
  M2 e=OR(OR(ANDN(a,OR(b,c)),ANDN(b,OR(a,c))),ANDN(c,OR(a,b)));return isz(e);}
static int dirok(int i,int j){return i!=j||atype[i]>=4;}
typedef struct{long key;int*l;int n;}CE;static CE*cct;
static CE*cget(int a,int m){long key=(long)a*40000+m+1;unsigned h=(unsigned)((key*0x9E3779B97F4A7C15ULL)>>40)&((1<<22)-1);
 while(cct[h].key){if(cct[h].key==key)return &cct[h];h=(h+1)&((1<<22)-1);}
 int*l=malloc(4*64);int n=0,cap=64;for(int q=0;q<nA;q++)if(tri(a,m,q)){if(n==cap){cap*=2;l=realloc(l,4*cap);}l[n++]=q;}
 cct[h].key=key;cct[h].l=l;cct[h].n=n;return &cct[h];}
static int usedm[64],nused;
static int okall(int m){for(int z=0;z<nused;z++)if(!dirok(m,usedm[z]))return 0;return 1;}
static void ext(int n,M2 U);
static HE*lhg;
static void pickM(int n,int x,M2 U,int*C0,int nC0){
  if(x==n){ // choose L_n among C0
    for(int z=0;z<nC0;z++){int l=C0[z];M2 V=U;int ok=1;
      for(int y=0;y<n&&ok;y++){M2 lo=ANDN(ANDN(AL[Mx[y][n]],LM[Ln[y]]),LM[l]);V=OR(V,lo);if(popc(V)>28)ok=0;}
      if(!ok)continue;cs[n]++;if(USECOV&&!coverable(V))continue;cc[n]++;if(n==2||n==3||n==4||n==5)bytyp[n]+=0;
      Ln[n]=l;ext(n+1,V);}
    return;}
  CE*ce=cget(Mx[0][x],Mx[0][n]);
  for(int zz=0;zz<ce->n;zz++){int m=ce->l[zz];
    int ok=1;for(int y=1;y<x&&ok;y++)if(!tri(Mx[y][x],Mx[y][n],m))ok=0;
    if(!ok||!okall(m))continue;
    // note tri must hold for triple (y,x,n): masks M_yx, M_yn, M_xn
    Mx[x][n]=m;usedm[nused++]=m;pickM(n,x+1,U,C0,nC0);nused--;}
}
static M2 *Lrep;static int nLrep;
static void ext(int n,M2 U){
  if(n==K){bytyp[7]++;if(getenv("FIRST")){printf("FOUND K=%d L:",K);for(int z=0;z<K;z++)printf(" %d",Ln[z]);printf(" U=%d masks:",0);for(int x=0;x<K;x++)for(int y=x+1;y<K;y++)printf(" %d%d=%s#%d",x,y,tn[(int)atype[Mx[x][y]]],Mx[x][y]);printf("\n");exit(0);}return;}
  if(n==1){ // M01 fixed rep chosen by curty ; loop L1
    int m=hget(NULL,U)<0?0:0;}
  int lo_t=0,hi_t=nA;
  for(int m=0;m<nA;m++){
    int t=atype[m];
    if(MODE==1&&t!=0)continue;
    if(n==2&&MODE==0&&t==0)continue;
    if(!okall(m))continue;
    {CE*c1=cget(Mx[0][1],m);if(!c1->n)continue;}
    // L_n candidates for pair (0,n)
    int*C0=malloc(4*nL);int nC=0;
    for(int l=0;l<nL;l++){M2 V=OR(U,ANDN(ANDN(AL[m],LM[Ln[0]]),LM[l]));if(popc(V)<=28)C0[nC++]=l;}
    if(nC){Mx[0][n]=m;usedm[nused++]=m;pickM(n,1,U,C0,nC);nused--;}
    free(C0);}
}
int main(int argc,char**argv){
 K=atoi(argv[1]); // number of sevens target
 MODE=atoi(argv[2]);int mode=MODE; // 0: DEG2 (h01,h02 nonroot); 1: control all-root
 int only=argc>3?atoi(argv[3]):-1; // restrict type of h01 (1..5)
 USECOV=argc>4?atoi(argv[4]):1;
 nd=4;dims[0]=4;dims[1]=4;dims[2]=4;dims[3]=3;cch=newh();
 int E[7][2]={{0,2},{2,3},{3,4},{4,5},{5,6},{6,7},{1,3}};for(int i=0;i<7;i++){adjm[E[i][0]][E[i][1]]=adjm[E[i][1]][E[i][0]]=1;}
 for(int i=0;i<8;i++){memset(R[i],0,32);R[i][i]=1;}nR=8;
 for(int k=0;k<nR;k++)for(int i=0;i<8;i++){int al[8]={0};al[i]=1;int c=ip(R[k],al);int w[8];for(int j=0;j<8;j++)w[j]=R[k][j]-c*al[j];
  int f=0;for(int q=0;q<nR&&!f;q++)if(!memcmp(R[q],w,32))f=1;if(!f)memcpy(R[nR++],w,32);}
 int np=0;for(int k=0;k<nR;k++){int ok=1;for(int j=0;j<8;j++)if(R[k][j]<0)ok=0;if(ok){memcpy(pos[np],R[k],32);np++;}}
 if(nR!=240||np!=120)return 1;
 for(int t=0;t<120;t++){int l=256;for(int j=0;j<8;j++)l|=(pos[t][j]&1)<<j;lab[t]=l;}
 for(int g=0;g<8;g++)for(int t=0;t<120;t++){int al[8]={0};al[g]=1;int c=ip(pos[t],al);int w[8];int neg=0;for(int j=0;j<8;j++){w[j]=pos[t][j]-c*al[j];if(w[j]<0)neg=1;}
   if(neg)for(int j=0;j<8;j++)w[j]=-w[j];int f=-1;for(int q=0;q<120;q++)if(!memcmp(pos[q],w,32))f=q;if(f<0)return 2;perm[g][t]=f;}
 // L masks
 LM=malloc(sizeof(M2)*130000);
 FILE*cf=fopen("LM.bin","rb");
 if(cf){nL=fread(LM,sizeof(M2),130000,cf);fclose(cf);}else{
 M2*all=malloc(sizeof(M2)*130000);int na=0;
 for(int f=1;f<512;f++)for(int g=f+1;g<512;g++){M2 m={0,0};for(int t=0;t<120;t++)if(!__builtin_parity(f&lab[t])&&!__builtin_parity(g&lab[t]))setb(&m,t);all[na++]=m;}
 qsort(all,na,sizeof(M2),cmp);int nm=0;for(int i=0;i<na;i++)if(i==0||cmp(&all[i],&all[i-1]))LM[nm++]=all[i];
 int k=0;for(int i=0;i<nm;i++){int dom=0;for(int j=0;j<nm&&!dom;j++)if(j!=i&&sub(LM[i],LM[j]))dom=1;if(!dom)LM[k++]=LM[i];}nL=k;cf=fopen("LM.bin","wb");fwrite(LM,sizeof(M2),nL,cf);fclose(cf);}
 HE*lh=newh();for(int i=0;i<nL;i++)hput(lh,LM[i],i);
 // direction masks
 int rep[6][2]={{7,-1},{0,-1},{1,-1},{6,-1},{6,7},{0,7}};
 AL=malloc(sizeof(M2)*30000);atype=malloc(30000);nA=0;HE*ah=newh();M2 repm[6];
 for(int ty=0;ty<6;ty++){M2 m={0,0};for(int t=0;t<120;t++)for(int z=0;z<2;z++)if(rep[ty][z]>=0&&pos[t][rep[ty][z]]!=0)setb(&m,t);repm[ty]=m;
  int s0=nA;AL[nA]=m;atype[nA]=ty;hput(ah,m,nA);nA++;
  for(int i=s0;i<nA;i++)for(int g=0;g<8;g++){M2 y=applyp(AL[i],g);if(hget(ah,y)<0){AL[nA]=y;atype[nA]=ty;hput(ah,y,nA);nA++;}}
  cntT[ty]=nA-s0;fprintf(stderr,"type %s |Off|=%d orbit %d\n",tn[ty],popc(m),nA-s0);}
 fprintf(stderr,"L masks %d (expect 43180)\n",nL);

 lhg=lh;cct=calloc(1<<22,sizeof(CE));
 for(int ty=(MODE==1?0:1);ty<(MODE==1?1:6);ty++){ if(only>=0&&ty!=only)continue;
   M2 m=repm[ty];
   int*uf=malloc(4*nL);for(int i=0;i<nL;i++)uf[i]=i;
   for(int g=0;g<8;g++){int inS=0;for(int z=0;z<2;z++)if(rep[ty][z]==g)inS=1;if(inS)continue;
     for(int i=0;i<nL;i++){int j=hget(lh,applyp(LM[i],g));if(j<0){fprintf(stderr,"LM not closed\n");return 3;}int a=i,b=j;while(uf[a]!=a)a=uf[a];while(uf[b]!=b)b=uf[b];if(a!=b)uf[a>b?a:b]=a<b?a:b;}}
   int nr=0;for(int i=0;i<nL;i++)if(uf[i]==i)nr++;
   int m01=hget(ah,m);memset(cs,0,sizeof cs);memset(cc,0,sizeof cc);memset(bytyp,0,sizeof bytyp);
   long pairc=0,pairs=0,minc=999;
   int NS=argc>6?atoi(argv[6]):1,SH=argc>5?atoi(argv[5]):0,ri=0;
   for(int a=0;a<nL;a++){if(uf[a]!=a)continue;if((ri++)%NS!=SH)continue;Ln[0]=a;
     for(int b=0;b<nL;b++){M2 lo=ANDN(ANDN(m,LM[a]),LM[b]);int c=popc(lo);if(c>28)continue;pairs++;
       if(USECOV&&!coverable(lo))continue;pairc++;if(c<minc)minc=c;
       if(K<3)continue;
       Ln[1]=b;Mx[0][1]=m01;nused=1;usedm[0]=m01;ext(2,lo);}}
   printf("TYPE %s: La-reps %d | pairs size-ok %ld cover-ok %ld (min cov leftover %ld) | K=%d states: seven3 size %ld cov %ld; seven4 size %ld cov %ld; seven5 size %ld cov %ld; seven6 size %ld cov %ld; seven7 size %ld cov %ld | final %ld\n",
     tn[ty],nr,pairs,pairc,minc,K,cs[2],cc[2],cs[3],cc[3],cs[4],cc[4],cs[5],cc[5],cs[6],cc[6],bytyp[7]);fflush(stdout);}
 return 0;}
