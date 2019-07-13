from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from deviceman.models import user_list, dept_list, pc_list, borrows,site,bl_list,adm_info,adm_site, operation_log, User,repair_record
from django.db.models import Q,F,Count
from django.db.models.functions import Concat
from django.db.models import Value
from datetime import datetime, time,timezone
from deviceman.form import UserModelForm, PcModelForm,borrowsModelForm,SiteModelForm,Bl_listModelForm,Dept_listModelForm, Adm_infoModelForm,AdmSiteModelForm, RepairrecordModelForm, Transfer_pcModelForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import random
from deviceman.tables import pc_listTable,User_listTable,siteTable,bl_listTable,Dept_listTable,adm_infoTable,user_Table2,adm_siteTable,operation_log_Table,repair_record_Table2
from django.contrib import messages
from table.views import FeedDataView
import json , pickle
#from dal import autocomplete
from django.urls import reverse,reverse_lazy
from django_tables2 import RequestConfig



def update_device_log(pc_list_id, user_list_id, operation_type_id, op_time=str(datetime.now().date()), op_content='--', user_id=''):
    operation_log.objects.create(pc_list_id=pc_list_id,user_list_id=user_list_id,operation_type_id=operation_type_id,op_time=op_time,op_content=op_content, User_id=user_id)
    print('add a record to the device log table')
    return '1'



def get_site_list(request):


    r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
    # 判断是否在redis server中存在 hash 'sitedict' 如果存在就读取出来
    if r.hlen(name='sitedict'):
        hsitedict = r.hgetall(name='sitedict')
        ##从redis读出hash  'sitedict',  通过for 循环，把结果转换成[{id: 'idxx',sitename: 'sitenamexxx'},{   }.....]格式
        hsitelist = []
        for i in hsitedict:
            hsitelist.append({'id': i, 'sitename': hsitedict[i]})

    #  如果redis server中不存在 hash 'sitedict' ,
    else:
        if request.user.adm_info.system_adm:
            sites=site.objects.all().values('id','sitename').order_by('id')
        else:
            user_id=request.session.get('current_user_id')
            sites=adm_site.objects.filter(User_id=user_id).values('site_id').annotate(id=F('site__id'),sitename=F('site__sitename')).order_by('id')

        for siteo in sites:
            r.hset(name='sitedict',key=siteo['id'],value=siteo['sitename'])



    #print('hsitedict is ',hsitedict)
    #print(hsitelist)

    #ret = list(sites)

    ret=list(hsitelist)
    result = json.dumps(ret)
    print(result)

    #result=[]


   

    #r.set('mydict', hsite)

    # read_dict = r.get('mydict')
    # yourdict = pickle.loads(read_dict)
    # print('yourdict is ',yourdict)


    return HttpResponse(result, "application/json")



#from table.columns import LinkColumn, Link
#from table.utils import A
#import django_tables2

def testdb(request):
    user1=user_list(user_name='liuzh',full_name='Liu, Zhehao', email_address='zhehao.liu@aecom.com',dept_no='dept03')
    user1.save()
    return HttpResponse('user数据添加成功！')

def t_dept_list(request):
    dept1=dept_list(dept_id='dept22',dept_name='test',dept_leader='liuhonghai')
    dept1.save()
    return HttpResponse('dept数据添加成功！')

@csrf_exempt
def get_user(request):

    id=request.POST.get('id',)
    if id=='':
        print('Null')
    else:
        #users=user_list.objects.filter(id=id)
        users = user_list.objects.filter(dept_list__dept_name__icontains=id,)
        return render(request,'hello.html',{'users':users,'i':10, 'id':id})
       # return HttpResponse(users)

@csrf_exempt
@login_required(login_url='/account/login')
def display_user(request):
    current_site=request.session.get('current_site')
    objs=site.objects.get(id=current_site)
    officename=objs.officename
    #user_lists=User_listTable(user_list.objects.all())

    user_lists=User_listTable(user_list.objects.filter( dept_list__dept_name__icontains=officename, user_status='active'))

    return render(request,'display_user.html',{'user_lists':user_lists, 'm':'um'})

