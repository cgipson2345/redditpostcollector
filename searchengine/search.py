import lucene
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, BooleanQuery, BooleanClause
from java.nio.file import Paths

def retrieve(storedir, query, num_docs):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
   
    body_parser = QueryParser('Body', StandardAnalyzer())
    body_query = body_parser.parse(query)
    
    # Title: Give higher score if query appears in title
    title_score = 0.5 
    title_field = 'Title'
    title_parser = QueryParser(title_field, StandardAnalyzer()).parse(query)
    title_query = BoostQuery(title_parser, title_score) # Boosts relevancy of title by title_score

    # Combine queries
    new_query = BooleanQuery.Builder()
    new_query.add(title_query, BooleanClause.Occur.SHOULD)
    new_query.add(body_query, BooleanClause.Occur.SHOULD)

    topDocs = searcher.search(new_query.build(), num_docs).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc) # convert to Lucene Doc object
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("Title"),
            "body": doc.get("Body"),
            "url": doc.get("URL"),
            "author": doc.get("Author")
        })
    
    return topkdocs

