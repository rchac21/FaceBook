from django.db import models
from django.utils import timezone

# Table of Facebook users.
class FaceBookUsers(models.Model):
     first_name = models.CharField(max_length=100)
     last_name = models.CharField(max_length=100)
     username = models.CharField(max_length=200)
     phone_num = models.IntegerField(primary_key=True)
     email = models.EmailField(max_length=254, unique=True)
     password = models.CharField(max_length=128)
     birthday = models.DateField()
     gender = models.CharField(max_length=100)


# Personal information of users is stored.
class PersonalInfo(models.Model):
     email = models.EmailField(max_length=254, unique=True)
     experience = models.CharField(max_length=100,null=True)
     university = models.CharField(max_length=100,null=True)
     school = models.CharField(max_length=100,null=True)
     city = models.CharField(max_length=200,null=True)
     country = models.CharField(max_length=200,null=True)


# Keep friendly pairs.
class Friends(models.Model):
     email = models.EmailField(max_length=254)
     friend_email = models.EmailField(max_length=254)
     
# Users' posts are stored.
class Posts(models.Model):
     email = models.EmailField(max_length=254)
     post = models.CharField(max_length=1000)
     date_added = models.DateTimeField(default=timezone.now)

     def save(self, *args, **kwargs):
        if not self.pk:
          self.date_added = timezone.now()
        return super(Posts, self).save(*args, **kwargs)


class SearchedUsersTable(models.Model):
     email = models.EmailField(max_length=254)
     username = models.CharField(max_length=100)


# Pairs of users who sent a friend request and who sent it are stored.
class Req_Resp_Table(models.Model):
     req_email = models.EmailField(max_length=254)
     resp_email = models.EmailField(max_length=254)

# Users' photos are stored.
class Photos(models.Model):
    image = models.ImageField(upload_to='photos/')
    email = models.EmailField(max_length=254)
    date_added = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
          self.date_added = timezone.now()
        return super(Photos, self).save(*args, **kwargs)


# Profile photos of users are stored.
class Profile_Photos(models.Model):
    image = models.ImageField(upload_to='photos/')
    email = models.EmailField(max_length=254,primary_key=True)
    date_added = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
          self.date_added = timezone.now()
        return super(Profile_Photos, self).save(*args, **kwargs)


# The default photo is saved, which is set on the user's 
# profile in case the user has nothing set.
class Default_Photo(models.Model):
    image = models.ImageField(upload_to='photos/')
     