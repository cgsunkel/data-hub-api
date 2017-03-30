# pip install boto3
# Run inside manage.py shell_plus

import datetime
import io
import json
import re
import tempfile
from collections import namedtuple, OrderedDict
from logging import getLogger

import boto3

from datahub.interaction.models import ServiceDelivery


logger = getLogger(__name__)
DATETIME_RE = re.compile('/Date\(([-+]?\d+)\)/')


s3 = boto3.resource(
    's3',
    region_name='eu-west-2',
    aws_access_key_id='foo',
    aws_secret_access_key='bar',
)
s3_bucket = s3.Bucket('cornelius.prod.uktrade.io')


def cdms_datetime_to_datetime(value):
    """Parses a cdms datetime as string and returns the equivalent datetime value. Dates in CDMS are always UTC."""
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value

    match = DATETIME_RE.match(value or '')
    if match:
        parsed_val = int(match.group(1))
        parsed_val = datetime.datetime.utcfromtimestamp(parsed_val / 1000)
        return parsed_val.replace(tzinfo=datetime.timezone.utc)
    else:
        logger.warning('Unrecognized value for a datetime: {} returning `None` instead'.format(value))
        return None


def extract(bucket, prefix, spec):
    """Extract data from bucket using given prefix and mapping spec."""
    row_mapping = namedtuple('row_mapping', spec.values())

    def get_by_path(srcdict, path):
        value = srcdict
        for chunk in path.split('.'):
            value = value[chunk]

        return value

    objects = bucket.objects.filter(Prefix=prefix)

    keys = [key.key for key in objects if key.key.endswith('response_body')]
    ret = set()

    for key in keys:
        with tempfile.TemporaryFile() as f:
            print('Processing: {}'.format(key))  # noqa: T003
            bucket.download_fileobj(key, f)
            f.seek(0, 0)
            try:
                results = json.load(io.TextIOWrapper(f))['d']['results']
            except KeyError:
                logger.error('Failed to load result page: {}'.format(key))
                results = []

        for row in results:
            ret.add(row_mapping(
                *(get_by_path(row, field) for field in spec.keys())
            ))

    return ret


spec_model = ServiceDelivery
spec = OrderedDict([
    ('optevia_servicedeliveryId', 'id'),
    ('optevia_Event.Id', 'event_id'),
    ('optevia_ServiceProvider.Id', 'dit_team_id'),
    ('optevia_Service.Id', 'service_id'),
    ('optevia_Contact.Id', 'contact_id'),
    ('optevia_LeadCountry.Id', 'country_of_interest_id'),
    ('optevia_Advisor.Id', 'dit_advisor_id'),
    ('optevia_Sector.Id', 'sector_id'),
    ('optevia_Organisation.Id', 'company_id'),
    ('optevia_ServiceDeliveryStatus.Id', 'status_id'),
    ('optevia_UKRegion.Id', 'uk_region_id'),
    ('optevia_ServiceOffer.Id', 'service_offer_id'),
    ('optevia_OrderDate', 'date'),
    ('optevia_Notes', 'notes'),
    ('optevia_name', 'subject'),
])

# spec_model = Event
# spec = OrderedDict([
#     ('optevia_eventId', 'id'),
#     ('optevia_name', 'name'),
# ])

# spec_model = ServiceOffer
# spec = OrderedDict([
#     ('optevia_serviceofferId', 'id'),
#     ('optevia_Event.Id', 'event_id'),
#     ('optevia_Service.Id', 'service_id'),
#     ('optevia_ServiceProvider.Id', 'dit_team_id'),
# ])

res = extract(
    s3_bucket,
    'CACHE/XRMServices/2011/OrganizationData.svc/optevia_servicedeliverySet',
    # 'CACHE/XRMServices/2011/OrganizationData.svc/optevia_eventSet',
    # 'CACHE/XRMServices/2011/OrganizationData.svc/optevia_serviceofferSet',
    spec,
)

for i, row in enumerate(res):
    if i % 100 == 0:
        print(i)  # noqa: T003

    try:
        data = row._asdict()
        data['date'] = cdms_datetime_to_datetime(data['date'])
        data['notes'] = data['notes'] or ''
        obj_id = data.pop('id')
        obj, created = spec_model.objects.get_or_create(
            id=obj_id, defaults=data
        )
        if not created:
            for name, value in data.items():
                setattr(obj, name, value)
            obj.save()

    except Exception as e:
        logger.exception('Exception during importing data')
