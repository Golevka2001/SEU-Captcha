import base64
import configparser
import os
import sys
import time
from hashlib import md5
from io import BytesIO

import ddddocr
import matplotlib.pyplot as plt
from PIL import Image

sys.path.append("..")
from seu_auth import seu_login


def login_postgraduate_lecture_system(username: str, password: str):
    """登录到研究生素质讲座系统，用于后续在此系统中进行其他操作。

    Args:
        username: 一卡通号
        password: 统一身份认证密码

    Returns:
        session: 登录到研究生素质讲座系统后的session
    """
    try:
        # 登录统一身份认证平台
        service_url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do"
        session, redirect_url = seu_login(username, password, service_url)
        if not session:
            raise Exception("统一身份认证平台登录失败")
        if not redirect_url:
            raise Exception("获取重定向url失败")

        # 访问研究生素质讲座系统页面
        res = session.get(url=redirect_url, verify=False)
        if res.status_code != 200:
            raise Exception(
                f"访问研究生素质讲座系统失败[{res.status_code}, {res.reason}]"
            )
        print("登录研究生素质讲座系统成功")
        return session
    except Exception as e:
        print("登录研究生素质讲座系统失败，错误信息：", e)
        return None


def get_captcha_in_postgraduate_lecture_system(session):
    """获取研究生素质讲座系统中的验证码图片。

    Args:
        session: 登录到研究生素质讲座系统后的session

    Returns:
        img: 验证码图片
    """
    try:
        res = session.post(
            url=f"https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/vcode.do?_={int(time.time() * 1000)}"
        )
        if res.status_code != 200:
            raise Exception(f"POST请求失败[{res.status_code}, {res.reason}]")
        img = base64.b64decode(res.json()["result"].split(",")[1])
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

    # 读取哈希表
    hash_table = {}
    with open("hash_table.csv", "r") as f:
        for line in f:
            key, value = line.strip().split(",")
            hash_table[key] = value

    ocr = ddddocr.DdddOcr()
    ocr.set_ranges("234567890")

    # 登录研究生素质讲座系统
    session = login_postgraduate_lecture_system(username, password)

    cnt = 0
    right = 0
    fig, ax = plt.subplots()
    ax.axis("off")
    img_display = ax.imshow([[0]])

    for i in range(100):
        # 获取验证码
        img = get_captcha_in_postgraduate_lecture_system(session)

        # 检查是否已存在
        img = Image.open(BytesIO(img))
        img.save(f"images/tmp.jpg")
        img = Image.open(f"images/tmp.jpg")
        calc_hash = md5(img.tobytes()).hexdigest()
        if calc_hash in hash_table.values():
            print("已存在")
            continue

        # 显示
        img_display.set_data(img)
        plt.draw()
        plt.pause(0.1)

        # 验证码识别
        result = ocr.classification(img, probability=True)
        s = ""
        for i in result["probability"]:
            s += result["charsets"][i.index(max(i))]
        print(s)

        # 输入验证码
        true_val = ""
        while len(true_val) != 4:
            true_val = input("按ENTER确认识别结果，或输入正确的验证码：")
            if true_val == "":
                true_val = s
                break

        # 保存
        os.rename(f"images/tmp.jpg", f"images/{true_val}_{calc_hash}.jpg")
        with open("hash_table.csv", "a") as f:
            f.write(f"{true_val},{calc_hash}\n")

        if true_val == s:
            right += 1
        cnt += 1
        print(f"当前正确率：{right}/{cnt}= {right/cnt*100:.2f}%")
    plt.close()