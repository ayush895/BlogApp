from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('signup/', views.signup_view, name='signup'),
    # path('login/', views.login_view, name='login'), 
    # path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_blog, name='create_blog'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:blog_id>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<int:blog_id>/delete/', views.blog_delete, name='blog_delete'),
    path('', views.blog_list, name='blog_list'),  # New URL pattern for blog list

]

# create one more directory named authenticate in which login,logout and signup files will be there