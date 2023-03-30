
import pulumi
import pulumi_azure_native as azure_native
import pulumi_azure_native.authorization as authorization
import pulumi_azure_native.resources as resource
import pulumi_azuread as azuread

prefix = "test001"
current = azuread.get_client_config()

resource_group = resource.ResourceGroup(
    resource_name=f"{prefix}-rg",
    resource_group_name=f"{prefix}-rg",
)

# Power BI Admin Service Principal
power_bi_aad_app = azuread.Application(
    resource_name=f"{prefix}-app",
    display_name=f"{prefix}-app",
    owners=[current.object_id],
)

power_bi_service_principal = azuread.ServicePrincipal(
    resource_name=f"{prefix}-sp",
    args=azuread.ServicePrincipalArgs(
        application_id=power_bi_aad_app.application_id,
        owners=[current.object_id],
    )
)

power_bi_app_password = azuread.ApplicationPassword(
    resource_name=f"{prefix}-pwd",
    args=azuread.ApplicationPasswordArgs(
        application_object_id=power_bi_aad_app.id,
    )
)

capacity = azure_native.powerbidedicated.CapacityDetails(
    resource_name=f"{prefix}embedcapacity".lower(),
    administration=azure_native.powerbidedicated.DedicatedCapacityAdministratorsArgs(
        members=[
            power_bi_service_principal.id
            # power_bi_service_principal.object_id:
            # current.object_id  # even the current user is not working.
            # Only a valid mail works in the first attempt: "validMail"
        ],
    ),
    location=resource_group.location,
    resource_group_name=resource_group.name,
    sku=azure_native.powerbidedicated.CapacitySkuArgs(
        name="A1",
        tier=azure_native.powerbidedicated.CapacitySkuTier.PBI_E_AZURE,
    ),
    # opts=pulumi.ResourceOptions(depends_on=[power_bi_service_principal]) # Does not help.
)

# Explicit apply does not fix the issue.
# power_bi_service_principal.id.apply(
#     lambda id:
#     azure_native.powerbidedicated.CapacityDetails(
#         resource_name=f"{prefix}embedcapacity".lower(
#         ),
#         administration=azure_native.powerbidedicated.DedicatedCapacityAdministratorsArgs(
#             members=[id],
#         ),
#         location=resource_group.location,
#         resource_group_name=resource_group.name,
#         sku=azure_native.powerbidedicated.CapacitySkuArgs(
#             name="A1",
#             tier=azure_native.powerbidedicated.CapacitySkuTier.PBI_E_AZURE,
#         ),
#     )
# )

# this role assignment is not enough. The use is not enough.
# authorization.RoleAssignment(
#     resource_name=f"{prefix}-admin-cap-ra",
#     args=authorization.RoleAssignmentArgs(
#         principal_id=power_bi_service_principal.id,
#         principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,

#         role_definition_id=f"/subscriptions/{authorization.get_client_config().subscription_id}/providers/Microsoft.Authorization/roleDefinitions/18d7d88d-d35e-4fb5-a5c3-7773c20a72d9",
#         # scope=capacity.id,
#         scope=pulumi.Output.all(resource_group.name,
#                                 capacity.name).apply(lambda args:
#                                                      f"/subscriptions/{authorization.get_client_config().subscription_id}/resourceGroups/{args[0]}/providers/Microsoft.PowerBIDedicated/capacities/{args[1]}")
#     ),
# )