@csrf_exempt
@login_required(login_url='/account/login')
def display_pc(request,id):
    # siteid=request.user.adm_info.site_id
    request.session['hosttype_id']=id
    #sites=get_site_list()
    # print('site id is ', siteid)
    # if id==1:
    #     pc_lists = pc_listTable(pc_list.objects.filter((Q(hosttype=1) | Q(hosttype=2) | Q(hosttype=3)) & Q(site_id=siteid)))
    # else:
    pc_lists = pc_listTable(pc_list.objects.all())


    return render(request, 'display_pc.html', {'pc_lists': pc_lists,'m':'dm'})
    #return render(request, 'display_pc.html', )

@csrf_exempt
@login_required(login_url='/account/login')
def borrow_pc(request,id):

    request.session['hosttype_id']=id
    request.session['operation_type']='borrow_pc'


    pc_lists = Borrow_pcTable(pc_list.objects.all())


    return render(request, 'borrow_pc.html', {'pc_lists': pc_lists})
    #return render(request, 'display_pc.html', )


@csrf_exempt
@login_required(login_url='/account/login')
def devicelog(request):
    device_op_logs = operation_log_Table(operation_log.objects.filter())

    return render(request, "devicelog.html",
                  {'device_op_logs': device_op_logs, 'modelname': 'Device Log'})




class pcDataView(FeedDataView):
       token = pc_listTable.token
       def get_queryset(self):
            #site_id=self.request.user.adm_info.site_id
            site_id=self.request.session.get('current_site')
            if self.request.session.get('hosttype_id') ==1:
                # if the operation type is borrow PC/device , return the inventory pc/device to the front page
                if self.request.session.get('operation_type')=='borrow_pc':
                    del self.request.session['operation_type']
                    return super(pcDataView, self).get_queryset().filter(
                        Q(site_id=site_id) & (Q(hosttype=1) | Q(hosttype=2) | Q(hosttype=3))&Q(user_list_id=180).exclude(host_status='disposed'))


                else:
                    print('hosttype_id '+str(self.request.session.get('hosttype_id')))
                    return super(pcDataView, self).get_queryset().filter(Q(site_id=site_id) & (Q(hosttype=1) | Q(hosttype=2) | Q(hosttype=3)) ).exclude(host_status='disposed')


           # if hosttype_id !=1, retuan the relate pc/device  to front page
            else:
                print('hosttype_id ' + str(self.request.session.get('hosttype_id')))
                return super(pcDataView, self).get_queryset().filter(
                    Q(site_id=site_id) & (Q(hosttype=self.request.session.get('hosttype_id'))))















def resign(request,id):

    pcs=pc_list.objects.filter(id=id)
    for users in pcs:
        full_name=users.user_list.full_name
        user_id=users.user_list_id
        host_name=users.host_name
        op_user=request.user.id

        us=user_list.objects.filter(id=user_id).update(resigndate=str(datetime.now().date()), user_status='inactive')
        pcs=pc_list.objects.filter(id=id).update(user_list_id='180', host_status='inventory')
        update_device_log(id, user_id, 7, str(datetime.now().date()), 'user resign, collect device ' + host_name, op_user)


    messages.info(request,'用户：'+full_name+' 的状态已经被设置为inactive，计算机： '+host_name+' 的使用人已经被设置为NA，状态为 Inventory！')
    return HttpResponseRedirect('/deviceman/userdetailtable2/'+str(user_id)+'/')



def dispose(request,id):

    pcs=pc_list.objects.filter(id=id)
    for users in pcs:
        full_name=users.user_list.full_name
        user_id=users.user_list_id
        host_name=users.host_name

        op_user=request.user.id
        pc_list.objects.filter(id=id).update(user_list_id='193', host_status='P-Dispose', seat_no='14000')

        update_device_log(id, user_id, 6, str(datetime.now().date()), 'apply to dispose asset ' + host_name, op_user)

        messages.info(request, host_name+' 的使用人已经被设置为PFD14，状态为 P-Dispose！')
    return HttpResponseRedirect('/deviceman/pcedit/'+id+'/')

