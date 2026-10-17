// DEG2 impl A: triple (a,b,c): h_ab=A, h_ac=C non-root types; third pair relaxed to Off(h_bc) >= A^C (alpha,beta!=0), or A if collinear (nongeneric A==C).
// union U = A\(La|Lb) | C\(La|Lc) | (A^C)\(Lb|Lc) ; count/min |U| <= cap. usage: triA cap repLo repHi [mode]  (mode 1: drop X_bc = control "pairs only")
#include "e8.h"
typedef struct{u X;int b;}ent;typedef struct{ent*e;int n,cap;}lst;

static int sl_[64],ns_;
static int cmpu64(const void*a,const void*b){unsigned long long x=*(unsigned long long*)a,y=*(unsigned long long*)b;return x<y?-1:x>y;}
// all distinct non-dominated masks (over S) of affine flats of affine dim k (2^k pts) through point p
static int flatsk(int p,int k,unsigned long long*out){int idx[64],m=0;for(int i=0;i<ns_;i++)if(i!=p)idx[m++]=i;int nr=0;unsigned long long*tmp=out;
 int kk=k<m?k:m;int c[4];for(int i=0;i<kk;i++)c[i]=i;
 while(1){int bs[8]={0};for(int i=0;i<kk;i++){int x=sl_[idx[c[i]]]^sl_[p];for(int t=7;t>=0&&x;t--)if(x>>t&1){if(bs[t])x^=bs[t];else{bs[t]=x;x=0;}}}
  unsigned long long mm=0;for(int j=0;j<ns_;j++){int x=sl_[j]^sl_[p];for(int t=7;t>=0&&x;t--)if((x>>t&1)&&bs[t])x^=bs[t];if(!x)mm|=1ULL<<j;}
  tmp[nr++]=mm;if(kk==0)break;int i=kk-1;while(i>=0&&c[i]==m-kk+i)i--;if(i<0)break;c[i]++;for(int j=i+1;j<kk;j++)c[j]=c[j-1]+1;}
 qsort(tmp,nr,8,cmpu64);int no=0;for(int q=0;q<nr;q++)if(q==0||tmp[q]!=tmp[q-1])tmp[no++]=tmp[q];
 {int w=0;for(int q=0;q<no;q++){int dom=0;for(int z=0;z<no&&!dom;z++)if(z!=q&&(tmp[q]&~tmp[z])==0)dom=1;if(!dom)tmp[w++]=tmp[q];}no=w;}
 return no;}
static unsigned long long *Mk[2][64];static int Mn[2][64];
static unsigned long long spanmask(int*pts,int np){ // affine span of pts (np points) intersected with S
 int bs[8]={0};for(int i=1;i<np;i++){int x=sl_[pts[i]]^sl_[pts[0]];for(int t=7;t>=0&&x;t--)if(x>>t&1){if(bs[t])x^=bs[t];else{bs[t]=x;x=0;}}}
 unsigned long long mm=0;for(int j=0;j<ns_;j++){int x=sl_[j]^sl_[pts[0]];for(int t=7;t>=0&&x;t--)if((x>>t&1)&&bs[t])x^=bs[t];if(!x)mm|=1ULL<<j;}return mm;}
static unsigned long long*tmpb;
static void buildmasks(){ // per point p and flat dim kind (0: 8-pt via 3 gens; 1: 4-pt via 2 gens): distinct non-dominated masks containing p
 if(!tmpb)tmpb=malloc(8*30000);
 for(int kd=0;kd<2;kd++)for(int p=0;p<ns_;p++){int g=kd==0?3:2;int m=0,idx[64];for(int i=0;i<ns_;i++)if(i!=p)idx[m++]=i;int nr=0;
  int c[3];int kk=g<m?g:m;for(int i=0;i<kk;i++)c[i]=i;
  while(1){int pts[4];pts[0]=p;for(int i=0;i<kk;i++)pts[i+1]=idx[c[i]];tmpb[nr++]=spanmask(pts,kk+1);if(kk==0)break;int i=kk-1;while(i>=0&&c[i]==m-kk+i)i--;if(i<0)break;c[i]++;for(int j=i+1;j<kk;j++)c[j]=c[j-1]+1;}
  qsort(tmpb,nr,8,cmpu64);int no=0;for(int q=0;q<nr;q++)if(q==0||tmpb[q]!=tmpb[q-1])tmpb[no++]=tmpb[q];
  int w=0;for(int q=0;q<no;q++){int dom=0;for(int z=0;z<no&&!dom;z++)if(z!=q&&(tmpb[q]&~tmpb[z])==0)dom=1;if(!dom)tmpb[w++]=tmpb[q];}
  free(Mk[kd][p]);Mk[kd][p]=malloc(8*(w+1));memcpy(Mk[kd][p],tmpb,8*w);Mn[kd][p]=w;}}
