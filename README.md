# SEU-Captcha

通用的验证码识别模型准确率就那样，在抢课抢讲座的时候怎么能允许验证码输不对啦，所以收集了你车各网站的验证码（已知）。
包括**验证码接口**、**数据集（及生成方法）**、**模型**等。

目前包含以下几个：

| Website                                                                          | Accuracy           | Model                         | Folder                                                          |
| -------------------------------------------------------------------------------- | ------------------ | ----------------------------- | --------------------------------------------------------------- |
| [研究生素质讲座](https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do) | $\approx 100\\%$   | :white_check_mark:            | [./postgraduate_lecture_system/](./postgraduate_lecture_system) |
| [本科生选课](https://newxk.urp.seu.edu.cn/)                                      | $\approx 100\\%$   | :white_check_mark:            | [./undergraduate_course_system/](./undergraduate_course_system) |
| [身份认证中心【新】](https://auth.seu.edu.cn/dist/#/dist/main/login)             | $80\\% \sim 90\\%$ | :writing_hand:                | [./auth_center/](./auth_center)                                 |
| [统一身份认证【旧】](https://newids.seu.edu.cn/authserver)                       | $\leq 50\\%$       | :negative_squared_cross_mark: | [./new_ids/](./new_ids)                                         |

:calendar: *注：截至 2024/12/31*
