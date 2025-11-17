from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from .models import Blog, Like, Comment
from .forms import BlogForm
from utils.common import get_default_blog_image, validate_image_file, send_email_notification, get_user_display_name

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
        
        # Validate image if provided
        if image and not validate_image_file(image):
            messages.error(request, "Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP) under 5MB.")
            return render(request, 'blogapp/create_blog.html')
        
        # Determine status based on button clicked
        status = 'published' if action == 'publish' else 'draft'
        
        # Create blog - the model will handle default image assignment
        blog = Blog.objects.create(
            title=title, 
            content=content, 
            image=image,  # Will be None if no image provided, model will set default
            author=request.user,
            status=status
        )
        
        # Send notification email for published blogs
        if status == 'published':
            user_name = get_user_display_name(request.user)
            email_subject = "Blog Published Successfully!"
            email_message = f"Hi {user_name},\n\nYour blog '{title}' has been published successfully!\n\nYou can view it on the home page.\n\nHappy Blogging!"
            
            send_email_notification(
                subject=email_subject,
                message=email_message,
                recipient_email=request.user.email
            )
            
            messages.success(request, "Blog published successfully!")
            return redirect('home')
        else:
            messages.success(request, "Blog saved as draft!")
            return redirect('my_blogs')

    return render(request, 'blogapp/create_blog.html')

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(blog=blog, user=request.user).exists()
    comments = Comment.objects.filter(blog=blog).order_by('-created_at')
    like_count = blog.likes.count()
    return render(request, 'blogapp/blog_detail.html', {
        'blog': blog,
        'is_liked': is_liked,
        'like_count': like_count,
        'comments': comments,
    })

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
def toggle_like(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    like, created = Like.objects.get_or_create(blog=blog, user=request.user)
    if not created:
        like.delete()
        messages.info(request, "You unliked this blog.")
        liked = False
    else:
        messages.success(request, "You liked this blog.")
        liked = True
    # If AJAX request, return JSON so frontend can update without reload
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'like_count': blog.likes.count()})
    return redirect('blog_detail', blog.id)

@login_required
def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if not content:
            messages.error(request, "Comment cannot be empty.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)
            return redirect('blog_detail', blog.id)
        comment = Comment.objects.create(blog=blog, user=request.user, content=content)
        messages.success(request, "Comment added.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # return minimal data to render on client
            return JsonResponse({
                'id': comment.id,
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d %b %Y %H:%M'),
            })
    return redirect('blog_detail', blog.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.user and request.user != comment.blog.author:
        return HttpResponseForbidden("You cannot delete this comment.")
    blog_id = comment.blog.id
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'deleted': True, 'comment_id': comment_id})
    return redirect('blog_detail', blog_id)

@login_required
def blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.author:
        return HttpResponseForbidden("You are not allowed to edit this blog.")

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        
        # Validate image if provided
        new_image = request.FILES.get('image')
        if new_image and not validate_image_file(new_image):
            messages.error(request, "Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP) under 5MB.")
            return render(request, 'blogapp/blog_edit.html', {'form': form, 'blog': blog})
        
        if form.is_valid():
            # Check if user wants to publish or save as draft
            action = request.POST.get('action')
            was_published = blog.status == 'published'
            
            if action == 'publish':
                blog.status = 'published'
                blog.save()
                
                # Send notification email if newly published
                if not was_published:
                    user_name = get_user_display_name(request.user)
                    email_subject = "Blog Published Successfully!"
                    email_message = f"Hi {user_name},\n\nYour blog '{blog.title}' has been published successfully!\n\nYou can view it on the home page.\n\nHappy Blogging!"
                    
                    send_email_notification(
                        subject=email_subject,
                        message=email_message,
                        recipient_email=request.user.email
                    )
                
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
                messages.success(request, "Blog updated successfully!")
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