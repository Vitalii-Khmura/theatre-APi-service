from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor
from theatre.serializers import ActorSerializer, ActorDetailSerializer

ACTOR_URL = reverse("theatre:actor-list")


def sample_actor(**params):
    default = {"first_name": "Test", "last_name": "User"}

    default.update(params)

    return Actor.objects.create(**default)


def actor_url(actor_id: int):
    return reverse("theatre:actor-detail", args={actor_id})


class UnathorizedActorApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ACTOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedActorApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="testpass"
        )

        self.client.force_authenticate(self.user)

    def test_list_actor(self):
        sample_actor()

        res = self.client.get(ACTOR_URL)
        plays = Actor.objects.all()
        serializers = ActorSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_retrieve_actor_detail(self):
        actor = Actor.objects.create(first_name="Test", last_name="User")

        url = actor_url(actor_id=actor.id)
        res = self.client.get(url)

        serializer = ActorDetailSerializer(actor)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_actor_forbidden(self):
        payload = {"first_name": "Test", "last_name": "User"}

        res = self.client.post(ACTOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="testpass", is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_actor(self):
        payload = {"first_name": "Test", "last_name": "User"}

        res = self.client.post(ACTOR_URL, payload)
        actor = Actor.objects.get(id=res.data["id"])
        serializer = ActorSerializer(actor)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], serializer.data[key])
