from django.db.models import Count, F, ExpressionWrapper, IntegerField
from django.urls import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination


from theatre.models import (
    Play,
    Actor,
    Performance,
    Genre,
    Reservation,
    TheatreHall)
from theatre.serializers import (
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    ActorSerializer,
    PerformanceSerializer,
    GenreSerializer,
    GenreListSerializer,
    ActorDetailSerializer,
    ReservationSerializer,
    TheatreHallSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationListSerializer,
)


class ActorViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Actor.objects.prefetch_related("play")
    serializer_class = ActorSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActorDetailSerializer
        return ActorSerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.prefetch_related("play")
    serializer_class = GenreSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return GenreListSerializer
        return GenreSerializer


class PlaysViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Play.objects.prefetch_related("actors", "genres")
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class PerformanceViewSet(
    viewsets.ModelViewSet
):
    queryset = Performance.objects.select_related(
        "play",
        "theatre_hall"
    )
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets"
            ).annotate(
                tickets_available=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row") - Count("tickets"),
                    output_field=IntegerField()
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class ReservationViewSet(
    viewsets.ModelViewSet
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play"
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
