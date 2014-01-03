# Create your views here.
from __future__ import division
import logging
import os
from django.http import HttpResponse
from polls.models import Poll
from django.shortcuts import render_to_response
from django.http import Http404
from polls.models import UserTable, ActivityTable, UserChargeTable, ActivityEnrollTable,UserConsumeTable
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
import time
from datetime import datetime
from django.core.context_processors import csrf
import string


GMT_FORMAT = '%b. %d, %Y'
logger = logging.getLogger('polls.app')

def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)


#TODO destroy the session
def logout(request):
    if 'register' in request.session:
        msg = 'user:'+request.session['register'].username+' logout'
        logger.debug(msg)
        del request.session['register'] 

    return login(request)

"""
TODO:
1) the form method should be POST iso GET
"""
def index(request):
    template_param = {}
    template_param.update(csrf(request))

    if 'email' in request.POST:
        email = request.POST['email']
        password = request.POST['password']
        users = UserTable.objects.filter(email=email,password=password)
        for user in users:
            #request.session.set_expiry(300)
            request.session['register'] = user
            template_param['user'] = user 
            activity_users = {}
            activity = ActivityTable.objects.filter(confirmed = 1)
            for a in activity:
                activity_users[a] = UserConsumeTable.objects.filter(activity_id = a)
            template_param['activity_users_dict'] = activity_users
            template_param['balance'] = user_detail_cost(request)
            template_param['total_balance'] = total_balance()

            return render_to_response('index.html', template_param)
        else:
            return render_to_response('error_info.html', {'errors': ['USER is not existing or PASSWORD is not correct']}, context_instance=RequestContext(request))

    elif 'register' in request.session:
        print '%s logged-in'%(request.session['register'].username)

    else:
        request.session['register'] = UserTable(username="Anonymous User", privilege=0)
        print "Guest User Login"
    
    template_param['balance'] = user_detail_cost(request)
    template_param['total_balance'] = total_balance()

    template_param['user'] = request.session['register'] 
    activity_users = {}
    activity = ActivityTable.objects.filter(confirmed = 1)
    for a in activity:
        activity_users[a] = UserConsumeTable.objects.filter(activity_id = a)
    user_consume_list = UserConsumeTable.objects.all()
    template_param['user_consume_list'] = user_consume_list 
    template_param['activity_users_dict'] = activity_users

    print activity_users
    print request.session['register']
    print template_param

    return render_to_response('index.html', template_param)



def get_published_activity():

    """
    published activity means the date of the activity is greater than now.
    this function will get return the activities that the date are greater than now.
    In fact there will be only one activity which the date greater than now.
    """

    now_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    activity = ActivityTable.objects.filter(date__gte=now_date, confirmed=0)
    #activity = ActivityTable.objects.filter(confirmed=0)
    print activity

    return activity

def get_enrolled_not_finished_activity(user):

    """
    get the user enrolled activity that have not be finished.
    In fact there will be only one enrolled and not finished activity for the user.
    A list will returned.
    """
    activity_list = get_published_activity()
    enrolled_activity = []
    for activity in activity_list:
        try:
            enrolledActivity = ActivityEnrollTable.objects.get(activity_id=activity,user_id=user)
        except ObjectDoesNotExist:
            print 'activity not existed'
        else:
            enrolled_activity.append(enrolledActivity)

    return enrolled_activity


def enrolled(request):
    if 'register' in request.session:

        if 'Anonymous User' == request.session['register'].username:
            return login(request)

        user = request.session['register']
        template_param = {'selected_activity':[],'user':user,'enroll_users':[]}

        selected_activity = request.POST.get('act_radio')

        enrolled_activity = get_enrolled_not_finished_activity(user) 
        print 'in enrolled:'
        print enrolled_activity
        template_param['selected_activity']=enrolled_activity
        template_param['balance']=user_detail_cost(request)
        template_param['total_balance'] = total_balance()
        if selected_activity and not enrolled_activity:
            date = selected_activity
            activity = ActivityTable.objects.get(date = date)
            enrolledActivity = ActivityEnrollTable(activity_id = activity, user_id = user)
            if enrolledActivity:
                enrolledActivity.save()
                enrolled_users = ActivityEnrollTable.objects.filter(activity_id = enrolledActivity.activity_id)
                template_param['enroll_users'] = enrolled_users
                template_param['selected_activity'] = get_enrolled_not_finished_activity(user)
            return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))
        elif enrolled_activity:
            enrolled_users = ActivityEnrollTable.objects.filter(activity_id = enrolled_activity[0].activity_id)
            template_param['enroll_users'] = enrolled_users
        else:
            template_param['activity_list'] = get_published_activity()

        return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))
    else:
        return login(request)

