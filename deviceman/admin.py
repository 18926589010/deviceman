from django.contrib import admin
from deviceman.models import borrows
from deviceman.models import user_list
from deviceman.models import pc_list
from deviceman.models import dept_list


class pc_listadmin(admin.ModelAdmin):
    list_display = ('host_name', 'service_tag', 'user_list', 'host_status', )
    search_fields = ('host_name','host_status','user_list__full_name','user_list__dept_list__dept_name')
    fk_fields = ('user_list__full_name',)
    #fields = ('host_name','user_name')

class user_listadmin(admin.ModelAdmin):

    list_display = ('user_name','full_name','email_address','dept_list')
    search_fields = ('full_name','email_address', 'dept_list__dept_name')



# Register your models here.

admin.site.site_header = "AECOM计算机设备管理信息系统-后台管理"
admin.site.register(borrows)
admin.site.register(user_list,user_listadmin)
admin.site.register(pc_list, pc_listadmin)
#admin.site.register(pc_list)
admin.site.register(dept_list)

