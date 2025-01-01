# SEU-Captcha

通用的验证码识别模型准确率就那样，在抢课抢讲座的时候怎么能允许验证码输不对啦，所以收集了你车几个网站的验证码（已知），顺带训练了一下模型。

包括了**验证码接口**、**数据集（及生成方法）**、**模型**等。

目前包含以下几个：

| Website                                                                          | Accuracy           | Model                         | Folder                                                          |
| -------------------------------------------------------------------------------- | ------------------ | ----------------------------- | --------------------------------------------------------------- |
| [研究生素质讲座](https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do) | $\approx 100\\%$   | :white_check_mark:            | [./postgraduate_lecture_system/](./postgraduate_lecture_system) |
| [本科生选课](https://newxk.urp.seu.edu.cn/)                                      | $\approx 100\\%$   | :white_check_mark:            | [./undergraduate_course_system/](./undergraduate_course_system) |
| [身份认证中心【新】](https://auth.seu.edu.cn/dist/#/dist/main/login)             | $80\\% \sim 90\\%$ | :writing_hand:                | [./auth_center/](./auth_center)                                 |
| [统一身份认证【旧】](https://newids.seu.edu.cn/authserver)                       | $\leq 50\\%$       | :negative_squared_cross_mark: | [./new_ids/](./new_ids)                                         |

:calendar: *注：截至 2024/12/31*

## Dependencies

验证码识别直接使用了 [DdddOcr](https://github.com/sml2h3/ddddocr)，训练也就用了它提供的工具 [dddd_trainer](https://github.com/sml2h3/dddd_trainer)。（没啥讲究，挑了个简单的，反正数据集有了想用别的都随意）

[选课系统的验证码生成](./undergraduate_course_system/gen_captcha.jar)需要用到 JDK17（其他版本未测试）及 [Easy-Captcha](https://gitee.com/ele-admin/EasyCaptcha)（已打包在 jar 中，无需额外安装）。

[requirements.txt](./requirements.txt) 中列出了**爬取、识别**所需的依赖，训练过程所需的依赖请参考 dddd_trainer 的文档。

## Usage

- 以下是直接使用训练好的模型的方法：

    ```python
    from ddddocr import DdddOcr

    ocr = DdddOcr(
        import_onnx_path="path/to/model/model.onnx",
        charsets_path="path/to/model/charsets.json",
    )

    # img_bytes = ...
    result_str = ocr.classification(img_bytes)
    ```

    *注：如果需要在其他语言中使用，[DdddOcr 文档](https://github.com/sml2h3/ddddocr?tab=readme-ov-file#%E7%9B%B8%E5%85%B3%E6%8E%A8%E8%8D%90%E6%96%87%E7%AB%A0or%E9%A1%B9%E7%9B%AE) 中好像也提供了 JS、Rust 等版本。*

- 或者需要训练模型，那么各子目录下的 `dataset/` 目录下是已经爬下来打好标签的数据集
  - `dataset/images/` 下是验证码图片，一般会命名为 `{label}_{hash}.jpg`；对于存在特殊字符的验证码则使用 `{hash}.jpg`，标签存储在下面的 `labels.txt` 中
  - `dataset/labels.txt` 是标签文件，每行一个文件，格式为 `{file_name}\t{label}`

  *注：[undergraduate_course_system](./undergraduate_course_system) 目录下没有 `dataset/`，因为可以本地大量生成*

- 或者你想要爬取、生成更多训练数据，请参考各子目录的 README。
