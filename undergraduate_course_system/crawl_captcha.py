import base64
import configparser
import os
from io import BytesIO

import ddddocr
import matplotlib.pyplot as plt
import requests
from PIL import Image


def get_captcha_in_undergraduate_course_system():
    """获取本科生选课系统中的验证码图片。（注：这个无需登录）

    Returns:
        img: 验证码图片
    """
    try:
        res = requests.post(
            url="https://newxk.urp.seu.edu.cn/xsxk/auth/captcha", verify=False
        )
        if res.status_code != 200:
            raise Exception(f"POST请求失败[{res.status_code}, {res.reason}]")
        img = base64.b64decode(res.json()["data"]["captcha"].split(",")[1])
        print("获取验证码成功")
        return img
    except Exception as e:
        print("获取验证码失败，错误信息：", e)
        return None


if __name__ == "__main__":
    # 读取配置文件，使用时须在`config.ini`中填入一卡通号和密码
    config = configparser.ConfigParser()
    config_file_name = (
        "local_config.ini" if os.path.exists("local_config.ini") else "config.ini"
    )
    config.read(config_file_name)
    username = config["ACCOUNT"]["username"]
    password = config["ACCOUNT"]["password"]

    # 初始化识别器
    charset = "1234567890+-x=?"
    ocr = ddddocr.DdddOcr(
        import_onnx_path="model/model.onnx",
        charsets_path="model/charsets.json",
    )
    ocr.set_ranges(charset)

    # 获取 - 识别 - 人工校对 - 保存
    cnt = 0
    correct_cnt = 0
    fig, ax = plt.subplots()
    ax.axis("off")
    img_display = ax.imshow([[0]], aspect="auto")

    # 加载./dataset/images/下的图片
    local_imgs = os.listdir("./dataset/images/")
    while cnt < 100:
        # 获取验证码
        img = get_captcha_in_undergraduate_course_system()

        # 显示
        img = Image.open(BytesIO(img))
        img_display.set_data(img)
        plt.draw()
        plt.pause(0.1)

        # 验证码识别
        result = ocr.classification(img)
        # result = ocr.classification(img, probability=True)
        # s = ""
        # for j in result["probability"]:
        #     s += result["charsets"][j.index(max(j))]
        # result = s
        print(result)

        # 判断结果正误
        is_correct = input("是否正确？(y/n): ")
        if is_correct == "y":
            correct_cnt += 1

        cnt += 1
        print(f"当前正确率：{correct_cnt}/{cnt}= {correct_cnt/cnt*100:.2f}%")
    plt.close()
