from django.shortcuts import render, redirect
from stationery.models import stationery, stat_type, provider, order_record_master, order_record_slave, purchase_master, \
    purchase_slave
from django.db.models import Count, Sum
from django.http import HttpResponseRedirect, HttpResponse
from deviceman.models import user_list
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
# from api.serializers import StaionerySerializer
import datetime
import json
from django.db.models import F
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/account/login')
def index(request):
    # stats = stationery.objects.all()
    #del request.session['entryid']
    stats = stationery.objects.values_list('stat_type', 'stat_type__name').annotate(Count('stat_type'))
    print(stats.query)
    print(stats)
    orders = order_record_master.objects.filter(order_status='submitted')
    print(orders)
    stock_alerts = stationery.objects.filter(alert_num__gte=F('stock_num')).order_by('stock_num')[0:10]
    return render(request, 'stationery/stat_index.html',
                  {'stats': stats, 'orders': orders, 'stock_alerts': stock_alerts})


def alert_stat_list(request):
    # stats = stationery.objects.all()
    # #del request.session['entryid']
    # stats = stationery.objects.values_list('stat_type', 'stat_type__name').annotate(Count('stat_type'))
    # print(stats.query)
    # print(stats)
    # orders = order_record_master.objects.filter(order_status='submitted')
    # print(orders)
    stock_alerts = stationery.objects.filter(alert_num__gte=F('stock_num')).order_by('stock_num')[0:10]
    return render(request, 'stationery/alert_stat_list.html',
                  {'stock_alerts': stock_alerts})

def orderlist(request):

    orders = order_record_master.objects.filter(order_status='submitted')

    return render(request, 'stationery/orderlist.html',
                  {'orders': orders})


def stat_list(request):
    id = request.GET.get('id')
    stat_list = stationery.objects.filter(stat_type=id)
    print(stat_list)
    return render(request, 'stationery/stat_list.html', {'stat_list': stat_list})


def order_detail(request):
    orderid = request.GET.get('orderid')
    orders = order_record_slave.objects.filter(order_record_master_id=orderid)
    users = order_record_master.objects.filter(id=orderid)

    # userid = users[0]['user_list_id']
    # users_list = user_list.objects.filter(id=userid)

    return render(request, 'stationery/order_detail.html',
                  {'orders': orders, 'users': users, 'orderid': orderid})


@csrf_exempt
def stat_apply_index(request):
    user_list_id = request.session.get('user_list_id')
    print('stat_apply_index1: user_list_id is %s' % (user_list_id))
    full_name = request.session.get('full_name')
    print('stat_apply_index1: full_name is %s' % (full_name))
    orderid = request.session.get('orderid')
    if orderid == None:
        return HttpResponseRedirect('apply_login')
    print('stat_apply_index1: orderid is %s' % (orderid))
    stat_types = stat_type.objects.all()

    # print(orderid)
    if user_list_id == None:
        return HttpResponseRedirect('apply_login')
    cart = request.session.get("cart", None)
    carts = order_record_slave.objects.filter(order_record_master_id=orderid)
    if request.method == 'GET':

        if 'id' in request.GET:
            stat_type_id = request.GET.get('id')
            # print(stat_type_id)
            stationerys = stationery.objects.filter(stat_type_id=stat_type_id)
            ######以下是实现分页
        # paginator = Paginator(stationerys, 20)
        # page = request.GET.get('page', 1)
        # currentPage = int(page)
        # try:
        # print(page)
        # stationerys = paginator.page(page)  # 获取当前页码的记录
        # except PageNotAnInteger:
        # stationerys = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        # except EmptyPage:
        # stationerys = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容

        # return render(request, 'stationery/stat_apply_index.html', locals())

        else:
            stationerys = order_record_slave.objects.values('stationery__spec').annotate(number=Sum("order_num"),
                                                                                         spec=F('stationery__spec'),
                                                                                         id=F('stationery_id'),
                                                                                         name=F('stationery__name'),
                                                                                         stat_img=F(
                                                                                             'stationery__stat_img'),
                                                                                         stock_num=F(
                                                                                             'stationery__stock_num')).order_by(
                '-number')[:12]
            print(stationerys)
        # return render(request, 'stationery/stat_apply_index.html', {'stationerys': stationerys,'stat_types':stat_types})
        return render(request, 'stationery/stat_apply_index_test.html',
                      {'carts': carts, 'stationerys': stationerys, 'stat_types': stat_types})
    if request.method == 'POST':
        stationery_name = request.POST.get('stationery_name')
        stationerys = stationery.objects.filter(name__icontains=stationery_name)
        # return render(request, 'stationery/stat_apply_index.html', {'stationerys': stationerys,'stat_types':stat_types})
    return render(request, 'stationery/stat_apply_index_test.html',
                  {'carts': carts, 'stationerys': stationerys, 'stat_types': stat_types})


