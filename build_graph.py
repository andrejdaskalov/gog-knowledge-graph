from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import FOAF, RDF
import requests
from validators import url

game_ids = []

BASE_URL = 'https://api.gog.com'
NAMESPACE = 'goggraph/'


with open("game_ids.txt", mode='r', encoding='utf-8') as f:
    game_ids = f.read().split("\n")

predicates = dict()

graph = Graph()

def dict_to_triples(subject: URIRef, props: dict, prefix: str = "") -> list[tuple]:
    tuples = []
    for key in props.keys():
        prefix_key = '_'.join([prefix, key]) if prefix != "" else key
        if prefix_key not in predicates.keys():
            predicates.update({prefix_key: URIRef(NAMESPACE+prefix_key)})

        obj = props[key]
        if type(obj) is dict:
            tuples.extend(dict_to_triples(subject, obj, prefix=prefix_key))
        else:
            if url(obj):
                obj = URIRef(obj)
            else:
                obj = Literal(obj)
            tuples.append((subject, predicates[prefix_key], obj))

    return tuples 


for game_id in game_ids[:10]:
    try:
        game : dict = requests.get(BASE_URL+'/products/'+ game_id).json()
    except ValueError:
        print(f'Problem with game id: {game_id}.')
        continue
    game_entity = URIRef(NAMESPACE+ str( game['id'] ))
    triples = dict_to_triples(game_entity, game)
    for triple in triples:
        graph.add(triple)

graph.serialize(destination="gog_kb.ttl", format="ttl")



