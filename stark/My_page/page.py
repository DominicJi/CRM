

class Page:
    """
    这是我写的一个自定义分页类
    可以实现Django ORM数据的分页展示
    使用说明：
        新建一个utils模块包，再建立一个名为mapage的py文件，即可应用
        from utils import mypage
        page_obj = mypage.Page(total_num, current_page,params)
        publisher_list = data[page_obj.data_start:page_obj.data_end]
        page_html = page_obj.page_html()
        为了显示效果，show_page_num最好使用奇数
    """
    def __init__(self, total_num, current_page, params, per_page=10, show_page_num=11,):
        """
        :param total_num: 数据的总条数
        :param current_page: 当前访问的页码
        :param params:传入的request.GET数据
        :param per_page: 每一页显示多少条数据
        :param show_page_num: 页面上最多显示多少个页码
        """
        #多传入一个get后面的所有请求参数
        self.params=params
        self.total_num = total_num

        self.per_page = per_page
        self.show_page_num = show_page_num

        # 通过初始化传入的值计算得到的值
        self.half_show_page_num = self.show_page_num // 2
        # 当前数据总共需要多少页码
        total_page, more = divmod(self.total_num, self.per_page)
        # 如果有余数，就把页码数+1
        if more:
            total_page += 1
        self.total_page = total_page
        # 对传进来的当前页码数做有效性校验
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        # 如果当前页码数大于总页码数，默认展示最后一页的数据
        # current_page = total_page if current_page > total_page else current_page
        if current_page > self.total_page:
            current_page = self.total_page
        # 如果当前页码数小于1，默认展示第一页的数据
        if current_page < 1:
            current_page = 1

        self.current_page = current_page

        # 求 页面上 需要展示的页码范围
        if self.current_page - self.half_show_page_num <= 1:
            page_start = 1
            page_end = show_page_num
        elif self.current_page + self.half_show_page_num >= self.total_page:
            page_end = self.total_page
            page_start = self.total_page - self.show_page_num + 1
        else:
            page_start = self.current_page - self.half_show_page_num
            page_end = self.current_page + self.half_show_page_num
        self.page_start = page_start
        self.page_end = page_end
        #上面的一通计算得到的页面显示的页码结束
        #如果计算得到的页码数比我总共的页码数还多，我就把页码结束指定成我总共有的页码数
        if self.page_end>self.total_page:
            self.page_end=self.total_page



    @property
    def data_start(self):
        # 返回当前页应该从哪儿开始切数据
        return (self.current_page-1)*self.per_page

    @property
    def data_end(self):
        # 返回当前页应该切到哪里为止
        return self.current_page*self.per_page

    def page_html(self):
        li_list = []
        #添加前面的nav和ul标签
        li_list.append('''
            <nav aria-label='Page navigation>'
            <ul class='pagination'>
        ''')
        # 添加首页
        li_list.append('<li><a href="?page=1">首页</a></li>')
        # 添加上一页
        if self.current_page <= 1:  # 没有上一页
            prev_html = '<li class="disabled"><a aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
        else:
            prev_html = '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
                self.current_page - 1)
        li_list.append(prev_html)
        import copy
        ret=copy.deepcopy(self.params)
        for i in range(self.page_start, self.page_end + 1):
            ret['page']=i
            if i == self.current_page:
                tmp = '<li class="active"><a href="?page={0}">{0}</a></li>'.format(i)
            else:
                tmp = '<li><a href="?{0}">{1}</a></li>'.format(ret.urlencode(), i)
            li_list.append(tmp)
        # 添加下一页
        if self.current_page >= self.total_page:  # 表示没有下一页
            next_html = '<li class="disabled"><a aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'
        else:
            next_html = '<li><a href="?page={}" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'.format(
                self.current_page + 1)
        li_list.append(next_html)
        # 添加尾页
        li_list.append('<li><a href="?page={}">尾页</a></li>'.format(self.total_page))
        # 将生成的li标签 拼接成一个大的字符串
        # 尾部添加标签
        li_list.append('''
                            </nav>
                            </ul>
                        ''')
        page_html = "".join(li_list)

        return page_html