def add_to_cart(request):
    user_list_id = request.session.get('user_list_id', None)
    statid = request.GET.get('statid')
    # obj=models.order_record(stationery_id=20,user_list_id=243, num=1)
    order_record_master.objects.create(order_status='submitted', user_list_id=243, date='2018-08-30')
    order_record_slave.objects.create(order_num=1, order_record_master_id=3, stationery_id=12)
    # obj.save()
    # carts=order_record.objects.filter(user_list_id=243)
    # print(carts)
    return HttpResponseRedirect('stat_apply_index1')


def clean_cart(request):
    ##清除购物车列表
    user_list_id = request.session.get('user_list_id')
    orderid = request.session.get('orderid')
    order_record_slave.objects.filter(order_record_master_id=orderid).delete()
    # order_record_master.objects.filter(user_list_id=user_list_id, order_status='shopping').delete()
    #return HttpResponseRedirect('showcart')
    return HttpResponse(2)


def submit_cart(request):
    user_list_id = request.session.get('user_list_id')
    orderid = request.session.get('orderid')
    # print(user_list_id)
    print('order id is %s' % (orderid))
    # orderid=request.session.get('orderid')
    ##提交订单，要将相应的文具的库存数减去员工领用数
    orders = order_record_slave.objects.filter(order_record_master_id=orderid)
    for order in orders:
        stationery_id = order.stationery_id
        print('stationery id is %s' % (stationery_id))
        order_num = order.order_num
        print('order num is %s' % (order_num))
        obj = stationery.objects.get(id=stationery_id)
        obj.stock_num = obj.stock_num - order_num
        print('stock num is %s' % (obj.stock_num))
        obj.save()

    # 提交订单位，将订单的状态改为submitted,
    order_record_master.objects.filter(user_list_id=user_list_id, id=orderid).update(order_status='submitted',
                                                                                     date=datetime.datetime.now().strftime(
                                                                                         "%Y-%m-%d"))
    request.session['orderid'] = None
    # del request.session['user_list_id']
    return HttpResponseRedirect('showcart')


def complete_order(request):
    orderid = request.GET.get('orderid')
    order_record_master.objects.filter(id=orderid).update(order_status='Completed')
    return HttpResponseRedirect('orderlist')


@csrf_exempt
def apply_login(request):
    if request.method == 'GET':
        return render(request, 'stationery/apply_login.html')
    if request.method == 'POST':
        email_address = request.POST.get('email_address')
        # print(email_address)
        users = user_list.objects.filter(email_address=email_address)
        if users.exists():
            for user in users:
                # 查询是否有未提交的申请，
                request.session['user_list_id'] = user.id  # #把当前user_list_id传给session
                request.session['full_name'] = user.full_name  # 把当前full_name传给session
                request.session['email_address'] = email_address
                request.session['dept_name'] = user.dept_list.dept_name

                order_record_masters = order_record_master.objects.filter(user_list_id=user.id, order_status='shopping')
                if order_record_masters.exists():
                    for order in order_record_masters:
                        request.session['orderid'] = order.id  # 如果有未提交的申请，取出ID号，传递给session
                        print('there is existing orderid in shopping statue ', order.id)

                else:
                    # 如果没有查询到未提交的申请，就创建一条主记录
                    order_record_master.objects.create(date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                                       order_status='shopping', user_list_id=user.id)
                    print(user.id)
                    orders = order_record_master.objects.filter(user_list_id=user.id, order_status='shopping')

                    print(orders)
                    for order in orders:
                        request.session['orderid'] = order.id
                        print('created a new order id ', order.id)
            return HttpResponseRedirect("apply_index")
            # return render(request,'stationery/apply_index.html',{'users':users})
        else:
            error_msg = "Not found any Employee match the email address you enter"
            return render(request, 'stationery/apply_login.html', {'msg': error_msg})


