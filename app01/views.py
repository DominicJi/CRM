from django.shortcuts import render,HttpResponse,redirect
from app01 import models
# Create your views here.
def login(request):
    if request.method=='POST':
        name=request.POST.get('username')
        pwd=request.POST.get('password')
        user_obj=models.User.objects.filter(name=name,pwd=pwd).first()
        if user_obj:
            #登陆成功在session里面记录用户登陆状态
            request.session['user_id']=user_obj.pk
            permission_list=[]
            #展示给用户可点击的权限
            show_list=[]
            #获取该用户的所有权限
            queryset_permission=user_obj.role.all().values('permission__url').distinct()
            for permission in queryset_permission:
                permission_list.append(permission['permission__url'])
            # 记录在session中
            request.session['permission_list'] = permission_list
            #获取可展示的权限
            total_list=[]
            for role_obj in user_obj.role.all():
                for permissions in role_obj.permission.all():
                    if permissions not in total_list:
                        total_list.append(permissions)
            for permission in total_list:
                if permission.is_show:
                    show_list.append({'title':permission.title,'link':permission.url})
            #记录在session中
            request.session['show_list']=show_list
            request.session['user_name']=user_obj.name
            return redirect('/index/')
    return render(request,'login.html')

def index(request):
    return render(request,'index.html')

def logout(request):
    request.session.flush()
    return redirect('/index/')