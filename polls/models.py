from django.db import models
import datetime
from django.utils import timezone
from django.contrib import admin
from datetime import date

# Create your models here.


class UserTable(models.Model):
    user_table_id = models.AutoField(primary_key=True, auto_created=True)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30, default='123456')
    email = models.EmailField(unique=True)
    usertype = models.CharField(max_length=30)
    privilege = models.BooleanField(default=0)

    def __unicode__(self):
        return self.username

    def IsAdmin(self):
        if self.privilege:
            return 'admin user'
        else:
            return 'common user'

    IsAdmin.short_description = 'Administrator Or Common User'


class ActivityTable(models.Model):
    activity_table_id = models.AutoField(primary_key=True, auto_created=True)
    date = models.DateField()
    location = models.CharField(max_length=50)
    cost = models.FloatField()
    comments = models.CharField(max_length=80)
    confirmed = models.BooleanField(
        default=0)  # flag to indicate whehter the consume of the activity is confirmed, 0:not confirmed,1:confirmed


    def __unicode__(self):
        print type(self.date)
        print self.date
        return date.strftime(self.date,'%Y-%m-%d')



class UserConsumeTable(models.Model):
    user_consume_table_id = models.AutoField(
        primary_key=True, auto_created=True)
    user_id = models.ForeignKey(UserTable)
    activity_id = models.ForeignKey(ActivityTable)
    cost = models.FloatField()
    comments = models.CharField(max_length=80)

    def __unicode__(self):
        return self.user_id.username


class ActivityEnrollTable(models.Model):
    activity_enroll_table_id = models.AutoField(
        auto_created=True, primary_key=True)
    activity_id = models.ForeignKey(ActivityTable)
    user_id = models.ForeignKey(UserTable)

    def __unicode__(self):
        return self.user_id.username


class UserChargeTable(models.Model):
    user_charge_table_id = models.AutoField(
        primary_key=True, auto_created=True)
    user_id = models.ForeignKey(UserTable)
    date = models.DateField()
    money = models.FloatField()
    comments = models.CharField(max_length=80, default='pay for activity')

    def __unicode__(self):
        return self.user_id.username


class Message(models.Model):
    message_id = models.AutoField(primary_key=True, auto_created=True)
    title = models.CharField('title', max_length=50)
    author = models.CharField(max_length=30)
    email = models.EmailField()
    content = models.TextField()

    def __unicode__(self):
        return self.title


class Comments(models.Model):
    comments_id = models.AutoField(primary_key=True, auto_created=True)
    message = models.ForeignKey(Message)
    author = models.CharField('comment author', max_length=30)
    comments = models.TextField()


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateField('published date new')

    def __unicode__(self):
        return self.question

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __unicode__(self):
        return self.choice
