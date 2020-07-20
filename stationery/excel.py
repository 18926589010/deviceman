#import MySQLdb
import xlwt
from django.contrib.auth.models import User
from deviceman.models import adm_info
#from io import StringIO
from django.db import connection
from django.shortcuts import HttpResponse
try:
    import cStringIO as stringIOModule
except ImportError:
    try:
        import StringIO as stringIOModule
    except ImportError:
        import io as stringIOModule
from deviceman.models import hosttype


#from MySQLdb.cursors import DictCursor

#conn = MySQLdb.connect(host='192.168.2.4', user='root', passwd='zj88friend', db='zz91crm', port=3306, charset='utf8',
 #                      cursorclass=MySQLdb.cursors.DictCursor)  # 其中cursorclass设定返回数据类型为字典
#cur = conn.cursor()  # 获取游标

def exc_sql(sql):

    cursor = connection.cursor()

    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def export2xls(request):

    response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
    #response['Content-Disposition'] = 'attachment;filename=export_list.xls'  # 指定返回文件名
    wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
    hosttype_id1 = 1  # workstation
    hosttype_id2 = 2    #laptop
    hosttype_id3 = 3    #desktop
    hosttype_id4 = 4    #server
    hosttype_id5 = 5    #switch

    host_status1 = "in use"   # was using by users
    host_status2 = "inventory"  # in space , no user
    host_status3 = "P-Dispose"  # apply for disposal,waiting for approval
    host_status4 = "disposed"   # disposed , but it is till in use
    IBM_ASS_PC = '%BPC%'
    IBM_ASS_LT = '%BLT%'


    if request.method=='GET':
        id=request.GET.get('id')
        #site_id=request.GET.get('site')
        site_id=request.session.get('current_site')
        list_version = request.GET.get('ver')
        sql_plus=''
        if list_version == 'plus':
            sql_plus = """ ,u.user_name, u.email_address, p.seat_no, p.mac """

        sql_base = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , 
                    TIMESTAMPDIFF(MONTH, p.receive_date,CURDATE())%12 ,u.full_name ,b.bl_name, d.dept_name, s.sitename as location, p.host_status, p.asset_code, p.remark """ + sql_plus + \
                   """ from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d, deviceman_hosttype as h, deviceman_site as s ,deviceman_bl_list as b
                    where p.user_list_id=u.id and u.dept_list_id=d.id and p.site_id=s.id and p.hosttype_id=h.id and b.id=d.bl_list_id """

        # 01 Deployed （工作站、笔记本、台式机清单）

        if id == '1':
            response['Content-Disposition'] = 'attachment;filename=01 Stationery.xls'  # 指定返回文件名
            sql = 'SELECT s.name,t.name,s.stock_num,s.alert_num FROM deviceman.stationery_stationery as s, deviceman.stationery_stat_type as t where s.stat_type_id=t.id'

            sheet = wb.add_sheet(u'01 Stationery')  # excel里添加类别






        #02 Servers （服务器清单）
        if id == '2':
            response['Content-Disposition'] = 'attachment;filename=02 Application.xls'  # 指定返回文件名

            sql = "SELECT u.full_name,d.dept_name, st.name,sl.order_num,  m.date FROM deviceman.stationery_order_record_main as m, deviceman.deviceman_user_list as u, deviceman.deviceman_dept_list as d,deviceman.stationery_order_record_subordinate as sl, deviceman.stationery_stationery as st where m.user_list_id=u.id and u.dept_list_id=d.id  and sl.order_record_main_id=m.id and sl.stationery_id=st.id and m.order_status='Completed'"
            sheet = wb.add_sheet(u'02 application')  # excel里添加类别







        #03 IBM Assets （IBM资产清单）
        if id == '3':
            response['Content-Disposition'] = 'attachment;filename=03 Alert List.xls'  # 指定返回文件名
            sql = 'SELECT s.name,t.name,s.stock_num,s.alert_num FROM deviceman.stationery_stationery as s, deviceman.stationery_stat_type as t where s.stat_type_id=t.id and s.stock_num < s.alert_num'


            sheet = wb.add_sheet(u'03 Alert List')  # excel里添加类别



        #04 Pending Disposal （待报废资产清单）
        if id == '4':
            response['Content-Disposition'] = 'attachment;filename=04 Pending Disposal.xls'  # 指定返回文件名
            # sql = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , \
            #  TIMESTAMPDIFF(MONTH,p.receive_date,CURDATE())%%12 ,u.full_name , b.bl_name,d.dept_name, s.sitename as location,p.host_status, \
            #  p.asset_code,p.remark \
            #  from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d, deviceman_hosttype as h, deviceman_site as s ,deviceman_bl_list as b\
            #   where p.user_list_id=u.id and u.dept_list_id=d.id and p.site_id=s.id and p.hosttype_id=h.id and b.id=d.bl_list_id  and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) \
            #    and (host_status = '%s' ) and p.site_id='%s' order by h.id, p.host_name """ % (hosttype_id1, hosttype_id2, hosttype_id3, host_status3,site_id)
            #
            sql = sql_base + """ and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) 
                and (host_status = '%s' ) and p.site_id='%s' order by h.id, p.host_name """ % (hosttype_id1, hosttype_id2, hosttype_id3, host_status3,site_id)
            sheet = wb.add_sheet(u'04 Pending Disposal')  # excel里添加类别

        #05 Refresh list （超过四年且有用户使用的电脑）
        if id == '5':
            response['Content-Disposition'] = 'attachment;filename=05 Refresh list.xls'  # 指定返回文件名
            age_year=4  # 使用期超过四年的电脑
            public_user='Public'   # public 用户名，在导出清单时要排队公用电脑
            # sql = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , \
            #  TIMESTAMPDIFF(MONTH,p.receive_date,CURDATE())%%12 ,u.full_name , b.bl_name,d.dept_name, s.sitename as location,p.host_status, \
            #  p.asset_code,p.remark from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d,deviceman_bl_list as b, deviceman_hosttype as h, deviceman_site as s \
            #   where p.user_list_id=u.id and u.dept_list_id=d.id and d.bl_list_id=b.id and p.site_id=s.id and p.hosttype_id=h.id and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) \
            #    and (host_status = '%s' ) and u.user_name<>'%s' and TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE())>=%s and p.site_id='%s' order by h.id, p.host_name """ % (hosttype_id1, hosttype_id2, hosttype_id3, host_status1,public_user,age_year,site_id)
            #
            sql = sql_base + """and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) 
                and (host_status = '%s' ) and u.user_name<>'%s' and TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE())>=%s and p.site_id='%s' order by h.id, p.host_name """ % (hosttype_id1, hosttype_id2, hosttype_id3, host_status1,public_user,age_year,site_id)
            #
            sheet = wb.add_sheet(u'05 Refresh List')  # excel里添加类别
            # 05 Refresh list （超过四年且有用户使用的电脑）
        if id == '6':
            response['Content-Disposition'] = 'attachment;filename=06 Changsha PC list.xls'  # 指定返回文件名
            #age_year = 4  # 使用期超过四年的电脑
            public_user = 'Public'  # public 用户名，在导出清单时要排队公用电脑
            # sql = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , \
            #   TIMESTAMPDIFF(MONTH,p.receive_date,CURDATE())%%12 ,u.full_name , b.bl_name, d.dept_name, s.sitename as location,p.host_status, \
            #   p.asset_code,p.remark from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d,deviceman_bl_list as b, deviceman_hosttype as h, deviceman_site as s \
            #    where p.user_list_id=u.id and u.dept_list_id=d.id and d.bl_list_id=b.id and p.site_id=s.id and p.hosttype_id=h.id and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) \
            #     and (host_status = '%s' ) and u.user_name<>'%s' and u.remark like '%s'and p.site_id='%s' order by h.id, p.host_name """ % (
            # hosttype_id1, hosttype_id2, hosttype_id3, host_status1, public_user,'%Changsha%',site_id)
            #
            sql = sql_base + """and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) 
                 and (host_status = '%s' ) and u.user_name<>'%s' and u.remark like '%s'and p.site_id='%s' order by h.id, p.host_name """ % (
             hosttype_id1, hosttype_id2, hosttype_id3, host_status1, public_user,'%Changsha%',site_id)
            sheet = wb.add_sheet(u'06 Changsha PC List')  # excel里添加类别
    else:
        print('error for export excel')
    #conn.cursor().execute(sql)  # 执行sql语句
    #conn.cursor().fetchall()  # 获取查询结果
    data_list = exc_sql(sql)
    print(data_list)
    #sheet = wb.add_sheet(u'清单')  # excel里添加类别

    style_heading = xlwt.easyxf("""
        font:
          name Calibri,
          colour_index white,
          bold on,
          height 0xA0;
        align:
          wrap off,
          vert center,
          horiz center;
        pattern:
          pattern solid,
          fore-colour 0x19;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
                                )
    style_body = xlwt.easyxf("""
        font:
          name Calibri,
          bold off,
          height 0XA0;
        align:
          wrap on,
          vert center,
          horiz left;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
                             )
    style_num_col = xlwt.easyxf("""
        font:
          name Arial,
          bold off,
          height 0XA0;
        align:
          wrap on,
          vert center,
          horiz left;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
           
        
    """
    )
    style_green = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x11;")
    style_red = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x0A;")
    fmts = [
        'M/D/YY',
        'D-MMM-YY',
        'D-MMM',
        'MMM-YY',
        'h:mm AM/PM',
        'h:mm:ss AM/PM',
        'h:mm',
        'h:mm:ss',
        'M/D/YY h:mm',
        'mm:ss',
        '[h]:mm:ss',
        'mm:ss.0',
    ]
    style_body.num_format_str = fmts[0]

    if id == '1':

        sheet.write(0, 0, 'Stationery Name', style_heading)
        sheet.write(0, 1, 'Type Name', style_heading)
        sheet.write(0, 2, 'Stock Num', style_heading)
        sheet.write(0, 3, 'Alert Num', style_heading)



        row = 1
        for list in data_list:
            sheet.write(row, 0, list[0], style_body)
            sheet.write(row, 1, list[1], style_body)
            sheet.write(row, 2, list[2], style_num_col)
            sheet.write(row, 3, list[3], style_num_col)

            row = row + 1
    if id == '2':

        sheet.write(0, 0, 'Full Name', style_heading)
        sheet.write(0, 1, 'Deparment', style_heading)
        sheet.write(0, 2, 'Statioinery', style_heading)
        sheet.write(0, 3, 'Num', style_heading)
        sheet.write(0, 4, 'Date', style_heading)


        row = 1
        for list in data_list:
            sheet.write(row, 0, list[0], style_body)
            sheet.write(row, 1, list[1], style_body)
            sheet.write(row, 2, list[2], style_body)
            sheet.write(row, 3, list[3], style_num_col)
            sheet.write(row, 4, list[4], style_body)

            row = row + 1



    if id == '3':

        sheet.write(0, 0, 'Stationery Name', style_heading)
        sheet.write(0, 1, 'Type Name', style_heading)
        sheet.write(0, 2, 'Stock Num', style_heading)
        sheet.write(0, 3, 'Alert Num', style_heading)



        row = 1
        for list in data_list:
            sheet.write(row, 0, list[0], style_body)
            sheet.write(row, 1, list[1], style_body)
            sheet.write(row, 2, list[2], style_num_col)
            sheet.write(row, 3, list[3], style_num_col)

            row = row + 1

    #output = StringIO.StringIO()
    output = stringIOModule.BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


