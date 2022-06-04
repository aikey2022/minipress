from PIL import Image,ImageDraw,ImageFont
import random,os


def image_code():
    
    size = (150,60)
    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    im = Image.new(mode='RGB', size=size, color=color)


    path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(path,'ttf/MSYH.TTC')
    # print("font-path--------------------------->>>",font_path)
    fnt = ImageFont.truetype(font_path, 30)
    draw = ImageDraw.Draw(im)
    code = ''
    
    # 生成随机字符串
    for i in range(0,4):
        code += random.choice("01235549874556qwe2rt1yuKAJPGOKGMLHGJSLJKWEJHi0oplkjhgfds5656904354543am3nbxv4czQPLOW5EIdURYdsda6TNG7daKS263565L8AMVNB9AsdXZHSdafgADK")

    # 将随机字符串写入图片
    n = 0
    for s in code:
        n += 1
        fill_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        x = 5+n*20+random.randint(5,30)
        y = 5+random.randint(0,20)
        draw.text((x, y), s, font=fnt, fill=fill_color)
        
    return im,code


if __name__ == '__main__':
    im,code= image_code()
    print(code)
    im.show()
