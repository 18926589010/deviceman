from django.db import connection
from django.http import HttpResponse
from django.template import loader
from pyecharts import Bar, Pie
from django.contrib.auth import  authenticate, login, logout

from deviceman.models import pc_list
from django.db.models import Count, Sum
from datetime import datetime
import redis


def get_device_total(request):
    siteid = request.session.get('current_site')
    r=redis.StrictRedis(host='localhost',port=6379, decode_responses=True)
    device_total=[]
    w_total=r.get(name='workstation_total_'+siteid)
    device_total.append({'workstation_total':w_total})
    l_total=r.get(name='laptop_total_'+siteid)
    device_total.append({'laptop_total':l_total})
    d_total=r.get(name='desktop_total_'+siteid)
    device_total.append({'desktop_total':d_total})
    print('device_total is ', device_total)
    return device_total



REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def exc_sql(sql):

    cursor = connection.cursor()

    cursor.execute(sql)

    result = cursor.fetchall()

    return result

def totalchart(request):

    template = loader.get_template('deviceman/pyecharts.html')

    device_t=get_device_total(request)



    b=wbar(request)
    c=bar(request)
    d=lbar(request)
    e=dbar(request)
    f=sbar(request)
    g=swbar(request)
    h=rbar(request)
    p=piebar(request)
    monthpc=monthpcbar(request)
    yearpc=yearpcbar(request)


    context = dict(
        device_total=device_t,
        myechart=b.render_embed(),
        wmyechart=c.render_embed(),
        lmyechart=d.render_embed(),
        dmyechart=e.render_embed(),
        smyechart=f.render_embed(),
        swmyechart=g.render_embed(),
        rmyechart=h.render_embed(),
        pmyechart=p.render_embed(),
        monthechart=monthpc.render_embed(),
        yearechart=yearpc.render_embed(),

        host=REMOTE_HOST,

        script_list=b.get_js_dependencies()

    )

    return HttpResponse(template.render(context, request))

def bar(request):
    site_id = request.session.get('current_site')
    #_data = []

    query_sql = "select h.name,count(*) from deviceman_pc_list as p,deviceman_hosttype as h where h.id=p.hosttype_id and p.site_id='%s' and h.id in (1,2,3,4) and p.host_status!='disposed' group by hosttype_id"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
   # x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
   # y = [10,20,30]
    #_data.append()

    bar=Bar("设备分类",width='100%',height=300)

    bar.add("数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")



    return bar


def monthpcbar(request):
    site_id = request.session.get('current_site')

    x = []
    y = []
    for i in range(datetime.now().year - 4, datetime.now().year + 1):
         #print(i)
         select_data = {"receive_month": 'extract(month from receive_date )'}
         res = pc_list.objects.filter(receive_date__year=i, site_id=site_id, hosttype_id__in=[1,2,3]).exclude(host_status='disposed').extra(select=select_data).values(
            'receive_month').annotate(count=Count('id')).order_by('receive_month')


         #print(res)
         for re in res:

             
             x.append(str(i)+'-'+str(re['receive_month']))

             y.append(re['count'])
         #x=[i[0] for i in res]
         #print(x)
    #x = ['sz','bj','gz']
   #
         #y=[i[1] for i in res]
         #print(y)
    #y = [10,20,30]
   #  #_data.append()

    bar=Bar("Computers Per Month",width='100%',height=500)
    #bar.use_theme('dark')
    #
    bar.add("数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,
    #
            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",
    #
             bar_normal_color="#0000ff", bar_emphasis_color="#0000ff",xaxis_rotate=40)
    #


    return bar



def yearpcbar(request):
    site_id = request.session.get('current_site')
    #_data = []

    # query_sql = "select h.name,count(*) from deviceman_pc_list as p,deviceman_hosttype as h where h.id=p.hosttype_id and p.site_id='%s' and h.id in (1,2,3,4) group by hosttype_id"%(site_id)
    #
    # data_list = exc_sql(query_sql)

    #select_data = {"receive_month": 'extract(month from receive_date )'}
    # print(datetime.now().year)

    x = []
    y = []
    duration=4
    for i in range(datetime.now().year - duration, datetime.now().year + 1):
         #print(i)
         select_data = {"receive_year": 'extract(year from receive_date )'}
         res = pc_list.objects.filter(receive_date__year=i, site_id=site_id, hosttype_id__in= [1,2,3]).extra(select=select_data).values(
            'receive_year').annotate(count=Count('id')).exclude(host_status='disposed').order_by('receive_year')


         #print(res)
         for re in res:

             #print(str(i)+'-'+str(re['receive_month']))
             x.append(str(i))
             #print(re['count'])
             y.append(re['count'])
         #x=[i[0] for i in res]

    #x = ['sz','bj','gz']
   #
         #y=[i[1] for i in res]

    res = pc_list.objects.filter(receive_date__year__lt=(i-4), site_id=site_id,hosttype_id__in= [1,2,3]).extra(select=select_data).values(
        'receive_year').aggregate(count=Count('id'))
    print(res)
    # for re in res:
    x.insert(0, str(i-duration-1)+' and early')
    y.insert(0, res['count'])
    #y = [10,20,30]
   #  #_data.append()
    print(x)
    print(y)
    bar=Bar("Computers Per Year",width='100%',height=500)
    #bar.use_theme('dark')
    bar.add("数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,
    #
            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",
    #
             bar_normal_color="#006edd", bar_emphasis_color="#0000ff",xaxis_rotate=40)
    #


    return bar

def get_site_id(request):
    siteid = request.session.get('current_site')
    return siteid


    #device_total.append()


def wbar(request):
    #site_id=request.user.adm_info.site_id
    site_id=request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=1 and p.site_id='%s' and p.host_status!='disposed' group by host_status "%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Workstation",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def lbar(request):
    #site_id = request.user.adm_info.site_id
    site_id=request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=2 and p.site_id='%s' and p.host_status!='disposed' group by host_status"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Laptop",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def dbar(request):
    #site_id = request.user.adm_info.site_id
    site_id= request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=3 and p.site_id='%s' and p.host_status!='disposed' group by host_status"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Desktop",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def sbar(request):
    #site_id = request.user.adm_info.site_id
    site_id = request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=4 and p.site_id='%s' and p.host_status!='disposed' group by host_status"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Server",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def swbar(request):
    #site_id = request.user.adm_info.site_id
    site_id = request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=5 and p.site_id='%s' and p.host_status!='disposed' group by host_status"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Switch",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def rbar(request):
    #site_id = request.user.adm_info.site_id
    site_id = request.session.get('current_site')
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=6 and p.site_id='%s' and p.host_status!='disposed' group by host_status"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Router",width='100%',height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def piebar(request):
    site_id = request.session.get('current_site')
    #_data = []

    query_sql = "select h.name,count(*) from deviceman_pc_list as p,deviceman_hosttype as h where h.id=p.hosttype_id  and p.site_id='%s' and h.id in (1,2,3,4) and p.host_status!='disposed' group by hosttype_id"%(site_id)

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    nrows=[i[0] for i in data_list]
   # x = ['sz','bj','gz']

    cols=[i[1] for i in data_list]
   # y = [10,20,30]
    #_data.append()

    pie = Pie("分类百分比",  width='100%', title_text_size=20, page_title='我的图')

    pie.add("", nrows, cols, is_label_show=True, is_legend_show=True, legend_pos="right")

    return pie
