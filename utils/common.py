import os
import random
from django.conf import settings


def get_default_blog_image():
    """
    Returns a random default image path for blogs when no image is provided.
    """
    default_images = [
        'blog_images/DSC_0476.JPG',
        'blog_images/DSC_0528.JPG', 
        'blog_images/DSC_0530.JPG',
        'blog_images/IMG_20221012_125144.jpg',
        'blog_images/IMG_20230520_182953.jpg',
        'blog_images/IMG_20230612_154653.jpg',
        'blog_images/IMG_20230612_154719.jpg',
        'blog_images/IMG_20230612_175538.jpg',
        'blog_images/IMG_20230612_175546.jpg',
        'blog_images/IMG_20230614_125123.jpg',
        'blog_images/IMG_20230615_060554.jpg',
        'blog_images/IMG_20230615_183930.jpg',
    ]
    
    # Check if any default images exist
    existing_images = []
    for image_path in default_images:
        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        if os.path.exists(full_path):
            existing_images.append(image_path)
    
    if existing_images:
        return random.choice(existing_images)
    else:
        # Fallback to first image if none exist
        return default_images[0]


def get_blog_image_or_default(image_field):
    """
    Returns the image field value or a default image if no image is provided.
    """
    if image_field and hasattr(image_field, 'name') and image_field.name:
        return image_field.name
    return get_default_blog_image()


def validate_image_file(file):
    """
    Validates uploaded image file.
    Returns True if valid, False otherwise.
    """
    if not file:
        return True  # No file is valid (will use default)
    
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        return False
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return False
    
    return True


def send_email_notification(subject, message, recipient_email, from_email=None):
    """
    Common function to send email notifications.
    Can be reused across different apps.
    """
    from django.core.mail import send_mail
    
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def format_date_for_display(date_obj, format_string="%B %d, %Y"):
    """
    Format date objects for consistent display across the app.
    """
    if not date_obj:
        return "N/A"
    
    return date_obj.strftime(format_string)


def truncate_text(text, max_length=150, suffix="..."):
    """
    Truncate text to specified length with suffix.
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + suffix


def get_user_display_name(user):
    """
    Get display name for user (first_name + last_name or username).
    """
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return user.username
