import base64
import datetime

from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from users.models import User, Profile, ResidentialAddress
from users.serializers import (
    SignUpSerializer,
    UserSerializer,
    ProfileSerializer,
    ResidentialAddressSerializer,
)
from users.utils import account_activation_token


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    """
    Sample request
    {
        "email":"daniel2@gmail.com",
        "password":"mylena"
    }
    """
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response(
            {"error": "Please provide both email and password"},
            status=HTTP_400_BAD_REQUEST,
        )
    user = authenticate(email=email, password=password)
    if not user:
        return Response(
            {"error": "Invalid Credentials or Inactive"},
            status=HTTP_404_NOT_FOUND,
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    """
    Sample request
    {
      "email": "danielkakai@gmail.com",
      "first_name": "dan akai",
      "password": "hhhh"
    }
    """
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        if User.objects.filter(
            email=serializer.validated_data["email"]
        ).exists():
            return Response(
                {"error": "User already exists"}, status=HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        serializer = UserSerializer(user)
        current_site = get_current_site(request)
        activation_link = f"http://{current_site.domain}/activate/{urlsafe_base64_encode(force_bytes(user.id))}/{account_activation_token.make_token(user)}"
        send_mail(
            "New user",
            f"Activation link: \n{activation_link}",
            "Test <no-reply@test.com>",
            [user.email],
            fail_silently=False,
        )
        return Response(
            {
                "user": serializer.data,
                "message": "Activation link sent to your email",
            },
            status=HTTP_201_CREATED,
        )
    return Response({"error": serializer.errors}, status=HTTP_400_BAD_REQUEST)


def activate_user(request, uid, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account."
        )
    else:
        return HttpResponse("Activation link is invalid!")


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def forgot_password(request):
    """
    sample request
    {"email":"user@gmail.com"}
    """
    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email required"}, status=HTTP_400_BAD_REQUEST
        )
    code = str(datetime.datetime.now())[-4:] + email
    new_pass = (
        base64.b64encode(code.encode(), altchars=None).decode().lower()[:8]
    )
    user = get_object_or_404(User, email=email)
    user.set_password(new_pass)
    user.save()
    send_mail(
        "New password",
        "New password: \n{}".format(new_pass),
        "Test <no-reply@test.com>",
        [email],
        fail_silently=False,
    )
    return Response(
        {"message": "New password sent to your email"}, status=HTTP_200_OK
    )


@csrf_exempt
@api_view(["POST"])
@login_required
def change_password(request):
    user = request.user
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")
    if password1 == password2:
        if len(password1) >= 6:
            user.set_password(password1)
            user.save()
            logout(request)
            Token.objects.get(user=user).delete()
            return Response(
                {"message": "Password changed"}, status=HTTP_200_OK
            )
        return Response(
            {"error": "Minimun password length is 6"},
            status=HTTP_400_BAD_REQUEST,
        )
    return Response(
        {"error": "Passwords don't match"}, status=HTTP_400_BAD_REQUEST
    )


class UserView(LoginRequiredMixin, APIView):
    """
    API endpoint that allows users to be viewed.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user_id=user.id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data
        data["user_id"] = user.id
        serializer = ProfileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            _saved_instance = serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data
        data["user_id"] = user.id
        profile = get_object_or_404(Profile, user_id=user.id)
        serializer = ProfileSerializer(
            data=data, instance=profile, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            _saved_instance = serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        user = request.user
        profile = Profile.objects.filter(user__id=user.id).first()
        profile.delete()
        return Response({"message": "Profile ID deleted"}, status=HTTP_200_OK)


class ResidentialAddressView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        address = get_object_or_404(ResidentialAddress, user_id=user.id)
        serializer = ResidentialAddressSerializer(address)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data
        data["user_id"] = user.id
        serializer = ResidentialAddressSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            _saved_instance = serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data
        data["user_id"] = user.id
        address = get_object_or_404(ResidentialAddress, user_id=user.id)
        serializer = ResidentialAddressSerializer(
            data=request.data, instance=address, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            _saved_instance = serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        user = request.user
        address = ResidentialAddress.objects.filter(user__id=user.id).first()
        address.delete()
        return Response(
            {"message": "ResidentialAddress ID deleted"}, status=HTTP_200_OK
        )
