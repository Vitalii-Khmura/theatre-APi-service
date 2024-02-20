import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor, Play, TheatreHall, Performance, Ticket, Reservation
from theatre.serializers import (
    ActorSerializer,
    ActorDetailSerializer,
    PerformanceListSerializer,
    PerformanceSerializer,
    TheatreHallSerializer,
    ReservationSerializer,
)

RESERVATION_URL = reverse("theatre:reservation-list")


def theatre_url(reservation_id: int):
    return reverse("theatre:reservation-detail", args={reservation_id})


def sample_performance(**params):
    play = Play.objects.create(title="Test Play")
    theatre_hall = TheatreHall.objects.create(name="Big Hall", rows=10, seats_in_row=25)
    defaults = {"play": play, "theatre_hall": theatre_hall}

    defaults.update(params)

    return Performance.objects.create(**defaults)


class UnauthorizedTheatreHallApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminActorApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="testpass", is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        performance = sample_performance()

        payload = {"tickets": [{"row": 5, "seat": 10, "performance": performance.id}]}

        json_payload = json.dumps(payload)
        res = self.client.post(
            RESERVATION_URL, data=json_payload, content_type="application/json"
        )
        reservation = Reservation.objects.get(id=res.data["id"])
        serializer = ReservationSerializer(reservation)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], serializer.data[key])

    def test_validation_reservation(self):
        performance = sample_performance()

        payload = {"tickets": [{"row": 5, "seat": 165, "performance": performance.id}]}

        json_payload = json.dumps(payload)
        res = self.client.post(
            RESERVATION_URL, data=json_payload, content_type="application/json"
        )
        print(res.data)
        print(res.data["tickets"][0]["seat"])

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
