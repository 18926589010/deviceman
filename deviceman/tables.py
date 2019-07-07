from deviceman.models import pc_list, user_list, bl_list, dept_list,site, adm_info,adm_site, operation_log, repair_record
from table import Table
import django_tables2 as tables
from table.columns import Column,LinkColumn,Link
from table.utils import A
from django.urls import reverse_lazy
from datetime import date
from deviceman import testdb,views
from django.contrib.auth.models import User

class pc_listTable(Table):
    #id = Column(field='id',header='ID')

    name = Column(field='host_name', header='Host Name')
    service_tag = Column(field='service_tag', header='Service_Tag')
    hosttype = Column(field='hosttype.name', header='Type')
    host_model = Column(field='host_model', header='Model')
    receive_date =Column(field='receive_date', header='Receive_date')
    user = Column(field='user_list.full_name', header='User Name')
    bl_list = Column(field='user_list.dept_list.bl_list.bl_name', header='BL')
    site = Column(field='site.sitename', header='Site Code')
    host_status = Column(field='host_status', header='Status')
    seatno = Column(field='seat_no', header='Seat No')
    asset_code = Column(field='asset_code', header='Asset Code')
    OP = LinkColumn(header=u'操作', searchable=False, sortable=False,
                    links=[Link(text=u'编辑', viewname='pcedit', args=(A('id'),)), ])

    class Meta:
        model = pc_list
        ext_button = True
        template_name = 'table/buttons_table.html'
        ajax = True
        ajax_source = reverse_lazy('pc_table_data')







class User_listTable(Table):
    id = Column(field='id',header='ID')
    user_name =Column(field='user_name', header='User Name')
    full_name = Column(field='full_name',header='Full Name')
    email_address = Column(field='email_address', header='Email')
    bl_list = Column(field='dept_list.bl_list', header='BL')
    dept_list = Column(field='dept_list',header='Department')
    Regdate = Column(field='regdate',header='RegisterDate')
   # resigndate = Column(field='resigndate', header='ResignDate')
    lastupdate = Column(field='lastupdate', header='Last Update')
    #user_status = Column(field='user_status',header='Status')
    OP = LinkColumn(header=u'操作', sortable=False, links=[Link(text=u'详细', viewname='userdetailtable2', args=(A('id'),)),])
    class Meta:
        model = user_list
        ext_button = True
        template_name = 'table/buttons_table.html'




class siteTable(Table):
    id= Column(field='id',header='ID')
    sitename = Column(field='sitename', header='Site Code')
    officename = Column(field='officename', header='Office Name')
    address = Column(field='address', header='Address')
    OP = LinkColumn(header=u'操作', sortable=False, links=[])
    class Meta:
        model = site

class operation_log_Table(Table):
    id=Column(field='id', header='ID')
    pc_list=Column(field='pc_list.host_name', header='Host Name')
    user_list=Column(field='user_list.full_name',header='User Name')
    operation_type_id=Column(field='operation_type.operation_type',header='Operation Type')
    op_time=Column(field='op_time', header='Date Time')
    op_content=Column(field='op_content',header='Content')
    User=Column(field='User.username', header='IT Name')

    class Meta:
        model = operation_log


class Dept_listTable(Table):
    bl_list= Column(field='bl_list', header='BL Name')
    dept_name = Column(field='dept_name', header='Dept Name')
    dept_leader = Column(field='dept_leader', header='dept_leader')
    #address = Column(field='address', header='Address')
    OP = LinkColumn(header=u'操作', sortable=False, links=[])

    class Meta:
        model = dept_list

class bl_listTable(Table):
    bl_name = Column(field='bl_name', header='BL Name')
    bl_leader = Column(field='bl_leader', header='BL Leader')

    OP = LinkColumn(header=u'操作', sortable=False, links=[])

    class Meta:
        model = bl_list


class adm_infoTable(Table):
    username = Column(field='User.username', header='IT Name')
    #site = Column(field='site', header='Site Name')
    pc_dispose = Column(field='pc_dispose',header='PC-Dispose')
    stat_adm = Column(field='stat_adm',header='Stat Admin')
    it_adm = Column(field='it_adm',header='IT Admin')
    system_adm = Column(field='system_adm',header='System Admin')
    OP = LinkColumn(header=u'操作', sortable=False, links=[Link(text=u'详细', viewname='sitepermission', args=(A('User.id'),)),])

    class Meta:
        model = adm_info


class adm_siteTable(Table):
    username = Column(field='User.username', header='IT Name')
    site = Column(field='site', header='Site Name')
    # pc_dispose = Column(field='pc_dispose',header='PC-Dispose')
    # stat_adm = Column(field='stat_adm',header='Stat Admin')
    # it_adm = Column(field='it_adm',header='IT Admin')
    # system_adm = Column(field='system_adm',header='System Admin')
    OP = LinkColumn(header=u'操作', sortable=False, links=[])

    class Meta:
        model = adm_site


##below is the testing code for the django-table2



class user_Table2(tables.Table):
    class Meta:
        model  = user_list
        template_name = 'django_tables2/bootstrap.html'



class repair_record_Table2(tables.Table):
    class Meta:
        model = repair_record
        template_name = 'django_tables2/bootstrap.html'