from elasticsearch_dsl import Document, Text, analyzer, tokenizer
from elasticsearch_dsl.connections import connections
from .models import Product

connections.create_connection(hosts=['http://localhost:9200'])

edge_ngram_tokenizer = tokenizer(
    'edge_ngram_tokenizer',
    type='edge_ngram',
    min_gram=2,
    max_gram=10,
    token_chars=["letter", "digit"]
)

edge_ngram_analyzer = analyzer(
    'edge_ngram_analyzer',
    tokenizer=edge_ngram_tokenizer,
    filter=["lowercase"]
)

class ProductDocument(Document):
    name = Text(analyzer=edge_ngram_analyzer, search_analyzer="standard")

    class Index:
        name = 'products'

    def from_django(self, instance):
        self.meta.id = instance.id
        self.name = instance.name
        return self

