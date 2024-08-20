import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph 
import networkx as nx
import matplotlib.pyplot as pt
import matplotlib
matplotlib.use('TkAgg')

g = rdflib.Graph()

g = g.parse("gog_kb.ttl", format='turtle')

nxg = rdflib_to_networkx_multidigraph(g)

pos = nx.spring_layout(nxg, scale=2)
edge_labels = nx.get_edge_attributes(nxg, 'r')
nx.draw_networkx_edge_labels(nxg, pos, edge_labels=edge_labels)
nx.draw(nxg, with_labels=True)

pt.show()

