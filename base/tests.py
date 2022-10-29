import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


# class TestJWTAuthWorks(TestCase):
#     def setUp(self):

#         user = User.objects.create_user("correct_username", password="correct_password")
#         user.is_superuser = True
#         user.is_staff = True
#         user.save()

#         self.get_new_jwt_pair_url = reverse("token_obtain_pair")
#         self.users_list_url = reverse("users_list")

#     def test_jwt_does_not_authenticate_random_user(self):
#         client = APIClient()

#         # make sure we can not authenticate with incorrect data
#         resp = client.post(
#             self.get_new_jwt_pair_url,
#             {"username": "na", "password": "no_pass"},
#         )

#         # unauthorized error
#         self.assertEqual(resp.status_code, 401)

#     def test_jwt_authenticates_properly(self):
#         # for some reason default django client does not work with jwt headers correctly(?)
#         client = APIClient()

#         # we can get access & refresh tokens with correct username & password
#         auth_resp = client.post(
#             self.get_new_jwt_pair_url,
#             json.dumps({"username": "correct_username", "password": "correct_password"}),
#             content_type="application/json",
#         )

#         self.assertEqual(auth_resp.status_code, 200)

#         auth_resp = auth_resp.json()

#         # received access and refresh tokens
#         self.assertIn("access", auth_resp)
#         self.assertIn("refresh", auth_resp)

#         # no access without access token header
#         resp_1 = client.get(self.users_list_url)
#         # forbidden error - meaning not logged in users can not access it
#         self.assertEqual(resp_1.status_code, 403)

#         # make request with access token
#         client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_resp["access"]}')

#         resp_1 = client.get(self.users_list_url)

#         # success
#         self.assertEqual(resp_1.status_code, 200)

#         # todo: add more complete JWT tests including with refresh tokens e.t.c
