import re

import pytest
from django.core.management import call_command

from datahub.company.test.factories import CompanyFactory
from datahub.core.constants import Country
from datahub.core.postcode_constants import CountryPostcodeReplacement
from datahub.core.test_utils import has_reversion_comment, has_reversion_version

pytestmark = pytest.mark.django_db


def setup_us_company_with_all_addresses(post_code):
    """Sets up US Company for tests"""
    return CompanyFactory(
        address_town='New York',
        address_country_id=Country.united_states.value.id,
        address_postcode=post_code,
        address_area_id=None,
        registered_address_town='New York',
        registered_address_country_id=Country.united_states.value.id,
        registered_address_postcode=post_code,
        registered_address_area_id=None,
        uk_region_id=None,
    )


def setup_us_company_with_address_only(post_code):
    """Sets up US Company with address only for tests"""
    return CompanyFactory(
        address_town='New York',
        address_country_id=Country.united_states.value.id,
        address_postcode=post_code,
        address_area_id=None,
        registered_address_town='',
        registered_address_country_id=None,
        registered_address_postcode='',
        registered_address_area_id=None,
        uk_region_id=None,
    )


def setup_us_company_with_registered_address_only(post_code):
    """Sets up US Company with registered address only for tests"""
    return CompanyFactory(
        registered_address_town='New York',
        registered_address_country_id=Country.united_states.value.id,
        registered_address_postcode=post_code,
        registered_address_area_id=None,
        address_town='',
        address_country_id=None,
        address_postcode='',
        address_area_id=None,
        uk_region_id=None,
    )


@pytest.mark.parametrize(
    'post_code, expected_result',
    [
        ('1 0402', '10402'),
        ('123456789', '123456789'),
        ('8520 7402', '07402'),
        ('CA90025', '90025'),
        ('NY 10174 – 4099', '10174 – 4099'),
        ('NY 10174 - 4099', '10174 - 4099'),
        ('MC 5270 3800', '03800'),
        ('K1C1T1', 'K1C1T1'),
        ('NY 1004', 'NY 1004'),
        ('YO22 4PT', 'YO22 4PT'),
        ('RH175NB', 'RH175NB'),
        ('WA 6155', 'WA 6155'),
        ('BT12 6RE', 'BT12 6RE'),
        ('M2 4JB', 'M2 4JB'),
        ('CA USA', 'CA USA'),
        ('n/a', 'n/a'),
        ('MN5512', 'MN5512'),
        ('BB12 7DY', 'BB12 7DY'),
        ('PO6 3EZ', 'PO6 3EZ'),
        ('Nw1 2Ew', 'Nw1 2Ew'),
        ('WC1R 5NR', 'WC1R 5NR'),
        ('BH12 4NU', 'BH12 4NU'),
        ('CT 6506', 'CT 6506'),
        ('ME9 0NA', 'ME9 0NA'),
        ('DY14 0QU', 'DY14 0QU'),
        ('12345', '12345'),
        ('12345-1234', '12345-1234'),
        ('12345 - 1234', '12345 - 1234'),
        ('0 12345', '01234'),
    ])
def test_command_regex_generates_the_expected_postcode_substitution(post_code, expected_result):
    """
    Test regex efficiently without connecting to a database
    :param post_code: POSTCODE format good and bad
    :param expected_result: regular expression substituted value using the
           Command pattern
    """
    actual_result = re.sub(
        CountryPostcodeReplacement.united_states.value.postcode_pattern,
        CountryPostcodeReplacement.united_states.value.postcode_replacement,
        post_code,
        0,
        re.MULTILINE)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'post_code, area_code, area_name',
    [
        ('00589', 'NY', 'New York'),
        ('00612-1234', 'PR', 'Puerto Rico'),
        ('01012', 'MA', 'Massachusetts'),
        ('02823', 'RI', 'Rhode Island'),
    ])
def test_us_company_with_unique_zips_generates_valid_address_area(
        post_code,
        area_code,
        area_name):
    """
    Test postcode is fixed for the purpose of admin area
    generation with valid zip codes format
    :param post_code: POSTCODE good
    :param area_code: Area Code to be generated from Command
    :param area_name: Area Name to describe area code
    """
    company = setup_us_company_with_all_addresses(post_code)
    assert company.address_area is None

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.address_area is not None
    assert company.address_area.area_code == area_code
    assert company.address_postcode == post_code


@pytest.mark.parametrize(
    'post_code, area_code, area_name',
    [
        ('030121234', 'NH', 'New Hampshire'),
        ('03912', 'ME', 'Maine'),
        ('04946', 'ME', 'Maine'),
        ('05067-1234', 'VT', 'Vermont'),
    ])