def recallpc(request,id):

    pcs=pc_list.objects.filter(id=id)
    for users in pcs:
        full_name=users.user_list.full_name
        user_id=users.user_list_id
        host_name=users.host_name
        op_user=request.user.id
        borrows_query=borrows.objects.filter(pc_list_id=id, rdate='2000-01-01')
        if borrows_query:
            return HttpResponseRedirect('/deviceman/ajax_return_pc?pcid='+str(id) +'&user_list_id=' +str(user_id) )

        else:
            pcs = pc_list.objects.filter(id=id).update(user_list_id='180', host_status='Inventory', seat_no='14000')
            update_device_log(id, user_id, 7, str(datetime.now().date()), 'collect device from user '+full_name, op_user)

    messages.info(request, host_name+' 的使用人已经被设置为NA，状态为 Inventory！')

    return HttpResponseRedirect('/deviceman/pcedit/'+id+'/')





@csrf_exempt
def get_username_from_pcid(pcid):
    #pcid = request.GET.get('id', )
    pclist= pc_list.objects.filter(id=pcid)
    for pcs in pclist:
        userid=pcs.user_list_id
        userlist = user_list.objects.filter(id=userid)
        for users in userlist:
            username = users.full_name
    return username

def newdevice(request):
    context={}
    context['pcid']=request.GET.get('pcid')
    request.session['ifnew'] = 'Yes'
    return render(request, 'newdevice.html', context,)


def usercreate(request):
    if request.method == "GET":
        obj = UserModelForm(request=request)
        return render(request, "usercreate.html", {'obj': obj})
    elif request.method == "POST":
        obj = UserModelForm(request.POST, request=request)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            save_status="用户信息已经成功创建"
        else:
            print(obj.errors.as_json())
            save_status='出错，请检查你输入的信息!!!!'
    return render(request, "usercreate.html", {'obj': obj,'status':save_status})



# def transforcreate(request, id):
#     if request.method == "GET":
#         #pcs=pc_list.objects.get(id=id)
#         obj = Transfor_logModelForm(request=request,id=id)
#         return render(request, "transforcreate.html", {'obj': obj})
#     elif request.method == "POST":
#         obj = Transfor_logModelForm(request.POST,request=request)
#         print(obj.is_valid())  # 这是方法，别忘记了加括号
#         print(obj.cleaned_data)
#         print(obj.errors)
#         if obj.is_valid():
#             obj.save()
#             save_status="用户信息已经成功创建"
#         else:
#             print(obj.errors.as_json())
#             save_status='出错，请检查你输入的信息!!!!'
#     return render(request, "transforcreate.html", {'obj': obj,'status':save_status})
#




@csrf_exempt
@login_required(login_url='/account/login')
def pccreate(request):
    if request.method == "GET":
        obj = PcModelForm(request=request)
        return render(request, "newdevice.html", {'obj': obj, 'acton': 'pccreate', 'modelname': '-新建设备'})
    elif request.method == "POST":
        obj = PcModelForm(request.POST, request=request)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return render(request, "newdevice.html", {'obj': obj, 'acton': 'pccreate', 'modelname': '-新建设备'})

@csrf_exempt
@login_required(login_url='/account/login')
def pcedit(request, pcid):
    pcobj = pc_list.objects.get(id=pcid)
    print('pcobj is ',pcobj)
    CURRENT_USER_ID=request.user.id
    if request.method=='GET':
        officename = request.session.get('officename')
        print('office is ', officename)
        # PcModelForm.fields['user_list'].queryset=user_list.object.filter(dept_list__dept_name__icontains=officename)
        #pcobj = pc_list.objects.get(id=pcid)
        obj = PcModelForm(instance=pcobj, request=request)


    if request.method == 'POST':
        obj = PcModelForm(request.POST, instance=pcobj, request=request)
        hosttype_id = request.session.get('hosttype_id',None)
        print('hosttype_id is',hosttype_id)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)

        print(obj.errors)
        if obj.is_valid():
            user_list_id =obj.data['user_list']

            obj.save()
            update_device_log(pcid, user_list_id, 2, str(datetime.now().date()),'update the device information', CURRENT_USER_ID)
            print(pcid)
            messages.info(request,obj.data.get('host_name') +'保存成功！')

            return HttpResponseRedirect('/deviceman/display_pc/'+str(hosttype_id)+'/')
        else:
            print(obj.errors.as_json())

    device_op_logs = operation_log_Table(operation_log.objects.filter(pc_list_id=pcid))

    return render(request, "pcedit.html", {'obj': obj, 'device_op_logs':device_op_logs,'acton': 'pcedit', 'modelname': '-编辑设备','pcid':pcid})


