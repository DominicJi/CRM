from django.conf.urls import url
from django.shortcuts import redirect,render
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from stark.My_page.page import Page
from django.db.models import Q
#由于展示页面需要添加的功能模块较多，我们将其封装到一个类下面，大大减少list_view函数代码
#当我们以后遇到一个模块代码比较多的时候，也应该考虑是否可以将其再封装到类里面去来减少代码量使得你的处理逻辑更清晰
'''
pop功能解析:首先我们的需求的是给外键字段添加加号，点击加号跳转到对应的添加页面去执行添加操作，并且通过父子联动方式在不刷新父页面的情况下，在对应的加号选项内添加我们新增的数据
首先在展示页面中，我们先判断form字段是否是外键的ModelChoiceField类型，如果是则是外键字段，那么我们需要先给对应的form字段对象标识出需要增加加号，
再来需要给加号一个url来跳转到新增页面，需要通过当前的类来获取类的外键字段(._meta.get_filed('字段字符串'))再由此外键字段找到对应的外键类变量名(.rel.to)，之后利用这个关联类就可以拼接出我们的url
获取该类的类名小写(._meta.model_name),类所在项目名(._meta.app_label),拼接出url，后面再跟一个参数来标识这个加号对应的到底是那个外键展示标签，
通过form对象(.auto_id)即可获取到该form对象生成的html标签的id值，这里为什么要加这个是因为外键字段不止一个，那我们不仅要能正常跳转，并且还要在添加数据后，找到对应的标签添加新增的数据完成实时更新
前端添加页面需要定义一个给子页面调用的函数，需要的参数有标签id值，新增数据的id，新增数据的名字，点击加号给加号绑定的点击事件函数需要传入的参数就是url
在子页面提交post请求的时候，我们再拿到这个url里面后面跟的参数即我们自己添加的标签id，如果有值则需要父子联动，如果没有值则是正常的添加页面，不需要父子联动。
父子联动时，将创建的对象的id 名字以及标签id传给过渡页面，让其能够调用父页面里的函数，并且将值传给父页面去做查找和渲染
'''
'''
filter功能解析:filter主要用来筛选外键字段，传输类型{[],[]}
不好理解的是点击一个标签这个标签的状态到底什么时候被修改，到底如何修改，首先循环遍历用户自定义的要过滤的字段(最好是外键字段，因为一般字段用我们前面的模糊查询功能就可以了)
拿到每一个用户定义的过滤字段再根据(当前操作的类._meta.get_field('字段字符串').rel.to)拿到外键关联表名，据此查询出表下所有的数据，
先生成ALL标签，该标签主要就是去除url里面包含该标签所在字段的信息，也就是说该标签的href里面去除该标签所在字段内容即可，当url后面的数据为空时，该标签url后面也不应该跟参数
其次在循环表的大循环下循环表下面的每个对象构建一个个可以点击查询对应信息的a标签，其实就是对href后面的url进行赋值操作，需要注意的就是不同字段之间的点击操作会保存上一次的点击信息
也就是说初始情况下，href后面的跟的get请求数据只有一个，但是当你点击了一个标签后，我们会将该标签的数据获取并重新赋值给新页面的a标签


'''


