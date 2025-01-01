import configparser
import json
import os
import sys
from io import BytesIO

import ddddocr
import matplotlib.pyplot as plt
from PIL import Image

sys.path.append("..")
from seu_auth import (
    get_pub_key,
    is_captcha_required,
    new_session,
    rsa_encrypt,
    seu_logout,
)


def trigger_captcha(session, username):
    while True:
        if is_captcha_required(session):
            break
        pub_key = get_pub_key(session)
        encrypted_password = rsa_encrypt("0", pub_key)
        res = session.post(
            url="https://auth.seu.edu.cn/auth/casback/casLogin",
            verify=False,
            data=json.dumps(
                {
                    "captcha": "",
                    "loginType": "account",
                    "mobilePhoneNum": "",
                    "mobileVerifyCode": "",
                    "password": encrypted_password,
                    "rememberMe": False,
                    "service": "",
                    "username": username,
                    "wxBinded": False,
                }
            ),
        )
    # print("触发验证码成功")


def get_captcha_in_auth_center(session=None):
    if not session:
        session = new_session()
    try:
        res = session.get(
            url="https://auth.seu.edu.cn/auth/casback/getCaptcha", verify=False
        )
        if res.status_code != 200:
            raise Exception(f"GET请求失败[{res.status_code}, {res.reason}]")
        img = res.content
        # print("获取验证码成功")
        return img
    except Exception as e:
        print("获取验证码失败，错误信息：", e)
        return None


def check_captcha_in_auth_center(session, username, password, captcha):
    pub_key = get_pub_key(session)
    encrypted_password = rsa_encrypt(password, pub_key)
    url = "https://auth.seu.edu.cn/auth/casback/casLogin"
    data = {
        "captcha": captcha,
        "loginType": "account",
        "mobilePhoneNum": "",
        "mobileVerifyCode": "",
        "password": encrypted_password,
        "rememberMe": False,
        "service": "",
        "username": username,
        "wxBinded": False,
    }
    res = session.post(url=url, data=json.dumps(data), verify=False)
    if res.status_code != 200:
        print(f"POST请求失败[{res.status_code}, {res.reason}]")
        return False
    if not res.json()["success"] and "验证码" in res.json()["info"]:
        print(res.json())
        print("识别错误")
        return False
    if not res.json()["success"]:
        print(res.json())
        print("其他错误")
        input("按ENTER继续")
        return False
    print("识别正确")
    seu_logout(session)
    return True


if __name__ == "__main__":
    # 读取配置文件，使用时须在`config.ini`中填入一卡通号和密码
    config = configparser.ConfigParser()
    config_file_name = (
        "local_config.ini" if os.path.exists("local_config.ini") else "config.ini"
    )
    config.read(config_file_name)
    username = config["ACCOUNT"]["username"]
    password = config["ACCOUNT"]["password"]

    label_file_path = "dataset/labels.txt"
    if not os.path.exists(label_file_path):
        os.makedirs("dataset/images", exist_ok=True)
        os.mknod(label_file_path)

    # 初始化识别器
    ocr = ddddocr.DdddOcr(
        # import_onnx_path="model/model.onnx",
        # charsets_path="model/charsets.json",
    )
    ocr.set_ranges(1)

    session = new_session()

    # 获取 - 识别 - 检查正误 - 保存
    cnt = 0
    correct_cnt = 0
    # fig, ax = plt.subplots()
    # ax.axis("off")
    # img_display = ax.imshow([[0]], aspect="auto")

    while cnt < 500:
        trigger_captcha(session, username)

        # 获取验证码
        img = get_captcha_in_auth_center(session)
        img = Image.open(BytesIO(img))

        # 显示
        # img_display.set_data(img)
        # plt.draw()
        # plt.pause(0.1)

        # 验证码识别
        # result = ocr.classification(img)
        result = ocr.classification(img, probability=True)
        s = ""
        for j in result["probability"]:
            s += result["charsets"][j.index(max(j))]
        result = s
        print(result)

        # 判断结果正误
        if not check_captcha_in_auth_center(session, username, password, result):
            cnt += 1
            continue

        # 保存
        result = result.lower()
        calc_hash = hash(img.tobytes())
        img.save(f"dataset/images/{result}_{calc_hash}.jpg")
        with open(label_file_path, "a") as f:
            f.write(f"{result}_{calc_hash}.jpg\t{result}\n")

        correct_cnt += 1
        cnt += 1
        print(f"当前正确率：{correct_cnt}/{cnt}= {correct_cnt/cnt*100:.2f}%")
    plt.close()