def ajax(request):
    id = request.GET.get('id')
    orderid = request.GET.get('orderid')
    # user_list_id=request.session.get('user_list_id',None)
    # msg='sucessfully'
    # print(id)
    # print(msg)
    # print("get the stationery id is '%s'"%(id))
    # print("get order is is '%s'"%(orderid))
    # search if there is any same stationery_id on the shopping orderid
    res = order_record_slave.objects.filter(order_record_master_id=orderid, stationery_id=id)

    if res.exists():
        # print("find same stationery '%s'" % (id))
        for stat in res:
            id = stat.id
            # print("stat id is '%s'"%(id))
            obj = order_record_slave.objects.get(id=id)
            obj.order_num = obj.order_num + 1
            obj.save()
            stats = order_record_slave.objects.filter(order_record_master_id=orderid).values('id', 'stationery__name',
                                                                                             'order_num')
            ret = list(stats)
            result = json.dumps(ret)
            print(result)
            return HttpResponse(result, "application/json")
    else:
        # print("not found any same stationery")
        order_record_slave.objects.create(order_num=1, order_record_master_id=orderid, stationery_id=id)
        # stats=serializers.serialize('json',order_record_master.objects.filter(id=orderid))
        stats = order_record_slave.objects.filter(order_record_master_id=orderid).values('id', 'stationery__name',
                                                                                         'order_num')
        ret = list(stats)
        result = json.dumps(ret)
        print(result)
        return HttpResponse(result, "text/json;charset=utf-8")


def ajax_layer_show_cart(request):
    # id=request.GET.get('id')
    orderid = request.session.get('orderid')

    # order_record_slave.objects.create(order_num=1, order_record_master_id=orderid, stationery_id=id)
    carts = order_record_slave.objects.filter(order_record_master_id=orderid)
    # stats= order_record_slave.objects.filter(order_record_master_id=orderid).values('id','stationery__name', 'order_num')
    # ret = list(stats)
    # ret = json.dumps(ret)
    # print(ret)
    #print(carts)
    return render(request, 'stationery/showcart.html', {'carts': carts})


def apply_index(request):
    user_list_id = request.session.get('user_list_id')
    orderid = request.session.get('orderid')
    orders = order_record_master.objects.filter(user_list_id=user_list_id).exclude(order_status='shopping')
    return render(request, 'stationery/apply_index.html', {'orders': orders})


@csrf_exempt
def pur_index(request):
    stat_types = stat_type.objects.all()
    #pur_historys = purchase_master.objects.filter(pur_status='submitted').order_by('-date')[:8]
    purs = purchase_slave.objects.filter(entryid_id=request.session.get('entryid'))
    return render(request, 'stationery/purchase_index.html', locals())


@csrf_exempt
def pur_list(request):

    pur_historys = purchase_master.objects.filter(pur_status='submitted').order_by('-date')[:10]
    #purs = purchase_slave.objects.filter(entryid_id=request.session.get('entryid'))
    return render(request, 'stationery/purchase_list.html', locals())

@csrf_exempt
def stock_report(request):

    return render(request, 'stationery/stock_report.html', locals())

##get the stationery list via stat_type_id from select list
def ajax_load_stationery(request):
    if request.method == 'GET':
        stat_type_id = request.GET.get('stat_type_id', None)
        print('get stat_type_id from ajax "%s"' % (stat_type_id))
        if stat_type_id:
            data = list(stationery.objects.filter(stat_type_id=stat_type_id).values("id", "name"))
            result = json.dumps(data)
            print(result)
    return HttpResponse(result, "application/json")


@csrf_exempt
def update_pur_slave(request):
    entryid = request.session.get('entryid')
    stationery_id = request.POST.get('id_stationery')
    pur_num = request.POST.get('pur_num')
    print('stationery id is "%s"' % (stationery_id))
    print('pur num is "%s"' % (pur_num))
    purchase_slave.objects.create(entryid_id=entryid, num=pur_num, stationery_id=stationery_id)
    request.session['entryid']
    return HttpResponseRedirect('pur_index')


def submit_pur(request):
    entryid = request.session.get('entryid')
    res = purchase_slave.objects.filter(entryid_id=entryid)
    if res.exists():
        print("find  stationery with entryid '%s'" % (entryid))
        for purs in res:
            id = purs.stationery_id
            print("stat id is '%s'" % (id))
            obj = stationery.objects.get(id=id)
            obj.stock_num = obj.stock_num + purs.num
            obj.save()
    purchase_master.objects.filter(entryid=entryid).update(pur_status='submitted')
    del request.session['entryid']
    return HttpResponseRedirect('pur_index')


