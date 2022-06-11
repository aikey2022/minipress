from flask import Flask
from apps.user.check_login import check_login_status
from modules.photo_module import *
from flask import Blueprint,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import time,settings,os
from exts import cache

photo_bp = Blueprint('photo',__name__)


@photo_bp.route('/showpics',endpoint="showpics",  methods=['GET'])
def photo_showpics():
    # 获取uid
    uid = session.get('uid')
    user = cache.get(str(uid))
    if not uid or not user:
        g.user = None
        
    # 查看询图片
    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 8

    # 获取pagination对象
    pagination = Photo.query.order_by(-Photo.create_time).paginate(page=current_page,per_page=per_page)
    
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

    return render_template('photo/showpic.html',user=g.user,types=g.types,pagination=pagination,middle_page=middle_page)    



@photo_bp.route('/adminpic', endpoint="adminpic", methods=['GET', 'POST'])
@check_login_status
def photo_admin():
    form = PhotoForm()
    # 获取uid
    uid = session.get('uid')
    
    # post请求
    if form.validate_on_submit():
        # 校验get_uid
        get_uid = request.form.get('hidden')
        if get_uid != str(uid):
            flash('非法操作,上传失败TAT',category='error')
            return render_template('photo/info.html',user=g.user,types=g.types)
        
        pic = form.file.data
        file_name = secure_filename(pic.filename)
        suffix = file_name.rsplit('.')[-1]
        
        nowtime = time.time()
        
        newfilename = f'{nowtime}_{uid}.{suffix}'
        # 拼接本地路径
        pic_path = os.path.join(settings.Development.PHOTO_DIR,newfilename)
        
        # 保存图片到本地
        pic.save(pic_path)
        
        # 保存数据库
        photo = Photo()
        photo.uid = uid
        photo.pic_url = f'upload/photo/{newfilename}'
        db.session.add(photo)
        db.session.commit()
        # return redirect(url_for('photo.adminpic'))
        
    # get请求
    form.hidden.data = uid
    
    # 查看询图片
    # 获取当前分页数默认为1 类型为int
    # 当前页码
    current_page = request.args.get('page',1,type=int)
    # 每页条数
    per_page = 8

    # 获取pagination对象
    pagination = Photo.query.filter(Photo.uid == uid).order_by(-Photo.create_time).paginate(page=current_page,per_page=per_page)
    
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

    return render_template('photo/admpic.html',user=g.user,types=g.types,form=form,pagination=pagination,middle_page=middle_page)


# 删除图片
@photo_bp.route('/delpics',endpoint="delpics",  methods=['GET', 'POST'])
@check_login_status
def photo_del():
    uid = session.get('uid')
    pic_id = request.args.get('ppid')
    
    if uid and pic_id:
        # 获取图片对象
        pic = Photo.query.filter(and_(Photo.id == pic_id,Photo.uid == uid)).first()
        pic_url = pic.pic_url
        # 提取图片文件名
        pic_name = pic_url.rsplit('/')[-1]
        
        # 图片本地路径
        pic_path = os.path.join(settings.Development.PHOTO_DIR,pic_name)
        if os.path.exists(pic_path):
            # 删除本地图片
            os.remove(pic_path)
            
        # 更新数据库
        db.session.delete(pic)
        db.session.commit()
        return jsonify(code=200,msg='删除成功')
    
    return jsonify(code=400,msg='删除失败')  