def delete_enrolled(request):
    if 'register' in request.session:
        if 'Anonymous User' == request.session['register'].username:
            return login(request)
        user = request.session['register']
        template_param = {'selected_activity':[],'user':user,'enroll_users':[]}

        delete_activity_date = request.POST.getlist('delete')
        if delete_activity_date:
            date = delete_activity_date[0]

            try:
                deleted_activity = ActivityTable.objects.get(date=date)
            except ObjectDoesNotExist:
                print 'activity does not existed'

            try:
                enrolledActivity = ActivityEnrollTable.objects.get(activity_id = deleted_activity,user_id=user)
            except ObjectDoesNotExist:
                print 'enrolled Activity does not existed'

            if enrolledActivity:
                enrolledActivity.delete()
        else:
            print 'must select an activity!!!'


        enrolled_activity = get_enrolled_not_finished_activity(user) 
        template_param['selected_activity']=enrolled_activity
        template_param['balance']=user_detail_cost(request)
        template_param['total_balance'] = total_balance()
        template_param['activity_list'] = get_published_activity()

        if enrolled_activity:
            enrolled_users = ActivityEnrollTable.objects.filter(activity_id = enrolled_activity[0].activity_id)
            template_param['enroll_users'] = enrolled_users

        return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))


    else:
        return login(request)



def enroll(request):
    if 'register' in request.session:

        if 'Anonymous User' == request.session['register'].username:
            return login(request)

        user = request.session['register']
        published_activity_list = get_published_activity()  # the published activity list
        enroll_activity = request.POST.get('act_radio')

        delete_activity_date = request.POST.getlist('delete')
        errors = []
        template_param = {'activity_list':published_activity_list,'user':user,'errors':errors,'enroll_users':[]}

        enrolledActivity_list = get_enrolled_not_finished_activity(user)
        template_param['balance']=user_detail_cost(request)
        template_param['total_balance'] = total_balance()

        if enrolledActivity_list:
            selected_activity = enrolledActivity_list 
            template_param['selected_activity'] = selected_activity
            print 'selected_activity is'
            print selected_activity
            enrolled_users = ActivityEnrollTable.objects.filter(activity_id = selected_activity[0].activity_id)
            template_param['enroll_users'] = enrolled_users
            return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))
        elif published_activity_list:
            return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))
        else:          
            errors.append('no published activities! please wait...')
            return render_to_response('enroll.html', template_param,context_instance=RequestContext(request))
    else:
        return login(request)


def userlist(request):
    if 'register' in request.session:
        pass
    else:
        request.session['register'] = UserTable(username="Anonymous User", privilege=0)
        logger.debug("Guest User Login")

    user_list = UserChargeTable.objects.all()
    user_consume_list = UserConsumeTable.objects.all()
    return render_to_response('userlist.html', {'user_list': user_list,'user_consume_list':user_consume_list,'balance':user_detail_cost(request),'user':request.session['register'],'total_balance':total_balance()})


