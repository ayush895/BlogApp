from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Blog
from .forms import BlogForm

# Home page (show blogs)
def home(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogapp/home.html', {'blogs': blogs})

# Signup
def signup_view(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         confirm_password = request.POST['confirm_password']

#         if password != confirm_password:
#             messages.error(request, "Passwords do not match")
#             return redirect('signup')

#         if User.objects.filter(username=username).exists():
#             # messages.error(request, "Username already exists")    
#             return redirect('signup')

#         user = User.objects.create_user(username=username, password=password)
#         login(request, user)
#         messages.success(request, "Signup successful! You are now logged in.")
#         return redirect('home')

#     return render(request, 'blogapp/signup.html')

# # Login
# def login_view(request):
#     error_message= None
#     if request.method == "POST":
#         email = request.POST.get['email']
#         password = request.POST.get['password']
#         user = authenticate(request, username=username, password=password)
#         try:
#             user_obj = User.objects.get(email=email)
#             user = authenticate(request, username=user_obj.username, password=password)    
#             if user is not None:
#                 login(request, user)
#             # messages.success(request, f"Welcome {username}!")
#                 return redirect('home')
#             else:
#             # messages.error(request, "Invalid username or password")
#                 error_message = "Invalid username or password"
#             # return redirect('login')
#         except User.DoesNotExist:
#             error_message = "No user found with this email"

#     return render(request, 'blogapp/login.html', {'error_message': error_message})

# # Logout
# def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# Create Blog (only logged-in users)
@login_required(login_url='login')
def create_blog(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')
        Blog.objects.create(title=title, content=content,image=image, author=request.user)
        messages.success(request, "Blog posted successfully!")
        return redirect('home')

    return render(request, 'blogapp/create_blog.html')

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blogapp/blog_detail.html', {'blog': blog})

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogapp/home.html', {'blogs': blogs})

@login_required
def blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.author:
        return HttpResponseForbidden("You are not allowed to edit this blog.")

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', blog.id)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blogapp/blog_edit.html', {'form': form, 'blog': blog})


@login_required
def blog_delete(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.author:
        return HttpResponseForbidden("You are not allowed to delete this blog.")

    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blogapp/blog_delete.html', {'blog': blog})