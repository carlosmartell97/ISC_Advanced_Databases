#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <list>
using namespace std;

vector<string> split(string s, string separator){
  vector<string> result;
  string toAdd;
  size_t foundPos = s.find_first_of(separator);
  if(foundPos==string::npos){
    result.push_back(s);
    return result;
  }
  while(foundPos!=string::npos){
    toAdd = s.substr(0, foundPos);
    result.push_back(toAdd);
    s = s.substr(foundPos+1, s.size());
    foundPos = s.find_first_of(separator);
    if(foundPos==string::npos) result.push_back(s);
  }
  return result;
}

class Node {
public:
  string id, label;
  bool visited=0;
  vector<string> connections;
    vector<string> entryPoints;
    float pageRank=1;
  Node(string id, string label){
    this->id=id; this->label=label;
  }
  void addEdge(string id){
    this->connections.push_back(id);
  }
void addEntryPoint(string id){
    this->entryPoints.push_back(id);
  }
};

map<string, Node*> mostInfluential(map<string, Node*> pages){
    float d = 0.85;
    for(int i=0; i<100; i++){
        map<string, Node*>::iterator it = pages.begin();
        while(it != pages.end()){
            float sum = 0;
            for(int j=0; j<it->second->entryPoints.size(); j++){
                if(pages.find( it->second->entryPoints[j] ) != pages.end()){
                    sum += pages[it->second->entryPoints[j]]->pageRank / it->second->connections.size();
                }
            }
            it->second->pageRank = (1-d)+(d*sum);
            it++;
        }
    }
    return pages;
}

int main(){
  ifstream nodos("nodos_se.csv");
  string line, id, label;
  map<string, Node*> pages;
  nodos>>line;
  while(nodos>>line){
    vector<string> atributes = split(line, ",");
    id=atributes[0]; label=atributes[1];
    if(id!="" && label!=""){
      // printf("id:%s\tlabel:%s\n", id.c_str(), label.c_str());
      if(pages.find(id)==pages.end()){
        pages[id] = new Node(id, label);
      }
    }
  }
  string source, target;
  ifstream edges("edges.csv");
  int notFound = 0;
    int notFoundTarget = 0;
  edges >> line;
  while(edges>>line){
    vector<string> atributes = split(line, ",");
    source=atributes[0]; target=atributes[1];
    // printf("source: %s\ttarget:%s\n", source.c_str(), target.c_str());
    if(pages.find(source)!=pages.end()){
      // printf("source %s exists\n", source.c_str());
      pages[source]->addEdge(target);
    } else {
      notFound++;
    }
    if(pages.find(target)!=pages.end()){
      // printf("target %s exists\n", target.c_str());
      pages[target]->addEntryPoint(source);
    } else {
      notFoundTarget++;
    }
  }
  printf("edges not found:%d notFoundTarget:%d\n", notFound, notFoundTarget);

  ofstream output;
  output.open("results.csv");
  map<string, Node*> result = mostInfluential(pages);
  map<string, Node*>::iterator it = result.begin();
  while(it != result.end()){
      printf("%s : %f\n", it->second->label.c_str(), it->second->pageRank);
      output << it->second->label<<","<<it->second->pageRank<<","<<endl;
      it++;
  }
  output.close();

  return 0;
}
