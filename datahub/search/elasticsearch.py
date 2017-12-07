from collections import defaultdict
from itertools import chain

from django.conf import settings
from elasticsearch.helpers import bulk as es_bulk
from elasticsearch_dsl import analysis, Index, Search
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import MatchPhrase, MultiMatch, Q

from .apps import get_search_apps

MAX_RESULTS = 10000

lowercase_keyword_analyzer = analysis.CustomAnalyzer(
    'lowercase_keyword_analyzer',
    tokenizer='keyword',
    filter=('lowercase',)
)

# Trigram tokenizer enables us to support partial matching
trigram = analysis.tokenizer(
    'trigram',
    'nGram',
    min_gram=3,
    max_gram=3,
    token_chars=('letter', 'digit',)
)

# Filters out "-" so that t-shirt and tshirt can be matched
special_chars = analysis.char_filter('special_chars', 'mapping', mappings=('-=>',))
trigram_analyzer = analysis.CustomAnalyzer(
    'trigram_analyzer',
    tokenizer=trigram,
    char_filter=special_chars,
    filter=('lowercase',),
)

english_possessive_stemmer = analysis.token_filter(
    'english_possessive_stemmer',
    type='stemmer',
    language='possessive_english'
)

english_stemmer = analysis.token_filter(
    'english_stemmer',
    type='stemmer',
    language='english'
)

english_stop = analysis.token_filter(
    'english_stop',
    type='stop',
    stopwords='_english_'
)

english_analyzer = analysis.CustomAnalyzer(
    'english_analyzer',
    tokenizer='standard',
    filter=[
        english_possessive_stemmer,
        'lowercase',
        english_stop,
        english_stemmer,
    ]
)

lowercase_analyzer = analysis.CustomAnalyzer(
    'lowercase_analyzer',
    tokenizer='standard',
    filter=('lowercase',)
)


def configure_connection():
    """Configure Elasticsearch default connection."""
    connections.configure(
        default={
            'hosts': [settings.ES_URL],
            'verify_certs': settings.ES_VERIFY_CERTS
        }
    )


ANALYZERS = (
    lowercase_keyword_analyzer,
    trigram_analyzer,
    english_analyzer,
    lowercase_analyzer,
)


def configure_index(index_name, settings=None):
    """Configures Elasticsearch index."""
    client = connections.get_connection()
    if not client.indices.exists(index=index_name):
        index = Index(index_name)
        for analyzer in ANALYZERS:
            index.analyzer(analyzer)

        if settings:
            index.settings(**settings)
        index.create()


def get_search_term_query(term, fields=None):
    """Returns search term query."""
    if term == '':
        return Q('match_all')

    should_query = [
        # Promote exact name match
        MatchPhrase(name_keyword={'query': term, 'boost': 2}),
        # Exact match by id
        MatchPhrase(id=term),
        # Cross match fields
        MultiMatch(
            query=term,
            fields=fields,
            type='cross_fields',
            operator='and',
        )
    ]

    return Q('bool', should=should_query)


def remap_sort_field(field):
    """Replaces fields to aliases suitable for sorting."""
    name_map = {
        'name': 'name_keyword',
    }
    return name_map.get(field, field)


def get_sort_query(qs, field_order=None):
    """Attaches sort query."""
    if field_order is None:
        return qs

    tokens = field_order.rsplit(':', maxsplit=1)
    order = tokens[1] if len(tokens) > 1 else 'asc'

    sort_params = {
        'order': order,
        'missing': '_first' if order == 'asc' else '_last'
    }

    # check if we sort by field in nested document (example: 'stage.name')
    if '.' in tokens[0]:
        # extract and add path to nested document (example: 'stage')
        sort_params['nested_path'] = tokens[0].split('.', 1)[0]

    qs = qs.sort({
        remap_sort_field(tokens[0]): sort_params
    })
    return qs


def get_basic_search_query(
        term,
        entities=None,
        field_order=None,
        ignored_entities=(),
        offset=0,
        limit=100
):
    """Performs basic search looking for name and then SEARCH_FIELDS in entity.

    Also returns number of results in other entities.
    """
    limit = _clip_limit(offset, limit)

    all_models = (search_app.ESModel for search_app in get_search_apps())
    fields = set(chain.from_iterable(entity.SEARCH_FIELDS for entity in all_models))

    # Sort the fields so that this function is deterministic
    # and the same query is always generated with the same inputs
    fields = sorted(fields)

    query = get_search_term_query(term, fields=fields)
    s = Search(index=settings.ES_INDEX).query(query)
    s = s.post_filter(
        Q('bool', should=[
            Q('term', _type=entity._doc_type.name) for entity in entities
            if entity._doc_type.name not in ignored_entities
        ])
    )

    s = get_sort_query(s, field_order=field_order)
    s.aggs.bucket(
        'count_by_type', 'terms', field='_type'
    )

    return s[offset:offset + limit]


