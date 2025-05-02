# -*- coding: utf-8 -*-
# @time    : 2025/5/1 23:48
# @Author  : Sophomores
# @File    : __init__.py.py
# @Software: PyCharm

# diet_analyzer/__init__.py

# 从 evaluator 模块导入 Evaluation 类和其助手函数
from .evaluator import Evaluation, get_major_food_group_from_code, count_food_types

# 从 preprocessing 模块导入 clean_food_code 函数
from .preprocessing import clean_food_code, clean_food_code_main, find_project_root

# 定义 __all__ 列表，控制 'from diet_analyzer import *' 导入的内容
__all__ = [
    "Evaluation",
    "get_major_food_group_from_code",
    "count_food_types",
    "clean_food_code",
    "clean_food_code_main",
    "find_project_root",
]
