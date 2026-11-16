// K579T impl B (independent of base.py/a3e.c/cover.py/ext.py): E8 from the Bourbaki Cartan matrix (simple-root coords),
// labels = coeffs mod 2 | const bit, own maximal 7-flat masks, own W(D5) orbits, own flat-cover (explicit F4/F3 line-set lists).
// Searches the A4 (5 sevens) pair cover: Off(h_ab) minus (L_a u L_b) inside E, |E|<=CAP, E = 3 F4 + 1 F3 line sets.
// usage: ./b5 CAP [nocover]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u;
static inline int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int A[8][8]={{2,0,-1,0,0,0,0,0},{0,2,0,-1,0,0,0,0},{-1,0,2,-1,0,0,0,0},{0,-1,-1,2,-1,0,0,0},{0,0,0,-1,2,-1,0,0},{0,0,0,0,-1,2,-1,0},{0,0,0,0,0,-1,2,-1},{0,0,0,0,0,0,-1,2}};
int rt[240][8],nr=0,lab[120];
int ipr(int*a,int*b){int s=0;for(int i=0;i<8;i++)for(int j=0;j<8;j++)s+=a[i]*A[i][j]*b[j];return s;}
int find(int*v){for(int i=0;i<nr;i++)if(!memcmp(rt[i],v,32))return i;return -1;}
int lineof(int*v){int w[8];int neg=0;for(int i=0;i<8;i++)if(v[i]<0)neg=1;for(int i=0;i<8;i++)w[i]=neg?-v[i]:v[i];return find(w);}
int cmpu(const void*a,const void*b){u x=*(u*)a,y=*(u*)b;return x<y?-1:x>y;}
u *F4,*F3;int n4,n3;int **ix4,**ix3,*c4,*c3;
int cover(u U,int cu,int pl){if(!U)return 1;if(pc(U)>8*cu+4*pl)return 0;int t=0;while(!((U>>t)&1))t++;
 if(cu)for(int k=0;k<c4[t];k++)if(cover(U&~F4[ix4[t][k]],cu-1,pl))return 1;
 if(pl)for(int k=0;k<c3[t];k++)if(cover(U&~F3[ix3[t][k]],cu,pl-1))return 1;return 0;}
u* flats(int k,int*n){ // maximal-by-construction line sets {t: lab_t in span of k independent labels}
 int cap=1<<24;u*S=malloc(cap*sizeof(u));int m=0;int id[4];
 for(id[0]=0;id[0]<120;id[0]++)for(id[1]=id[0]+1;id[1]<120;id[1]++)for(id[2]=id[1]+1;id[2]<120;id[2]++)for(id[3]=(k==4?id[2]+1:119);id[3]<120;id[3]++){
  int sp[16]={0},ns=1;for(int j=0;j<k;j++){int v=lab[id[j]];int in=0;for(int s=0;s<ns;s++)if(sp[s]==v)in=1;if(in)goto nx;for(int s=0;s<ns;s++)sp[ns+s]=sp[s]^v;ns*=2;}
  {u x=0;for(int t=0;t<120;t++)for(int s=0;s<ns;s++)if(sp[s]==lab[t])x|=(u)1<<t;S[m++]=x;if(m==cap){qsort(S,m,sizeof(u),cmpu);int w=0;for(int i=0;i<m;i++)if(!w||S[w-1]!=S[i])S[w++]=S[i];m=w;}}
  nx:;}
 qsort(S,m,sizeof(u),cmpu);int w=0;for(int i=0;i<m;i++)if(!w||S[w-1]!=S[i])S[w++]=S[i];*n=w;return S;}
void index_(u*S,int n,int***ix,int**c){*ix=malloc(120*sizeof(int*));*c=calloc(120,4);for(int t=0;t<120;t++){(*ix)[t]=malloc(n*4);}
 for(int i=0;i<n;i++)for(int t=0;t<120;t++)if((S[i]>>t)&1)(*ix)[t][(*c)[t]++]=i;}
