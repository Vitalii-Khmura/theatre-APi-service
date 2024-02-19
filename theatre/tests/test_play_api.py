from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlaySerializer, PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theatre:play-list")


def detail_url(play_id: int):
    return reverse("theatre:play-detail", args={play_id})


def sample_play(**params):
    defaults = {
        "title": "Test Play",

    }

    defaults.update(params)

    return Play.objects.create(**defaults)


class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )

        self.client.force_authenticate(self.user)

    def test_list_play(self):
        play_with_genre = sample_play()
        play_with_actors = sample_play()

        genre1 = Genre.objects.create(name="Action")
        genre2 = Genre.objects.create(name="Drama")

        actor1 = Actor.objects.create(
            first_name="Brad",
            last_name="Pitt"
        )

        actor2 = Actor.objects.create(
            first_name="Leonardo",
            last_name="Dicaprio"
        )

        play_with_genre.genres.add(genre1, genre2)
        play_with_actors.actors.add(actor1, actor2)

        res = self.client.get(PLAY_URL)

        plays = Play.objects.all()

        serializers = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_filter_play_by_genre(self):
        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        genre1 = Genre.objects.create(name="Action")
        genre2 = Genre.objects.create(name="Drama")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        play3 = sample_play(title="Play without genre")

        res = self.client.get(PLAY_URL, {
            "genres": f"{genre1.id}, {genre2.id}"
        })

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_play_by_actor(self):
        play1 = sample_play(title="Play 1")
        play2 = sample_play(title="Play 2")

        actor1 = Actor.objects.create(
            first_name="Brad",
            last_name="Pitt"
        )

        actor2 = Actor.objects.create(
            first_name="Leonardo",
            last_name="Dicaprio"
        )

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        play3 = sample_play(title="Play without actor")

        res = self.client.get(PLAY_URL, {
            "actors": f"{actor1.id}, {actor2.id}"
        })

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.actors.add(Actor.objects.create(
            first_name="Brad",
            last_name="Pitt"
        ))
        play.genres.add(Genre.objects.create(name="Drama"))

        url = detail_url(play_id=play.id)
        res = self.client.get(url)

        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "info": "Play"
        }

        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpass",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_play(self):
        genre1 = Genre.objects.create(name="Drama")
        genre2 = Genre.objects.create(name="Action")
        actors = Actor.objects.create(
            first_name="Brad",
            last_name="Pitt"
        )

        payload = {
            "title": "Play",
            "genres": [genre1.id, genre2.id],
            "actors": [actors.id]
        }

        res = self.client.post(PLAY_URL, payload)

        play = Play.objects.get(id=res.data["id"])
        play_actor = play.actors.all()
        play_genre = play.genres.all()

        serializer = PlaySerializer(play)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(actors, play_actor)
        self.assertIn(genre1, play_genre)
        self.assertIn(genre2, play_genre)
        for key in payload:
            self.assertEqual(payload[key], (serializer.data[key]))

