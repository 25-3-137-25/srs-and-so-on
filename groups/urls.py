from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import groups_dashboard, FacultyViewSet, StudyGroupViewSet

router = DefaultRouter()
router.register("faculties", FacultyViewSet, basename="faculties")
router.register("groups", StudyGroupViewSet, basename="groups")

urlpatterns = [
    path("", groups_dashboard, name="groups_dashboard"),
    path("api/", include(router.urls)),
]