def test_us_company_with_address_data_only_will_generate_address_area(
        post_code,
        area_code,
        area_name):
    """
    Test postcode fixes and area generation with address area data
    :param post_code: POSTCODE good
    :param area_code: Area Code to be generated from Command
    :param area_name: Area Name to describe area code
    """
    company = setup_us_company_with_address_only(post_code)
    assert company.address_area is None

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.address_area is not None
    assert company.address_area.area_code == area_code
    assert company.address_postcode == post_code


@pytest.mark.parametrize(
    'post_code, area_code, area_name',
    [
        ('05512', 'MA', 'Massachusetts'),
        ('05612-1234', 'VT', 'Vermont'),
        ('060123456', 'CT', 'Connecticut'),
        ('07045', 'NJ', 'New Jersey'),
    ])
def test_us_company_with_unique_zips_generates_the_valid_registered_address_area(
        post_code,
        area_code,
        area_name):
    """
    Test registered address postcode fixes and area generation a
    couple of valid Zip Codes using the real DB
    :param post_code: POSTCODE good
    :param area_code: Area Code to be generated from Command
    :param area_name: Area Name to describe area code
    """
    company = setup_us_company_with_all_addresses(post_code)
    assert company.registered_address_area is None

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.registered_address_area is not None
    assert company.registered_address_area.area_code == area_code
    assert company.registered_address_postcode == post_code


@pytest.mark.parametrize(
    'post_code, area_code, area_name',
    [
        ('10057', 'NY', 'New York'),
        ('15078', 'PA', 'Pennsylvania'),
        ('19789-4567', 'DE', 'Delaware'),
        ('20067', 'DC', 'District of Columbia'),
    ])
def test_us_company_with_registered_address_data_only_will_generate_registered_address_area(
        post_code,
        area_code,
        area_name):
    """
    Test registered address data only creates data expected
    :param post_code: POSTCODE good
    :param area_code: Area Code to be generated from Command
    :param area_name: Area Name to describe area code
    """
    company = setup_us_company_with_registered_address_only(post_code)
    assert company.registered_address_area is None

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.registered_address_area is not None
    assert company.registered_address_area.area_code == area_code
    assert company.registered_address_postcode == post_code


@pytest.mark.parametrize(
    'post_code, expected_result',
    [
        ('1 0402', '10402'),
        ('8520 7402', '07402'),
        ('CA90025', '90025'),
        ('NY 10174 – 4099', '10174 – 4099'),
        ('NY 10174 - 4099', '10174 - 4099'),
        ('NY 123456789', '123456789'),
    ])
def test_command_fixes_invalid_postcodes_in_all_post_code_fields(
        post_code,
        expected_result):
    """
    Test Patterns that need fixing in all postcode fields
    :param post_code: Invalid Postcode Format
    :param expected_result:  The expected result of the fix
    """
    company = setup_us_company_with_all_addresses(post_code)
    assert company.address_postcode == post_code
    assert company.registered_address_postcode == post_code

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.address_postcode == expected_result
    assert company.registered_address_postcode == expected_result


@pytest.mark.parametrize(
    'post_code, expected_result',
    [
        ('A1B 4H7', 'A1B 4H7'),
        ('MA 02 111', 'MA 02 111'),
        ('PO Box 2900', 'PO Box 2900'),
        ('5 Westheimer Road', '5 Westheimer Road'),
        ('CA USA', 'CA USA'),
        ('n/a', 'n/a'),
        ('VA 2210', 'VA 2210'),
        ('tbc', 'tbc'),
    ])
def test_command_leaves_invalid_postcodes_in_original_state_with_no_area(
        post_code,
        expected_result):
    """
    Test edge cases are preserved
    :param post_code: Invalid Postcode Format
    :param expected_result:  The expected result of the fix
    """
    company = setup_us_company_with_all_addresses(post_code)

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.address_postcode == expected_result
    assert company.registered_address_postcode == expected_result
    assert company.address_area is None
    assert company.registered_address_area is None


@pytest.mark.parametrize(
    'post_code, expected_result',
    [
        ('1 0402', '10402'),
        ('8520 7402', '07402'),
        ('CA90025', '90025'),
    ])
def test_audit_log(post_code, expected_result):
    """
    Verify auditable versions of the code are retained
    :param post_code: Invalid Postcode Format
    :param expected_result:  The expected result of the fix
    """
    company = setup_us_company_with_all_addresses(post_code)

    call_command('fix_us_company_address_postcode_for_company_address_area')

    company.refresh_from_db()
    assert company.address_postcode == expected_result
    assert company.registered_address_postcode == expected_result
    assert has_reversion_version(company)
    assert has_reversion_comment('US Area and postcode Fix.')
