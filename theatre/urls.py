from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from theatre.views import PlaysViewSet, ActorViewSet, PerformanceViewSet, GenreViewSet, ReservationViewSet, \
    TheatreHallViewSet

router = routers.DefaultRouter()
router.register("plays", PlaysViewSet)
router.register("actors", ActorViewSet)
router.register("performances", PerformanceViewSet)
router.register("genres", GenreViewSet)
router.register("reservation", ReservationViewSet, basename="reservation")
router.register("theatre_hall", TheatreHallViewSet, basename="theatrehall")


urlpatterns = [
    path("", include(router.urls))
]

app_name = "theatre"
