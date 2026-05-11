from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import analyzer, tokenizer
from django_elasticsearch_dsl.registries import registry
from .models import Product
persian_normalizer = analyzer(
    'persian_normalizer',
    tokenizer=tokenizer('standard'),
    filter=['lowercase', 'persian_normalization']
)

@registry.register_document
class ProductDocument(Document):
    name = fields.TextField(analyzer=persian_normalizer, fields={'raw': fields.KeywordField()})
    brand = fields.TextField(analyzer=persian_normalizer)
    description = fields.TextField(analyzer=persian_normalizer)

    class Index:
        name = 'products'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Product
        fields = [
            'id',
            'price',
            'quantity',
        ]