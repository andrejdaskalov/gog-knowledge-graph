from rdflib import Graph
from rdflib_endpoint.sparql_endpoint import SparqlEndpoint
import uvicorn

# load the graph
g = Graph()
g = g.parse("gog_kb.ttl", format="turtle")

example_query = """
    prefix gog: <file:///home/andrej/wbs/goggraph>
    select ?game_title ?dlc_title
    where {
        ?game gog:hasDLC ?dlc .
        ?game gog:title ?game_title .
        ?dlc gog:title ?dlc_title
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
