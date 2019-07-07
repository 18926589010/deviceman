from django.shortcuts import render
from deviceman.models import user_list, pc_list
from django.db.models import Count
from django.forms.models import model_to_dict

# Create your views here.
from django.http import HttpResponse
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def total(request):
    n=map(str, range(100))
    result = pc_list.objects.values('hosttype__name' , 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    result_dict ={'result': result, 'n': n}

    return render(request, 'total.html', result_dict, )



def tuser_list(request):
    return HttpResponse("this is user list")

def dept_list(request):
    return HttpResponse("this is department list")

def read_deviceman():
    return HttpResponse("this is deviceman data")

def hello(request):
    context={}
    context['hello']='Hello World, This is my first Templates'
    context['name']='My name is Liu, Honghai'
    context['date']=date.today()
    return render(request,'hello.html',context)

def display_user(request):
    context={}
    return render(request,'display_user.html',context)

def search(request):
    context={}
    context['message']=message= request.GET['q']
    return render(request,'search.html', context,)



def showusers(request):
    users=user_list.objects.all()
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    currentPage = int(page)
    try:
        print(page)
        users = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        users = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容

    return render(request, "showuser.html", locals())


    #return render(request,'showuser.html',{'users':users})
