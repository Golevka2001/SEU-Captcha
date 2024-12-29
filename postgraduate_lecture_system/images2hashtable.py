import os
from hashlib import md5

from PIL import Image

hash_table = {}

for file in os.listdir("images"):
    if file == "tmp.jpg":
        os.remove(f"images/{file}")
        continue
    true_val, hash_val = file.split("_")
    hash_val = hash_val.split(".")[0]

    # 检查结果
    if len(true_val) != 4 or not true_val.isdigit():
        print(true_val)
        true_val = input("结果不正确，输入正确的验证码：")
        os.rename(f"images/{file}", f"images/{true_val}_{hash_val}.jpg")
        file = f"{true_val}_{hash_val}.jpg"

    # 检查哈希值
    img = Image.open(f"images/{file}")
    calc_hash = md5(img.tobytes()).hexdigest()
    if calc_hash != hash_val:
        print(f"{true_val}: {hash_val} -> {calc_hash}")
        input("HASH值错误，按ENTER确认重命名")
        os.rename(f"images/{file}", f"images/{true_val}_{calc_hash}.jpg")

    hash_table[true_val] = calc_hash

with open("hash_table.csv", "w") as f:
    for key, value in hash_table.items():
        f.write(f"{key},{value}\n")
