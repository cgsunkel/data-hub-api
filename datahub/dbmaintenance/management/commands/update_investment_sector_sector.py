from logging import getLogger

import reversion

from datahub.dbmaintenance.management.base import CSVBaseCommand
from datahub.dbmaintenance.utils import parse_uuid
from datahub.investment.project.models import InvestmentSector
from datahub.metadata.models import Sector
from datahub.search.signals import disable_search_signal_receivers

logger = getLogger(__name__)


class Command(CSVBaseCommand):
    """Command to update InvestmentSector.sector."""

    @disable_search_signal_receivers(InvestmentSector)
    def _handle(self, *args, **options):
        """
        Disables search signal receivers for investment sectors.
        Avoid queuing huge number of Celery tasks for syncing investment sectors to Elasticsearch.
        (Syncing can be manually performed afterwards using sync_es if required.)
        """
        return super()._handle(*args, **options)

    def _process_row(self, row, simulate=False, overwrite=False, **options):
        """Process a single row."""
        old_sector_id = parse_uuid(row['old_sector_id'])
        investment_sector = InvestmentSector.objects.get(pk=old_sector_id)
        new_sector_id = parse_uuid(row['new_sector_id'])

        investment_sector.sector = Sector.objects.get(pk=new_sector_id)

        if simulate:
            return

        with reversion.create_revision():
            investment_sector.save(update_fields=('sector',))
            reversion.set_comment('InvestmentSector sector correction.')