@csrf_exempt
@login_required(login_url='/account/login')
def useredit(request, id):

    userobj = user_list.objects.get(id=id)
    if request.method == 'GET':
        obj = UserModelForm(instance=userobj, request=request)

    if request.method == 'POST':
        obj = UserModelForm(request.POST, instance=userobj,request=request)  #
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        #obj.cleaned_data['dept_name']=obj.cleaned_data['dept_name']+' - '+request.user.adm_info.site.officename
        print(obj.errors)
        if obj.is_valid():
            #dept_name=
            #print(obj.cleaned_data.get('dept_name'))

            obj.save()
            messages.info(request,obj.data.get('full_name') +'保存成功！')
            return HttpResponseRedirect('/deviceman/display_user')
        else:
            print(obj.errors.as_json())
    return render(request, "useredit.html", {'obj': obj, 'acton': 'useredit', 'modelname': '-编辑user', 'id': id})
    #print(obj)
    #nexturl=request.session.get(request.path)




@csrf_exempt
def borrowscreate(request,id):
    if request.method == "GET":
        request.session['current_pcid']=id
        #print('pcid is ',pcid)
        obj = borrowsModelForm()
        obj.fields['pc_list'].initial=id
        obj.fields['pc_list'].queryset=pc_list.objects.filter(id=id)
        obj.fields['bdate'].initial=datetime.now().date()
        obj.fields['User'].initial=request.user.id
        obj.fields['User'].queryset = User.objects.filter(id=request.user.id)
        #obj=borrowsModelForm()
        return render(request, "borrowpc.html", {'obj': obj, 'acton': 'borrowscreate', 'modelname': '-borrow设备'})
    elif request.method == "POST":
        obj = borrowsModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        CURRENT_USER=request.user
        CURRENT_USER_ID=CURRENT_USER.id
        print('CURRENT USER ID IS ',CURRENT_USER_ID)
        if obj.is_valid():
            print(obj.data['pc_list'])
            print(obj.data['User'])

            pc_list_id=obj.data['pc_list']
            user_list_id=obj.data['user_list']
            full_names=user_list.objects.filter(id=user_list_id).values('full_name')
            full_name=full_names[0].get('full_name')

            pc_list.objects.filter(id=pc_list_id).update(user_list_id=user_list_id, host_status='in use')

            obj.save()
            update_device_log(pc_list_id, user_list_id, 3, str(datetime.now().date()),
                              full_name+' borrow asset from IT', CURRENT_USER_ID)
            return HttpResponseRedirect("/deviceman/userdetailtable2/" + user_list_id + '/')
        else:
            print(obj.errors.as_json())
            return HttpResponse(obj.errors.as_json())





def createrep_record(request,id):
    user_lists = pc_list.objects.filter(id=id).values('user_list_id')
    user_list_id = user_lists[0].get('user_list_id')
    if request.method=='GET':
        request.session['current_pcid'] = id

        # print('pcid is ',pcid)
        objs = RepairrecordModelForm(request=request)
        objs.fields['User'].initial = request.user.id
        objs.fields['User'].queryset = User.objects.filter(id=request.user.id)

    if request.method=='POST':
        objs=RepairrecordModelForm(request.POST, request=request)
        print(objs.is_valid())  # 这是方法，别忘记了加括号
        print(objs.cleaned_data)
        print(objs.errors)
        CURRENT_USER = request.user
        CURRENT_USER_ID = CURRENT_USER.id
        print('CURRENT USER ID IS ', CURRENT_USER_ID)
        if objs.is_valid():
            objs.save()
            update_device_log(id,user_list_id,9,datetime.now().time(),'starting the repairing on the computer',request.user.id)
    return render(request,'repair_record.html',{'objs':objs})