int main(int argc,char**argv){int CAP=atoi(argv[1]);int NOCOV=argc>2;
 for(int i=0;i<8;i++){memset(rt[nr],0,32);rt[nr][i]=1;nr++;}
 for(int q=0;q<nr;q++)for(int i=0;i<8;i++){int e[8]={0};e[i]=1;int k=ipr(rt[q],e);int v[8];memcpy(v,rt[q],32);v[i]-=k;
   int pos=1,neg=1;for(int j=0;j<8;j++){if(v[j]<0)pos=0;if(v[j]>0)neg=0;} if(pos&&!neg&&find(v)<0){memcpy(rt[nr++],v,32);}}
 if(nr!=120){printf("roots %d\n",nr);return 1;}
 for(int t=0;t<120;t++){lab[t]=256;for(int j=0;j<8;j++)lab[t]|=(rt[t][j]&1)<<j;}
 // masks
 u*ms=malloc(130816*sizeof(u));int nm=0;
 for(int f=1;f<512;f++)for(int g=f+1;g<512;g++){u x=0;for(int t=0;t<120;t++)if(!(__builtin_popcount(f&lab[t])&1)&&!(__builtin_popcount(g&lab[t])&1))x|=(u)1<<t;ms[nm++]=x;}
 qsort(ms,nm,sizeof(u),cmpu);int w=0;for(int i=0;i<nm;i++)if(!w||ms[w-1]!=ms[i])ms[w++]=ms[i];nm=w;
 u*M=malloc(nm*sizeof(u));int NM=0;for(int i=0;i<nm;i++){int sub=0;for(int j=0;j<nm&&!sub;j++)if(j!=i&&(ms[i]&ms[j])==ms[i])sub=1;if(!sub)M[NM++]=ms[i];}
 printf("roots 120, masks %d\n",NM);fflush(stdout);
 F4=flats(4,&n4);F3=flats(3,&n3);index_(F4,n4,&ix4,&c4);index_(F3,n3,&ix3,&c3);printf("F4 sets %d F3 sets %d\n",n4,n3);fflush(stdout);
 // chain alpha1-alpha3-alpha4 (indices 0,2,3); extensions c4: roots with ip(c4,a4)=-1, ip(c4,a1)=ip(c4,a3)=0 (both signs of lines)
 int ch[3]={0,2,3};int H[6][8];u off[10];int pa[10][2],np=0;
 for(int a=0;a<4;a++)for(int b=a+1;b<4;b++){int h[8]={0};for(int k=a;k<b;k++)for(int j=0;j<8;j++)h[j]+=rt[ch[k]][j];
   u x=0;for(int t=0;t<120;t++)if(ipr(rt[t],h))x|=(u)1<<t;pa[np][0]=a;pa[np][1]=b;off[np++]=x;}
 // R579b K5^- : new seven 4 with v_a=u_a-u_4 = s_a + x ROOT for a!=m and NON-ROOT (nonzero, not a root line) for a=m; s_a = sum_{k>=a} chain
 int ext[4096][8],ne=0,em[4096];int S4[4][8];for(int a=0;a<4;a++){for(int j=0;j<8;j++)S4[a][j]=0;for(int k=a;k<3;k++)for(int j=0;j<8;j++)S4[a][j]+=rt[ch[k]][j];}
 for(int sg=-1;sg<=1;sg+=2)for(int t=0;t<120;t++)for(int a0=0;a0<4;a0++){int x[8];for(int j=0;j<8;j++)x[j]=sg*rt[t][j]-S4[a0][j];
  for(int m=0;m<4;m++){int ok=1,nonroot=0;for(int a=0;a<4;a++){int v[8],z=1;for(int j=0;j<8;j++){v[j]=S4[a][j]+x[j];if(v[j])z=0;}int isr=(!z&&ipr(v,v)==2);
     if(a!=m&&!isr)ok=0; if(a==m){int w[8],ev=1;for(int j=0;j<8;j++){if(v[j]&1)ev=0;w[j]=v[j]/2;}int dbl=ev&&!z&&ipr(w,w)==2; nonroot=!z&&!isr&&!dbl;}}
   if(ok&&nonroot){int dup=0;for(int e=0;e<ne;e++)if(em[e]==m&&!memcmp(ext[e],x,32))dup=1;if(!dup){memcpy(ext[ne],x,32);em[ne++]=m;}}}}
 u offx[4096][4];for(int e=0;e<ne;e++)for(int a=0;a<4;a++){int h[8];for(int j=0;j<8;j++)h[j]=ext[e][j]+S4[a][j];
   u x=0;for(int t=0;t<120;t++)if(ipr(rt[t],h))x|=(u)1<<t;offx[e][a]=x;}
 {int nh[16]={0};for(int e=0;e<ne;e++){int h[8];for(int j=0;j<8;j++)h[j]=ext[e][j]+S4[em[e]][j];int n=ipr(h,h);if(n<16)nh[n]++;}printf("K5- extensions %d, norms of h_m4: 4:%d 6:%d 8:%d\n",ne,nh[4],nh[6],nh[8]);}
 printf("chain pairs %d, extensions %d\n",np,ne);
 // W(D5): positive roots orthogonal to chain -> line permutations; orbits of masks
 int *par=malloc(NM*4);for(int i=0;i<NM;i++)par[i]=i;int ng=0;
 for(int r=0;r<120;r++){if(ipr(rt[r],rt[0])||ipr(rt[r],rt[2])||ipr(rt[r],rt[3]))continue;ng++;int pm[120];
  for(int t=0;t<120;t++){int k=ipr(rt[t],rt[r]);int v[8];for(int j=0;j<8;j++)v[j]=rt[t][j]-k*rt[r][j];pm[t]=lineof(v);}
  for(int i=0;i<NM;i++){u y=0;for(int t=0;t<120;t++)if((M[i]>>t)&1)y|=(u)1<<pm[t];
   int lo=0,hi=NM-1,j=-1;while(lo<=hi){int md=(lo+hi)/2;if(M[md]==y){j=md;break;}if(M[md]<y)lo=md+1;else hi=md-1;}
   if(j<0){printf("closure fail\n");return 1;} int x=i,z=j;while(par[x]!=x)x=par[x];while(par[z]!=z)z=par[z];if(x!=z)par[x]=z;}}
 int nrep=0;for(int i=0;i<NM;i++){int x=i;while(par[x]!=x)x=par[x];par[i]=x;}for(int i=0;i<NM;i++)if(par[i]==i)nrep++;
 printf("perp roots %d, L0 orbits %d\n",ng,nrep);fflush(stdout);
 // DFS: order L1, L0(rep? no: reps on L0) ... L0 rep, L3, L1, L2 (different order from impl A), then L4 over all extensions
 int*l=malloc(NM*4);int minU=999;long long s3=0,s4=0,s4c=0,s5=0;
 for(int r=0;r<NM;r++){if(par[r]!=r)continue;u L0=M[r];
  int n3l=0,n1l=0,n2l=0;int*l3=malloc(NM*4),*l1=malloc(NM*4),*l2=malloc(NM*4);for(int i=0;i<NM;i++){if(pc(off[2]&~L0&~M[i])<=CAP)l3[n3l++]=i;if(pc(off[0]&~L0&~M[i])<=CAP)l1[n1l++]=i;if(pc(off[1]&~L0&~M[i])<=CAP)l2[n2l++]=i;}   // pair (0,3)
  for(int a=0;a<n3l;a++){u L3=M[l3[a]];u U3=off[2]&~L0&~L3;
   for(int bb=0;bb<n1l;bb++){u L1=M[l1[bb]];u U1=U3|(off[0]&~L0&~L1)|(off[4]&~L1&~L3);if(pc(U1)>CAP)continue;      // (0,1),(1,3)
    for(int cc=0;cc<n2l;cc++){u L2=M[l2[cc]];u U2=U1|(off[1]&~L0&~L2)|(off[3]&~L1&~L2)|(off[5]&~L2&~L3);if(pc(U2)>CAP)continue; // (0,2),(1,2),(2,3)
     s4++;if(!NOCOV&&!cover(U2,3,1))continue;s4c++;
     u Ls[4]={L0,L1,L2,L3};
     for(int e=0;e<ne;e++){u D=0;for(int q=0;q<4;q++)D|=offx[e][q]&~Ls[q];
      for(int d=0;d<NM;d++){u U4=U2|(D&~M[d]);if(pc(U4)<minU)minU=pc(U4);if(pc(U4)<=CAP&&(NOCOV||cover(U4,3,1))){s5++;if(s5<=5)printf("A4 SOL rep %d U %d\n",r,pc(U4));}}}}}}
  free(l3);free(l1);free(l2);}
 printf("DONE CAP %d nocover %d: A3 quads %lld, coverable %lld, K5- solutions %lld, min |U| over K5- %d\n",CAP,NOCOV,s4,s4c,s5,minU);}
