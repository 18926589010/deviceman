from django.db import connection

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader

from pyecharts import Bar,Pie
from deviceman.models import pc_list, site
from django.db.models import Count

REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def exc_sql(sql):

    cursor = connection.cursor()

    cursor.execute(sql)

    result = cursor.fetchall()

    return result

@csrf_exempt
def index(request):

    template = loader.get_template('deviceman/indexecharts.html')
    site_id=request.POST.get('siteid')
    if site_id:
        site_id=site_id
    else:
        site_id='0'
    print('site_id is ',site_id)
    b=sitebar(site_id)[0]
    c=bar()
    #d=lbar()
   # e=dbar()
   # f=sbar()
    i = piebar()
    context = dict(

        siteechart=b.render_embed(),
        wmyechart=c.render_embed(),

        #lmyechart=d.render_embed(),
        #dmyechart=e.render_embed(),
       # smyechart=f.render_embed(),
        ipie=i.render_embed(),
        host=REMOTE_HOST,
        total_types=sitebar(site_id)[1],
        script_list=c.get_js_dependencies(),
        siteid=site_id,

    )

    return HttpResponse(template.render(context, request))

def bar():

    #_data = []

    query_sql = "select h.name,count(*) from deviceman_pc_list as p,deviceman_hosttype as h where h.id=p.hosttype_id and h.id in (1,2,3,4) group by hosttype_id"

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
   # x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
   # y = [10,20,30]
    #_data.append()

    bar=Bar("设备数量",width=550,height=400)

    bar.add("数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")



    return bar

def sitebar(site_id):


    site_id = site_id
    x = []
    y = []
    #duration = 4
    # for i in range(datetime.now().year - duration, datetime.now().year + 1):
    #     # print(i)
    #     select_data = {"receive_year": 'extract(year from receive_date )'}
    # res = pc_list.objects.filter(receive_date__year=i, site_id=site_id, hosttype_id__in=[1, 2, 3]).extra(
    #         select=select_data).values(
    #         'receive_year').annotate(count=Count('id')).exclude(host_status='disposed').order_by('receive_year')

    if site_id=='0':
        sitename='China All Office'
        res = pc_list.objects.filter(hosttype_id__in=(1, 2, 3)).exclude(
            host_status='disposed').values('hosttype__name').annotate(count=Count('id')).order_by('hosttype')

        total_types = pc_list.objects.filter(hosttype_id__in=(1, 2, 3)).exclude(
            host_status='disposed').values('hosttype__name', 'host_status').annotate(count=Count('id')).order_by(
            'hosttype','host_status')


    else:
        sitenames = site.objects.filter(id=site_id).values('sitename')
        sitename = sitenames[0].get('sitename')

        res = pc_list.objects.filter(site_id=site_id,hosttype_id__in=(1, 2, 3)).exclude(
            host_status='disposed').values('hosttype__name').annotate(count=Count('id')).order_by('hosttype')

        total_types = pc_list.objects.filter(site_id=site_id,hosttype_id__in=(1, 2, 3)).exclude(
            host_status='disposed').values('hosttype__name', 'host_status').annotate(count=Count('id')).order_by(
            'hosttype','host_status')

    #print(res)
    for re in res:
             # print(str(i)+'-'+str(re['receive_month']))

        x.append(re['hosttype__name'])
             # print(re['count'])
        y.append(re['count'])

    print(total_types)
    bar=Bar("Location: "+sitename,'Asset Type',width='80%',height=400)

    bar.add("数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    bars=[bar,total_types]
    return bars

def lbar():
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=2 group by host_status"

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Laptop",width=400,height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def dbar():
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=3 group by host_status"

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Desktop",width=400,height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def sbar():
    query_sql = "select p.host_status,count(*) from deviceman_pc_list as p where p.hosttype_id=4 group by host_status"

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    x=[i[0] for i in data_list]
    #x = ['sz','bj','gz']

    y=[i[1] for i in data_list]
    #y = [10,20,30]
    #_data.append()

    bar=Bar("Server",width=400,height=300)

    bar.add("各种状态数量",x, y, type="effectScatter", border_color="#ffffff", symbol_size=2,

            is_label_show=True, label_text_color="#0000FF", label_pos="inside", symbol_color="yellow",

            bar_normal_color="#006edd", bar_emphasis_color="#0000ff")
    return bar

def piebar():

    #_data = []

    query_sql = "select h.name,count(*) from deviceman_pc_list as p,deviceman_hosttype as h where h.id=p.hosttype_id and h.id in (1,2,3,4) group by hosttype_id"

    data_list = exc_sql(query_sql)
    #data_list=pc_list.objects.values('hosttype__name', 'host_status').annotate(count=Count('host_status')).order_by('hosttype_id')
    nrows=[i[0] for i in data_list]
   # x = ['sz','bj','gz']

    cols=[i[1] for i in data_list]
   # y = [10,20,30]
    #_data.append()

    pie = Pie("设备分类百分比",  width=550, title_text_size=20, page_title='我的图')

    pie.add("", nrows, cols, is_label_show=True, is_legend_show=True, legend_pos="right")

    return pie