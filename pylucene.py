import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search import BooleanQuery, BooleanClause # Added to combine queries
from org.apache.lucene.search.similarities import BM25Similarity

def create_index(post_data, index_dir):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    # Add post data
    for post in post_data:
        subreddit = post['subreddit']
        body = post['body']
        title = post['title']
        id = post['id']
        score = post['score']
        url = post['url']
        permalink = post['permalink']
        author = post['author']

        #print(f"Getting post: {id}")

        doc = Document()
        doc.add(Field('Subreddit', str(subreddit), contextType))
        doc.add(Field('Body', str(body), contextType))
        doc.add(Field('Title', str(title), contextType))
        doc.add(Field('Id', str(id), metaType))
        doc.add(Field('Score', str(score), metaType))
        doc.add(Field('URL', str(url), metaType))
        doc.add(Field('Permalink', str(permalink), metaType))
        doc.add(Field('Author', str(author), metaType))
        
        # Add comment data
        for comment in post.get('comments', []):
            comment_id = comment['id']
            comment_body = comment['body']
            comment_score = comment['score']
            comment_author = comment['author']
            
            doc.add(Field('Comment_Id', str(comment_id), metaType))
            doc.add(Field('Comment_Body', str(comment_body), contextType))
            doc.add(Field('Comment_Score', str(comment_score), metaType))
            doc.add(Field('Comment_Author', str(comment_author), metaType))
        writer.addDocument(doc)

    writer.close()

def retrieve(storedir, query, num_docs):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    # Body
    body_parser = QueryParser('Body', StandardAnalyzer())
    body_query = body_parser.parse(query)
    
    # https://lucene.apache.org/core/2_9_4/queryparsersyntax.html#Boosting%20a%20Term
    # Title (Give more score if query appears in title)
    title_score = 0.5 # Posts more relevant if query is in title
    title_field = 'Title'
    title_parser = QueryParser(title_field, StandardAnalyzer()).parse(query)
    title_query = BoostQuery(title_parser, title_score) # Boosts relevancy of title by title_score

    # https://lucene.apache.org/core/8_0_0/core/org/apache/lucene/search/BooleanQuery.Builder.html
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
            "text": doc.get("Body")
        })
    
    print(topkdocs)

def load_data(data_dir):
    post_data = []
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.json'):
            with open(os.path.join(data_dir, file_name), 'r') as f:
                post_data.extend(json.load(f))
    return post_data

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
num_docs = 10 # Top docs from query
data_dir = 'Data/'
index_dir = 'sample_lucene_index/'
query = 'best game engine'
    
print(f"Loading posts from {data_dir} folder")
post_data = load_data(data_dir)
print(f"Creating index from post data")
create_index(post_data, index_dir)
print(f"Top {num_docs} scores for query: {query}")
retrieve(index_dir, query, num_docs)