def showrepair_record(request,id):
    table = repair_record_Table2(repair_record.objects.filter(pc_list_id=id))
    RequestConfig(request).configure(table)
    return render(request,'showrepair_record.html',{'table':table})



# this is returnpc on Url

def ajax_return_pc(request):
    pcid = request.GET.get('pcid')
    user_list_id=request.GET.get('user_list_id')
    full_names=user_list.objects.filter(id=user_list_id).values('full_name')
    full_name=full_names[0].get('full_name')
    if pcid != None:
        return_status=borrows.objects.filter(Q(pc_list_id=pcid)&Q(rdate='2000-01-01')).update(rdate=datetime.now().date())
        pc_update_status=pc_list.objects.filter(id=pcid).update(user_list_id=180, host_status='inventory')

        if return_status:

            op_user=request.user.id

            #print('current user is ', str(op_user))
            update_device_log(pcid, user_list_id,4, str(datetime.now().date()),full_name+' return asset to IT', op_user)

            data = {'state': "Computer has been returned"}

        else:

            data = {'state': "Computer return failed"}


    result=json.dumps(data)

    return HttpResponse(result,"application/json")





@login_required(login_url='/account/login')
def report(request):
    context={'m':'rp'}
    return render(request, 'report.html',context)

@csrf_exempt
def planmap(request):
    if request.method=="GET":
        seatno=request.GET.get("seatno")
        pcs=pc_list.objects.filter(seat_no=seatno)
        return render(request,"map.html",{'pcs': pcs,'seatno':seatno})
    else:
        if request.method=='POST':
            seatno=request.POST.get("seatno")
            pcs={}
            pcs = pc_list.objects.filter(seat_no=seatno)
            #return render(request, "map.html", {'pcs': pcs, 'seatno': seatno})
    return render(request, "map.html", {'pcs': pcs, 'seatno': seatno})

@csrf_exempt
def gps(request):
    seatno = request.GET['seatno']
    #pcs = pc_list.objects.filter(seat_no=seatno)
    return HttpResponse(seatno)

def userdetail(request,id):

    #返回用户ID相匹配的用户记录
    userdetails = User_listTable(user_list.objects.filter(id=id))

    #userdetails.OP.links = [Link(text=u'test', viewname='userdetail', args=(A('id'),)), ]
    #列出这个用户使用的电脑记录
    pcs=pc_list.objects.filter(user_list_id=id)

    # for pc in pcs:
    #     pcid=pc.id
     #列出这个用户借用的物品
    borws=borrows.objects.filter(user_list_id=id, rdate='2000-01-01')
    modelname='用户信息'
    rand_num=random.randint(1000, 9999)
    request.session['op_rand_num']=rand_num
    return render(request,'userdetail.html', locals())

##udate the pc information use ajax, user resign from the company, udate the user_list_id to 180, status to inventory,update remark
def ajax_update_pc(request):
    if request.method == 'GET':
        pc_id = request.GET.get('id', None)
        user_list_id = request.GET.get('user_list_id')
        print('get pc_id from ajax "%s"'%(pc_id))
        if pc_id:
            pc_list.objects.filter(id=pc_id).update(user_list_id='180', host_status='inventory')
            data={'state':"Computer information has been sucessfully updated"}
            #data = list(pc_list.objects.filter(user_list_id=user_list_id).values("id", "host_name","service_tag","hosttype"))
            #data.append(data1)
            result=json.dumps(data)
            print(result)
    return HttpResponse(result, "application/json")


##udate the pc information use ajax, disposed the pc  f, udate the user_list_id to 180, status to disposed,update remark
def ajax_disposed_pc(request):
    if request.method == 'GET':
        pc_id = request.GET.get('id', None)
        user_list_ids=pc_list.objects.filter(id=pc_id).values('user_list_id','host_name')
        user_list_id=user_list_ids[0].get('user_list_id')
        host_name = user_list_ids[0].get('host_name')
        print('host_name is is '+host_name)
        #user_list_id = request.GET.get('user_list_id')
        print('get pc_id from ajax "%s"'%(pc_id))
        if pc_id:
            pc_list.objects.filter(id=pc_id).update(user_list_id='193', host_status='disposed',asset_code=0)
            update_device_log(pc_id, user_list_id,8,datetime.now().time(),'disposed device '+ host_name, request.user.id)
            data={'state':"Computer has been disposed"}
            #data = list(pc_list.objects.filter(user_list_id=user_list_id).values("id", "host_name","service_tag","hosttype"))
            #data.append(data1)
            result=json.dumps(data)
            print(result)
    return HttpResponse(result, "application/json")

