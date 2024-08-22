from SPARQLWrapper import JSON, SPARQLWrapper
from rdflib import URIRef


NAMESPACE = 'gograph/'


def dbpedia_fetch(title: str) -> tuple:
    """
    Fetches the entries from dbpedia for the matching title passed as an argument.

    Args:
        title (str): the title string for the entry

    Returns:
        a tuple of (game (str), dev (str), pub (str), genre (str))
    """


    q = f""" 
            select ?game ?genre ?pub ?dev
            where {{
                ?game dbo:publisher ?pub .
                ?game dbo:developer ?dev .
                ?game dbo:genre ?genre .
                ?game dbp:title ?title .
                FILTER regex(?title, ".*{title}.*", "i")
            }}
            limit 1
        """



    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(q)

    game, dev, pub, genre = '', '', '', ''

    # print(q)
    try:
        ret = sparql.queryAndConvert()
        res = ret['results']['bindings'][0]
        game = res['game']['value']
        dev = res['dev']['value']
        pub = res['pub']['value']
        genre = res['genre']['value']



        # print(f"Game: {game}, pub: {pub}, dev: {dev}, genre: {genre}")

    except Exception as e:
        print(e)

    return game, dev, pub, genre

if __name__ == "__main__":
    title = "A Golden Wake"

    dbp_entry = URIRef(NAMESPACE+'dbpedia_entry')
    developer = URIRef(NAMESPACE+'developer')
    publisher = URIRef(NAMESPACE+'publisher')
    genre = URIRef(NAMESPACE+'genre')
    


    dbpedia_fetch(title)
