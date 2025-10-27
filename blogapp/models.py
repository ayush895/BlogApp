from django.db import models
from django.contrib.auth.models import User
from utils.common import get_default_blog_image

class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    # Store only filenames at upload time (no folder prefix)
    image = models.ImageField(upload_to='', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def get_image_url(self):
        """
        Returns the image URL or default image URL if no image is set.
        """
        if self.image and hasattr(self.image, 'name') and self.image.name:
            return self.image.url
        else:
            # Return default image URL
            default_image = get_default_blog_image()
            return f"/media/{default_image}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to set default image if none provided.
        """
        # If no image is provided and this is a new instance, set default image
        if not self.pk and not self.image:
            self.image = get_default_blog_image()
        super().save(*args, **kwargs)


class Like(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.blog.title}"


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"