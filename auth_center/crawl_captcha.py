import os
from io import BytesIO

import ddddocr
import matplotlib.pyplot as plt
import requests
from PIL import Image


def get_captcha_in_auth_center():
    try:
        res = requests.get(
            url="https://auth.seu.edu.cn/auth/casback/getCaptcha", verify=False
        )
        if res.status_code != 200:
            raise Exception(f"GET请求失败[{res.status_code}, {res.reason}]")
        img = res.content
        print("获取验证码成功")
        return img
    except Exception as e:
        print("获取验证码失败，错误信息：", e)
        return None


if __name__ == "__main__":
    label_file_path = "dataset/labels.txt"
    if not os.path.exists(label_file_path):
        os.makedirs("dataset/images", exist_ok=True)
        os.mknod(label_file_path)

    # 初始化识别器
    ocr = ddddocr.DdddOcr()
    ocr.set_ranges(1)

    # 获取 - 识别 - 人工校对 - 保存
    cnt = 0
    correct_cnt = 0
    fig, ax = plt.subplots()
    ax.axis("off")
    img_display = ax.imshow([[0]], aspect="auto")

    while cnt < 100:
        # 获取验证码
        img = get_captcha_in_auth_center()

        # 显示
        img = Image.open(BytesIO(img))
        img_display.set_data(img)
        plt.draw()
        plt.pause(0.1)

        # 验证码识别
        # result = ocr.classification(img)
        result = ocr.classification(img, probability=True)
        s = ""
        for j in result["probability"]:
            s += result["charsets"][j.index(max(j))]
        result = s
        print(result)

        # 输入验证码
        true_val = ""
        while len(true_val) != 4 or not true_val.isalpha():
            true_val = input("按ENTER确认识别结果，或输入正确的验证码：")
            true_val = true_val.lower()
            if true_val == "":
                true_val = result
                break

        # 保存
        calc_hash = hash(img.tobytes())
        img.save(f"dataset/images/{true_val}_{calc_hash}.jpg")
        with open(label_file_path, "a") as f:
            f.write(f"{true_val}_{calc_hash}.jpg\t{true_val}\n")

        if true_val == result:
            correct_cnt += 1
        cnt += 1
        print(f"当前正确率：{correct_cnt}/{cnt}= {correct_cnt/cnt*100:.2f}%")
    plt.close()
