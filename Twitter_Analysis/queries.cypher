// show all nodes
MATCH(p) RETURN p

// delete all nodes and their relationships
MATCH(p) DETACH DELETE p

// top 10 User nodes in Page Rank
CALL algo.pageRank.stream('User', 'FOLLOWS', {iterations:20}) YIELD node, score
WITH * ORDER BY score DESC LIMIT 10
RETURN node.name, score
