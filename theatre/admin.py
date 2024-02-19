from django.contrib import admin

from theatre.models import (
    Play,
    Actor,
    Genre,
    Performance,
    TheatreHall,
    Ticket,
    Reservation,
)

# Register your models here.
admin.site.register(Play)
admin.site.register(Performance)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(TheatreHall)
admin.site.register(Reservation)
admin.site.register(Ticket)
