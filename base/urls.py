"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    # DRF browsable api
    path("api-auth/", include("rest_framework.urls")),
    # JWT tokens
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    # ours
    # path("songs/", include("songs.urls")),
    path("", include("songs.urls")),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ################################################################################
# """
#     delete this part if not needed, it is used for demonstration
#     purposes only to display some information in DRF browsable api -
#     specifically - listing all users that are currently in a database,
#     and only staff users can access it.
# """
# # flake8: noqa
# from django.contrib.auth.models import User
# from rest_framework import generics, permissions

# ################################################################################
# from rest_framework.serializers import ModelSerializer


# class UserSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["username", "id", "is_staff", "is_superuser"]


# class UsersList(generics.ListAPIView):
#     queryset = User.objects.all()

#     serializer_class = UserSerializer
#     permission_classes = [
#         permissions.IsAdminUser,
#     ]


# urlpatterns += [
#     path("", UsersList.as_view(), name="users_list"),
# ]
