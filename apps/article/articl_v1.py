from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from apps.user.check_login import check_login_status
from modules.article_module import *
from exts.utils.logsout import CreateLogging
from sqlalchemy import and_,or_,not_


article_bp = Blueprint('article', __name__)
bp_logging = CreateLogging('article_v1','debug')


@article_bp.route('/',endpoint='articles')
def article_index():
    return render_template('article/index.html',types=g.types,user=g.user)


# 文章发布
@article_bp.route('/publish',endpoint='publish',methods=['GET','POST'])
@check_login_status
def article_publish():
    form = ArticleForm()
    # 校验通过
    if form.validate_on_submit():
        title = request.form.get('title')
        artilceType = request.form.get('artilceType',type=int)
        content = request.form.get('content')
        bp_logging.logger.debug(f'{title},{artilceType},{content}')
        
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
        return render_template('article/publish_success.html',user=g.user,types=g.types)

    # 默认展示文章发布页面
    return render_template('article/publish.html',form=form,user=g.user,types=g.types)
    

# 文章的删除
@article_bp.route('/delete',endpoint='delete',methods=['GET','POST'])
def delete_article():
    aid = request.args.get('aid',int)
    # 删除文章---软删除
    article =  Article.query.filter(and_(Article.id==aid,Article.uid==g.user.id)).first()
    if article:
        # 更新数据库
        article.isdelete = 1
        db.session.commit()
        return jsonify(code=200,msg='ok'),200
    
    # 删除失败
    return jsonify(code=400,msg='failed'),400


# 管理文章
@article_bp.route('/admarts',endpoint='admarts',methods=['GET'])
def admin_article():
    # 查询作者所有文章
    user_articles = Article.query.filter(Article.uid == g.user.id,Article.isdelete != 1).all()
    
    return render_template('article/admin_article.html',user=g.user,types=g.types,articles=user_articles)
    

