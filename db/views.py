from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from db.generator import gen, z1, z2, z3, test_p


class SessionJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.session.get('jwt_token')
        if not jwt_token:
            raise AuthenticationFailed('Invalid token')

        try:
            refresh = AccessToken(jwt_token)
            user = refresh.get('user')
        except Exception as e:
            raise AuthenticationFailed('Invalid token')

        return user, jwt_token


class LogoutView(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)

        if 'jwt_token' in request.session:
            del request.session['jwt_token']

        return JsonResponse({'message': 'Logged out successfully'})


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('u')
        password = request.POST.get('p')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Генерируем JWT-токен
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Сохраняем токен в сессии или в другом месте
            request.session['jwt_token'] = access_token

            return JsonResponse({'message': 'Logged in successfully'})

        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)


def test(request):
    test_p()
    return HttpResponse()


def generator(request):
    gen()
    print("Generate success")
    return HttpResponse("Generate success")


class Zadanie1(APIView):
    authentication_classes = [SessionJWTAuthentication]

    def get(self, request, search_term, start_date, end_date):
        return HttpResponse(z1(search_term, start_date, end_date), content_type="text/plain; charset=utf-8")


class Zadanie2(APIView):
    # authentication_classes = [SessionJWTAuthentication]

    def get(self, request, semester, year):
        return HttpResponse(z2(semester, year), content_type="text/plain; charset=utf-8")


class Zadanie3(APIView):
    # authentication_classes = [SessionJWTAuthentication]

    def get(self, request, group_name, tag_department):
        return HttpResponse(z3(group_name, tag_department), content_type="text/plain; charset=utf-8")
