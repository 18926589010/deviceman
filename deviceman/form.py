from django import forms
from django.forms import fields
from deviceman.models import user_list, pc_list,dept_list,borrows,site, bl_list,adm_info,adm_site, repair_record,pc_transfer
from django.db.models import Q
from datetime import datetime
#from dal import autocomplete
from django.urls import reverse,reverse_lazy,resolvers
from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, ModelSelect2MultipleWidget,
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget
)
import json

class UserModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs, ):
        self.request = kwargs.pop("request")
        officename = self.request.session.get('officename')
        super(UserModelForm, self).__init__(*args, **kwargs, )
    # self.instance=kwargs.pop("instance")
        if 'instance' in kwargs.keys():
            print(kwargs['instance'])
            #super(UserModelForm, self).__init__(*args, **kwargs,)
            self.fields['user_name'].disabled = True
            officename=self.request.session.get('officename')

            self.fields['dept_list'].queryset = dept_list.objects.filter(
            Q(dept_name=self.instance.dept_list) | Q(dept_name__icontains=officename))
        else:
            self.fields['dept_list'].queryset = dept_list.objects.filter(dept_name__icontains=officename)

    class Meta:
        model = user_list  # 与models建立了依赖关系
        fields = "__all__"




class PcModelForm(forms.ModelForm):

    # so = globals(get_site_office(request='site_office'))
    #user_list = forms.ModelChoiceField(queryset=user_list.objects.all(),required=True, widget=autocomplete.ModelSelect2(url='userautocomplete'))
    def __init__(self, *args, **kwargs, ):

        self.request = kwargs.pop("request")
        # get the officename of the site IT ,
        officename = self.request.session.get('officename')
        current_site=self.request.session.get('current_site')
        super(PcModelForm, self).__init__(*args, **kwargs, )
        # self.instance=kwargs.pop("instance")
        # save objects code as below

        if 'instance' in kwargs.keys():

            print(kwargs['instance'])

            # site_office=request.session.get('officename')
            self.fields['user_list'].queryset = user_list.objects.filter(
                Q(full_name=self.instance.user_list) | Q(dept_list__dept_name__icontains=officename))
            self.fields['site'].queryset = site.objects.filter(id=current_site)

        # new objects code as below
        else:
            self.fields['user_list'].queryset = user_list.objects.filter(
                Q(dept_list__dept_name__icontains=officename)|Q(dept_list_id=8))
            self.fields['site'].queryset = site.objects.filter(id=current_site)

    class Meta:
        model = pc_list  # 与models建立了依赖关系
        fields = "__all__"
        widgets = {

            'receive_date': forms.DateInput(attrs={'class': "form-control",
                                                   'placeholder': "YYYY-MM-DD"}),
            'remark': forms.Textarea(attrs={'rows': '3', 'cols': '80'}),
            #'user_list': autocomplete.ModelSelect2(url='userautocomplete')

        }





    # class Meta:
    #     model = pc_list    # 与models建立了依赖关系
    #     fields = "__all__"
    #     widgets = {
    #
    #         'receive_date': forms.DateInput(attrs={'class': "form-control",
    #                                                'placeholder': "YYYY-MM-DD"}),
    #         'remark':  forms.Textarea(attrs={'rows':'3','cols':'80'})
    #     }


class MyWidget(ModelSelect2Widget):
    Qqueryset = user_list.objects.all()
    #model = user_list
    search_fields = [
        'user_name__icontains',
    ]

class borrowsModelForm(forms.ModelForm):


     class Meta:
        model = borrows # 与models建立了依赖关系
        fields = '__all__'

class RepairrecordModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs, ):
        self.request = kwargs.pop("request")
        current_pcid = self.request.session.get('current_pcid')
        super(RepairrecordModelForm, self).__init__(*args, **kwargs, )
        self.fields['rp_date'].initial = datetime.now().date()
        self.fields['pc_list'].initial = current_pcid


    class Meta:
        model = repair_record
        fields = '__all__'
        widgets = {

            'problem_desc': forms.Textarea(attrs={'rows': '3', 'cols': '80'}),
            'fix_result': forms.Textarea(attrs={'rows': '3', 'cols': '80'}),
            # 'user_list': autocomplete.ModelSelect2(url='userautocomplete')

        }










class SiteModelForm(forms.ModelForm):
    class Meta:
        model = site # 与site建立了依赖关系
        fields = "__all__"

class AdmSiteModelForm(forms.ModelForm):
    class Meta:
        model = adm_site # 与site建立了依赖关系
        fields = "__all__"



class Bl_listModelForm(forms.ModelForm):
    class Meta:
        model =  bl_list # 与site建立了依赖关系
        fields = "__all__"


class Dept_listModelForm(forms.ModelForm):
    class Meta:
        model = dept_list  # 与site建立了依赖关系
        fields = "__all__"

class Adm_infoModelForm(forms.ModelForm):
    class Meta:
        model = adm_info  # 与site建立了依赖关系
        fields = "__all__"


class Transfer_pcModelForm(forms.ModelForm):
    class Meta:
        model =pc_transfer
        fields = "__all__"
        widgets = {

            'remark': forms.Textarea(attrs={'rows': '3', 'cols': '80'}),
            #'fix_result': forms.Textarea(attrs={'rows': '3', 'cols': '80'}),
            # 'user_list': autocomplete.ModelSelect2(url='userautocomplete')

        }