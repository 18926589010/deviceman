# from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from account.form import LoginForm
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from account.form import LoginForm
from django.shortcuts import redirect
from deviceman.models import adm_site


@csrf_exempt
def userlogin(request):
    if request.method == "GET":

        return render(request, "login3.html")
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.adm_info.system_adm:
                request.session['current_site'] = '1'
                request.session['site_name'] = 'CNSHZ1'
                request.session['officename'] = 'Luohu'
            else:
                # request.session['current_site']
                userid = user.id
                print('user id is ' + str(userid))
                request.session['current_user_id'] = userid
                sites = adm_site.objects.filter(User_id=userid)
                for siteid in sites:
                    request.session['current_site'] = siteid.site_id
                    print('current site is ' + str(siteid.site_id))
                    request.session['officename'] = siteid.site.officename
                    print('office name is' + siteid.site.officename)
                    request.session['site_name'] = siteid.site.sitename
                    print('site name is ' + siteid.site.sitename)
            return HttpResponseRedirect('/deviceman/totalchart')

        # login_form=LoginForm(request.POST)
        # if login_form.is_valid():
        #     cd=login_form.cleaned_data
        #     #user = authenticate(username=cd['username'],password=cd['password'])
        #     if user:
        #         login(request,user)
        #         if user.adm_info.system_adm :
        #             request.session['current_site']='1'
        #             request.session['site_name'] = 'CNSHZ1'
        #         else:
        #             #request.session['current_site']
        #             userid=user.id
        #             print('user id is '+str(userid))
        #             request.session['current_user_id']=userid
        #             sites=adm_site.objects.filter(User_id=userid)
        #             for siteid  in sites:
        #
        #                 request.session['current_site']=siteid.site_id
        #                 print('current site is '+str(siteid.site_id) )
        #                 request.session['officename']=siteid.site.officename
        #                 print('office name is'+siteid.site.officename)
        #                 request.session['site_name']=siteid.site.sitename
        #                 print('site name is '+siteid.site.sitename)
        #
        #         #return HttpResponse('WELCOME')
        #         return redirect('../account/log_index')
        else:
             return HttpResponse('Failed')



def userlogout(request):
    logout(request)
    context = {}
    return render(request, 'logout.html', context,)

def log_index(request):
    contex={}
    return render(request, 'login_index.html',contex)
