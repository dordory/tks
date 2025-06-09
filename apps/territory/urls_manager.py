# apps/territory/urls_manager.py
from django.urls import path
from . import manager_views  # 새로 만들 manager 전용 뷰

app_name = "territory_manager"

urlpatterns = [
    path("congregations/", manager_views.congregations_view, name="select_congregation"),
    path("congregation/<int:pk>/territories/", manager_views.manager_territory_list_view, name="territory_list"),
]
