from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
#from example.views import AboutView,PublisherList
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #url(r'^polls/$', 'polls.views.index'),
    url(r'^polls/login.html$', 'polls.views.login'),
    url(r'^polls/index.html$', 'polls.views.index'),
    url(r'^polls/enroll.html$', 'polls.views.enroll'),
    url(r'^polls/userlist.html$', 'polls.views.userlist'),
    url(r'^polls/adduser.html$', 'polls.views.adduser'),
    url(r'^polls/usercharge.html$', 'polls.views.usercharge'),
    url(r'polls/logout.html', 'polls.views.logout'),
    url(r'polls/activity.html', 'polls.views.activity'),
    url(r'polls/enrolled.html','polls.views.enrolled'),
    url(r'polls/delete_enrolled','polls.views.delete_enrolled'),
    url(r'polls/consume.html','polls.views.consume'),
    url(r'polls/register.html','polls.views.register'),
    url(r'polls/register$','polls.views.register_show'),
	url(r'polls/excel','polls.views.excel_view'),
)
