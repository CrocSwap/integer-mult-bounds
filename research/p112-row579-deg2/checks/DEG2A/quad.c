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

// DEG2A quad: sevens a,b,c,d. legs (A=h_ab,b),(C=h_ac,c) non-root types, (K=h_ad,d) any (incl root).
// Prefilter: legs' leftovers + relaxed lower bounds of bc,bd,cd (PΔQ); then exact masks for bc,bd,cd from D4 with all 4 triangle conditions
// (no line in exactly one of the three Off-masks), U=all six leftovers <=cap, coverable by 3F4+F3.
// usage: quad cap rep chunk nchunks   (chunk over leg-1 index h)
typedef struct{u X;int k,b;}leg;
static u *D4;static int nd4,nd,*dt4,*gen4;
static inline u Tf(int hi,int gi){ // lower bound of Off of third pair given indices into D4
  u P=D4[hi],Q=D4[gi]; if(P==Q&&!gen4[hi]) return P; return P^Q;}
static inline int tri_ok(u P,u Q,u R){ // no line in exactly one
  u one=(P&~Q&~R)|(Q&~P&~R)|(R&~P&~Q); return one==0;}

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
int main(int argc,char**argv){build();HT=calloc(1UL<<HB,sizeof(hent));
 int cap=atoi(argv[1]),ri=atoi(argv[2]),ch=atoi(argv[3]),nch=atoi(argv[4]);
 int Ss[6]={0x01,0x02,0x40,0x81,0xc0,0x80},gen[6]={0,0,0,1,1,0};D4=0;nd4=0;dt4=0;
 for(int k=0;k<6;k++){u*o;int n=orbit(offS(Ss[k]),&o);D4=realloc(D4,(nd4+n)*sizeof(u));dt4=realloc(dt4,(nd4+n)*sizeof(int));for(int i=0;i<n;i++){D4[nd4+i]=o[i];dt4[nd4+i]=k;}nd4+=n;free(o);if(k==4)nd=nd4;}
 gen4=malloc(nd4*sizeof(int));for(int i=0;i<nd4;i++)gen4[i]=gen[dt4[i]];
 int*seen=calloc(NM,sizeof(int)),*q=malloc(NM*sizeof(int));int nrep=0,reps[64];
 for(int s=0;s<NM;s++)if(!seen[s]){int n=1;q[0]=s;seen[s]=1;for(int i=0;i<n;i++)for(int r=0;r<8;r++){int j=mfind(act(r,M[q[i]]));if(!seen[j]){seen[j]=1;q[n++]=j;}}reps[nrep++]=s;}
 u La=M[reps[ri]];
 // leg lists: legs1 (non-root, k<nd) and legsK (all)
 long cp=1<<20,n1=0;leg*Lg=malloc(cp*sizeof(leg));
 for(int k=0;k<nd4;k++){u R=D4[k]&~La;if(pc(R)>cap+40)continue;for(int b=0;b<NM;b++){u X=R&~M[b];if(pc(X)>cap)continue;if(n1==cp){cp*=2;Lg=realloc(Lg,cp*sizeof(leg));}Lg[n1].X=X;Lg[n1].k=k;Lg[n1].b=b;n1++;}}
 // sort by k so non-root entries first (k<nd): they are already ordered by k
 long nnr=0;while(nnr<n1&&Lg[nnr].k<nd)nnr++;
 fprintf(stderr,"rep %d legs total %ld nonroot %ld\n",ri,n1,nnr);
 long ntri=0,npre=0,nex=0,nsurv=0;
 for(long i=0;i<nnr;i++){ if((i%nch)!=ch)continue; leg*l1=&Lg[i];
  for(long j=i;j<nnr;j++){leg*l2=&Lg[j];if(l1->k==l2->k&&!gen4[l1->k])continue;
   u U12=l1->X|l2->X;if(pc(U12)>cap)continue;
   u T=Tf(l1->k,l2->k)&~(M[l1->b]|M[l2->b]);u U2=U12|T;if(pc(U2)>cap)continue;ntri++;
   for(long m=0;m<n1;m++){leg*l3=&Lg[m];if(!gen4[l3->k]&&(l3->k==l1->k||l3->k==l2->k))continue;
    u U3=U2|l3->X;if(pc(U3)>cap)continue;
    u Tb=Tf(l1->k,l3->k)&~(M[l1->b]|M[l3->b]);u Tc=Tf(l2->k,l3->k)&~(M[l2->b]|M[l3->b]);
    u U4=U3|Tb|Tc;if(pc(U4)>cap)continue;npre++;
    u Ma=M[l1->b],Mb2=M[l2->b],Md=M[l3->b];
    u PA=D4[l1->k],PC=D4[l2->k],PK=D4[l3->k];
    // exact masks for bc (A,C), bd (A,K), cd (C,K)
    int*lbc,*lbd,*lcd;int nbc,nbd,ncd;
    getlist(l1->k,l2->k,&lbc,&nbc);getlist(l1->k,l3->k,&lbd,&nbd);getlist(l2->k,l3->k,&lcd,&ncd);
    static int cbc[40000],cbd[40000],ccd[40000];int a1=0,a2=0,a3=0;
    for(int x=0;x<nbc;x++)if(pc(U4|(D4[lbc[x]]&~(Ma|Mb2)))<=cap)cbc[a1++]=lbc[x];
    for(int x=0;x<nbd;x++)if(pc(U4|(D4[lbd[x]]&~(Ma|Md)))<=cap)cbd[a2++]=lbd[x];
    for(int x=0;x<ncd;x++)if(pc(U4|(D4[lcd[x]]&~(Mb2|Md)))<=cap)ccd[a3++]=lcd[x];
    nbc=a1;nbd=a2;ncd=a3;
    if(!nbc||!nbd||!ncd)continue;
    for(int x=0;x<nbc;x++)for(int y=0;y<nbd;y++)for(int z=0;z<ncd;z++){
      int ix[6]={l1->k,l2->k,l3->k,cbc[x],cbd[y],ccd[z]};int bad=0;for(int s1=0;s1<6&&!bad;s1++)for(int s2=s1+1;s2<6;s2++)if(ix[s1]==ix[s2]&&!gen4[ix[s1]]){bad=1;break;}if(bad)continue;
      u P1=D4[cbc[x]],P2=D4[cbd[y]],P3=D4[ccd[z]];if(!tri_ok(P1,P2,P3))continue;
      u U=U3|(P1&~(Ma|Mb2))|(P2&~(Ma|Md))|(P3&~(Mb2|Md));
      // note: leg X's are relative to La; bc,bd,cd leftovers relative to the other sevens' masks (b,c,d)
      u Ub=l1->X|l2->X|l3->X|(P1&~(M[l1->b]|M[l2->b]))|(P2&~(M[l1->b]|M[l3->b]))|(P3&~(M[l2->b]|M[l3->b]));
      (void)U; if(pc(Ub)>cap)continue;nex++;
      if(coverable(Ub)){nsurv++;
        printf("SURV rep %d La %d b %d c %d d %d | hab %d hac %d had %d hbc %d hbd %d hcd %d | U",ri,reps[ri],l1->b,l2->b,l3->b,l1->k,l2->k,l3->k,cbc[x],cbd[y],ccd[z]);
        for(int t=0;t<120;t++)if((Ub>>t)&1)printf(" %d",t);printf("\n");fflush(stdout);}
    }
   }}
  if((i%64)==0){fprintf(stderr,"i %ld/%ld tri %ld pre %ld ex %ld surv %ld\n",i,nnr,ntri,npre,nex,nsurv);}
 }
 printf("DONE rep %d chunk %d/%d tri %ld pre %ld exact %ld surv %ld\n",ri,ch,nch,ntri,npre,nex,nsurv);return 0;}
