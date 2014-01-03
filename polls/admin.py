__author__ = 'jasonas'
from polls.models import Poll
from polls.models import Choice
from polls.models import Message
from polls.models import Comments
from polls.models import UserTable, ActivityTable, ActivityEnrollTable, UserConsumeTable, UserChargeTable
#from example.models import Publisher, Book, Author
#from example.models import Fact
from django.contrib import admin


class PollAdmin(admin.ModelAdmin):
    fields = ['pub_date', 'question']
    list_display = ('pub_date', 'question')


class CommentsInline(admin.TabularInline):
    model = Comments
    extra = 3


class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'email', 'content')
    list_filter = ['title', 'author']
    search_fields = ['author']
    inlines = [CommentsInline]


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author', 'comments')


#class ActivityEnrollTableAdmin(admin.ModelAdmin):
#    list_display = ('activity_id','user_id')


class UserTableAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'email', 'usertype', 'privilege', 'IsAdmin')

#class UserConsumeTableAdmin(admin.ModelAdmin):
#    list_display = ('user_id',"activity_id")



admin.site.register(UserTable, UserTableAdmin)
admin.site.register(ActivityTable)
#admin.site.register(Fact)
admin.site.register(UserChargeTable)
admin.site.register(UserConsumeTable)#,UserConsumeTableAdmin)
admin.site.register(ActivityEnrollTable)#,ActivityEnrollTableAdmin)

#admin.site.register(Publisher)
#admin.site.register(Book)
#admin.site.register(Author)
"""
admin.site.register(Message, MessageAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Choice)
"""
