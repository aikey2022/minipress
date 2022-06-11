from flask import Flask,Blueprint,render_template,request,redirect,url_for,flash,session,abort,g,jsonify
from exts import cache,db
from apps.user.check_login import check_login_status
from modules.msg_aboard_module import MsgAboard,MsgAboardForm
from sqlalchemy import and_,or_

msg_abort_bp = Blueprint('msg_abort',__name__)



# 展示留言板
@msg_abort_bp.route('/aborts',endpoint="aborts",methods=['GET','POST'])
def msg_aborts():
    form = MsgAboardForm()
    # 判断用户是否登录
    uid = session.get('uid')
    if not uid or not cache.get(str(uid)):
        g.user = None
    
    form.hidden.data = session.get('uid')    
    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 10

    # 获取pagination对象
    pagination = MsgAboard.query.order_by(-MsgAboard.create_time).paginate(page=current_page,per_page=per_page)
    
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

    return render_template('msgabort/abort.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page,form=form)



# 发布留言
@msg_abort_bp.route('/publishaborts',endpoint="publishaborts",methods=['POST'])
@check_login_status
def msg_publishaborts():
    form = MsgAboardForm()
    # 从表单隐藏域获取用户id
    uid = request.form.get('hidden')
    if not uid or uid != str(g.user.id):
        flash('非法用户无法留言',category='info')
        return render_template('msgabort/info.html',user=g.user,types=g.types,form=form)
    
    if form.validate_on_submit():
        msg = MsgAboard()
        msg.uid = g.user.id
        msg.msg_content = request.form.get('msg_content')
        
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('msg_abort.aborts'))
    
    flash('留言失败',category='info')
    return render_template('msgabort/info.html',user=g.user,types=g.types,form=form)



# 管理留言
@msg_abort_bp.route('/admaborts',endpoint="admaborts",methods=['GET', 'POST'])
@check_login_status
def msg_admborts():

    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 10

    # 获取pagination对象
    pagination = MsgAboard.query.filter(MsgAboard.uid==g.user.id).order_by(-MsgAboard.create_time).paginate(page=current_page,per_page=per_page)
    
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

    return render_template('msgabort/admabort.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page)



# 删除留言
@msg_abort_bp.route('/delborts',endpoint="delborts",methods=['GET','POST'])
@check_login_status
def msg_delborts():
    msgid = request.args.get('msgid',int)
    # 删除留言---物理删除
    abort =  MsgAboard.query.filter(and_(MsgAboard.id==msgid,MsgAboard.uid==g.user.id)).first()
    if abort:
        # 更新数据库
        # abort.isdelete = 1
        db.session.delete(abort)   # 物理删除
        db.session.commit()
        return jsonify(code=200,msg='ok'),200
    
    # 删除失败
    return jsonify(code=400,msg='failed'),400




# 审核留言

