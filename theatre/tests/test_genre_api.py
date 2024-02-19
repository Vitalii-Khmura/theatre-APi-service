from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Genre, Play
from theatre.serializers import GenreListSerializer, GenreSerializer

GENRE_URL = reverse("theatre:genre-list")


def sample_genre(**params):
    defaults = {"name": "Test Drama"}

    defaults.update(params)

    return Genre.objects.create(**defaults)


def detail_url(genre_id: int):
    return reverse("theatre:genre-detail", args={genre_id})


class UnauthorizedGenreApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedGenreApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="testpass"
        )

        self.client.force_authenticate(self.user)

    def test_list_genre(self):
        sample_genre()
        sample_genre(name="Action")

        genre = Genre.objects.all()

        res = self.client.get(GENRE_URL)
        serializers = GenreListSerializer(genre, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_retrieve_genre_detail(self):
        genre = sample_genre()

        genre.play.add(Play.objects.create(title="Test Drama"))

        url = detail_url(genre_id=genre.id)
        res = self.client.get(url)
        serializer = GenreListSerializer(genre)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre_forbidden(self):
        payload = {"name": "Test"}

        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="testpass", is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_genre(self):
        payload = {"name": "Drama"}

        res = self.client.post(GENRE_URL, payload)
        genre = Genre.objects.get(id=res.data["id"])
        serializer = GenreSerializer(genre)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)
