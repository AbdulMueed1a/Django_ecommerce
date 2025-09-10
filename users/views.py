import logging
import string
import random

from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model,authenticate
from django.core.mail import send_mail
from django.core import signing
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer,SellerSerializer
from .models import EmailToken

User=get_user_model()
logger=logging.getLogger(__name__)
# def generate_otp(length=6):
#     characters = string.ascii_letters + string.digits
#     otp = ''.join(random.choice(characters) for _ in range(length))
#     return otp
class RegistrationView(APIView):
    @staticmethod
    def send_verification_mail(user,token):
        url=f'{settings.FRONTEND_URL}/user/verify_email/{str(token.token)}'
        try:
            send_mail(
                subject="Your Email Verification link",
                message=f"""
                       here is your emil verification link : 
                       {url}
                  """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email]
                )
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")

    def post(self,request):
        if get_user_model().is_authenticated:
            return Response({
                'message': 'Already signed in'
            },status=status.HTTP_403_FORBIDDEN)
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
                user.refresh_from_db()

                verification_token=EmailToken.objects.create(user=user)

                self.send_verification_mail(user,verification_token)

            return Response({
                'success':True,
                'message':'Account created verification still expected',
                'errors': serializer.errors
            },status.HTTP_201_CREATED)

        except Exception as e:
            print(f'exception occurred while signup: {e}')
            return Response({
                'success':False,
                'message':'internal server or someshit causing issues',
                'errors': serializer.errors
            },status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def email_verification(request,token):
    if request.method=='GET':
        # token=request.data.get('token')
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

@api_view(['GET','POST'])
@permission_classes([AllowAny])
def resend_verification_mail(request):
    if request.method=='POST':
        email=request.data.get('email')
        if not email:
            return Response({
                "success":False,
                'message':'provide email : REQUIRED!!'
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            user=User.objects.get(email=email)

            if user.is_verified:
                return Response({
                    'success':False,
                    'msg':"Email is already verified",
                },status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                EmailToken.objects.filter(user=user,used=False).update(used=True)
                token=EmailToken.objects.create(user=user)
                RegistrationView.send_verification_mail(token=token,user=user)

            return Response({
                'success':True,
                'message':'If the email exists, a verification link has been sent.',
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
        return Response(f'this request method {request.method} is not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)

class PasswordReset(APIView):
    @staticmethod
    def send_password_reset_mail(user, token):
        url = f'{settings.FRONTEND_URL}/user/password_reset/confirm/{str(token)}'
        try:
            send_mail(
                subject="Your password reset link",
                message=f"""
                           here is your password reset link : 
                           {url}
                      """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email]
            )
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")
    @permission_classes([AllowAny])
    def post(self,request):
        try:
            email = request.data.get('email')
            token = request.data.get('token') or None
            if not email:
                return Response({
                    "success": False,
                    'message': 'provide email : REQUIRED!!'
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': True,
                'message': 'If user exists the password was set'
            }, status=status.HTTP_200_OK)
        if not token:
            try:
                reset_token=default_token_generator.make_token(user=user)
                self.send_password_reset_mail(user=user,token=reset_token)
                return Response(
                    {'success': True,
                     'message': 'Password reset mail sent'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                print(f'error  : {e}')
                return Response(
                    {'success':False,
                     'message':'Password reset mail failed : Internal server error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            password=request.data.get('password')
            password_conform=request.data.get('password_confirm')
            if not password or not password_conform:
                return Response(
                    {'success': False,
                     'message': 'No Password Provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if password != password_conform:
                return Response(
                    {'success': False,
                     'message': "Provided passwords don't match"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token_bool=default_token_generator.check_token(user=user,token=token)
            if not token_bool:
                return Response({
                    "success": False,
                    'message': 'The provided password reset token is either wrong or expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response({
                'success': True,
                'message': 'If user exists the password was set'
            }, status=status.HTTP_200_OK)


class ObtainTokenWith2fa(TokenObtainPairView):
    @staticmethod
    def generate_otp(email,length=6):
        characters = string.ascii_letters + string.digits
        otp = ''.join(random.choice(characters) for _ in range(length))
        cache.set(f'otp_{email}',otp,timeout=300)
        return otp
    @staticmethod
    def verify_otp(email,otp):
        code=cache.get(f'otp_{email}',default=None)
        return str(code)==str(otp)
    @staticmethod
    def send_otp_mail(email,code):
        try:
            send_mail(
                subject="Your Email Verification link",
                message=f"""
                       here is your 2fa code : 
                       {code}
                  """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email]
                )
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")
    def post(self, request: Request, *args, **kwargs) -> Response:
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(email=email,password=password)
        if getattr(user,'is_2fa_enabled',False):
            token2fa=signing.dumps({'email':email,'purpose':'2fa'},)
            otp=self.generate_otp(email=email)
            self.send_otp_mail(email=email,code=otp)
            logger.debug('2fa enabled and mail sent')
            return Response({
                'details':'Two factor verification required',
                'token2fa': token2fa,
            },status=status.HTTP_401_UNAUTHORIZED)
        logger.debug('2fa not enabled proceeding with normal login')
        serializer=self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_2fa(request):
    if request.method=='POST':
        try:
            token2fa=request.data.get('token2fa')
            otp = request.data.get('otp')
            data=signing.loads(token2fa,max_age=500)
            if data.get('purpose') != '2fa':
                return Response({
                    'success': False,
                    'message': 'The provided token cant be used in this context'
                }, status.HTTP_400_BAD_REQUEST)
            email=data.get('email')
            user=User.objects.get(email=email)
            # totp=pyotp.TOTP(user.otp_secret)
            ok=ObtainTokenWith2fa.verify_otp(email, otp)
            # ok=totp.verify(otp=otp,valid_window=1)
            print(ok)

            if ok:
                refresh = RefreshToken.for_user(user=user)
                return Response({
                    'access':str(refresh.access_token),
                    'refresh':str(refresh)
                },status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid or expired OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
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
        except Exception as e:
            print(f"2fa verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to verify 2fa.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"msg":f"request method {request.method} is not allowed"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

@permission_classes([IsAuthenticated])
def setup_authenticator_app(request):
    user=request.user
    if user.is_2fa_enabled:
        return Response({
            "success": False,
            'message': '2fa Already setup'
        }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seller_registration(request):
    if request.method=='POST':
        serializer=SellerSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                'message': 'Store created',
                'errors':serializer.errors
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            'message': 'Store not created created',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "success": False,
            'message': '2fa Already setup'
        },status=status.HTTP_405_METHOD_NOT_ALLOWED)


# @login_not_required
# def signin(request):
#     if request.user.is_authenticated:
#         return redirect('/logout')
#     if request.method == 'post':
#         email=request.body