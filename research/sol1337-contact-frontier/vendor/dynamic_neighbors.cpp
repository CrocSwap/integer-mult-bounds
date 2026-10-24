#include "neighbors.hpp"
#include <limits>
#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <fstream>
#include <iostream>
#include <random>
#include <vector>
using V=std::vector<unsigned>;
V basis(V a){V b(18);for(auto x:a){while(x){int j=31-std::countl_zero(x);if(b[j])x^=b[j];else{b[j]=x;break;}}}V r;for(auto x:b)if(x)r.push_back(x);return r;}
V ann(V a){a=basis(a);int k=0;V piv;for(int j=0;j<18;j++){int z=k;while(z<(int)a.size()&&!(a[z]>>j&1))z++;if(z==(int)a.size())continue;std::swap(a[k],a[z]);for(int i=0;i<(int)a.size();i++)if(i!=k&&(a[i]>>j&1))a[i]^=a[k];piv.push_back(j);k++;}V out;for(int j=0;j<18;j++)if(std::find(piv.begin(),piv.end(),j)==piv.end()){unsigned v=1u<<j;for(int i=0;i<k;i++)if(a[i]>>j&1)v|=1u<<piv[i];out.push_back(v);}return out;}
bool contains(const V& a,unsigned x){for(auto y:a)if(std::popcount(x&y)&1)return false;return true;}
unsigned mv(const V& a,unsigned x){unsigned y=0;while(x){int j=std::countr_zero(x);y^=a[j];x&=x-1;}return y;}
V map(const V& a,const V& b){V r;for(auto x:b)r.push_back(mv(a,x));return r;}
V inverse(V a){std::vector<unsigned long long> rows(18);for(int i=0;i<18;i++){unsigned long long x=1ull<<(18+i);for(int j=0;j<18;j++)if(a[j]>>i&1)x|=1u<<j;rows[i]=x;}for(int j=0;j<18;j++){int k=j;while(k<18&&!(rows[k]>>j&1))k++;if(k==18)throw 1;std::swap(rows[k],rows[j]);for(int i=0;i<18;i++)if(i!=j&&(rows[i]>>j&1))rows[i]^=rows[j];}V out(18);for(int j=0;j<18;j++)for(int i=0;i<18;i++)if(rows[i]>>(18+j)&1)out[j]|=1u<<i;return out;}
unsigned symp(unsigned a,unsigned b){return (std::popcount((a&511)&(b>>9))+std::popcount((a>>9)&(b&511)))&1;}
void turn(V& lag,unsigned axis){for(auto& x:lag)if(symp(x,axis))x^=axis;}
struct Edge{int a,b,r,sign,map;};
struct Local{V neighbor,sum;int r,sign;std::array<unsigned,18> base{},part{};};
Local make_local(V u,V v,int r,int sign){V both=u;both.insert(both.end(),v.begin(),v.end());Local t{ann(v),ann(both),r,sign};for(int group=0;group<2;group++)for(auto z:(group?v:u)){unsigned x=z,p=group?0:z;while(x){int j=31-std::countl_zero(x);if(t.base[j]){x^=t.base[j];p^=t.part[j];}else{t.base[j]=x;t.part[j]=p;break;}}}return t;}
int change(const Local& t,unsigned axis){if(contains(t.neighbor,axis))return 0;if(!contains(t.sum,axis))return 1;unsigned x=axis,u=0;while(x){int j=31-std::countl_zero(x);u^=t.part[j];x^=t.base[j];}return symp(u,axis)?-1:0;}
int main(int argc,char**argv){if(argc!=5&&argc!=6)return 2;double temperature=argc==6?std::stod(argv[5]):0;if(temperature<0)return 2;std::ifstream in(argv[1]);int n,f,m,e;in>>n>>f>>m>>e;std::vector<int> frame(n),fixed(n);for(int i=0;i<n;i++)in>>frame[i]>>fixed[i];std::vector<V> fs(f,V(9)),maps(m,V(18)),inv;for(auto& b:fs)for(auto& x:b)in>>x;for(auto& b:maps){for(auto& x:b)in>>x;inv.push_back(inverse(b));}std::vector<Edge> edges(e);std::vector<V> lags;for(auto x:frame)lags.push_back(fs[x]);std::vector<std::vector<int>> adj(n);for(int i=0;i<e;i++){auto& t=edges[i];in>>t.a>>t.b>>t.r>>t.sign>>t.map;adj[t.a].push_back(i);adj[t.b].push_back(i);}if(!in)return 3;
 double pw[11];for(int r=0;r<=10;r++)pw[r]=std::pow(r,1-.00302177585);std::mt19937 rng(std::stoul(argv[3]));int passes=std::stoi(argv[4]);std::vector<std::pair<int,unsigned>> moves;double total=0;std::vector<int> order;for(int i=2;i<n;i++)if(!fixed[i])order.push_back(i);
 for(int pass=0;pass<passes;pass++){
  std::shuffle(order.begin(),order.end(),rng);int neutral=0,winning=0;double temp=pass+1==passes?0:temperature*(1.0-double(pass)/passes);
  for(int node:order){std::vector<Local> local;auto own=ann(lags[node]);for(int ei:adj[node]){auto& t=edges[ei];auto other=t.a==node?map(inv[t.map],lags[t.b]):map(maps[t.map],lags[t.a]);auto both=other;both.insert(both.end(),lags[node].begin(),lags[node].end());int r=(int)basis(both).size()-9;local.push_back(make_local(lags[node],other,r,t.sign));}
   double best=temp>0?std::numeric_limits<double>::infinity():0;unsigned axisbest=0;unsigned zeros=0;
   for(unsigned axis:canonical_transvection_axes(lags[node])){
    double delta=0;bool valid=true;for(const auto& t:local){int d=change(t,axis);int r=t.r+d;if(r<0||r>9||(t.sign<0&&r<2)){valid=false;break;}delta+=t.sign*(pw[r]-pw[t.r]);}
    if(!valid)continue;
    if(delta<best-1e-10){best=delta;axisbest=axis;zeros=1;}
    else if(std::abs(delta-best)<1e-12){zeros++;if(rng()%zeros==0)axisbest=axis;}
   }
   if(axisbest&&(best< -1e-10||(std::abs(best)<1e-12&&(temp>0||rng()%3==0))||(temp>0&&best>0&&std::uniform_real_distribution<double>(0,1)(rng)<std::exp(-best/temp)))){turn(lags[node],axisbest);double check=0;for(int ei:adj[node]){auto& t=edges[ei];V both=map(maps[t.map],lags[t.a]);both.insert(both.end(),lags[t.b].begin(),lags[t.b].end());int actual=(int)basis(both).size()-9;auto it=std::find(adj[node].begin(),adj[node].end(),ei);int old=local[it-adj[node].begin()].r;check+=t.sign*(pw[actual]-pw[old]);}if(std::abs(check-best)>1e-8){std::cerr<<"INDEPENDENT LOCAL RANK MISMATCH "<<check<<" versus "<<best<<"\n";return 5;}moves.push_back({node,axisbest});total+=best;if(best< -1e-10){winning++;std::cerr<<"GAIN "<<best<<" total "<<total<<" node "<<node<<" axis "<<axisbest<<"\n";}else neutral++;}
   if(total< -1e-6)break;
  }
  std::cerr<<"pass "<<pass<<" neutral "<<neutral<<" winning "<<winning<<" total "<<total<<" temperature "<<temp<<"\n";
  if(total< -1e-6)break;
 }
 std::array<int,10> paid{},helper{},oldpaid{},oldhelper{};for(auto& t:edges){V both=map(maps[t.map],lags[t.a]);both.insert(both.end(),lags[t.b].begin(),lags[t.b].end());int r=(int)basis(both).size()-9;(t.sign>0?paid:helper)[r]++;(t.sign>0?oldpaid:oldhelper)[t.r]++;}
 double delta=0;for(int r=0;r<=9;r++)delta+=pw[r]*(paid[r]-oldpaid[r]-helper[r]+oldhelper[r]);
 std::ofstream out(argv[2]);out.precision(17);out<<"{\"scope\":\"floating coordinated Clifford contact discovery; no acceptance\",\"delta\":"<<delta<<",\"moves\":[";bool first=true;for(auto [n,a]:moves){if(!first)out<<',';first=false;out<<'['<<n<<','<<a<<']';}out<<"],\"paid_delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<paid[r]-oldpaid[r];out<<"],\"helper_delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<helper[r]-oldhelper[r];out<<"]}\n";std::cerr<<"verified floating delta "<<delta<<"\n";
 return 0;
}
