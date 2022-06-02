from apps import create_app

# 创建app
app = create_app()


if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0',port=80)