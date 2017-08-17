import pytest

from datahub.omis.order.test.factories import OrderFactory

from ..models import Order as ESOrder

pytestmark = pytest.mark.django_db


def test_order_to_dict():
    """Test converting an order to dict."""
    order = OrderFactory()
    result = ESOrder.dbmodel_to_dict(order)

    assert result == {
        'id': str(order.pk),
        'company': {
            'id': str(order.company.pk),
            'name': order.company.name
        },
        'contact': {
            'id': str(order.contact.pk),
            'first_name': order.contact.first_name,
            'last_name': order.contact.last_name,
            'name': order.contact.name
        },
        'primary_market': {
            'id': str(order.primary_market.pk),
            'name': order.primary_market.name
        },
        'sector': {
            'id': str(order.sector.pk),
            'name': order.sector.name
        },
        'service_types': [
            {
                'id': str(service_type.pk),
                'name': service_type.name
            }
            for service_type in order.service_types.all()
        ],
        'created_on': order.created_on,
        'created_by': {
            'id': str(order.created_by.pk),
            'first_name': order.created_by.first_name,
            'last_name': order.created_by.last_name,
            'name': order.created_by.name
        },
        'reference': order.reference,
        'description': order.description,
        'contacts_not_to_approach': order.contacts_not_to_approach,
        'delivery_date': order.delivery_date,
        'contact_email': order.contact_email,
        'contact_phone': order.contact_phone,
    }


def test_orders_to_es_documents():
    """Test converting 2 orders to Elasticsearch documents."""
    orders = OrderFactory.create_batch(2)

    result = ESOrder.dbmodels_to_es_documents(orders)

    assert {item['_id'] for item in result} == {str(item.pk) for item in orders}
