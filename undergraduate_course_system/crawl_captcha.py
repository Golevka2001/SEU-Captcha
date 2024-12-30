import base64
import configparser
import os
from hashlib import md5
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

    # 由于存在特殊字符，所以用 label.txt 保存
    # 格式：{hash_val}.jpg\t{label}
    label_file_path = "dataset/labels.txt"
    hash_table = {}
    if not os.path.exists(label_file_path):
        os.mknod(label_file_path)
    with open(label_file_path, "r") as f:
        for line in f:
            file_name, label = line.strip().split("\t")
            hash_val = file_name.split(".")[0]
            hash_table[label] = hash_val

    # 初始化识别器
    charset = "1234567890+-x=?"
    ocr = ddddocr.DdddOcr()
    ocr.set_ranges(charset)

    # 获取 - 识别 - 人工校对 - 保存
    cnt = 0
    right = 0
    fig, ax = plt.subplots()
    ax.axis("off")
    img_display = ax.imshow([[0]], aspect="auto")
    while cnt < 100:
        # 获取验证码
        img = get_captcha_in_undergraduate_course_system()

        # 检查是否已存在
        # NOTE: 直接对img进行hash和存储后hash的结果不同
        img = Image.open(BytesIO(img))
        img.save("tmp.jpg")
        img = Image.open("tmp.jpg")
        calc_hash = md5(img.tobytes()).hexdigest()
        if calc_hash in hash_table.values():
            print("已存在")
            os.remove("tmp.jpg")
            continue

        # 显示
        img_display.set_data(img)
        plt.draw()
        plt.pause(0.1)

        # 验证码识别
        result = ocr.classification(img)
        result = ocr.classification(img, probability=True)
        s = ""
        for j in result["probability"]:
            s += result["charsets"][j.index(max(j))]
        result = s
        # print(result)

        # 输入验证码
        true_val = ""
        while true_val == "" or not set(true_val).issubset(set(charset)):
            true_val = input("按ENTER确认识别结果，或输入正确的验证码：")
            if true_val == "":
                true_val = result
                break
            # 修正
            true_val = true_val.replace("？", "?").replace("*", "x")
            if true_val[-1].isdigit():
                true_val = true_val + "=?"

        # 保存
        os.rename("tmp.jpg", f"dataset/images/{calc_hash}.jpg")
        hash_table[true_val] = calc_hash
        with open(label_file_path, "a") as f:
            f.write(f"{calc_hash}.jpg\t{true_val}\n")

        if true_val == result:
            right += 1
        cnt += 1
        print(f"当前正确率：{right}/{cnt}= {right/cnt*100:.2f}%")
    plt.close()
