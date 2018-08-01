import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,render,redirect



class My_permission_middleware(MiddlewareMixin):
    def process_request(self,request):
        #先定义白名单，不设置任何访问限制
        white_list=['/login/','/register/','/admin/*','/index/','/logout/']
        #获取用户访问的url
        url=request.path
        #正则判断是否在白名单内
        for permission in white_list:
            res=re.search(permission,url)
            if res:
                return None

        #检查用户是否登陆
        is_login=request.session.get('user_id','')
        #没登陆直接跳转登录界面
        if not is_login:
            return redirect('/login/')

        #判断登陆用户是否拥有访问权限
        user_permission=request.session.get('permission_list','')
        for permissions in user_permission:
            #模仿Django视图函数匹配原则，设置完全配置模式
            permissions="^%s$"%permissions
            if re.search(permissions,url):
                return None
        else:
            return HttpResponse('<h3>您没有访问权限</h3>')


