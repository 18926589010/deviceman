from django.db import models
from django.contrib.auth.models import User
#import select2
from django.forms import fields
#from select2.fields import  forms
# Create your models here.
import json

class borrows(models.Model):
    user_list=models.ForeignKey('user_list', to_field='id',  on_delete=None)
    pc_list=models.ForeignKey('pc_list',  on_delete=None, to_field='id')
    bdate=models.DateField(null=True,blank=True,default='2019-01-01')
    rdate = models.DateField(null=True,blank=True, default='2000-01-01')
    ticketid=models.CharField(max_length=40,null=True,blank=True)
    User=models.ForeignKey(User,on_delete=False,to_field='id')

class user_list(models.Model):
    user_name=models.CharField(unique=True, max_length=40)
    full_name=models.CharField(max_length=40)
    email_address=models.CharField(max_length=40)
    dept_list=models.ForeignKey('dept_list', on_delete=None, to_field='id', )
    regdate=models.DateField(auto_now=True)
    resigndate=models.DateField(blank=True)
    lastupdate = models.DateField(blank=True)
    user_status=models.CharField(max_length=40, default='active')
    remark = models.CharField(max_length=40, default='--')
    class Meta:
        ordering = ('full_name',)
    def __str__(self):
         return self.full_name

class adm_info(models.Model):
    User = models.OneToOneField(User, on_delete=None, to_field='id')
    #site = models.ForeignKey('site', on_delete=None, to_field='id')
    pc_dispose = models.BooleanField(default=0)
    stat_adm = models.BooleanField(default=0)
    it_adm = models.BooleanField(default=0)
    system_adm = models.BooleanField(default=0)

class adm_site(models.Model):
    site=models.ForeignKey('site',on_delete=None, to_field='id')
    User = models.ForeignKey(User,on_delete=None,to_field='id')

class pc_list(models.Model):
    host_name=models.CharField(max_length=64, unique=True)
    service_tag=models.CharField(max_length=45,unique=True)
    hosttype=models.ForeignKey('hosttype', to_field='id', related_name='hosttype_name', verbose_name='host_type', on_delete=None)
    host_model=models.CharField(max_length=45)
    host_spec=models.CharField(max_length=45)
    price=models.FloatField(default=0)
    receive_date=models.DateField(auto_now_add =False, default='2018-01-01')
    user_list = models.ForeignKey('user_list', to_field='id', related_name='user_list_full_name', on_delete=None, )
    seat_no = models.IntegerField(default=14000)
    host_status=models.CharField(max_length=45)
    studio = models.CharField(max_length=45, default='-')
    site=models.ForeignKey('site',to_field='id', related_name='site_sitename', on_delete=None)
    asset_code = models.IntegerField(default=1)
    remark=models.TextField(max_length=200, default='-')
    mac=models.CharField(max_length=15, default='-')
    class Meta:
        ordering = ('hosttype','host_name',)

    def __str__(self):
        return self.host_name



class dept_list(models.Model):
    bl_list = models.ForeignKey('bl_list',to_field='id',on_delete=None,default=2)
    dept_name = models.CharField(max_length=45)
    dept_leader = models.CharField(max_length=45)
    def __str__(self):
        return self.dept_name


class bl_list(models.Model):
    bl_name = models.CharField(max_length=10)
    bl_leader = models.CharField(max_length=20)

    def __str__(self):
        return self.bl_name



class hosttype(models.Model):
    name=models.CharField(max_length=20,unique=True)
    cname=models.CharField(max_length=20)
    def __str__(self):
        return self.name
class site(models.Model):
    sitename=models.CharField(max_length=20, unique=True)
    officename = models.CharField(max_length=20,default='Luohu')
    address=models.CharField(max_length=50)
    def __str__(self):
        return self.sitename


class repair_record(models.Model):
    pc_list = models.ForeignKey('pc_list',  on_delete=False)
    problem_desc = models.TextField(max_length=50)
    rp_date = models.DateField(null=True, blank=True, default='2019-01-01')
    fix_result = models.TextField(max_length=50)
    fix_date = models.DateField(default='2000-01-01')
    User = models.ForeignKey(User, on_delete=False, to_field='id')

class operation_type(models.Model):
    operation_type =models.CharField(max_length=20)

class operation_log(models.Model):
     pc_list = models.ForeignKey('pc_list', to_field='id', on_delete=False)
     user_list=models.ForeignKey('user_list',to_field='id', on_delete=False,)
     operation_type = models.ForeignKey('operation_type', to_field='id', on_delete=False)
     op_time = models.DateTimeField(auto_now=True)
     op_content = models.CharField(max_length=60, default='--')
     User = models.ForeignKey(User, on_delete=False, to_field='id')

class pc_transfer(models.Model):
    pc_list =models.ForeignKey('pc_list', to_field='id',on_delete=False)
    source_site = models.ForeignKey('site', to_field='id',on_delete=False,related_name='source_site')
    dest_site = models.ForeignKey('site', to_field='id',on_delete=False,related_name='dest_site')
    transfer_date= models.DateField(default='2019-01-01')
    remark = models.TextField(max_length=500, default='-')
    User = models.ForeignKey(User,on_delete=False, to_field='id')
