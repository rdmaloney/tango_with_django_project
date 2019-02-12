from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class UserProfile(models.Model):
    # To link the UserProfile to the in built User model,
    # Inheriting the use model derectly could cause problems if other apps want to use the User model
    user = models.OneToOneField(User)

    # Additional attributes we want for or user
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    # 'profile_images' causes the the uploaded picture to be stored in the media/profile_images/ directory
    # Overwrite the to-string method to display something useful.
    def __str__(self):
        return self.user.username

class Category(models.Model):
    maxCharFeildLength = 128
    name = models.CharField(max_length=maxCharFeildLength, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return  self.name

class Page(models.Model):
    maxCharFeildLength = 128
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=maxCharFeildLength)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title 
