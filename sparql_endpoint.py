from rdflib import Graph
from rdflib_endpoint.sparql_endpoint import SparqlEndpoint
import uvicorn

# load the graph
g = Graph()
g = g.parse("gog_kb.ttl", format="turtle")

example_query = """
    # get the titles of all games that have dlcs along with the genre, publisher and developer (if information exists) 
    prefix gog: <file:///home/andrej/wbs/goggraph/>
    select ?game_title ?dlc_title ?genre ?developer ?publisher
    where {
        ?game gog:title ?game_title .
        ?game gog:hasDLC ?dlc .
        ?dlc gog:title ?dlc_title .
        optional {?game gog:genre ?genre.} .
        optional {?game gog:developer ?developer} .
        optional {?game gog:publisher ?publisher} .

    }
"""

app = SparqlEndpoint(
    path='/',
    graph=g,
    example_query=example_query,
    public_url="http://gog.com",
    cors_enabled=False,
    title="GOG Graph SPARQL endpoint",
    description="""A FCSE student project for the purpose of 
        distilling the GOG game library metadata 
        into an RDF graph and provide useful applications""",

)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8080)
