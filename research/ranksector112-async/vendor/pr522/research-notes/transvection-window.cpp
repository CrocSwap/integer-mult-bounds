#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <vector>
using namespace std;using B=array<int,9>;
int dim(B b){int n=0;for(int x:b)n+=x!=0;return n;}
B joinb(B a,B b){for(int x:b)for(int j=8;j>=0;j--)if(x>>j&1){if(a[j])x^=a[j];else{a[j]=x;break;}}return a;}
bool sub(B a,B b){return dim(joinb(b,a))==dim(b);}
struct E{int typ,t,s;B f;};
bool commute(E a,E b){if(a.typ)return a.t!=b.t&&(b.typ||a.t!=b.s);if(b.typ)return b.t!=a.t&&b.t!=a.s;return a.t!=b.s&&b.t!=a.s;}
double p(int n){return n?pow(double(n),1.-.001396):0.;}
double eval(const vector<E>&es,vector<B>cur,const vector<B>&finish){double cost=0;for(auto&e:es){for(int r:{e.t,e.typ?-1:e.s})if(r>=0){if(!sub(cur[r],e.f))return 1e30;cost+=p(dim(e.f)-dim(cur[r]));cur[r]=e.f;}}for(int i=0;i<int(cur.size());i++){if(!sub(cur[i],finish[i]))return 1e30;cost+=p(dim(finish[i])-dim(cur[i]));}return cost;}
int main(){int parts;cin>>parts;bool first=true;cout<<"[";long long tested=0;
for(int part=0;part<parts;part++){int n,r;cin>>n>>r;vector<B>initial(r),finish(r);for(auto&v:initial)for(int&x:v)cin>>x;for(auto&v:finish)for(int&x:v)cin>>x;vector<E>es(n);for(auto&e:es){cin>>e.typ>>e.t>>e.s;for(int&x:e.f)cin>>x;}double base=eval(es,initial,finish);
for(int i=0;i<n;i++){E e=es[i];if(e.typ)continue;
for(int j=i+1;j<n&&j<=i+128;j++){E z=es[j];int kind=0;if(!z.typ){if(e.s==z.t&&e.t!=z.s)kind=1;else if(e.t==z.s&&e.s!=z.t)kind=2;}
if(kind&&sub(e.f,z.f)&&dim(e.f)<dim(z.f)){
 vector<E>a(es.begin(),es.begin()+i);a.insert(a.end(),es.begin()+i+1,es.begin()+j);a.push_back(z);E ee=e;ee.f=z.f;a.push_back(ee);E corr={0,kind==1?e.t:z.t,kind==1?z.s:e.s,z.f};a.push_back(corr);a.insert(a.end(),es.begin()+j+1,es.end());tested++;
 double gain=base-eval(a,initial,finish);if(gain>1e-10){if(!first)cout<<",";first=false;cout<<"{\"part\":"<<part<<",\"index\":"<<i<<",\"second\":"<<j<<",\"kind\":"<<kind<<",\"gain\":"<<gain<<"}";}
}
if(!commute(e,z))break;
}}
}cout<<"]\n";cerr<<"tested "<<tested<<" actual frame-cost candidates\n";}
