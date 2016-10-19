"""General mixins."""
from rest_framework import status

from core.utils import model_to_dictionary
from es.services import save_model
from korben.connector import Connector
from korben.exceptions import KorbenException


class DeferredSaveModelMixin:
    """Handles add and update models."""

    def __init__(self, *args, **kwargs):
        """Add third part services connectors to the instance."""

        self.korben_connector = Connector(table_name=self._meta.db_table)
        super(DeferredSaveModelMixin, self).__init__(*args, **kwargs)

    def save(self, use_korben=True, *args, **kwargs):
        """Save to Korben first, then alter the model instance with the data received back from Korben.
        Also (temporarily) write to ES.
        We force feed an ID to Django, so we cannot differentiate between update or create without querying the db
        https://docs.djangoproject.com/en/1.10/ref/models/instances/#how-django-knows-to-update-vs-insert

        :param use_korben: bool - Whether or not it should make a call to Korben before saving.
        """

        self.clean()  # triggers custom validation

        # objects is not accessible via instances
        update = type(self).objects.filter(id=self.id).exists()

        if use_korben:
            korben_data = self._convert_model_to_korben_format()
            korben_response = self.korben_connector.post(data=korben_data, update=update)
            self._map_korben_response_to_model_instance(korben_response)

        retval = super().save(*args, **kwargs)
        # update ES
        save_model(self)
        return retval

    def _map_korben_response_to_model_instance(self, korben_response):
        """Override this method to control what needs to be converted back into the model."""
        if korben_response.status_code == status.HTTP_200_OK:
            for key, value in korben_response.json().items():
                setattr(self, key, value)
            else:
                raise KorbenException(korben_response.json())

    def _convert_model_to_korben_format(self):
        """Override this method to have more granular control of what gets sent to Korben."""

        return model_to_dictionary(self, fk_ids=True)

    def update_from_korben(self):
        """Update the model fields from Korben.

        :return the new instance
        """

        korben_response = self.korben_connector.get(object_id=self.id)
        self._map_korben_response_to_model_instance(korben_response)
        self.save(use_korben=False)
        return self
