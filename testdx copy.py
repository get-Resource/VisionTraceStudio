from pathlib import Path
import zipfile
import os
 
# ZIP文件路径
zip_path = r"log.zip"
print(Path(zip_path).is_fifo())
# 要提取的文件名（在ZIP文件内）
filename = "example.txt"
 
# 打开ZIP文件
with zipfile.ZipFile(zip_path) as zf:
    print(zf.namelist())
    # 从ZIP文件中获取指定文件的二进制数据
    for name in zf.namelist():
        if not name.endswith("/"):
            os.makedirs(os.path.dirname(name),exist_ok=True)
            with open(name, "wb") as f:
                f.write(zf.read(name))
    
    # # 将文件保存到本地
    # with open("saved_file", "wb") as f:
    #     f.write(filedata)
        
print("文件已成功保存为 saved_file.")