def export_excel(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
    # response['Content-Disposition'] = 'attachment;filename=export_list.xls'  # 指定返回文件名
    wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
    hosttype_id1 = 1  # workstation
    hosttype_id2 = 2  # laptop
    hosttype_id3 = 3  # desktop
    hosttype_id4 = 4  # server
    hosttype_id5 = 5  # switch

    # host_status1 = "in use"  # was using by users
    # host_status2 = "inventory"  # in space , no user
    # host_status3 = "P-Dispose"  # apply for disposal,waiting for approval
    # host_status4 = "disposed"  # disposed , but it is till in use
    IBM_ASS_PC = '%BPC%'
    IBM_ASS_LT = '%BLT%'
    # sql_base= """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) ,
    #         TIMESTAMPDIFF(MONTH, p.receive_date,CURDATE())%12 ,u.full_name ,b.bl_name, d.dept_name, s.sitename as location, p.host_status, p.asset_code, p.remark
    #         from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d, deviceman_hosttype as h, deviceman_site as s ,deviceman_bl_list as b
    #         where p.user_list_id=u.id and u.dept_list_id=d.id and p.site_id=s.id and p.hosttype_id=h.id and b.id=d.bl_list_id """
    #

    if request.method == 'GET':
        hosttype_name= request.GET.get('hosttype')
        hosttype_ids=hosttype.objects.filter(name=hosttype_name).values('id')
        hosttype_id=hosttype_ids[0].get('id')
        host_status = request.GET.get('host_status')
        site_id=request.GET.get('site_id')

        #site_id = request.session.get('current_site')
        # list_version = request.GET.get('ver')
        # sql_plus = ''
        # if list_version == 'plus':
        #     sql_plus = """ ,u.user_name, u.email_address, p.seat_no, p.mac """

        sql_base = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , 
                    TIMESTAMPDIFF(MONTH, p.receive_date,CURDATE())%12 ,u.full_name ,b.bl_name, d.dept_name, s.sitename as location, p.host_status, p.asset_code, p.remark """ \
                   """ from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d, deviceman_hosttype as h, deviceman_site as s ,deviceman_bl_list as b
                    where p.user_list_id=u.id and u.dept_list_id=d.id and p.site_id=s.id and p.hosttype_id=h.id and b.id=d.bl_list_id """

        # 01 Deployed （工作站、笔记本、台式机清单）

        if site_id == '0':
            site_sql=''
        else:
            site_sql='and p.site_id=' + str(site_id)

        response['Content-Disposition'] = 'attachment;filename=Asset_list.xls'  # 指定返回文件名
            # sql = """select p.host_name ,p.service_tag,h.name , p.host_model,p.receive_date , CURDATE(),TIMESTAMPDIFF(YEAR,p.receive_date,CURDATE()) , \
            # TIMESTAMPDIFF(MONTH,p.receive_date,CURDATE())%%12 ,u.full_name ,b.bl_name, d.dept_name, s.sitename as location,p.host_status, p.asset_code,p.remark \
            # from deviceman_pc_list as p, deviceman_user_list as u, deviceman_dept_list as d, deviceman_hosttype as h, deviceman_site as s ,deviceman_bl_list as b\
            # where p.user_list_id=u.id and u.dept_list_id=d.id and p.site_id=s.id and p.hosttype_id=h.id and b.id=d.bl_list_id \
            # and ( hosttype_id ='%s' or hosttype_id='%s' or hosttype_id= '%s' ) \
            # and (host_status = '%s' or host_status='%s' ) and p.host_name not like '%s' and p.site_id='%s' order by h.id, p.host_name """ % (hosttype_id1, hosttype_id2, hosttype_id3, host_status1, host_status2,IBM_ASS,site_id )
        sql = sql_base + """ and ( hosttype_id ='%s' ) 
             and (host_status = '%s' ) %s order by h.id, p.host_name """ % (hosttype_id, host_status,  site_sql)

        sheet = wb.add_sheet(u'asset list')  # excel里添加类别


    # conn.cursor().execute(sql)  # 执行sql语句
    # conn.cursor().fetchall()  # 获取查询结果
    data_list = exc_sql(sql)
    print(data_list)
    # sheet = wb.add_sheet(u'清单')  # excel里添加类别

    style_heading = xlwt.easyxf("""
        font:
          name Calibri,
          colour_index white,
          bold on,
          height 0xA0;
        align:
          wrap off,
          vert center,
          horiz center;
        pattern:
          pattern solid,
          fore-colour 0x19;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
                                )
    style_body = xlwt.easyxf("""
        font:
          name Calibri,
          bold off,
          height 0XA0;
        align:
          wrap on,
          vert center,
          horiz left;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
                             )
    style_num_col = xlwt.easyxf("""
        font:
          name Arial,
          bold off,
          height 0XA0;
        align:
          wrap on,
          vert center,
          horiz left;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;


    """
                                )
    style_green = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x11;")
    style_red = xlwt.easyxf(" pattern: pattern solid,fore-colour 0x0A;")
    fmts = [
        'M/D/YY',
        'D-MMM-YY',
        'D-MMM',
        'MMM-YY',
        'h:mm AM/PM',
        'h:mm:ss AM/PM',
        'h:mm',
        'h:mm:ss',
        'M/D/YY h:mm',
        'mm:ss',
        '[h]:mm:ss',
        'mm:ss.0',
    ]
    style_body.num_format_str = fmts[0]

    sheet.write(0, 0, 'Host Name', style_heading)
    sheet.write(0, 1, 'Service Tag', style_heading)
    sheet.write(0, 2, 'Type', style_heading)
    sheet.write(0, 3, 'Model', style_heading)
    sheet.write(0, 4, 'Receive Date', style_heading)
    sheet.write(0, 5, 'Today', style_heading)
    sheet.write(0, 6, 'Age(Yr)', style_heading)
    sheet.write(0, 7, 'Age(M)', style_heading)
    sheet.write(0, 8, 'Users', style_heading)
    sheet.write(0, 9, 'BL', style_heading)
    sheet.write(0, 10, 'Studio(Department)', style_heading)
    sheet.write(0, 11, 'Location', style_heading)
    sheet.write(0, 12, 'Status', style_heading)
    sheet.write(0, 13, 'FA Code', style_heading)
    sheet.write(0, 14, 'Remark', style_heading)

    # if list_version == 'plus':
    #     sheet.write(0, 15, 'AD Login', style_heading)
    #     sheet.write(0, 16, 'Email Addr', style_heading)
    #     sheet.write(0, 17, 'Seat No', style_heading)
    #     sheet.write(0, 18, 'MAC Addr', style_heading)

    row = 1
    for list in data_list:
        sheet.write(row, 0, list[0], style_body)
        sheet.write(row, 1, list[1], style_body)
        sheet.write(row, 2, list[2], style_body)
        sheet.write(row, 3, list[3], style_body)
        sheet.write(row, 4, list[4], style_body)
        sheet.write(row, 5, list[5], style_body)
        sheet.write(row, 6, list[6], style_num_col)
        sheet.write(row, 7, list[7], style_num_col)
        sheet.write(row, 8, list[8], style_body)
        sheet.write(row, 9, list[9], style_body)
        sheet.write(row, 10, list[10], style_body)
        sheet.write(row, 11, list[11], style_body)
        sheet.write(row, 12, list[12], style_body)
        sheet.write(row, 13, list[13], style_num_col)
        sheet.write(row, 14, list[14], style_body)
        # if list_version == 'plus':
        #     sheet.write(row, 15, list[15], style_body)
        #     sheet.write(row, 16, list[16], style_body)
        #     sheet.write(row, 17, list[17], style_num_col)
        #     sheet.write(row, 18, list[18], style_body)
        row = row + 1
    # output = StringIO.StringIO()
    output = stringIOModule.BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response