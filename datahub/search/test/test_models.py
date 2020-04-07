import inspect

import pytest
from django.utils.functional import cached_property
from elasticsearch_dsl.index import DEFAULT_DOC_TYPE

from datahub.search.elasticsearch import bulk
from datahub.search.test.search_support.models import RelatedModel, SimpleModel
from datahub.search.test.search_support.relatedmodel import RelatedModelSearchApp
from datahub.search.test.search_support.relatedmodel.models import ESRelatedModel
from datahub.search.test.search_support.simplemodel.models import ESSimpleModel
from datahub.search.utils import get_model_field_names


class TestBaseESModel:
    """Tests for BaseESModel."""

    @pytest.mark.parametrize('include_index', (False, True))
    @pytest.mark.parametrize('include_source', (False, True))
    def test_es_document(self, include_index, include_source):
        """Test that es_document() creates a dict with the expected keys and values."""
        obj = SimpleModel(id=5, name='test-name')
        doc = ESSimpleModel.es_document(
            obj,
            include_index=include_index,
            include_source=include_source,
        )
        source = {
            '_document_type': 'simplemodel',
            'id': obj.pk,
            'name': 'test-name',
            'date': None,
        }

        expected_doc = {
            '_id': obj.pk,
            '_type': DEFAULT_DOC_TYPE,
            **({'_index': ESSimpleModel.get_write_alias()} if include_index else {}),
            **({'_source': source} if include_source else {}),
        }

        assert doc == expected_doc

    @pytest.mark.django_db
    def test_bulk_with_legacy_mapping_type_name(self, es):
        """Test that it does not."""
        related_object = RelatedModel.objects.create()
        doc = ESRelatedModel.es_document(related_object)

        assert doc['_type'] == DEFAULT_DOC_TYPE

        bulk(actions=(doc,), chunk_size=1)

        es.indices.refresh()

        es.exists(
            index=ESRelatedModel.get_write_index(),
            doc_type=RelatedModelSearchApp.name,
            id=related_object.pk,
        )


def test_validate_model_fields(search_app):
    """Test that all top-level fields defined in search models are valid."""
    es_model = search_app.es_model
    db_model = search_app.queryset.model

    fields = get_model_field_names(es_model)

    computed_fields = es_model.COMPUTED_MAPPINGS.keys()
    db_model_properties = _get_object_properties(db_model)
    db_model_fields = _get_db_model_fields(db_model)

    valid_fields = computed_fields | db_model_properties | db_model_fields | {'_document_type'}
    invalid_fields = fields - valid_fields

    assert not invalid_fields


def test_validate_model_mapping_fields(search_app):
    """Test that all fields defined in MAPPINGS exist on the ES model."""
    es_model = search_app.es_model
    valid_fields = get_model_field_names(es_model)
    fields = es_model.MAPPINGS.keys()
    invalid_fields = fields - valid_fields

    assert not invalid_fields


def test_validate_model_computed_mapping_fields(search_app):
    """Test that all fields defined in COMPUTED_MAPPINGS exist on the ES model."""
    es_model = search_app.es_model
    valid_fields = get_model_field_names(es_model)
    fields = es_model.COMPUTED_MAPPINGS.keys()
    invalid_fields = fields - valid_fields

    assert not invalid_fields


def test_validate_model_no_mapping_and_computed_intersection(search_app):
    """Test that MAPPINGS and COMPUTED_MAPPINGS on ES models don't overlap."""
    es_model = search_app.es_model
    intersection = es_model.MAPPINGS.keys() & es_model.COMPUTED_MAPPINGS.keys()

    assert not intersection


def test_validate_model_search_fields(search_app):
    """Test that all field paths in SEARCH_FIELDS exist on the ES model."""
    es_model = search_app.es_model
    mapping = es_model._doc_type.mapping
    invalid_fields = {
        field for field in es_model.SEARCH_FIELDS
        if not mapping.resolve_field(field)
    }

    assert not invalid_fields, (
        f'Invalid search fields {invalid_fields} detected on {es_model.__name__} search model'
    )


def _get_db_model_fields(db_model):
    return {field.name for field in db_model._meta.get_fields()}


def _get_object_properties(obj):
    return {prop[0] for prop in inspect.getmembers(obj, _is_property)}


def _is_property(obj):
    return isinstance(obj, (property, cached_property))