#receive the data from cli that run on the user machine
def cli_update(request, **kwargs):
    if request.method == 'GET':
        username = kwargs['username']
        full_name = kwargs['full_name']
        email_address = kwargs['email_address']
        host_name = kwargs['host_name']
        macadd = kwargs['macadd']
        seat_no = kwargs['seat_no']


        ### begin to process the user record
        users=user_list.objects.filter(user_name=username)
        #if the record is exists on the database?
        if users.exists():
            for user in users:
                user_list_id=user.id
                # found the user record, update the lastupdate field
                user_list.objects.filter(id=user_list_id).update(lastupdate=str(datetime.now().date()))
                print('found the user_list id: '+str(user_list_id))
                data={'state':'found the record of the user '+full_name+' on database'}
        else:
            # not found the record, create it
            user_list.objects.create(user_name=username,full_name=full_name,email_address=email_address,regdate=str(datetime.now().date()),dept_list_id=23, lastupdate=str(datetime.now().date()))
            data = {'state': "not found record of the user, created it"}
        ### end of process the user record

        ### begin to process the PC record

        users = user_list.objects.filter(user_name=username)
        if users.exists():
            for user in users:
                user_list_id=user.id
        pcs=pc_list.objects.filter(host_name=host_name)
        if pcs.exists():
            if seat_no == '1':
                pc_list.objects.filter(host_name=host_name).update(user_list_id=user_list_id, host_status='in use',
                                                                   mac=macadd)
            else:
                pc_list.objects.filter(host_name=host_name).update(user_list_id=user_list_id, host_status='in use',
                                                                   mac=macadd, seat_no=seat_no)

        result=json.dumps(data)
        print(result)
    return HttpResponse(result, "application/json")





#

@csrf_exempt
@login_required(login_url='/account/login')
def sitecreate(request):
    sites = siteTable(site.objects.all())
    if request.method == "GET":
        obj = SiteModelForm()
        #sites = siteTable(site.objects.all())
        return render(request, "sitecreate.html", {'obj': obj, 'sites':sites,'acton': 'sitecreate', 'modelname': 'sitecreate'})
    elif request.method == "POST":
        obj = SiteModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return HttpResponseRedirect('sitecreate')


@csrf_exempt
@login_required(login_url='/account/login')
def blcreate(request):
    bls = bl_listTable(bl_list.objects.all())
    if request.method == "GET":
        obj = Bl_listModelForm()
        #sites = siteTable(site.objects.all())
        return render(request, "blcreate.html", {'obj': obj, 'bls':bls,'acton': 'blcreate', 'modelname': 'blcreate'})
    elif request.method == "POST":
        obj = Bl_listModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return HttpResponseRedirect('blcreate')

@csrf_exempt
@login_required(login_url='/account/login')
def deptcreate(request):
    officename=request.session.get('officename')
    bls = Dept_listTable(dept_list.objects.filter(dept_name__icontains=officename))
    if request.method == "GET":
        obj = Dept_listModelForm()
        #sites = siteTable(site.objects.all())
        return render(request, "deptcreate.html", {'obj': obj, 'bls':bls,'acton': 'deptcreate', 'modelname': 'deptcreate'})
    elif request.method == "POST":
        mutable = request.POST._mutable
        request.POST._mutable = True
        obj = Dept_listModelForm(request.POST)
        print(obj.data['dept_name'])
        obj.data['dept_name'] = obj.data['dept_name'] +  ' - ' + officename
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)


        if obj.is_valid():

            #obj.data['dept_name'] = request.user.adm_info.site.officename
            obj.save()
            obj.data['dept_name'] = ''
            request.POST._mutable = mutable

            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return HttpResponseRedirect('deptcreate')