class Showlist(object):
    def __init__(self,request,config_obj,queryset):
        self.request=request
        self.config_obj=config_obj
        self.queryset=queryset

        #分页
        current_page=self.request.GET.get('page')
        page_obj=Page(self.queryset.count(),current_page,self.request.GET,per_page=10)
        self.pagination=page_obj
        self.page_queryset=self.queryset[self.pagination.data_start:self.pagination.data_end]
    #获取表头
    def get_head_list(self):
        # 处理表头
        head_list = []
        for field_or_func in self.config_obj.get_new_list_display():  # ["title","price","publish",delete_col]
            if isinstance(field_or_func, str):
                # 如果用的默认的则取注册表名全大写形式
                if field_or_func == '__str__':
                    val = self.config_obj.model._meta.model_name.upper()
                else:
                    # 获取表的字段对象
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)
                    # 如果该字段定义了中文名则显示中文
                    val = field_obj.verbose_name
            else:
                # 直接拿自定义的表头名
                val = field_or_func(self, is_header=True)
            head_list.append(val)
        return head_list
    #获取表单
    def get_body_list(self):
        # 处理表单数据
        data_list = []
        for obj in self.page_queryset:
            tmp = []
            for field_or_func in self.config_obj.get_new_list_display():
                # 如果是字符串类型，那么直接用反射去拿，对象点__str__自身没有去类里面找，刚好我们在类里面都定义了__str__的方法，拿到的就是表的中文名
                # 如果你没有定义__str__，那么会执行默认的绑定方法，拿到的是对应的
                if isinstance(field_or_func, str):
                    #这里用捕获异常，主要是在用户没有定义时走到__str__时获取不到这样的字段对象
                    try :
                        if self.config_obj.model._meta.get_field(field_or_func).choices:
                            val=getattr(obj,'get_%s_display'%field_or_func)
                        else:
                            val = getattr(obj, field_or_func)
                        if field_or_func in self.config_obj.list_display_links:
                            val = mark_safe('<a href="%s">%s</a>' % (self.config_obj.get_change_url(obj), val))
                    except Exception:
                        val=getattr(obj,field_or_func)
                else:
                    # 如果是我们自己自定义的函数，则需要给他们传入必要的参数
                    val = field_or_func(self.config_obj, obj)
                tmp.append(val)
            data_list.append(tmp)
        return data_list
    #获取action内容
    def get_action(self):
        tmp=[]
        for action in self.config_obj.actions:
            tmp.append(
                {'name':action.__name__,
                 'desc':action.desc
                 }
            )
        return tmp
    #获取filter内容
    def get_filter_links(self):
        links_dict={}
        for filter_field in self.config_obj.list_filter:
            #获取字符串对应的字段对象
            filter_filed_obj=self.config_obj.model._meta.get_field(filter_field)
            #通过model字段.rel.to获取到字段所在的类变量名,获取该表下的所有的数据
            queryset=filter_filed_obj.rel.to.objects.all()
            #字典的value为一个个的列表，因为一个filter字段(表)一般情况下肯定是有多个数据的
            tmp=[]
            #复制请求信息
            import copy
            params=copy.deepcopy(self.request.GET)
            #all的标签
            params2=copy.deepcopy(self.request.GET)
            #如果循环的该字段已经在url get的请求部分了，那么我们的all中就需要去除这个键值，也是说all标签的url就是要去除自身所在的循环的字段信息
            if filter_field in params2:
                #去除当前循环字段的信息
                params2.pop(filter_field)
                all_link="<a href='?%s'>ALL</a>"%params2.urlencode()
            #没有当前该字段信息则生成空
            else:
                all_link="<a href=''>ALL</a>"
            tmp.append(all_link)

            #表不变的情况下，循环表中的每一个对象
            for obj in queryset:
                #动态保存上一次get请求数据内容
                params[filter_field]=obj.pk
                #调用固定方法，将键值对转换成urlencoded格式
                _url=params.urlencode()
                current_filter_field_id = self.request.GET.get(filter_field)
                #我们要搞清楚的是，这里的方法都仅仅是为了产生一个个的标签，仅此而已。所以我们不能想的太复杂
                if current_filter_field_id==str(obj.pk):
                    s = "<a class='item active' href='?%s'>%s</a>" % (_url, str(obj))
                else:
                    s = "<a class='item' href='?%s'>%s</a>" % (_url, str(obj))
                tmp.append(s)
            links_dict[filter_field]=tmp
        return links_dict

