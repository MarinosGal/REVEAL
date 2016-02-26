# Marinos Galiatsatos
# February 24, 2016

import numpy as np
import networkx as nx
import pandas as pd
import json
import sys
import matplotlib.pyplot as plt
import operator
import scipy.stats as stats
from sklearn import preprocessing
from math import*
from difflib import SequenceMatcher


#__Functions__#

# reads any json file
# Argument: the json file's name
# Returns: all json data
def readjson(jf):
	line_generator = open(jf)
	return line_generator


# Creates a Graph, based on the mentions interactions between users
# Argument: all json lines
# Returns: Graph, unique users, all hashtags, all tweet texts
def createGraph(line_generator):
	allusers = []
	G = nx.Graph()
	hashtags = []
	alltexts = []
	for line in line_generator:
		line_obj = json.loads(line)
		hashtags.append(( line_obj['user']['id'], line_obj['entities']['hashtags']))
		G.add_node(line_obj['user']['id'], user=line_obj['user'], hashtag=line_obj['entities']['hashtags'])
		allusers.append(line_obj['user']['id']) # all users' ids (not neccessarelly all mentions' ids)		
		for mentions in line_obj['entities']['user_mentions']:
			if mentions:
				G.add_edge(line_obj['user']['id'], mentions['id'], mention=mentions)
				alltexts.append((line_obj['user']['id'], mentions['id'],line_obj['text']))

	return (G,set(allusers), hashtags, alltexts)


# Finds Degree Centrality of Nodes
# Arguments: a Graph
# Returns: a sorted list with the degree centrality of each graph node
def getDegreeCentrality(Graph):
	degree_cen = nx.degree_centrality(Graph)
	return sorted(degree_cen.items(), key=operator.itemgetter(1), reverse=True)


# Finds Betweeness Centrality of Nodes
# Arguments: a Graph
# Returns: a sorted list with the betweenness centrality of each graph node
def getBetweennessCentrality(Graph):
	betweenness_cen = nx.betweenness_centrality(Graph, normalized=True)
	return sorted(betweenness_cen.items(), key=operator.itemgetter(1), reverse=True)


# Finds the pagerank of Nodes
# Arguments: a Graph
# Returns: a sorted list with the pagerank of each graph node
def getPagerank(Graph):
	page_rank = nx.pagerank(Graph)
	return sorted(page_rank.items(), key=operator.itemgetter(1), reverse=True)


# Collencts all the followers of each node
# Arguments: a Graph and twitter users
# Returns: a sorted unique list with all the nodes' followers 
def getFollowers(Graph, allusers):
	followers = []
	restnodes = []
	for node in Graph.nodes():
		if node not in allusers:
			restnodes.append(node)
	followers = []
	for user in allusers:
		followers.append((user, Graph.node[user]['user']['followers_count']))
	for rest in restnodes:
		followers.append((rest, 0))

	return sorted(followers, key=lambda f:f[1], reverse=True)


# Normalizes ranks with MinMaxScaler between 0 and 1
# Arguments: a rank
# Returns: a rank with nomralized values
def normalizeData(diction):
	min_max_scaler = preprocessing.MinMaxScaler()
	ids = []
	values = []
	for d in diction: 
		ids.append(float(d[0]))
		values.append(float(d[1]))
	norm_values = min_max_scaler.fit_transform(np.asarray(values).reshape(-1,1))
	nv = []
	for norm in norm_values:
		nv.append(norm[0])
	final = []
	for i in range(len(nv)):
		final.append((ids[i],nv[i]))

	return final

# Finds Kendall Tau Correlation between two ranks
# Arguments: two same sized ranks
# Returns: tau statistics and p_value
def getKendallTauCorrelation(rank1,rank2):
	r1values = []
	for r1 in rank1:
		r1values.append(r1[1])
	r2values = []
	for r2 in rank2:
		r2values.append(r2[1])

	tau, p_value = stats.kendalltau(r1values,r2values)
	return (tau,p_value)


# Returns the top 5 rankings
# Arguments: a ranking list
# Returns: a list with the top 5 emelents
def getTop5ranking(rank):
	topfive = []
	for i in range(5):
		topfive.append(rank[i])
	return topfive


