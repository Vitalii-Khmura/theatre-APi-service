from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor, Play, TheatreHall, Performance, Ticket, Reservation
from theatre.serializers import ActorSerializer, ActorDetailSerializer, PerformanceListSerializer, \
    PerformanceSerializer, PerformanceDetailSerializer

PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_performance(**params):
    play = Play.objects.create(
        title="Test Play"
    )
    theatre_hall = TheatreHall.objects.create(
        name="Big Hall",
        rows=15,
        seats_in_row=20
    )

    default = {
        "play": play,
        "theatre_hall": theatre_hall,
        "show_time": "2024-02-16 20:42:00"
    }

    default.update(params)

    return Performance.objects.create(**default)


def performance_url(performance_id: int):
    return reverse("theatre:performance-detail", args={performance_id})


class UnauthorizedPerformanceApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PERFORMANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedPerformanceApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass"
        )

        self.client.force_authenticate(self.user)

    def test_list_performance(self):
        sample_performance()
        one = Reservation.objects.create(user=self.user)

        Ticket.objects.create(
            row=1,
            seat=5,
            performance_id=1,
            reservation=one
        )

        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_performance_detail(self):
        sample_performance()

        url = performance_url(performance_id=1)
        res = self.client.get(url)
        performance = Performance.objects.get(id=1)
        serializer = PerformanceDetailSerializer(performance, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_performance_forbidden(self):
        payload = {
            "play": Play.objects.create(
                title="test play"
            ),
            "theatre_hall": TheatreHall.objects.create(
                name="Big hall",
                rows=10,
                seats_in_row=20
            )
        }

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_performance(self):
        play = Play.objects.create(
                title="test play"
            )
        theatre_hall =TheatreHall.objects.create(
            name="Big hall",
            rows=10,
            seats_in_row=20
        )
        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id
        }

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)