@csrf_exempt
@login_required(login_url='/account/login')
def adm_infocreate(request):
    bls = adm_infoTable(adm_info.objects.all())
    if request.method == "GET":
        obj = Adm_infoModelForm()
        #sites = siteTable(site.objects.all())
        return render(request, "adm_infocreate.html", {'obj': obj, 'bls':bls,'acton': 'adm_infocreate', 'modelname': 'adm_infocreate'})
    elif request.method == "POST":
        obj = Adm_infoModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return render(request, "adm_infocreate.html",
                  {'obj': obj, 'bls': bls, 'acton': 'adm_infocreate', 'modelname': 'adm_infocreate'})


@csrf_exempt
@login_required(login_url='/account/login')
def SitePermissionCreate(request,id):
    request.session['User_id']=id
    admsitetbls = adm_siteTable(adm_site.objects.filter(User_id=id))
    if request.method == "GET":
        obj = AdmSiteModelForm()

        return render(request, "adm_sitecreate.html", {'obj': obj, 'bls':admsitetbls,'acton': 'adm_sitecreate', 'modelname': 'adm_sitecreate'})
    elif request.method == "POST":
        obj = AdmSiteModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            messages.info(request, '保存成功！')
        else:
            print(obj.errors.as_json())
    return render(request, "adm_sitecreate.html",
                  {'obj': obj, 'bls': admsitetbls, 'acton': 'adm_sitecreate', 'modelname': 'adm_sitecreate'})





# below is the testing code for django-tables2
#from django_tables2 import RequestConfig
def userdetailtable2(request,id):
    table = user_Table2(user_list.objects.filter(id=id))
    RequestConfig(request).configure(table)
    pcs = pc_list.objects.filter(user_list_id=id).exclude(borrows__user_list_id=id)

    # for pc in pcs:
    #     pcid=pc.id
    # 列出这个用户借用的物品
    borws = borrows.objects.filter(user_list_id=id, rdate='2000-01-01')
    modelname = '用户信息'
    rand_num = random.randint(1000, 9999)
    request.session['op_rand_num'] = rand_num
    return render(request,'userdetail.html',{'table':table,'id':id,'pcs':pcs,'borws':borws, 'modelname':modelname})

def newuserman(request):

    dept_list_id=23     #the deptid of new reg user defaultly was set to 23  AECOM new staff
    current_site=request.session.get('current_site')
    new_user_list=user_list.objects.filter(dept_list_id=dept_list_id, user_status='active')
    users=[]
    for user in new_user_list:
        users.append(user.id)
    print(users)

    new_user_pcs=pc_list.objects.filter(user_list_id__in=users,site_id=current_site)
    print(new_user_pcs)
    userids=[]
    for new_user_pc in new_user_pcs:
        userids.append(new_user_pc.user_list_id)
    print(userids)
    #site_new_reg_users_ids=pc_list.objects.filter(id__in=pcs)
    #user_list_ids=pc_list_of_new_user('user_list_id')



    user_lists = User_listTable(user_list.objects.filter(id__in=userids))
    return render(request, 'newuserman.html', {'user_lists': user_lists})

def ajax_switch_site(request):
    id=request.GET.get('id')
    request.session['current_site'] = id
    if id == '0':
        sitename='ALL'
        officename='ALL'

    else:
        obj=site.objects.get(id=id)
        sitename=obj.sitename
        officename=obj.officename
        print("site name is :"+sitename)
    data = {'id': id, 'sitename': sitename}
    request.session['site_name']=sitename
    request.session['officename']=officename
    result = json.dumps(data)
    print(result)
    return HttpResponse(result, "application/json")


