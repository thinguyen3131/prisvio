import elastic_transport
from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules
from elasticsearch import AuthenticationException
from elasticsearch_dsl.connections import connections
from loguru import logger
from django.utils.module_loading import import_string


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "prismvio.search"
    signal_processor = None

    def ready(self):
        try:
            connections.configure(**settings.ELASTICSEARCH_DSL)
            conn = connections.get_connection()
            logger.info(conn.cluster.health())
        except elastic_transport.ConnectionError:
            logger.error("Elasticsearch Connection Error")
        except AuthenticationException as err:
            logger.error("Elasticsearch Authentication Error")
            if settings.DEBUG:
                raise err

        autodiscover_modules('documents')

        if not self.signal_processor:
            signal_processor_path = getattr(
                settings,
                'ELASTICSEARCH_DSL_SIGNAL_PROCESSOR',
                'prismvio.core.dsl.signals.RealTimeSignalProcessor'
            )
            signal_processor_class = import_string(signal_processor_path)
            self.signal_processor = signal_processor_class(connections)
