import random,string,os
from PIL import Image,ImageDraw,ImageFont



# 生成验证码
def AuthCode(length):
    # 利用random生成length位数字加字母随机验证码
    rand=[]
    
    for x in range(length):
        y=random.randrange(length)
        if y % 2 == 0:
            # 随机选取0-9的数字
            num=random.choice(string.digits)
            rand.append(num)
        else:
            # 随机选取a-zA-Z的字母
            temp = random.choice(string.ascii_letters)
            rand.append(temp)
    # 拼接验证码
    result="".join(rand)
    return str(result)


# 生成随机密码
def GenPassword(length):
    #随机出数字的个数
    numOfNum = random.randint(1,length-1)
    numOfLetter = length - numOfNum
 
    #选中numOfNum个数字
    slcNum = [random.choice(string.digits) for i in range(numOfNum)]
 
    #选中numOfLetter个字母
    slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
 
    #打乱这个组合
    slcChar = slcNum + slcLetter
    random.shuffle(slcChar)
    #生成密码
    genPwd = ''.join([i for i in slcChar])
    return genPwd


# 生成验证码图片
def generate_codeimage(code):
    """
        param code: 参数为验证码字符串
    """
    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    size = (150,60)

    # 构建图像---等同于画布  模式rgb  宽高   颜色随机变化
    im = Image.new(mode='RGB', size=size, color=color)

    # 使用一个字体
    
    path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(path,'ttf/MSYH.TTC')
    fnt = ImageFont.truetype(font_path, 30)

    # 创建画图对象
    draw = ImageDraw.Draw(im)

    i = 0
    for code_str in code:
        # x,y,进行随机
        i += 1
        x = 5 + random.randint(10,20) + 20*i
        y = 10 + random.randint(0,10)
        fill_color = (random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
        
        # 画验证码到图形上
        draw.text((x,y),code_str,font=fnt,fill=fill_color)
        
        # 画干扰线
        x1 = random.randint(0,150)
        y1 = random.randint(0,60/2)
        
        x2 = random.randint(0,150)
        y2 = random.randint(60/2, 60)
        draw.line((x1,y1,x2,y2), fill=random.randint(0,255))
        
        # 画干扰点
        for x in range(random.randint(10,20)):
            draw.point((random.randint(0,150),random.randint(0,60)), fill=random.randint(0,255))
            
    return im


if __name__ == '__main__':
    print(AuthCode(4))
    print(GenPassword(6))
    im = generate_codeimage(AuthCode(4))
    im.show()
