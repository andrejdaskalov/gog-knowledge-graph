from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS, XSD
import requests
from validators import url
from fetch_from_dbpedia import dbpedia_fetch

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
        elif prefix_key == 'game_type':
            game_type = obj
            if game_type not in game_types.keys():
                game_types.update({game_type: URIRef(NAMESPACE+game_type)})
            triples.append((subject, predicates['gameType'], game_types[game_type]))
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
    game_types = dict()
    
    # fill predicates with some hard-coded values
    predicates.update([
        ( "hasLanguage", URIRef(NAMESPACE+"hasLanguage") ),
        ( "systemCompat", URIRef(NAMESPACE+"isSystemCompatibleWith")),
        ( "hasDLC", URIRef(NAMESPACE+"hasDLC")),
        ( "gameType", URIRef(NAMESPACE+"gameType") ),
        ( "dbpEntry", URIRef(NAMESPACE+"dbpEntry") ),
        ( "developer", URIRef(NAMESPACE+"developer") ),
        ( "publisher", URIRef(NAMESPACE+"publisher") ),
        ( "genre", URIRef(NAMESPACE+"genre") ),
    ])

    graph = Graph()
    
    processed_games = 0
    total_games = len(game_ids)

    for game_id in game_ids:

        try:
            game : dict = requests.get(BASE_URL+'/products/'+ game_id).json()
        except ValueError:
            print(f'Problem with game id: {game_id}.')
            continue

        game_entity = URIRef(NAMESPACE+ str( game['id'] ))
        triples = dict_to_triples(game_entity, game)

        for triple in triples:
            graph.add(triple)

        title = game['title']
        dbp_game, dev, pub, genre = dbpedia_fetch(title)
        if dbp_game != '' :
            graph.add((game_entity, predicates['dbpEntry'], URIRef( dbp_game )))
        if dev != '' :
            graph.add((game_entity, predicates['developer'], URIRef( dev )))
        if pub != '' :
            graph.add((game_entity, predicates['publisher'], URIRef( pub )))
        if genre != '' :
            graph.add((game_entity, predicates['genre'], URIRef( genre )))
        
        processed_games+=1
        print(f"{processed_games}/{total_games} processed...",end="\r")

    print()
    graph.serialize(destination="gog_kb.ttl", format="ttl")
    print("Finished building graph!")



