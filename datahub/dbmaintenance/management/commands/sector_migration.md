# Sector migration

Queries can be executed by running: `cf conduit datahub-db -- psql`

Commands can be executed by running: `cf v3-ssh datahub-api` and `/tmp/lifecycle/shell`

## Modify sector tree

#### Create new sectors

1) Check that `select count(1) from metadata_sector;` returns 257
2) `./manage.py create_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_create.csv`
3) Check that the query from step 1 now returns 434

#### Rename existing sectors

1) Check that `select segment from metadata_sector where id = 'af959812-6095-e211-a939-e4115bead28a';` returns "Advanced Engineering"
2) `./manage.py update_sector_segment upload.datahub.trade.gov.uk sector_migration/sectors_to_rename_or_adopt.csv`
3) Check that the query from step 1 now returns "Advanced engineering"

#### Change sector levels

1) Check that `select p.segment from metadata_sector c left join metadata_sector p on c.parent_id = p.id where c.id = '9a38cecc-5f95-e211-a939-e4115bead28a';` returns nothing
2) Check that `select p.segment from metadata_sector c left join metadata_sector p on c.parent_id = p.id where c.id = '6f535406-6095-e211-a939-e4115bead28a';` returns "Healthcare services"
3) Check that `select p.segment from metadata_sector c left join metadata_sector p on c.parent_id = p.id where c.id = 'a41a72f1-5f95-e211-a939-e4115bead28a';` returns "Environment"
4) `./manage.py update_sector_parent upload.datahub.trade.gov.uk sector_migration/sectors_to_rename_or_adopt.csv`
5) Check that the query from step 1 now returns "Financial and professional services"
6) Check that the query from step 2 now returns nothing
7) Check that the query from step 3 now returns "Water"

#### Delete investment sectors

1) Check that `select count(1) from investment_investmentsector;` returns 44
2) `./manage.py delete_investment_sector upload.datahub.trade.gov.uk sector_migration/investment_sectors_to_delete.csv`
3) Check the query from step 1 now returns 23


#### Create investment sectors

1) Check that `select count(1) from investment_investmentsector;` returns 23
2) `./manage.py create_investment_sector upload.datahub.trade.gov.uk sector_migration/investment_sectors_to_create.csv`
3) Check the query from step 1 now returns 26

## Map data

#### Companies
1) Check that `select sector_id from company_company where id = '2bfeecf2-bef0-44d8-8b8c-00ac87ae2fe0';` returns "b4959812-6095-e211-a939-e4115bead28a";
2) `./manage.py update_company_sector_disabled_signals upload.datahub.trade.gov.uk sector_migration/sector_migration_company_company.csv`
3) Check that the query from step 1 now returns "9938cecc-5f95-e211-a939-e4115bead28a"

#### Investment projects
1) Check that `select sector_id from investment_investmentproject where id = '3f122351-2ac8-4533-a86d-2c6c554db737';` returns "a922c9d2-5f95-e211-a939-e4115bead28a"
2) `./manage.py update_investment_project_sector_disabled_signals upload.datahub.trade.gov.uk sector_migration/sector_migration_investment_investmentproject.csv`
3) Check that the query from step 1 now returns "b1959812-6095-e211-a939-e4115bead28a"

#### Omis orders
1) Check that `select sector_id from order_order where id = 'b0fdb9dd-1309-e411-8a2b-e4115bead28a';` returns "a922c9d2-5f95-e211-a939-e4115bead28a"
2) `./manage.py update_order_sector upload.datahub.trade.gov.uk sector_migration/sector_migration_order_order.csv`
3) Check that the query from step 1 now returns "b1959812-6095-e211-a939-e4115bead28a"

#### Pipeline items
1) Check that `select sector_id from company_list_pipelineitem where id = 'c1351417-88bd-440d-903d-bb86d7712877';` returns "95e61afa-5f95-e211-a939-e4115bead28a"
2) `./manage.py update_pipeline_item_sector upload.datahub.trade.gov.uk sector_migration/sector_migration_company_list_pipelineitem.csv`
3) Check that the query from step 1 now returns "a51a72f1-5f95-e211-a939-e4115bead28a"

## Cleanup

#### Delete sectors

1) Check that `select count(1) from metadata_sector;` returns 434
2) `./manage.py delete_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_delete_level_4.csv`
3) Check that the query from step 1 now returns 420
4) `./manage.py delete_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_delete_level_3.csv`
5) Check that the query from step 1 now returns 372
6) `./manage.py delete_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_delete_level_2.csv`
7) Check that the query from step 1 now returns 353
8) `./manage.py delete_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_delete_level_1.csv`
9) Check that the query from step 1 now returns 347

#### Recalculate GVA for each investment project

`./manage.py refresh_gross_value_added_values`

#### Sync elastic search

1) `./manage.py sync_es --model company`
2) `./manage.py sync_es --model investment_project`
3) `./manage.py sync_es --model order`
4) Run `cf logs data-hub-api-clone-production` to tail the logs to monitor the progress of the syncing

## Rollback

Every step can be rolled back by running the same command but appending `_reversed` to the csv file name. For example, instead of passing `sectors_to_rename_or_adopt.csv` to the command, pass `sectors_to_rename_or_adopt_reversed.csv`.

To roll back many steps or the entire thing, ensure the steps are rolled back in reverse order to how they were run. 

Rolling back the `delete_sector`, `create_sector`, `delete_investment_sector` and `create_investment_sector` commands works differently, as shown below:

#### Delete sectors

`./manage.py create_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_delete_reversed.csv` 

#### Create new sectors

`./manage.py delete_sector upload.datahub.trade.gov.uk sector_migration/sectors_to_create_reversed.csv` 

#### Delete investment sectors

`./manage.py create_investment_sector upload.datahub.trade.gov.uk sector_migration/investment_sectors_to_delete_reversed.csv`


#### Create investment sectors

`./manage.py delete_investment_sector upload.datahub.trade.gov.uk sector_migration/investment_sectors_to_create_reversed.csv`