@csrf_exempt
def add_pur_master(request):
    if request.method == 'POST':
        entryid = request.POST.get('entryid')
        user_id = request.POST.get('user_id')
        stat_types = stat_type.objects.all()
        pur_historys = purchase_master.objects.filter(pur_status='submitted').order_by('-date')[:8]
        try:
            pur_masters = purchase_master.objects.filter(entryid=entryid, pur_status='submitted')
            pur_masters_entering = purchase_master.objects.filter(entryid=entryid, pur_status='entering')
            if pur_masters.exists():
                msg = '** 无效的入库单编号“%s”，请重新输入！ **' % (entryid)

                return render(request, 'stationery/purchase_index.html', locals())

            elif pur_masters_entering.exists():
                request.session['entryid'] = entryid
                msg = 'have a not submiting order'

                return render(request, 'stationery/purchase_index.html', locals())

            else:
                purchase_master.objects.create(date=datetime.datetime.now().strftime('%Y-%m-%d'), provider_id=1,
                                               user_id=user_id, entryid=entryid)
                request.session['entryid'] = entryid
                return render(request, 'stationery/purchase_index.html', locals())
        except:
            msg = 'error, please check and input again'
            return render(request, 'stationery/purchase_index.html', locals())


@csrf_exempt
def upload_img(request):
    if request.method == 'GET':
        stat_id = request.GET.get('stat_id')
        request.session['stat_id'] = stat_id
        print(stat_id)
    context = {}
    if request.method == 'POST':
        file_content = ContentFile(request.FILES['stat_img'].read())
        imgfiles = request.FILES.get('stat_img')
        img = stationery(stat_img=request.FILES.get('stat_img'))
        img.save(imgfiles)
        stat_id = request.session.get('stat_id')
        stationery.objects.filter(id=stat_id).update(stat_img=request.FILES.get('stat_img'))
    return render(request, 'stationery/upload_img.html', locals())


def layer(request):
    return render(request, 'stationery/layer.html', locals())


def ajax_stat_increase(request):
    id = request.GET.get('id')
    orderid = request.GET.get('orderid')
    # 相应ID的文具数量加1，更新数据库
    res = order_record_slave.objects.get(id=id)
    res.order_num = res.order_num + 1
    res.save()
    ##将有相同订单号orderid 的所有文具列出来，以json格式反回给前端的ajax函数stat_increase
    stats = order_record_slave.objects.filter(order_record_master_id=orderid).values('id', 'stationery__name',
                                                                                     'order_num')
    ret = list(stats)
    result = json.dumps(ret)
    print(result)
    return HttpResponse(result, "application/json")


def ajax_stat_decrease(request):
    id = request.GET.get('id')
    orderid = request.GET.get('orderid')
    res = order_record_slave.objects.get(id=id)
    ## 如果申请领用的文具数量大于1，则减去1，
    if (res.order_num > 1):
        res.order_num = res.order_num - 1
        res.save()
        ##将有相同订单号orderid 的所有文具列出来，以json格式反回给前端的ajax函数stat_decrease
        stats = order_record_slave.objects.filter(order_record_master_id=orderid).values('id', 'stationery__name',
                                                                                         'order_num')
        ret = list(stats)
        result = json.dumps(ret)
        print(result)
        return HttpResponse(result, "application/json")


def ajax_stat_remove(request):
    id = request.GET.get('id')
    orderid = request.GET.get('orderid')
    order_record_slave.objects.filter(id=id).delete()

    ##将有相同订单号orderid 的所有文具列出来，以json格式反回给前端的ajax函数stat_decrease
    stats = order_record_slave.objects.filter(order_record_master_id=orderid).values('id', 'stationery__name',
                                                                                     'order_num')
    ret = list(stats)
    result = json.dumps(ret)
    print(result)
    return HttpResponse(result, "application/json")

def purchase_details(request):
    entryid=request.GET.get('entryid')
    #request.session['entryid']=entryid
    pur_masters=purchase_master.objects.filter(entryid=entryid)
    pur_slaves=purchase_slave.objects.filter(entryid=entryid)
    return render(request,'stationery/purchase_details.html',{'pur_masters':pur_masters,'pur_slaves':pur_slaves})