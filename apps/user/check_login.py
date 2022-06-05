from flask import g,render_template,request,redirect,url_for,flash,session,g,jsonify,make_response,abort
from modules.user_module import User
from exts import db,cache,csrf




# 检查登录状态
def check_login_status(func):
    def outer(*args, **kwargs):
        uid = session.get('uid')
        # 1 uid不存在->未登录
        if not uid:
            # print('----------------->>>',"未登录")
            return redirect(url_for('user.login'))
        
        # 2 登陆过期
        if not cache.get(str(uid)):
            # print('----------------->>>',"登陆过期")
            return redirect(url_for('user.login'))
        
        # 3 已登录
        user = User.query.filter(User.id == session.get('uid')).first()
        g.user = user
        # print('----------------->>>',"已登录")
        return func(*args, **kwargs)
    return outer