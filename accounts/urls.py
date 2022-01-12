from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('activate/<uidb64>/<token>/',views.activate,name="activate"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('',views.dashboard,name="dashboard"),
    path('forgotPassword/',views.forgotPassword,name="forgotPassword"),
    path('resetPassword_Validate/<uidb64>/<token>/',views.resetPassword_Validate,name="resetPassword_Validate"),
    path('resetPassword/',views.resetPassword,name="resetPassword"),
]