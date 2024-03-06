import random
import colorsys
def generate_distinct_colors(num_colors):
    # 通过色相、饱和度和亮度来生成不同的颜色
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        saturation = 0.7
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append('#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)))
    return colors