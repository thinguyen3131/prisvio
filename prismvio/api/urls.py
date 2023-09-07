from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.api.menu_merchant.views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    HashtagListCreateView,
    HashtagRetrieveUpdateDestroyView,
    ParentIDListView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    PromotionListCreateView,
    PromotionRetrieveUpdateDestroyView,
    ServiceListCreateView,
    ServiceRetrieveUpdateDestroyView,
)
from prismvio.api.merchant.views import MerchantViewSet
from prismvio.api.staff.views import (
    CancelInviteAPIView,
    InviteStaffAPI,
    LinkToStaffAPIView,
    StaffAcceptedInviteAPIView,
    StaffDetailAPIView,
    StaffListCreateAPIView,
    UnlinkStaffAPIView,
    UserListAPIView,
)
from prismvio.api.users.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# ViewSets
router.register("users", UserViewSet)
router.register(r"merchants", MerchantViewSet)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]

# mechant
urlpatterns += [
    path("merchants/<int:pk>/delete/", MerchantViewSet.as_view({"delete": "delete_merchant"}), name="delete_merchant"),
]

# staff
urlpatterns += [
    path("staffs/", StaffListCreateAPIView.as_view(), name="staffs-list-create"),
    path("staffs/invite/", InviteStaffAPI.as_view(), name="staffs-invite"),
    path("staffs/users/", UserListAPIView.as_view(), name="staffs-users"),
    path("staffs/<int:pk>/", StaffDetailAPIView.as_view(), name="staffs-detail"),
    path("staffs/<int:pk>/link/", LinkToStaffAPIView.as_view(), name="link-to-staff"),
    path("staffs/<int:pk>/unlink/", UnlinkStaffAPIView.as_view(), name="merchant-unlink"),
    path("staffs/<int:pk>/cancel/", CancelInviteAPIView.as_view(), name="staff-cancel-invite"),
    path("staffs/<int:pk>/accept/", StaffAcceptedInviteAPIView.as_view(), name="staff-accept-invite"),
]

# menu_merchant
urlpatterns += [
    path("hashtags/", HashtagListCreateView.as_view(), name="hashtag-list-create"),
    path("hashtags/<int:pk>/", HashtagRetrieveUpdateDestroyView.as_view(), name="hashtag-detail"),
    path("promotions/", PromotionListCreateView.as_view(), name="promotion-list-create"),
    path("promotions/<int:pk>/", PromotionRetrieveUpdateDestroyView.as_view(), name="promotion-detail"),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),
    path("services/", ServiceListCreateView.as_view(), name="service-list-create"),
    path("services/<int:pk>/", ServiceRetrieveUpdateDestroyView.as_view(), name="service-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"),
    path("parent_ids/", ParentIDListView.as_view(), name="parent-id-list"),
]
