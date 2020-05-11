# NAME: SAISUMA DODDA
# UIN: 672075210
# NETID: sdodda4

import math

page_rank_dict = {}     # dictionary to maintain page rank of each node
damping_factor = 0.85

def calculate_page_rank(page_graph):  
    n = 10      # maximum number of iterations for convergence of pagerank
    v = len(page_graph)
    
    # initialize page rank of each node to 1/v
    for url, node_url in page_graph.items():
        node_url.rank = 1 / float(v)
    
    for i in range(n):
        trail_page_rank = 0
        url_rank = {}
        # calculating page rank for all nodes
        for url, node_url in page_graph.items():
            if(len(node_url.out_edges) == 0):   # assign a trail page rank to nodes with outdegree 0
                trail_page_rank += node_url.rank / v
                continue
            previous_rank = node_url.rank / node_url.num_neighbors

            for end_url in node_url.out_edges:
                if end_url not in url_rank:
                    url_rank[end_url] = previous_rank
                else:
                    url_rank[end_url] += previous_rank

        # calculating page rank with damping factor
        for url in page_graph:
            node_rank = 0
            if url in url_rank:
                node_rank = url_rank[url]
            page_graph[url].rank = (1 - damping_factor) * (1 / float(v)) + damping_factor * (node_rank + trail_page_rank)
            
    for url, node_url in page_graph.items():
        page_rank_dict[url] = node_url.rank
    return page_rank_dict