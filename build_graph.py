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

for game_id in game_ids:
    try:
        game : dict = requests.get(BASE_URL+'/products/'+ game_id).json()
    except ValueError:
        print(f'Problem with game id: {game_id}.')
        continue
    game_entity = URIRef(NAMESPACE+ str( game['id'] ))

    for key in game.keys():
        if key not in predicates.keys():
            predicates.update({key: URIRef(NAMESPACE+key)})

        subject = game[key]
        if url(subject):
            subject = URIRef(subject)
        else:
            subject = Literal(subject)


        graph.add((game_entity, predicates[key], subject))

graph.serialize(destination="gog_kb.ttl", format="ttl")



