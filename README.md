# Introduction
In this test we create four ranking lists from a graph that represents tweets . More specifically, we
create a degree, betweenness, pagerank and followers ranking lists and apply to them the Kendall's
Tau correlation. Also, we try to find similarities among the tweet's content of the top users of each
ranking list.

# Problem
Suppose you have a stream of data which is produced by a set of users and you want to find the
most influential users in this set. If you represent the data as a graph where the nodes are the users
and the edges are the interactions between the users then your problem can be translated in finding
the most central nodes in the graph.

# Implementation
For the implementation we used Python, with the NetworkX package for the creation of the Graph,
and sklearn package for the normalization of the rank values. Other usefull packages that were used
are scipy, pandas and json.

1. We load the json file. For the Graph Nodes we collect all the users with their details and the
hashtags that they may have used in the tweet. For the Graph Edges we combine the users with the
mention users for a tweet. If a user A has mentioned B and C, then we create 2 edges (A-B) and (A-
C). Also, because some users don't use hashtags we store the tweet text, in order to use it later for
better results in content similarities.

2. After the creation of the Graph, we apply 3 centrality measures on it, degree, betweenness
and pagerank, and we create 3 ranks. We also create a rank of the users with respect to the number
of followers that they have.

3. We created 4 more lists with the top 5 users from every ranking list. Using the similar
function that python provides, we compare the tweets among the users from each ranking list.
Similar function returns a value between 0 and 1 and finds the relation between 2 strings. For
example, similar(“Apple”, “Appel”)=0.8 but similar (“Apple”, “Mango”)=0.0.

# Info
This application is an excercise for the Reveal Project https://revealproject.eu/
