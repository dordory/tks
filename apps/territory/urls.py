# apps/territory/urls.py
from django.urls import path, include
from .admin_views import territory_upload_view, visit_history_upload_view
from . import user_views, admin_views


app_name = "territory"

urlpatterns = [
#    path("upload-territory/", admin_views.territory_upload_view, name="upload_territory"),
#    path("upload-visit-history/", admin_views.visit_history_upload_view, name="upload_visit_history"),
#    path("upload-congregation/", admin_views.congregation_upload_view, name="upload_congregation"),

    path("territories/", user_views.territory_list, name="territory_list"),
    path("territories/<int:pk>/", user_views.territory_detail_view, name="territory_detail"),
    path("territories/<int:territory_id>/visit/add/", user_views.visit_history_create_view, name='visit_add'),

    path("congregations/", user_views.congregation_list_view, name="congregation_list"),
    path("congregations/<int:pk>/territories/", user_views.territories_by_congregation_view, name="congregation_territories"),
    path('congregations/<int:congregation_id>/territories/<int:territory_id>/detail/',
          user_views.territory_detail_from_congregation,
          name='territory_detail_from_congregation'),
    path('territories/<int:territory_id>/update_note/', user_views.update_territory_note, name='update_note'),

    path("select-member/", user_views.select_member_view, name="select_member"),
    path("territories/<int:territory_id>/update_info/", user_views.update_territory_info, name="update_territory_info"),

    path('user/groups/', user_views.user_groups_view, name="user_groups"),
    path('user/login/', user_views.user_login_view, name='user_login'),
    path('user/<int:member_id>/territories/', user_views.user_assigned_territories, name="user_assigned_territories"),
    path("user/<int:member_id>/territory/<int:territory_id>/", user_views.user_territory_detail, name="user_territory_detail"),
]
