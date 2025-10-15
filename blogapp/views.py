from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Blog
from .forms import BlogForm

# Home page (show only published blogs)
def home(request):
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    return render(request, 'blogapp/home.html', {'blogs': blogs, 'page_title': 'All Blogs'})



# Create Blog (only logged-in users)
@login_required(login_url='login')
def create_blog(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')
        action = request.POST.get('action')  # 'publish' or 'save_draft'
        
        # Determine status based on button clicked
        status = 'published' if action == 'publish' else 'draft'
        
        blog = Blog.objects.create(
            title=title, 
            content=content, 
            image=image, 
            author=request.user,
            status=status
        )
        
        if status == 'published':
            messages.success(request, "Blog published successfully!")
            return redirect('home')
        else:
            messages.success(request, "Blog saved as draft!")
            return redirect('my_blogs')

    return render(request, 'blogapp/create_blog.html')

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blogapp/blog_detail.html', {'blog': blog})

def blog_list(request):
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    return render(request, 'blogapp/home.html', {'blogs': blogs, 'page_title': 'All Blogs'})

@login_required
def my_blogs(request):
    # Show all user's blogs (both draft and published) in My Blogs
    user_blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blogapp/home.html', {
        'blogs': user_blogs,
        'page_title': 'My Blogs',
        'showing_my_blogs': True,
    })

@login_required
def blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.author:
        return HttpResponseForbidden("You are not allowed to edit this blog.")

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            # Check if user wants to publish or save as draft
            action = request.POST.get('action')
            if action == 'publish':
                blog.status = 'published'
                blog.save()
                messages.success(request, "Blog published successfully!")
                return redirect('home')
            elif action == 'save_draft':
                blog.status = 'draft'
                blog.save()
                messages.success(request, "Blog saved as draft!")
                return redirect('my_blogs')
            else:
                # Just save without changing status
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
        # Redirect back to the page the user was on, if provided
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('blog_list')
    return render(request, 'blogapp/blog_delete.html', {'blog': blog})


@login_required
def publish_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.author:
        return HttpResponseForbidden("You are not allowed to publish this blog.")
    
    if blog.status != 'published':
        blog.status = 'published'
        blog.save()
        messages.success(request, "Blog published successfully!")
    else:
        messages.info(request, "Blog is already published.")
    
    # If coming from My Blogs, go back there; else go to detail/home
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('blog_detail', blog.id)