class ModelStark():#配置类对象
    list_display = ['__str__']
    list_display_links=[]
    model_form_class=None
    search_fields=[]
    actions=[]
    list_filter=[]

    def __init__(self,model):
        self.model=model
        self.app_label=self.model._meta.app_label
        self.model_name=self.model._meta.model_name
    #选择 删除 编辑按钮
    def delete_col(self,obj=None,is_header=False):
        '''
        :param obj:用来标识对应的数据id
        :param is_header: 用来辨别获取表头还是表单数据
        :return: 表头则返回表头字段，表单则返回具体html
        '''
        #调用根据is_header关键字参数来辨别到底是获取表头时候表身
        if is_header:
            return '删除'
        #mark_safe于|safe一样，也是标识我们写的html不自动转译
        #单个url解析函数
        _url=self.get_delete_url(obj)
        #统一url解析函数
        _url=self.get_reverse_url('delete',obj)
        return mark_safe('<a href="%s">删除</a>'%_url)

    def edit_col(self,obj=None,is_header=False):
        if is_header:
            return '编辑'
        #单个url解析函数
        _url = self.get_change_url(obj)
        #统一url解析函数
        _url=self.get_reverse_url('change',obj)
        return mark_safe('<a href="%s">编辑</a>'%_url)

    def check_col(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="actions" value="%s">'%obj.pk)

    def get_new_list_display(self):
        #这里之所以在这里重新对list_display进行扩充修改，是为了让所有的注册类都添加上我们自定义的内容
        new_list_display=[]
        new_list_display.extend(self.list_display)#列表添加列表extend
        if not self.list_display_links:
            new_list_display.append(ModelStark.edit_col)
        new_list_display.insert(0,ModelStark.check_col)
        new_list_display.append(ModelStark.delete_col)
        return new_list_display

    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse('%s_%s_add' % (app_label, model_name))
        return _url
    def get_change_url(self,obj):
        model_name=self.model._meta.model_name
        app_label=self.model._meta.app_label
        _url=reverse('%s_%s_change'%(app_label,model_name),args=(obj.pk,))
        return _url
    def get_delete_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse('%s_%s_delete' % (app_label, model_name), args=(obj.pk,))
        return _url
    def get_list_url(self):
        model_name=self.model._meta.model_name
        app_label=self.model._meta.app_label
        _url=reverse('%s_%s_list'%(app_label,model_name))
        return _url
    #上面四个解析url函数的统一解析函数
    def get_reverse_url(self,type,obj=None):
        if obj:
            url=reverse('%s_%s_%s'%(self.app_label,self.model_name,type),args=(obj.pk,))
        else:
            url=reverse('%s_%s_%s'%(self.app_label,self.model_name,type))
        return url

    #获取ModelForm类
    @property
    def get_modelform(self):
        if self.model_form_class:
            return self.model_form_class
        class AllModelForm(forms.ModelForm):
            class Meta:
                model=self.model
                fields='__all__'
        return AllModelForm
    #获取模糊匹配查询
    def search_field(self,queryset,key_word):
        q = Q()
        for field in self.search_fields:
            q.children.append((field+'__icontains',key_word))
        q.connector='or'
        queryset=queryset.filter(q)
        return queryset

    def get_filter_fields(self,request,queryset):
        #filter
        #这里在过滤查询的时候，要先判断get请求是否分页请求或模糊查询的情况，这两种情况下不应该再走我们的request.GET。items()
        #不然拿到的就是page key_word这肯定是会报错的，因为表中根本没有这两个字段
        if request.GET.get('page') or request.GET.get('key_word'):
            return queryset
        q=Q()
        for key,val in request.GET.items(): #publish=2&author=1
            q.children.append((key,val))#这里需要知道的是外键字段当你直接外键字段=数字的时候，ORM会帮你转换成对应的外键id去查询
        #如果有需要过滤的字段那么对queryset进行修改
        if q:
            #默认就是和的意思
            try:
                queryset=queryset.filter(q)
            except Exception:
                pass
        return queryset
    def list_view(self,request):
        # self.model就是对应的表名(类名)
        if request.method=='POST':
            func_name=request.POST.get('func_name')
            if func_name:
                action_id=request.POST.getlist('actions')
                queryset=self.model.objects.filter(pk__in=action_id)
                func=getattr(self,func_name)
                func(request,queryset)
        queryset = self.model.objects.all()
        add_url = self.get_add_url()
        #查询操作
        key_word=request.GET.get('key_word','')
        if key_word:
            queryset=self.search_field(queryset,key_word)
        #过滤操作
        queryset=self.get_filter_fields(request,queryset)

        show_obj = Showlist(request, self, queryset)
        return render(request, 'stark/list_view.html', locals())

    def add_view(self,request):
        if request.method=='POST':
            form_list=self.get_modelform(request.POST)
            if form_list.is_valid():
                obj=form_list.save()
                #获取pop_back_id值,如果有值表示是通过小界面提交过来的数据
                #我们需要走父子联动！！！
                pop_back_id=request.GET.get('pop_back_id')
                if pop_back_id:
                    pk=obj.pk
                    text=str(obj)
                    return render(request, 'stark/pop.html', {'pk':pk, 'text':text, 'pop_back_id':pop_back_id})
                #正常添加数据，走正常跳转
                return redirect(self.get_list_url())
        form_list=self.get_modelform()
        for form in form_list:
            if isinstance(form.field,forms.models.ModelChoiceField):
                #判断是否是选择类型，选择类型意味着是外键字段
                form.is_pop=True
                #form对象点name拿到的就是该对象对应的model字段名
                #获取当前操作表/类名   model字段.rel.to即可拿到对应的表名
                field_rel_model=self.model._meta.get_field(form.name).rel.to
                #获取类的小写名
                model_name=field_rel_model._meta.model_name
                #获取该类所在的项目名
                app_label=field_rel_model._meta.app_label
                #拼接url
                _url=reverse('%s_%s_add'%(app_label,model_name))
                #再给标签对象增加一对键值对，目的就是为了实现点击哪个标签就跳转到对应的增加界面
                form.url='%s?pop_back_id=%s'%(_url,form.auto_id)
                #form字段点auto_id获取生成的html的id值
        return render(request, 'stark/add_view.html', locals())
    def change_view(self,request,id):
        change_obj=self.model.objects.filter(pk=id).first()
        form_list=self.get_modelform(instance=change_obj)
        if request.method=='POST':
            form_list=self.get_modelform(request.POST,instance=change_obj)
            if form_list.is_valid():
                form_list.save()
                return redirect(self.get_list_url())
        return render(request, 'stark/edit_view.html', locals())
    def delete_view(self,request,id):
        if request.method=="POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(self.get_list_url())
        delete_obj=self.model.objects.filter(pk=id).first()
        form_list=self.get_modelform(instance=delete_obj)
        add_url=self.get_list_url()
        return render(request, 'stark/delete_view.html', locals())

    #对完开放一个生成额外url的接口
    def extra_urls(self):
        return []

    #生成对应注册表的二级路由 增删改查
    def get_urls(self):
        model_name=self.model._meta.model_name
        app_label=self.model._meta.app_label
        tmp=[
            url('^$',self.list_view,name='%s_%s_list'%(app_label,model_name)),
            url('^add/$',self.add_view,name='%s_%s_add'%(app_label,model_name)),
            url('^(\d+)/change/$',self.change_view,name='%s_%s_change'%(app_label,model_name)),
            url('^(\d+)/delete/$',self.delete_view,name='%s_%s_delete'%(app_label,model_name)),
        ]
        #用户有自定义的就添加自定义的额外url,没有则默认不添加
        tmp.extend(self.extra_urls())
        return tmp
    @property
    def urls(self):
        return self.get_urls(),None,None

class StarkSite(object):
    '''
    将注册的表注册到_registry当中,并且生成对应注册表的一级路由
    '''
    def __init__(self,name='admin'):
        self._registry={}
    def register(self,model,admin_class=None,**kwargs):
        if not admin_class:
            admin_class=ModelStark
        self._registry[model]=admin_class(model)
    def get_urls(self):
        tmp=[]
        for model_class,config_obj in self._registry.items():
            model_name=model_class._meta.model_name
            app_label=model_class._meta.app_label
            tmp.append(url(r'^%s/%s/'%(app_label,model_name),config_obj.urls))
        return tmp
    @property
    def urls(self):
        return self.get_urls(),None,None

site=StarkSite()



