"""
TODO:maybe the logic should be changed, there should be only one activity published.
"""
def activity(request):
    if 'register' in request.session:
        if 0 == request.session['register'].privilege:
            return login(request)
        errors = []
        user = request.session['register']
        template_param = {'user':user,'errors':errors}
        template_param['balance'] = user_detail_cost(request)
        template_param['total_balance'] = total_balance()

        if 'activity_date' in request.POST:
            date = request.POST['activity_date']

            """the published activity date must be greater than now"""
            if date:
                now_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                if not date > now_date:
                    errors.append("the date must be greater than now")
            else:
                errors.append('you must add the date')

            location = request.POST['activity_location']
            if not location:
                errors.append('you must add the location')

            comments = request.POST['activity_comments']
            if not comments:
                errors.append('you must add the comments')

            if not errors:
                activity = ActivityTable.objects.filter(date=date)
                if activity:
                    errors.append('the published activity has already been published')

            if errors:
                return render_to_response('activity.html',template_param,context_instance=RequestContext(request))
            else:
                if not activity:
                    activity = ActivityTable(date=date,location=location,comments = comments, cost=50)
                    activity.save()
            return render_to_response('activity.html',template_param,context_instance=RequestContext(request))
        else:
            return render_to_response('activity.html',template_param,context_instance=RequestContext(request))
    else:
        return render_to_response('login.html',context_instance=RequestContext(request))


def register_show(request):
    return render_to_response('register.html', context_instance=RequestContext(request))


