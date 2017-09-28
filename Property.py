import numpy as np
from numpy import asarray
from scipy import log
import networkx as nx

class Property:
    def __init__(self, G):
        self.G = G

    # def averageKL(self, data1, data2):
    #
    #     data1, data2 = map(asarray, (data1, data2))
    #     n1 = data1.shape[0]
    #     n2 = data2.shape[0]
    #     data1 = np.sort(data1)
    #     data2 = np.sort(data2)
    #     cdf1 = np.searchsorted(data1, data2, side='right') / (1.0 * n1)
    #     cdf2 = np.searchsorted(data2, data2, side='right') / (1.0 * n2)
    #     pmf1 = []
    #     pmf2 = []
    #     pmf1.append(cdf1[0])
    #     pmf2.append(cdf2[0])
    #
    #     value = cdf1[0]
    #     for i in range(1, len(cdf1)):
    #         if cdf1[i - 1] == cdf1[i]:
    #             pmf1.append(value)
    #         else:
    #             value = cdf1[i] - cdf1[i - 1]
    #             pmf1.append(cdf1[i] - cdf1[i - 1])
    #
    #     value = cdf2[0]
    #     for i in range(1, len(cdf2)):
    #         if cdf2[i - 1] == cdf2[i]:
    #             pmf2.append(value)
    #         else:
    #             value = cdf2[i] - cdf2[i - 1]
    #             pmf2.append(value)
    #
    #     alpha = 0.99
    #     pmf1 = np.array(pmf1)
    #     pmf2 = np.array(pmf2)
    #
    #     results = abs((alpha * pmf1 + (1 - alpha) * pmf2) * (
    #         log(alpha * pmf1 + (1 - alpha) * pmf2) - log(alpha * pmf2 + (1 - alpha) * pmf1))).sum()
    #     return results/n2

    def averageKL(self, data1, data2):

        number_of_bins = int(min(len(data1), len(data2))/2)
        lowScope = min(min(data1), min(data2))
        highScope = max(max(data1), max(data2))
        hist_1, _ = np.histogram(data1, bins=number_of_bins, range=[lowScope, highScope])
        hist_2, _ = np.histogram(data2, bins=number_of_bins, range=[lowScope, highScope])
        minima = np.minimum(hist_1, hist_2)
        intersection = np.true_divide(np.sum(minima), np.sum(hist_2))
        return intersection

    def getDegree(self):
        return sorted(nx.degree(self.G).values())

    def getInDegree(self):
        return sorted(self.G.in_degree().values())

    def getOutDegree(self):
        return sorted(self.G.out_degree().values())

    def getAverageNeighborDegree(self):
        return sorted(nx.average_neighbor_degree(self.G).values())

    def getNodeBetweennessCentrality(self):
        dictBetweenness = nx.betweenness_centrality(self.G)
        return sorted(list(dictBetweenness.values()))

    def getLocalClusteringCoefficient(self):
        if self.G.is_multigraph() or self.G.is_directed():
            G = nx.Graph(self.G)
        else:
            G = self.G
        return sorted(list((nx.clustering(G).values())))
    def getPageRank(self):
        if self.G.is_multigraph():
            G = nx.Graph(self.G)
        else:
            G = self.G
        return sorted(list((nx.pagerank(G).values())))

    def getTriangles(self):
        if self.G.is_multigraph() or self.G.is_directed():
            G = nx.Graph(self.G)
        else:
            G = self.G
        return sorted(list((nx.triangles(G).values())))

    def getHarmonicCentrality(self):
        return sorted(list((nx.harmonic_centrality(self.G).values())))

    def getCoreNumber(self):
        if self.G.is_multigraph() or self.G.is_directed():
            G = nx.Graph(self.G)
        else:
            G = self.G
        G.remove_edges_from(G.selfloop_edges())
        return sorted(list((nx.core_number(G).values())))

