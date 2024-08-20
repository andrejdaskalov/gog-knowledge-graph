from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS, XSD
import requests
from validators import url

# constants 
BASE_URL = 'https://api.gog.com'
NAMESPACE = 'goggraph/'
# external resource constants
MAC_OS = 'http://dbpedia.org/resource/MacOS'
WINDOWS = 'http://dbpedia.org/resource/Microsoft_Windows'
LINUX = 'http://dbpedia.org/resource/Linux'

def load_game_ids():
    with open("game_ids.txt", mode='r', encoding='utf-8') as f:
        game_ids = f.read().split("\n")
        return game_ids


def dict_to_triples(subject: URIRef, props: dict, prefix: str = "") -> list[tuple]:
    triples = []
    for key in props.keys():
        prefix_key = '_'.join([prefix, key]) if prefix != "" else key
        if prefix_key not in predicates.keys():
            predicates.update({prefix_key: URIRef(NAMESPACE+prefix_key)})

        obj = props[key]
        if prefix_key == 'languages':
            triples.extend(lang_to_triples(subject, obj))
        elif prefix_key == 'dlcs_products':
            triples.extend(dlc_triples(subject, obj))
        elif prefix_key == 'content_system_compatibility':
            triples.extend(system_compatibility_triples(subject, obj))
        elif type(obj) is dict:
            triples.extend(dict_to_triples(subject, obj, prefix=prefix_key))
        else:
            if url(obj):
                obj = URIRef(obj)
            else:
                obj = Literal(obj)
            triples.append((subject, predicates[prefix_key], obj))

    return triples 

def lang_to_triples(subject: URIRef, props: dict ) -> list[tuple]:
    triples = []
    for key in props.keys():
        if key not in languages.keys():
            new_lang = URIRef(NAMESPACE+"lang_"+key)
            triples.append((new_lang, RDFS.label, Literal(props[key], datatype=XSD.string)))
            languages.update({key : new_lang})

        triples.append((subject, predicates['hasLanguage'], languages[key]))

    return triples

def system_compatibility_triples(subject: URIRef, props: dict) -> list[tuple]:
    triples = []
    for key in props.keys():
        obj = None
        match key:
            case 'windows':
                obj = URIRef(WINDOWS)
            case 'linux': 
                obj = URIRef(LINUX)
            case 'osx': 
                obj = URIRef(MAC_OS)

        if obj is not None:
            triples.append((subject, predicates["systemCompat"], obj))

    return triples

def dlc_triples(subject: URIRef, dlcs: list[dict]) -> list[tuple]:
    triples = []
    for dlc in dlcs:
        dlc_id = str(dlc['id'])
        triples.append((subject, predicates["hasDLC"], URIRef(NAMESPACE+dlc_id)))
    return triples

if __name__ == "__main__":

    # load game ids from file 
    game_ids = load_game_ids()
    if len(game_ids) == 0:
        print("Game id file is empty")
    
    # dicts to hold some reused nodes
    predicates = dict()
    languages = dict()
    
    # fill predicates with some hard-coded values
    predicates.update([
        ( "hasLanguage", URIRef(NAMESPACE+"hasLanguage") ),
        ( "systemCompat", URIRef(NAMESPACE+"isSystemCompatibleWith")),
        ( "hasDLC", URIRef(NAMESPACE+"hasDLC")),
    ])

    graph = Graph()


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



