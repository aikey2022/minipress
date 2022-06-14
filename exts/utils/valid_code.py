from exts.utils.generate_code import AuthCode,generate_codeimage

def image_code():
    code = AuthCode(4)
    im = generate_codeimage(code)

    return im,code


if __name__ == '__main__':
    im,code= image_code()
    print(code)
    im.show()


