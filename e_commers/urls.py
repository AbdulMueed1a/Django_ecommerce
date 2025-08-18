from users.views import ObtainTokenWith2fa
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('user/',include('users.urls')),
    path('admin/', admin.site.urls),
]
urlpatterns += [
    path('api/token/', ObtainTokenWith2fa.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]