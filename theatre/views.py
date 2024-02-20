from django.db.models import Count, F, ExpressionWrapper, IntegerField
from django.urls import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination

from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly

from theatre.models import (
    Play,
    Actor,
    Performance,
    Genre,
    Reservation,
    TheatreHall
)
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


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.prefetch_related("play")
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActorDetailSerializer
        return ActorSerializer


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.prefetch_related("play")
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return GenreListSerializer
        return GenreSerializer


class PlaysViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Play.objects.prefetch_related("actors", "genres")
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _param_to_int(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")
        queryset = self.queryset

        if genres:
            genre_ids = self._param_to_int(genres)

            queryset = self.queryset.filter(genres__id__in=genre_ids)
        if actors:
            actor_ids = self._param_to_int(actors)
            queryset = self.queryset.filter(actors__id__in=actor_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "genres",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genres id (ex. ?genres=1,2)",
            ),
            OpenApiParameter(
                "actors",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genres id (ex. ?actors=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related("play", "theatre_hall")
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.prefetch_related("tickets").annotate(
                tickets_available=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets"),
                    output_field=IntegerField(),
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


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__performance__play")

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TheatreHallViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
