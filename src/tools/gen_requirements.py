# 导入所需的库
import os
import pipreqs

# 定义项目目录路径
project_path = '../src'

# 使用pipreqs生成requirements.txt文件
# pipreqs.generate(project_path)

out = os.popen(f"pipreqs {project_path} --encoding=utf8 --force").read()
