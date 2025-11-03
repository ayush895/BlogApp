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
    path('blog/<int:blog_id>/publish/', views.publish_blog, name='publish_blog'),
    path('blog/<int:blog_id>/like/', views.toggle_like, name='toggle_like'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('my/', views.my_blogs, name='my_blogs'),

]

# create one more directory named authenticate in which login,logout and signup files will be there