from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from apps.user.check_login import check_login_status
from modules.article_module import *
from exts.utils.logsout import CreateLogging
from sqlalchemy import and_,or_,not_
from exts import cache

article_bp = Blueprint('article', __name__)
bp_logging = CreateLogging('article_v1','debug')


# 文章首页
@article_bp.route('/',endpoint='articles')
def article_index():
    # 判断用户是否登录
    if not session.get('uid') or not cache.get(str(session.get('uid'))):
        g.user = None
        
    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 20

    # 获取pagination对象
    pagination = Article.query.filter(Article.isdelete == False).order_by(-Article.create_time).paginate(page=current_page,per_page=per_page)
    
    #========实现显示固定分页数====================

    # 1 需要显示的固定页数长度
    page_control = 5
    
    # 2 计算当前页到尾页的长度
    page_len = pagination.pages - pagination.page
    
    # 3 比较当前页到尾页的长度与设定的长度
    if pagination.pages<page_control:
        # 3.1 总页数小于固定页数长度
        middle_page = range(1,pagination.pages+1)
    elif page_len < page_control<= pagination.pages:
        # 3.2 当前页到尾页全部显示
        middle_page = range(pagination.pages-page_control+1,pagination.pages+1)
    else:
        # 3.3 当前页到设置的长度
        middle_page = range(pagination.page,pagination.page+page_control)

    return render_template('article/index.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page)


# 发布文章
@article_bp.route('/publish',endpoint='publish',methods=['GET','POST'])
@check_login_status
def article_publish():
    form = ArticleForm()

    # 校验通过
    if form.validate_on_submit():
        title = request.form.get('title')
        artilceType = request.form.get('artilceType',type=int)
        content = request.form.get('content')
        # bp_logging.logger.debug(f'{title},{artilceType},{content}')
        
        # 验证artilceType
        typelist = [type.id for type in g.types]
        if artilceType not in typelist:
            return render_template('article/publish.html',form=form,user=g.user,types=g.types,typeError="必须选择文章类型")
        
        # 创建文章对象
        article = Article()
        article.article_title = title
        article.uid = g.user.id
        article.type_id = artilceType
        article.content = content
        
        # 保存到数据库
        db.session.add(article)
        db.session.commit()
        flash(message="文章发布成功",category="info")
        return render_template('article/info.html',user=g.user,types=g.types,tip="发布成功")

    # 默认展示文章发布页面
    return render_template('article/publish.html',form=form,user=g.user,types=g.types)
    

# 文章的删除
@article_bp.route('/delete',endpoint='delete',methods=['GET','POST'])
@check_login_status
def delete_article():
    aid = request.args.get('aid',int)
    # 删除文章---软删除
    article =  Article.query.filter(and_(Article.id==aid,Article.uid==g.user.id)).first()
    if article:
        # 更新数据库
        article.isdelete = 1
        # db.session.delete(article)   # 硬删除
        db.session.commit()
        return jsonify(code=200,msg='ok'),200
    
    # 删除失败
    return jsonify(code=400,msg='failed'),400


# 管理文章
@article_bp.route('/admarts',endpoint='admarts',methods=['GET'])
@check_login_status
def admin_article():
    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 10

    # 获取pagination对象
    pagination = Article.query.filter(Article.uid == g.user.id,Article.isdelete != 1).order_by(-Article.create_time).paginate(page=current_page,per_page=per_page)
    
    #========实现显示固定分页数====================

    # 1 需要显示的固定页数长度
    page_control = 5
    
    # 2 计算当前页到尾页的长度
    page_len = pagination.pages - pagination.page
    
    # 3 比较当前页到尾页的长度与设定的长度
    if pagination.pages<page_control:
        # 3.1 总页数小于固定页数长度
        middle_page = range(1,pagination.pages+1)
    elif page_len < page_control<= pagination.pages:
        # 3.2 当前页到尾页全部显示
        middle_page = range(pagination.pages-page_control+1,pagination.pages+1)
    else:
        # 3.3 当前页到设置的长度
        middle_page = range(pagination.page,pagination.page+page_control)

    return render_template('article/admin_article.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page)
    

# 修改文章
@article_bp.route('/artedit',endpoint='artedit',methods=['GET','POST'])
@check_login_status
def edit_article():
    form = EditArticleForm()
    # get请求
    if request.method == 'GET':
        # 获取文章ID
        aid = request.args.get('aid',type=int)
        # bp_logging.logger.debug(aid)
        # 查询文章
        article = Article.query.filter(and_(Article.id==aid,Article.uid==g.user.id,Article.isdelete==False)).first()
        
        if not article:
        # 错误展示
            return '文章不存在无法编辑!!!'
        # 没有提交修改
        form.title.data = article.article_title
        form.content.data = article.content
        form.hiddens.data = article.id
        typeid = article.type_id

        # 默认展示文章编辑页面
        return render_template('article/edit.html',form=form,typeid=typeid,user=g.user,types=g.types)
    
    # POST请求验证
    if form.validate_on_submit():
        # 获取标题
        title = request.form.get('title')
        # 获取文章类别
        artilceType = request.form.get('artilceType',type=int)
        # 获取文章内容
        content = request.form.get('content')
        # 获取文章id
        aid = request.form.get('hiddens',type=int)
        # 打印日志
        # bp_logging.logger.debug(f'{title},{artilceType},{content}')
        
        # 验证artilceType
        typelist = [type.id for type in g.types]
        if artilceType not in typelist:
            return render_template('article/edit.html',form=form,user=g.user,types=g.types,typeError="必须选择文章类型")
        
        # 重新赋值给文章对象
        article = Article.query.filter(and_(Article.id==aid,Article.uid==g.user.id,Article.isdelete==False)).first()
        if article:
            article.article_title = title
            article.type_id = artilceType
            article.content = content
            
            # 保存到数据库
            db.session.commit()
            flash(message="修改成功",category="info")
            return render_template('article/info.html',user=g.user,types=g.types,tip="修改成功")
        
        return render_template('article/edit.html',form=form,user=g.user,types=g.types,error="修改失败")
    
    return render_template('article/edit.html',form=form,user=g.user,types=g.types,error="修改失败")
    

# 文章详情
@article_bp.route('/detail',endpoint='detail',methods=['GET'])
def article_detail():
    form = CommentForm()
    
    # 判断用户是否登录
    if not session.get('uid') or not cache.get(str(session.get('uid'))):
        g.user = None
    
    # 获取文章id        
    aid = request.args.get('aid',type=int)
    article = Article.query.filter(and_(Article.id==aid,Article.isdelete==False)).first()
    if not article:
        return render_template('article/info.html',user=g.user,types=g.types,tip="您找的文章不存在TAT")
    
    # 提交评价时需要验证
    form.hiddens.data = aid
    
    # 收藏状态--已登录用户
    if g.user:
        g.save = Favorites.query.filter(and_(Favorites.uid==g.user.id,Favorites.aid==aid)).first()
    
    # 评论数
    comments_num = len(Comments.query.filter(Comments.art_id==aid,Comments.isdelete==False).all())
    favorites_num = len(Favorites.query.filter(Favorites.aid==aid).all())
    
    # 分页展示评论
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 5

    # 获取pagination对象
    pagination = Comments.query.filter(and_(Comments.art_id == aid,Comments.isdelete==False)).order_by(-Comments.create_time).paginate(page=current_page,per_page=per_page)
    
    #========实现显示固定分页数====================

    # 1 需要显示的固定页数长度
    page_control = 5
    
    # 2 计算当前页到尾页的长度
    page_len = pagination.pages - pagination.page
    
    # 3 比较当前页到尾页的长度与设定的长度
    if pagination.pages<page_control:
        # 3.1 总页数小于固定页数长度
        middle_page = range(1,pagination.pages+1)
    elif page_len < page_control<= pagination.pages:
        # 3.2 当前页到尾页全部显示
        middle_page = range(pagination.pages-page_control+1,pagination.pages+1)
    else:
        # 3.3 当前页到设置的长度
        middle_page = range(pagination.page,pagination.page+page_control)
    
    # 每次请求都要刷新浏览量
    article.views += 1
    db.session.commit()
    
    return render_template('article/detail.html',user=g.user,types=g.types,article=article,comments_num=comments_num,favorites_num=favorites_num,form=form,pagination=pagination,middle_page=middle_page)


# 发布文章评论
@article_bp.route('/comment',endpoint='comment',methods=['POST'])
@check_login_status
def article_comment():
    form = CommentForm()
    # 从表单隐藏域获取文章id
    aid = request.form.get('hiddens')
    artilce  = Article.query.filter(and_(Article.id==aid,Article.isdelete==False)).first()
    if not artilce:
        return render_template('article/info.html',user=g.user,types=g.types,tip="您评论的文章不存在TAT")
    if form.validate_on_submit():
        comment = Comments()
        comment.uid = g.user.id
        comment.art_id = aid
        comment.com_content = request.form.get('comment')
        
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('article.detail')+"?aid="+aid)
    
    flash('评论失败',category='info')
    return render_template('article/info.html',user=g.user,types=g.types)


# 文章点赞
@article_bp.route('/thumbs',endpoint='thumbs',methods=['GET'])
def article_thumbs():
    aid = request.args.get('aid',type=int)
    article = Article.query.filter(and_(Article.id==aid,Article.isdelete==False)).first()
    if not article:
        return jsonify(code=400,msg="点赞失败")
    
    # 点赞数加1
    article.thumbs_up += 1
    db.session.commit()
    return jsonify(code=200,num=article.thumbs_up,msg="感谢您的点赞")


# 收藏文章
@article_bp.route('/favorites',endpoint='favorites',methods=['GET'])
@check_login_status
def article_favorites():
    aid = request.args.get('aid',type=int)
    article = Article.query.filter(and_(Article.id==aid,Article.isdelete==False)).first()
    if not article:
        return jsonify(code=400,msg="收藏失败")
    
    # 查询用户收藏该文章的记录
    favorite = Favorites.query.filter(and_(Favorites.uid==g.user.id,Favorites.aid==aid)).first()
    # 不存在收藏记录
    if not favorite:
        favorite =Favorites()
        favorite.uid = g.user.id
        favorite.aid = aid
        favorite.isfavorite = True
        # 新增收藏记录
        db.session.add(favorite)
        islove=1
        msg = "收藏成功"
        
    # 存在收藏记录    
    else:
        # 删除搜藏记录
        db.session.delete(favorite)
        islove=0
        msg="取消收藏"
        
    db.session.commit()
    favorites_num = len(Favorites.query.filter(Article.id==aid).all())
    return jsonify(code=200,islove=islove,num=favorites_num,msg=msg)
    

    
