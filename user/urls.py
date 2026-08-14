from django.urls import path,include
from user import views


urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register_view, name="register"),
    path('login',views.login_view,name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('profile',views.profile_view,name="profile"),
    path('profile-setting',views.profile_setting,name="profile-setting"),
]
