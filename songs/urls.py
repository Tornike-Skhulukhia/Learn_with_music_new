from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views as v

urlpatterns = [
    path("", v.Home.as_view(), name="songs_home"),
    # path("edit/<int:pk>", v.Home.as_view(), name="songs_home"),
    path("new/", v.AddSong.as_view(), name="add_song"),
    path("delete/<int:pk>", v.DeleteSong.as_view(), name="delete_song"),
    path(
        "song_detail/<int:pk>",
        v.ViewSongDetail.as_view(),
        name="view_song_detail",
    ),
    path("edit_song/<int:pk>", v.UpdateSong.as_view(), name="edit_song"),
    path(
        "listen/<int:pk>",
        csrf_exempt(v.ListenToSong.as_view()),
        name="listen_to_song",
    ),
]
