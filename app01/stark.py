from stark.service.stark import site,ModelStark
from app01 import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import render,redirect
from django.http import JsonResponse
class UserConfig(ModelStark):
    list_display = ['name']
    list_display_links = ['name']
site.register(models.User,UserConfig)

site.register(models.Role)

site.register(models.Permission)

############业务表###############
#用户信息表与我们上面创建的User表一对一关联，可以说这是一张用户详情表
class UserinfoConfig(ModelStark):
    list_display = ['name','depart']
site.register(models.UserInfo,UserinfoConfig)

#班级表，需要明确的是班级所在的校区，班级名称，班级期数
class ClassListConfig(ModelStark):
    #这里我们灵活运用我们在源码里面写的自定义列，
    #需要注意的是list_display里面不能放多对多字段，因为多对多对象点name取不出来到底是谁
    #这就可以使用我自定义的列来添加多对多的外键字段
    list_display = ['school','course']
site.register(models.ClassList,ClassListConfig)

#班级上课信息记录表
class ClassStudyRecordConfig(ModelStark):
    #我们想在展示上课信息表中添加学习详情和录入成绩自定义列
    def study_display(self,obj=None,is_header=False):
        # 自定义学习详情点击进入学生学习考勤评分表
        if is_header:
            return '学习详情'
        #之所以加后面的参数，是利用之前写的过滤查询功能，所以点进去之后自动显示的就是对应于该数据的数据
        _url='/stark/app01/studentstudyrecord/?classstudyrecord=%s'%obj.pk
        return mark_safe('<a href="%s">学生学习记录</a>'%_url)

    def record_score_display(self,obj=None,is_header=False):
        if is_header:
            return '录入成绩'
        _url='/stark/app01/classstudyrecord/record_score/%s'%obj.pk
        return mark_safe('<a href="%s">录入成绩</a>'%_url)

    def record_score_view(self,request,classstudyrecord_id):
        if request.method=='POST':
            update_dict={}
            for k,v in request.POST.items():
                if k=='csrfmiddlewaretoken':
                    continue
                field_name,pk=k.rsplit("_",1)
                #为了尽量减少操作数据库的次数，我们对数据进行相应格式处理
                if pk not  in update_dict:
                    update_dict[pk]={field_name:v}
                else:
                    update_dict[pk][field_name]=v
            #拿到我们自己处理的数据结构，直接循环更新即可
            for pk,update_data in update_dict.items():
                #这里要巧妙运用我们学的字典的用法，
                #第一拆包传值
                #第二可以将字符串的key值拆包成变量名的形式！！！
                ## {pk:{score:10,homework_note:xxx}}
                models.StudentStudyRecord.objects.filter(pk=pk).update(**update_data)
            return redirect('%s?ok=1'%request.path)
        classstudyrecord=models.ClassStudyRecord.objects.filter(pk=classstudyrecord_id).first()
        studentstudyrecord_list=models.StudentStudyRecord.objects.filter(classstudyrecord=classstudyrecord)
        score_choice=models.StudentStudyRecord.score_choices
        ok=request.GET.get('ok')
        return render(request,'record_score_view.html',locals())

    def extra_urls(self):
        tmp=[]
        tmp.append(
            url('record_score/(\d+)',self.record_score_view)
        )
        return tmp
    list_display = ['class_obj','day_num','course_title',study_display,record_score_display]
site.register(models.ClassStudyRecord,ClassStudyRecordConfig)

#开设课程表
class CourseConfig(ModelStark):
    list_display = ['name']
site.register(models.Course,CourseConfig)

#客户跟进记录表
class ConsultRecordConfig(ModelStark):
    list_display = ['customer','consultant']
site.register(models.ConsultRecord,ConsultRecordConfig)

#部门表
class DepartmentConfig(ModelStark):
    list_display = ['title','code']
site.register(models.Department,DepartmentConfig)

#客户表与学生表一对一
class CustomerConfig(ModelStark):
    list_display = ['name','gender']
site.register(models.Customer,CustomerConfig)

#校区表
class SchoolConfig(ModelStark):
    list_display = ['title']
site.register(models.School,SchoolConfig)

#学生学习作业考勤记录表
class StudentStudyRecordConfig(ModelStark):
    def record_display(self,obj=None,is_header=False):
        #自定义动态修改学生考勤信息
        if is_header:
            return '考勤'
        html=''
        for i in models.StudentStudyRecord.record_choices:
            if obj.record==i[0]:
                s='<option selected value=%s>%s</option>'%i
            else:
                s = '<option  value=%s>%s</option>' % i
            html+=s
        return mark_safe('<select pk=%s>%s</select>' %(obj.pk,html))
    list_display = ['student','classstudyrecord','record','score',record_display]
site.register(models.StudentStudyRecord,StudentStudyRecordConfig)

#学员表
class studentConfig(ModelStark):
    def class_display(self,obj=None,is_header=False):
        if is_header:
            return "已报班级"
        temp=[]
        for i in obj.class_list.all():
            temp.append(str(i))
        return ",".join(temp)
    def score_display(self,obj=None,is_header=False):
        if is_header:
            return '查看成绩'
        return mark_safe("<a href='/stark/app01/student/score/%s'>查看成绩</a>"%obj.pk)
    def check_score(self,request,sid):
        if request.is_ajax():
            sid=request.GET.get('sid')
            cid=request.GET.get('cid')
            ret=models.StudentStudyRecord.objects.filter(student=sid,classstudyrecord__class_obj=cid).values_list("classstudyrecord__day_num","score")
            data=[['day%s'%i[0],i[1]]for i in ret]
            return JsonResponse(data,safe=False)
        student_obj=models.Student.objects.filter(pk=sid).first()
        class_list=student_obj.class_list.all()
        return render(request,'check_score.html',locals())
    def extra_urls(self):
        tmp=[]
        tmp.append(
            url('score/(\d+)',self.check_score)
        )
        return tmp
    list_display = ['customer',class_display,score_display]
site.register(models.Student,studentConfig)






