# -*- coding: utf-8 -*-
# @time    : 2025/5/1 23:49
# @Author  : Sophomores
# @File    : preprocessing.py
# @Software: PyCharm

# diet_analyzer/preprocessing.py
import os
import pandas as pd


def clean_food_code(code):
    """
    标准化食物编码：。
    1. 将编码转换为字符串并去除首尾空白。
    2. 分离出可能的末尾 'x' 和前面的主体部分。
    3. 如果是纯数字，根据长度（<6）决定是否补零。
    4. 将处理好的数字部分与末尾的 'x' 重新组合。
    5. 如果主体部分不全由数字组成，返回原始字符串。
    """
    # 1. 将编码转换为字符串并去除首尾空白
    code_str = str(code).strip()

    # 2. 分离出可能的末尾 'x' 和前面的主体部分
    numeric_part = code_str
    suffix_x = ''
    # 检查是否以 'x' 结尾（不区分大小写）
    if code_str.lower().endswith('x'):
        numeric_part = code_str[:-1]  # 取除最后一个字符外的所有部分作为数字主体
        suffix_x = code_str[-1]  # 获取最后一个字符，即 'x' 或 'X'

    # 3. 根据长度决定是否补零
    if len(numeric_part) < 6:
        # 长度小于6，补零至6位
        padded_numeric_part = numeric_part.zfill(6)
        # 6. 将处理好的数字部分与末尾的 'x' 重新组合
        return padded_numeric_part + suffix_x
    else:
        # 长度等于或大于6（且假设没有 >6 情况，或大于等于6都不补零）
        # 直接返回原字符串，因为数字主体已经是6位或更长，且末尾的 x 也已包含在原字符串中
        return code_str


def clean_food_code_main(df):
    df['食物编码'] = df['食物编码'].apply(clean_food_code)

def find_project_root(marker='.git'):
    """
    从当前目录向上搜索，直到找到包含指定标记目录的父目录，将其视为项目根目录。

    Args:
        marker: 用于标识项目根目录的子目录名称列表，默认为 ['.git', '.idea']。
    Returns:
        str: 项目根目录的绝对路径，如果未找到标记目录，则返回 None。
    """
    # 获取当前脚本或 Notebook 的工作目录
    # 在 Jupyter Notebook 中，os.getcwd() 通常是 Notebook 文件所在的目录
    current_dir = os.path.abspath(os.getcwd())

    while True:
        # 检查当前目录是否包含任何一个标记目录
        if os.path.exists(os.path.join(current_dir, marker)):
            return current_dir  # 找到根目录，返回

        # 向上移动到父目录
        parent_dir = os.path.dirname(current_dir)
        current_dir = parent_dir
# Note: clean_food_code_main from your notebook is an example usage,
# not typically part of the core library functionality.
# You would apply the clean_food_code function to your DataFrame column
# in your main script after importing it.