static int coverrec(unsigned long long rem,int used,int lvl){ if(!rem)return 1; if(lvl>=4)return 0;
 static const int dk[4]={1,1,1,0}; int capr=0;for(int L=0;L<4;L++)if(!(used>>L&1))capr+=dk[L]?8:4; if(__builtin_popcountll(rem)>capr)return 0;
 int p=__builtin_ctzll(rem);
 for(int L=0;L<4;L++){if(used>>L&1)continue;if(L>0&&L<3&&!(used>>(L-1)&1))continue;
  for(int q=0;q<Mn[dk[L]?0:1][p];q++){ if(coverrec(rem&~Mk[dk[L]?0:1][p][q],used|1<<L,lvl+1))return 1;}}
 return 0;}
int coverable(u U){ns_=0;for(int t=0;t<120;t++)if((U>>t)&1)sl_[ns_++]=lab[t]&255;buildmasks();return coverrec(ns_==64?~0ULL:((1ULL<<ns_)-1),0,0);}


typedef struct{u X;int k,b;}leg;
static u *D4;static int nd4,nd,*dt4,*gen4;
static inline int tri_ok(u P,u Q,u R){u one=(P&~Q&~R)|(Q&~P&~R)|(R&~P&~Q);return one==0;}
#define HB 24
typedef struct{unsigned long long key;int off,n;}hent;
static hent*HT;static int*pool;static long poolN,poolC;
static void getlist(int kx,int ky,int**lst,int*n){
 if(kx>ky){int t=kx;kx=ky;ky=t;}
 unsigned long long key=((unsigned long long)kx<<24|(unsigned long long)ky)+1;
 unsigned long h=(key*0x9E3779B97F4A7C15ULL)>>(64-HB);
 while(HT[h].key&&HT[h].key!=key)h=(h+1)&((1UL<<HB)-1);
 if(!HT[h].key){u P=D4[kx],Q=D4[ky];int c=0;
  if(poolN+nd4>poolC){poolC=poolC*2+nd4;pool=realloc(pool,poolC*sizeof(int));}
  for(int p=0;p<nd4;p++)if(tri_ok(P,Q,D4[p]))pool[poolN+c++]=p;
  HT[h].key=key;HT[h].off=poolN;HT[h].n=c;poolN+=c;}
 *lst=pool+HT[h].off;*n=HT[h].n;}