# Finds the all hastags of a node from the top 5 list
# Arguments: a rank and a Graph
# Returns: a list with the hashtags from each node
def getHashtags(rank,Graph,alltexts):
	allhashtags = []
	hashtag_flag = False
	for r in rank:
		if Graph.node[int(r[0])]:
			hashtag_flag=True
			temphashtag = Graph.node[int(r[0])]['hashtag']
		for uid, mid, text in alltexts:
			if mid==r[0] or uid==r[0]:
				temptext = text
				break

		if hashtag_flag==True and len(temphashtag)!=0:
			allhashtags.append( (r[0], temphashtag, temptext) )
			hashtag_flag=False
		else:
			allhashtags.append( (r[0], [], text) )
			
	return allhashtags


# Takes two lists and tries to find the similarities between them
# Arguments: two lists
# Returns: the ratio of the similarity
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Finds all the similarities of a rank with size=5
# Arguments: a rank with size = 5
# Returns: a list with all the similarities for every pair
def getContentSimilarities(Lista):
	similarities = []
	similarities.append( (Lista[0][2], Lista[1][2], (similar(Lista[0][2], Lista[1][2]))) )
	similarities.append( (Lista[0][2], Lista[2][2], (similar(Lista[0][2], Lista[2][2]))) )
	similarities.append( (Lista[0][2], Lista[3][2], (similar(Lista[0][2], Lista[3][2]))) )
	similarities.append( (Lista[0][2], Lista[4][2], (similar(Lista[0][2], Lista[4][2]))) )
	similarities.append( (Lista[1][2], Lista[2][2], (similar(Lista[1][2], Lista[2][2]))) )
	similarities.append( (Lista[1][2], Lista[3][2], (similar(Lista[1][2], Lista[3][2]))) )
	similarities.append( (Lista[1][2], Lista[4][2], (similar(Lista[1][2], Lista[4][2]))) )
	similarities.append( (Lista[2][2], Lista[3][2], (similar(Lista[2][2], Lista[3][2]))) )
	similarities.append( (Lista[2][2], Lista[4][2], (similar(Lista[2][2], Lista[4][2]))) )
	similarities.append( (Lista[3][2], Lista[4][2], (similar(Lista[3][2], Lista[4][2]))) )

	return similarities


#__Main__#
def main():
	jsonfile = sys.argv[1] # json file's name given by the user	
	line_generator = readjson(jsonfile) # returns the lines of json file	
	(Gr, allusers, hashtags, alltexts) = createGraph(line_generator) # creates the Graph

	#_Compute measures_#
	degree_cen = getDegreeCentrality(Gr) # returns Degree Centrality
	betweenness_cen = getBetweennessCentrality(Gr) # returns Betweenness Centrality
	page_rank = getPagerank(Gr) # returns Pagerank
	followers = getFollowers(Gr, allusers)

	#_Normalize all measures_#
	norm_degree_cen = normalizeData(degree_cen)
	norm_betweenness_cen = normalizeData(betweenness_cen)
	norm_page_rank = normalizeData(page_rank)
	norm_followers = normalizeData(followers)

	#_Compute Kendall's Tau correlation_#
	(db_tau, db_p_value) = getKendallTauCorrelation(norm_degree_cen,norm_betweenness_cen)
	(dp_tau, dp_p_value) = getKendallTauCorrelation(norm_degree_cen,norm_page_rank)
	(df_tau, df_p_value) = getKendallTauCorrelation(norm_degree_cen,norm_followers)
	(bp_tau, bp_p_value) = getKendallTauCorrelation(norm_betweenness_cen,norm_page_rank)
	(bp_tau, bp_p_value) = getKendallTauCorrelation(norm_betweenness_cen,norm_followers)
	(pf_tau, pf_p_value) = getKendallTauCorrelation(norm_page_rank,norm_followers)

	#_Find the top 5 users of each ranking list_#
	degree_cen_top5 = getTop5ranking(norm_degree_cen)
	betweenness_cen_top5 = getTop5ranking(norm_betweenness_cen)
	page_rank_top5 = getTop5ranking(norm_page_rank)
	followers_top5 = getTop5ranking(norm_followers)

	#_Find hashtags and texts for each tweet_#
	degree_hashs = getHashtags(degree_cen_top5,Gr,alltexts)
	betweenness_hashs = getHashtags(betweenness_cen_top5,Gr,alltexts)
	page_rank_hashs = getHashtags(page_rank_top5,Gr,alltexts)
	followers_hashs = getHashtags(followers_top5,Gr,alltexts)
	
	#_Finds the Content Similarity between users from each ranking list_#
	getContentSimilarities(degree_hashs)
	getContentSimilarities(betweenness_hashs)
	getContentSimilarities(page_rank_hashs)
	getContentSimilarities(followers_hashs)	


# Call main()
if __name__ == '__main__': main()