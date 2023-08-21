from django.conf import settings

# from dependency_injector import containers, providers

# from core.containers.gateways import Gateways
# from core.containers.services import Services


# class Container(containers.DeclarativeContainer):
#     config = providers.Configuration()

#     gateways = providers.Container(
#         Gateways,
#         config=config,
#     )

#     services = providers.Container(
#         Services,
#         config=config,
#         gateways=gateways,
#     )


# container = None


# def get_container() -> Container:
#     global container
#     if container is None:
#         container = Container()
#         container.config.from_dict(settings.__dict__['_wrapped'].__dict__)

#     return container