def _get_field_query(field, value):
    """Gets field query depending on field suffix."""
    if any(field.endswith(suffix) for suffix in ('.id', '_keyword')):
        return Q('match_phrase', **{field: value})

    if field.endswith('_exists'):
        return get_exists_query(field, value)

    field_query = {
        'query': value,
        'operator': 'and',
    }
    return Q('match', **{field: field_query})


def get_field_query(field, value):
    """Gets field query."""
    query = _get_field_query(field, value)
    if '.' not in field:
        return query

    return Q('nested', path=field.rsplit('.', maxsplit=1)[0], query=query)


def get_exists_query(field, value):
    """Gets exists query."""
    real_field = field[:field.rindex('_')]

    kind = 'must' if value else 'must_not'
    query = {
        kind: Q('exists', field=real_field)
    }
    return Q('bool', **query)


def apply_aggs_query(search, aggregates):
    """Applies aggregates query to the search."""
    for aggregate in aggregates:
        # skip range and "search" filters as we can't aggregate them
        if any(aggregate.endswith(x) for x in ('_before', '_after', '_trigram', '_exists')):
            continue

        search_aggs = search.aggs
        if '.' in aggregate:
            search_aggs = search_aggs.bucket(
                aggregate,
                'nested',
                path=aggregate.split('.', 1)[0]
            )

        search_aggs.bucket(aggregate, 'terms', field=aggregate)


def get_filter_query(key, value):
    """Gets filter query."""
    must_filter = []

    if isinstance(value, list):
        # perform "or" query
        must_filter.append(
            Q('bool',
              should=[get_field_query(key, v) for v in value],
              minimum_should_match=1
              )
        )
    else:
        must_filter.append(get_field_query(key, value))

    return must_filter


def get_range_queries(ranges):
    """Gets range queries."""
    return [Q('range', **{k: v}) for k, v in ranges.items()]


def get_search_by_entity_query(term=None,
                               filters=None,
                               composite_filters=None,
                               entity=None,
                               ranges=None,
                               field_order=None,
                               aggregations=None):
    """Perform filtered search for given terms in given entity."""
    query = [Q('term', _type=entity._doc_type.name)]
    if term != '':
        query.append(get_search_term_query(term, fields=entity.SEARCH_FIELDS))

    # document must match all filters in the list (and)
    must_filter = []

    if filters:
        for k, v in filters.items():
            should_filters = None
            if composite_filters and k in composite_filters:
                # process composite filters
                should_filters = (get_filter_query(ck, v) for ck in composite_filters[k])
            elif isinstance(filters[k], dict):
                # process nested or query
                all_nested_filters = {
                    f'{k}_{nested_k}': nested_v
                    for nested_k, nested_v in filters[k].items()
                }

                nested_filters, nested_ranges = date_range_fields(all_nested_filters)
                should_filters = [
                    get_filter_query(nested_k, nested_v)
                    for nested_k, nested_v in nested_filters.items()
                ]
                if nested_ranges:
                    should_filters.append(get_range_queries(nested_ranges))

            if should_filters:
                # builds "or" query for given list of fields
                should = list(chain.from_iterable(should_filters))
                must_filter.append(
                    Q('bool', should=should, minimum_should_match=1)
                )
            else:
                must_filter.extend(
                    get_filter_query(k, v)
                )

    if ranges:
        must_filter.extend(get_range_queries(ranges))

    s = Search(index=settings.ES_INDEX).query('bool', must=query)
    s = get_sort_query(s, field_order=field_order)

    s = s.post_filter('bool', must=must_filter)

    if aggregations:
        apply_aggs_query(s, aggregations)

    return s


def limit_search_query(query, offset=0, limit=100):
    """Limits search query to the page defined by offset and limit."""
    limit = _clip_limit(offset, limit)
    return query[offset:offset + limit]


def bulk(actions=None, chunk_size=None, **kwargs):
    """Send data in bulk to Elasticsearch."""
    return es_bulk(connections.get_connection(), actions=actions, chunk_size=chunk_size, **kwargs)


def date_range_fields(fields):
    """Finds and format range fields."""
    filters = {}
    ranges = defaultdict(dict)

    for k, v in fields.items():
        if k.endswith('_before') or k.endswith('_after'):
            range_key = k[:k.rindex('_')]

            if k.endswith('_before'):
                ranges[range_key]['lte'] = fields[k]
            if k.endswith('_after'):
                ranges[range_key]['gte'] = fields[k]

            continue

        filters.update({k: v})

    return filters, ranges


def _clip_limit(offset, limit):
    return max(min(limit, MAX_RESULTS - offset), 0)
