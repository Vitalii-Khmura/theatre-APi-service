from django.db import transaction
from rest_framework import serializers
from theatre.models import (
    Play,
    Actor,
    TheatreHall,
    Performance, Genre, Reservation, Ticket
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class ActorDetailSerializer(ActorSerializer):
    play = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Actor
        fields = (
            "id",
            "first_name",
            "last_name",
            "play"
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class GenreListSerializer(GenreSerializer):
    play = serializers.StringRelatedField(read_only=True, many=True)


class PlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Play
        fields = "__all__"


class PlayListSerializer(PlaySerializer):
    genres = serializers.StringRelatedField(many=True)
    actors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "genres",
            "actors",
            "description"
        )


class PlayDetailSerializer(PlaySerializer):
    actors = ActorSerializer(many=True)
    genres = GenreSerializer(many=True)


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = "__all__"


class PerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Performance
        fields = "__all__"


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.StringRelatedField(many=False)
    theatre_hall = serializers.StringRelatedField(many=False)
    tickets_available = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Performance
        fields = (
            "id",
            "play",
            "theatre_hall",
            "tickets_available",
            "show_time"
        )


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(many=False)
    theatre_hall = TheatreHallSerializer(many=False)


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "performance"
        )

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            row=attrs["row"],
            seat=attrs["seat"],
            theatre_hall=attrs["performance"].theatre_hall

        )
        return data


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "tickets",
            "created_at"
        )

    @transaction.atomic
    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop('tickets')
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=False, allow_null=False)
