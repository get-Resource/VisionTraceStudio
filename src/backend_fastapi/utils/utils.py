def convertFileSize(size):
    # 定义单位列表
    units = 'Bytes', 'KB', 'MB', 'GB', 'TB'
    # 初始化单位为Bytes
    unit = units[0]
    # 循环判断文件大小是否大于1024，如果大于则转换为更大的单位
    for i in range(1, len(units)):
        if size >= 1024:
            size /= 1024
            unit = units[i]
        else:
            break
    # 格式化输出文件大小，保留两位小数
    return size, unit
