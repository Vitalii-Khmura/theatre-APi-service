from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor, Play, TheatreHall, Performance
from theatre.serializers import ActorSerializer, ActorDetailSerializer, PerformanceListSerializer, \
    PerformanceSerializer, TheatreHallSerializer

THEATRE_HALL_URL = reverse("theatre:theatrehall-list")



def sample_theatre_hall(**params):

    default = {
        "name": "Big Hall",
        "rows": 15,
        "seats_in_row": 20
    }

    return TheatreHall.objects.create(**default)


def theatre_url(theatre_hall_id: int):
    return reverse("theatre:theatrehall-detail", args={theatre_hall_id})


class UnauthorizedTheatreHallApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(THEATRE_HALL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTheatreHallApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            password="testpass"
        )

        self.client.force_authenticate(self.user)

    def test_list_theatre_hall(self):
        sample_theatre_hall()

        res = self.client.get(THEATRE_HALL_URL)
        theatre_hall = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_hall, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_theatre_hall_detail(self):
        theatre_hall = sample_theatre_hall()

        url = theatre_url(theatre_hall.id)
        res = self.client.get(url)

        serializer = TheatreHallSerializer(theatre_hall)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_create_theatre_hall_forbidden(self):
        payload = {
            "name": "Big Hall",
            "rows": 15,
            "seats_in_row": 20
        }

        res = self.client.post(THEATRE_HALL_URL, payload)

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

    def test_create_theatre_hall(self):
        payload = {
            "name": "Big Hall",
            "rows": 15,
            "seats_in_row": 20
        }

        res = self.client.post(THEATRE_HALL_URL, payload)
        theatre_hall = TheatreHall.objects.get(id=res.data["id"])
        serializer = TheatreHallSerializer(theatre_hall)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
