# from dependency_injector import containers, providers

# from core.services.aws.ses import AWSSESService


# class Services(containers.DeclarativeContainer):
#     config = providers.Configuration()
#     core = providers.DependenciesContainer()
#     gateways = providers.DependenciesContainer()

#     aws_ses_service = providers.Resource(
#         AWSSESService,
#         ses_client=gateways.ses_client,
#         ses_configuration_set=config.SES_CONFIGURATION_SET,
#         ses_sender=config.SES_SENDER,
#     )
