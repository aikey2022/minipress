from flask import Flask,Blueprint,render_template,request,redirect,url_for,flash,session,abort,jsonify
from apps.user.check_login import check_login_status
from modules.about_module import *
from modules.user_module import *
from exts import db,cache,csrf




about_bp = Blueprint('about', __name__)



@about_bp.route('/aboutme', endpoint="aboutme",methods=['GET'])
def aboutme():
    uid = session.get('uid')
    if uid and cache.get(str(uid)):
        user = User.query.filter(User.id == uid).first()
        g.user =user
    else:
        g.user = None
        
    about = AboutMe.query.first()
    return render_template('about/show_about.html',user=g.user,types=g.types,about=about)



@about_bp.route('/setabout', endpoint="setabout",methods=['GET', 'POST'])
@check_login_status
def setabout():
    form = AboutMeForm()
    uid = session.get('uid')
    # 设置隐藏uid
    form.hidden.data = uid

    # POST请求
    if form.validate_on_submit():
        # 获取uid
        get_uid = request.form.get('hidden')
        # 获取提交的内容
        content = request.form.get('content')
        
        # 校验uid是否有效
        if not get_uid or get_uid != str(uid):
            flash('非法用户,无法设置信息', category='error')
            return render_template('about/info.html')
        
        # 校验是否已经有关于的设置
        isseted = AboutMe.query.filter(AboutMe.uid == get_uid).first()
        if not isseted:
            aboutme = AboutMe()
            aboutme.uid = get_uid
            aboutme.content = content
            db.session.add(aboutme)
        else:
            isseted.content = content
        
        # 提交数据
        db.session.commit()
        flash('设置成功', category='info')
        return render_template('about/set_about.html',user=g.user,types=g.types,form=form)
        
    # GET请求
    aboutme= AboutMe.query.filter(User.id == uid).first()
    if aboutme:
        form.content.data = aboutme.content
    return render_template('about/set_about.html',user=g.user,types=g.types,form=form)