// ext: read configs "n rep L1..L(n-1) pairs(i<j lexicographic)" ; add one more seven; print same format with n+1
static leg*Lg;static long n1;static int cap=28;
static int nn;static u Lm[9];static int P[9][9];static int newk,newb;static u Ucur;static long found=0;static int NP[9];
static void rec(int x,u U,int ri,int*pn){ // choose P[x][new] for x=1..nn-1
 if(x==nn){ // all chosen; check triangles (x,y,new) done incrementally; distinctness
   int all[40],m=0;for(int i=0;i<nn;i++)for(int j=i+1;j<nn;j++)all[m++]=P[i][j];for(int i=0;i<nn;i++)all[m++]=P[i][nn];
   for(int s1=0;s1<m;s1++)for(int s2=s1+1;s2<m;s2++)if(all[s1]==all[s2]&&!gen4[all[s1]])return;
   if(!coverable(U))return;found++;
   printf("%d %d",nn+1,ri);for(int i=1;i<nn;i++)printf(" %d",pn[i]);printf(" %d",newb);
   for(int i=0;i<=nn;i++)for(int j=i+1;j<=nn;j++)printf(" %d",P[i][j]);
   printf(" | U");for(int t=0;t<120;t++)if((U>>t)&1)printf(" %d",t);printf("\n");fflush(stdout);return;}
 int*lst;int n;getlist(P[0][x],newk,&lst,&n);
 for(int q=0;q<n;q++){int p=lst[q];u X=D4[p]&~(Lm[x]|M[newb]);u U2=U|X;if(pc(U2)>cap)continue;
   int ok=1;for(int y=1;y<x&&ok;y++)if(!tri_ok(D4[P[y][x]],D4[P[y][nn]],D4[p]))ok=0; // triangle (y,x,new): masks Off(yx),Off(y new),Off(x new)
   if(!ok)continue;P[x][nn]=p;rec(x+1,U2,ri,pn);}}
int main(int argc,char**argv){build();HT=calloc(1UL<<HB,sizeof(hent));
 int Ss[6]={0x01,0x02,0x40,0x81,0xc0,0x80},gen[6]={0,0,0,1,1,0};D4=0;nd4=0;dt4=0;
 for(int k=0;k<6;k++){u*o;int n=orbit(offS(Ss[k]),&o);D4=realloc(D4,(nd4+n)*sizeof(u));dt4=realloc(dt4,(nd4+n)*sizeof(int));for(int i=0;i<n;i++){D4[nd4+i]=o[i];dt4[nd4+i]=k;}nd4+=n;free(o);if(k==4)nd=nd4;}
 gen4=malloc(nd4*sizeof(int));for(int i=0;i<nd4;i++)gen4[i]=gen[dt4[i]];
 int*seen=calloc(NM,sizeof(int)),*q=malloc(NM*sizeof(int));int nrep=0,reps[64];
 for(int s=0;s<NM;s++)if(!seen[s]){int n=1;q[0]=s;seen[s]=1;for(int i=0;i<n;i++)for(int r=0;r<8;r++){int j=mfind(act(r,M[q[i]]));if(!seen[j]){seen[j]=1;q[n++]=j;}}reps[nrep++]=s;}

 static int lastri=-1;
 char line[4096];
 while(fgets(line,sizeof line,stdin)){char*p=line;int n,ri;int off;sscanf(p,"%d %d%n",&n,&ri,&off);p+=off;
  nn=n;int pn[9];pn[0]=0;for(int i=1;i<n;i++){sscanf(p,"%d%n",&pn[i],&off);p+=off;}
  for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){sscanf(p,"%d%n",&P[i][j],&off);p+=off;}
  u La=M[reps[ri]];Lm[0]=La;for(int i=1;i<n;i++)Lm[i]=M[pn[i]];
  u U=0;for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)U|=D4[P[i][j]]&~(Lm[i]|Lm[j]);
  if(ri!=lastri){free(Lg);long cp=1<<20;n1=0;Lg=malloc(cp*sizeof(leg));
   for(int k=0;k<nd4;k++){u R=D4[k]&~La;if(pc(R)>cap+40)continue;for(int b=0;b<NM;b++){u X=R&~M[b];if(pc(X)>cap)continue;if(n1==cp){cp*=2;Lg=realloc(Lg,cp*sizeof(leg));}Lg[n1].X=X;Lg[n1].k=k;Lg[n1].b=b;n1++;}}lastri=ri;}
  for(long m=0;m<n1;m++){u U1=U|Lg[m].X;if(pc(U1)>cap)continue;newk=Lg[m].k;newb=Lg[m].b;P[0][nn]=newk;
   int dup=0;for(int i=0;i<nn&&!dup;i++)for(int j=i+1;j<nn;j++)if(P[i][j]==newk&&!gen4[newk])dup=1;if(dup)continue;
   rec(1,U1,ri,pn);}
 }
 fprintf(stderr,"found %ld\n",found);return 0;}
