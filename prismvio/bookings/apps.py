from django.apps import AppConfig


class BookingsConfig(AppConfig):
    name = "bookings"

    def ready(self):
        import prismvio.bookings.signals  # noqa: F401
