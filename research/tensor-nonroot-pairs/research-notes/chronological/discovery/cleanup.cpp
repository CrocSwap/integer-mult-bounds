#include <bits/stdc++.h>
#include <json.hpp>
using namespace std;using J=nlohmann::json;using Gate=pair<int,int>;
bool commute(Gate a,Gate b){return a.first!=b.second&&b.first!=a.second;}
int main(int argc,char**argv){J z;ifstream(argv[1])>>z;vector<Gate> g;for(auto e:z["C"]){if(e[0]!=1)return 2;for(int x:e[2])g.push_back({e[1],x});}int before=g.size();J steps=J::array();bool changed=true;while(changed){changed=false;
for(int i=0;i<(int)g.size()&&!changed;i++){int block=-1;for(int j=i+1;j<(int)g.size();j++){if(g[i]==g[j]){if(block<0){steps.push_back({{"kind","trace_cancel"},{"i",i},{"j",j},{"gate",g[i]}});g.erase(g.begin()+j);g.erase(g.begin()+i);changed=true;break;}Gate a=g[i],b=g[block],c;if(a.first==b.second&&b.first!=a.second)c={b.first,a.second};else if(a.second==b.first&&b.second!=a.first)c={a.first,b.second};else break;
steps.push_back({{"kind","diamond_contract"},{"i",i},{"j",j},{"block",block},{"a",a},{"b",b},{"correction",c}});g.erase(g.begin()+j);g.insert(g.begin()+block+1,c);g.erase(g.begin()+i);changed=true;break;}
if(!commute(g[i],g[j])){if(block>=0)break;block=j;}}}
}
J C=J::array();for(auto[d,s]:g)C.push_back({1,d,J::array({s})});z["C"]=C;ofstream(argv[2])<<z.dump();ofstream(argv[3])<<J({{"before",before},{"after",g.size()},{"steps",steps}}).dump(2);cout<<before<<" -> "<<g.size()<<" steps "<<steps.size()<<endl;}
