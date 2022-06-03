from apps import create_app
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
from exts import db



# 创建app
app = create_app()

# 创建manager管理器
migrate =  Migrate(app=app,db=db)
manager = Manager(app=app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    print(app.url_map)
    # app.run(host='0.0.0.0',port=80)
    manager.run()