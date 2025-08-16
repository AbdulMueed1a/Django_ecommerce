import string
import random
import pyotp

from django.contrib.auth.decorators import login_not_required
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model,authenticate
from django.core.mail import send_mail
from django.core import signing
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .models import EmailToken

User=get_user_model()

# def generate_otp(length=6):
#     characters = string.ascii_letters + string.digits
#     otp = ''.join(random.choice(characters) for _ in range(length))
#     return otp
class RegistrationView(APIView):
    @staticmethod
    def send_verification_mail(user,token):
        url=f'{settings.FRONTEND_URL}/verify_email/{token}'
        try:
            send_mail(
                subject="Your Email Verification link",
                message=f"""
                       here is your emil verification link : 
                       {url}
                  """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user]
                )
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")

    def post(self,request):
        if request.user.is_authenticated:
            return redirect('/logout')
        # secretkey=pyotp.random_base32()
        # otp=pyotp.TOTP(
        #     s=secretkey,
        #     digits=6,
        #     interval=60,
        #     name='signup otp',
        #     issuer='django ecommerce'
        # )

        serializer=UserSerializer(data=request.data)

        if not serializer.is_valid():
         return Response({
            'success': False,
            'message': 'Registration failed due to validation errors.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user=serializer.save()

                verification_token=EmailToken.objects.create(user=user)

            self.send_verification_mail(user,verification_token)

            return Response({
                'success':True,
                'message':'Account created verification still expected',
                'errors': serializer.errors
            },status.HTTP_201_CREATED)

        except Exception as e:
            print(f'exeption occured while signup: {e}')
            return Response({
                'success':False,
                'message':'internal server or someshit causing issues',
                'errors': serializer.errors
            },status.HTTP_500_INTERNAL_SERVER_ERROR)

def email_verification(request):
    if request.method=='post':
        token=request.data.get('token')
        if not token:
            return Response({
                'success':False,
                'message':'Verification TOKEN missing',
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            validation_token=get_object_or_404(EmailToken,token=token,used=False)

            if validation_token.is_expired:
                return Response({
                    'success':False,
                    'message':'The provided token is expired'
                },status=status.HTTP_400_BAD_REQUEST)
            if validation_token.used:
                return Response({
                'success': False,
                'message':'This token is already Used'
            },status=status.HTTP_403_FORBIDDEN)
            with transaction.atomic():
                user=validation_token.user
                user.is_verified=True
                user.save()

                validation_token.used=True
                validation_token.save()
                return Response({
                    'success': True,
                    'message': 'User account successfully verified'
                }, status=status.HTTP_200_OK)
        except EmailToken.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid verification token.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Email verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Verification failed due to server error.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(f'this request method {request.method} is not allowed',status=status.HTTP_403_FORBIDDEN)

def resend_verification_mail(request):
    if request.method=='post':
        email=request.data.get('email')
        if not email:
            return Response({
                "success":False,
                'message':'provide email : REQUIRED!!'
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            user=get_object_or_404(User,email=email)

            if user.is_verified:
                return Response({
                    'success':False,
                    'msg':"Email is already verified",
                },status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                EmailToken.objects.filter(user=user,used=False).update(used=True)
                token=EmailToken.objects.create(user=user)

            RegistrationView.send_verification_mail(token=token.token,user=user)

            return Response({
                'success':True,
                'msg':'email verified successfully',
            },status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': True,
                'message': 'If the email exists, a verification link has been sent.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Resend verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to send verification email.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(f'this request method {request.method} is not allowed', status=status.HTTP_403_FORBIDDEN)

class ObtainTokenWith2fa(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        username=request.data.get('username')
        password=request.data.get('password')

        user=authenticate(request,username,password)
        if getattr(user,'is_2fa_enabled',False):
            token2fa=signing.dumps({'username':username,'purpose':'2fa'},)
            return Response({
                'details':'Two factor verification required',
                'token2fa': token2fa,
            },status=status.HTTP_401_UNAUTHORIZED)

        serializer=self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

def verify_2fa(request):
    if request.method=='post':
        try:
            token2fa=request.data.get('token2fa')
            data=signing.loads(token2fa,max_age=500)
            if data.get('purpose') != '2fa':
                return Response({
                    'success': False,
                    'message': 'The provided token was created for some other purpose'
                }, status.HTTP_400_BAD_REQUEST)
            username=data.get('username')
            user=User.objects.get(username=username)
            totp=pyotp.TOTP(request.user.otp_secret)
            ok=totp.verify(otp=request.data.get('otp'))

            if ok:
                refresh = RefreshToken.for_user(user=user)
                return Response({
                    'access':str(refresh.access_token),
                    'refresh':str(refresh)
                },status=status.HTTP_200_OK)
        except signing.SignatureExpired:
            return Response(
                {
                    'msg':'The provided 2fa token is tempered with or incorrect'
                },status=status.HTTP_400_BAD_REQUEST
            )
        except signing.BadSignature:
            return Response(
                {
                    'msg': 'The provided 2fa token is expired signin again'
                }, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response({"msg":f"request method {request.method} is not allowed"})

# @login_not_required
# def signin(request):
#     if request.user.is_authenticated:
#         return redirect('/logout')
#     if request.method == 'post':
#         email=request.body