def register(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('username', ''):
            errors.append("username is empty")
        if not request.POST.get('email', ''):
            errors.append('email is empty')
        if not request.POST.get('usertype', ''):
            errors.append('usertype is empty')
        if not request.POST.get('money'):
            errors.append('money is empty')
        if not request.POST.get('pwd'):
            errors.append('password is empty')
        if not request.POST.get('re_pwd'):
            errors.append('repeat password is empty')
        if not request.POST.get('re_pwd') == request.POST.get('pwd'):
            errors.append('password is not same')
        if not len(UserTable.objects.filter(username=request.POST['username'])) == 0:
            errors.append('Username is not unique')
        if not len(UserTable.objects.filter(email=request.POST['email'])) == 0:
            errors.append('Email is not unique')
        if not errors:
            user = UserTable(username=request.POST['username'],email=request.POST['email'],usertype=request.POST['usertype'],password=request.POST['pwd'])
            user.save()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            usercharge = UserChargeTable(user_id=user, money=request.POST['money'], date=date)
            usercharge.save()
            return login(request)
        else:
            return render_to_response('error_info.html', {'errors': errors})

    return render_to_response('register.html', {'errors': errors}, context_instance=RequestContext(request))



"""Todo: need check whether the user is already existed"""
def adduser(request):
    if 'register' in request.session:
        if 0 == request.session['register'].privilege:
            return login(request)
        user = request.session['register']
        print 'add user function'
        errors = []
        if request.method == 'POST':
            if not request.POST.get('username', ''):
                errors.append("username is empty")
            if not request.POST.get('email', ''):
                errors.append('email is empty')
            if not request.POST.get('usertype', ''):
                errors.append('usertype is empty')
            if not request.POST.get('money'):
                errors.append('money is empty')
            if not UserTable.objects.filter(username=request.POST['username']) == []:
                errors.append('Username is not unique')
            if not UserTable.objects.filter(email=request.POST['email']) == []:
                errors.append('Email is not unique')
            if not errors:
                user = UserTable(username=request.POST['username'],email=request.POST['email'],usertype=request.POST['usertype'])
                user.save()
                date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                usercharge = UserChargeTable(user_id=user, money=request.POST['money'], date=date)
                usercharge.save()
                return render_to_response('adduser.html', {'errors': errors,'user':user, 'balance':user_detail_cost(request),'total_balance':total_balance()}, context_instance=RequestContext(request))
            else:
                return render_to_response('error_info.html', {'errors': errors})

        return render_to_response('adduser.html', {'errors': errors, 'user':user, 'balance':user_detail_cost(request),'total_balance':total_balance()}, context_instance=RequestContext(request))
    else:
        return login(request)


def usercharge(request):
    if 'register' in request.session:
        if 0 == request.session['register'].privilege:
            return login(request)

        users = UserTable.objects.all()

        if request.method == 'GET':
            return render_to_response('usercharge.html', {'user':request.session['register'], 'users':users, 'balance':user_detail_cost(request),'total_balance':total_balance()}, context_instance=RequestContext(request))
        
        errors = []
        if request.method == 'POST':
            if not request.POST.get('selectUser'):
                errors.append('user is empty')
            if not request.POST.get('money'):
                errors.append('money is empty')
            if not errors:
                date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                usercharge = UserChargeTable(user_id=UserTable.objects.get(user_table_id = request.POST['selectUser']), money=request.POST['money'], date=date)
                usercharge.save()
                return render_to_response('usercharge.html', {'users':users, 'user':request.session['register'], 'balance':user_detail_cost(request),'total_balance':total_balance()}, context_instance=RequestContext(request))
            else:
                return render_to_response('error_info.html', {'errors': errors})
    else:
        return login(request)


def get_unconfirmed_activyt():
    return ActivityTable.objects.filter(confirmed = 0)


def consume(request):
    if 'register' in request.session:
        if 0 == request.session['register'].privilege:
            return login(request)
        user = request.session['register']
        unconfirmed_activity_list = ActivityTable.objects.filter(confirmed = 0)
        related_users = {}
        template_param = {}
        errors = []
        template_param['user'] = user
        template_param['all_users'] = UserTable.objects.all()
        template_param['errors'] = errors
        template_param['balance'] = user_detail_cost(request)
        template_param['total_balance'] = total_balance()
        radio = request.POST.get('radio')
        print radio
        print 'begin'
        print request.POST.get('cost')
        print 'end'
        if not radio:
            for ac in unconfirmed_activity_list:
                related_users[ac] = ActivityEnrollTable.objects.filter(activity_id = ac)
                for ra in related_users[ac]:
                    template_param['all_users'] = template_param['all_users'].exclude(email=ra.user_id.email)

            template_param['unconfirmed_activity_list']=unconfirmed_activity_list
            template_param['related_users'] = related_users
            return render_to_response('consume.html',template_param,context_instance=RequestContext(request))
        else:
            selected_activity = ActivityTable.objects.get(date=radio)
            cost = request.POST.get('cost')
            print "selected_activity is %s"%(selected_activity)
            if cost == None:
                errors.append('must input the cost') 
                return render_to_response('error_info.html',{'errors' : errors})
            else:
                attend_users = request.POST.getlist('cb_%s'%(selected_activity))
                selected_activity.cost = cost
                selected_activity.save()

                if len(attend_users) == 0:
                    return render_to_response('error_info.html',{'errors' : ['Attend user list is empty.']})

                confirm_consume(selected_activity,attend_users,cost)
                return render_to_response('consume.html',template_param,context_instance=RequestContext(request))

    else:
        return login(request)
    


def confirm_consume(activity,users,cost):

    print "!!!!!!!!!!!  ????????? users: %s"%(users)
 
    average_cost = string.atoi(cost) / len(users)
    print 'average_cost is %d'%(average_cost)

    for u in users:
        u_consume = UserConsumeTable(user_id = UserTable.objects.get(email=u), activity_id = activity,cost = average_cost,comments = activity.comments)
        u_consume.save()

    activity.confirmed = 1
    activity.save()



def user_detail_cost(request):
    if 'register' in request.session:
        user = request.session['register']
        if user.username == 'Anonymous User':
            print 'test'
            return 0

        user_charge_list = UserChargeTable.objects.filter(user_id=user)
        user_consume_list = UserConsumeTable.objects.filter(user_id=user)
        user_charge_total = 0
        user_consume_total = 0

        for u in user_charge_list:
            user_charge_total = user_charge_total + u.money

        for u in user_consume_list:
            user_consume_total = user_consume_total + u.cost


        balance = user_charge_total - user_consume_total
        print balance, user_charge_total, user_consume_total
        return balance

def total_balance():
    user_charge_all= UserChargeTable.objects.all()
    user_consume_all = UserConsumeTable.objects.all()
    user_charge_total= 0
    user_consume_total = 0

    for u in user_charge_all:
        user_charge_total = user_charge_total+u.money

    for u in user_consume_all:
        user_consume_total = user_consume_total + u.cost
    total_balance = user_charge_total - user_consume_total
    return total_balance