def ajax_get_user_list(request):
    """
    AJAX数据源视图-系统模块
    """
    start = int(request.GET.get('iDisplayStart', '0'))
    length = int(request.GET.get('iDisplayLength', '30'))
    search = request.GET.get('search', '')
    current_office=request.session.get('officename')
    #取得前台控件输入的关键字
    if search:
    #截取查询结果对象，以start开始截取start+length位
        orgs = user_list.objects.filter(   (Q(full_name__icontains=search) | Q ( email_address__icontains=search))&Q(dept_list__dept_name__icontains=current_office)).values('id').annotate(text=F('full_name')).exclude(user_status='inactive')
    else:
        orgs = user_list.objects.all().values('id').annotate(text=F('full_name'))

    # val_list = []
    # for org in orgs:
    #     val_list.append({'id': org.id, 'text': org.full_name})
    #     #根据关键字查询得到结果后开始拼装返回到前台的数据。先生成字典型数组，一般SELECT2组件使用的话生成id、name两个字段即可
    ret=list(orgs)
    result = json.dumps(ret)
    return HttpResponse(result)



def pc_transfer(request,pcid):
    pc_list_id=pcid
    pcs=pc_list.objects.filter(id=pc_list_id).values('site_id','site__sitename')
    #print(pcs)
    # get the current site id and site name of the Asset
    site_id=pcs[0].get('site_id')
    sitename=pcs[0].get('site__sitename')
    #print('site_id is ', site_id)
    #currente_site=request.session.get('current_site')

    if request.method=='GET':
        obj=Transfer_pcModelForm()
        #set the initial of the seletion to the current asset
        obj.fields['pc_list'].initial =pcid
        obj.fields['pc_list'].queryset=pc_list.objects.filter(id=pcid)
        #set the initial of the site to the current site
        obj.fields['source_site'].initial=site_id
        obj.fields['source_site'].queryset=site.objects.filter(id=site_id)
        # get the site list excluded the current site
        obj.fields['dest_site'].queryset = site.objects.all().exclude(id=site_id)

        #set the date to today
        obj.fields['transfer_date'].initial=datetime.now().date()
        #set the operation IT name to the logined IT
        obj.fields['User'].initial=request.user.id
        obj.fields['User'].queryset=User.objects.filter(id=request.user.id)
        return render(request,'transferpc.html', {'obj':obj})
    if request.method=='POST':
        obj = Transfer_pcModelForm(request.POST)
        print(obj.is_valid())  # 这是方法，别忘记了加括号
        print(obj.cleaned_data)
        print(obj.errors)
        if obj.is_valid():
            obj.save()
            pc_list.objects.filter(id=obj.data['pc_list']).update(site_id=obj.data['dest_site'])
            users=pc_list.objects.filter(id=obj.data['pc_list']).values('user_list_id')
            print('computer user is ',users)
            u_id=list(users)
            print('u_id is ', u_id)
            print(u_id[0].get('user_list_id'))
            dest_site_names=site.objects.filter(id=obj.data['dest_site']).values('sitename')
            dest_site_name=dest_site_names[0].get('sitename')
            remark=obj.data['remark']
            update_device_log(obj.data['pc_list'],u_id[0].get('user_list_id'),5,datetime.now().date(),'transfer asset from '+sitename+' to '+ dest_site_name+', '+remark,request.user.id)
            messages.info(request, '资产转移成功！')
        else:
            print(obj.errors.as_json())
        return HttpResponseRedirect('/deviceman/pctransfer/'+str(pcid)+'/')






def testcount(request):
        select_data = {"receive_month": 'extract(month from receive_date )'}
        #print(datetime.now().year)
        ret=[]
        for i in range(datetime.now().year-5, datetime.now().year+1):
            print(i)
            select_data = {str(i)+"receive_month": 'extract(month from receive_date )'}
            res=pc_list.objects.filter(receive_date__year=i, site_id=2).extra(select=select_data).values(str(i)+'receive_month').annotate(count=Count('id')).order_by(str(i)+'receive_month')

            ret.extend(list(res))

            # res = pc_list.objects.filter(receive_date__year=2006).extra(select=select_data).values('receive_date').annotate(
            #     count=Count('id')).order_by('receive_date')


        result=json.dumps(ret)
        return HttpResponse(result)

import redis
def redistest(request):
    result=[]
    r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)

    # ss=site.objects.all().values('id','sitename')
    #
    #
    # for s in ss:
    #    k= s.get('id')
    #    v=s.get('sitename')
    #    r.hset(name='h1',key=k,value=str(v))

    #
    #print(result)
    hall=r.hgetall(name='h1')
    return render(request,'redistest.html',{'result':result,'hall':hall})
