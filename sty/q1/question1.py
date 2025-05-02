# %%
import pandas as pd
import numpy as np

# %%
man_data_file_path = r'../处理后的数据/附件1_处理_final.xlsx'
woman_data_file_path = r'../处理后的数据/附件2_处理_final.xlsx'
# %%
df_man_origin = pd.read_excel(man_data_file_path)
df_woman_origin = pd.read_excel(woman_data_file_path)
df_man = df_man_origin.copy()
df_woman = df_woman_origin.copy()
df_man.name = '男学生'
df_woman.name = '女学生'


# %%
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


clean_food_code_main(df_man)
clean_food_code_main(df_woman)
# %% md
# ## 1．分析食物结构
# 代码
#
#
# 按类别将食谱中食物归类排序，
# - 列出每种食物的数量
# - 分析五大类别食物是否齐全
#
# （1）谷、薯类；01,02
#
# （2）蔬菜、菌藻、水果类； 04,05,06
#
# （3）畜、禽、鱼、蛋类及制品；08,09,12,11
#
# （4）奶、干豆、坚果、种子类及制品；10, ,07,
#
# （5）植物油类。
#
# - 食物种类是否大于12种
# - 周食谱评价要求大于25种
# %%
five_major_food_names = ["谷、薯类", "蔬菜、菌藻、水果类", "畜、禽、鱼、蛋类及制品", "奶、干豆、坚果、种子类及制品", "植物油类"]

five_major_food_groups = [
    {"谷类及制品": "01", "薯类、淀粉及制品": "02"},
    {"蔬菜类及制品": "04", "菌藻类": "05", "水果类及制品": "06"},
    {"畜肉类及制品": "08", "禽肉类及制品": "09", "鱼虾蟹贝类": "12", "蛋类及制品": "11"},
    {"乳类及制品": "10", "干豆类及制品": "03", "坚果、种子类": "07"},
    {"植物油类": "18"}
]

# %%
# 建立编号和组名的映射
code_to_group_map = {}
for i, group_codes_dict in enumerate(five_major_food_groups):
    group_name = five_major_food_names[i]

    for _, code in group_codes_dict.items():
        code_to_group_map[code] = group_name
code_to_group_map


# %% md
# 代码思路:
#
# 读取男女生的表,
#
# 按照食物编码进行统计数量, 怎么得出每一种的数量?
#
# 将男女生的食物编码进行拆分, 保留前两个数字, 设为新列, 即为类别编码,
#
#
# %% md
# ### 1.1 统计食物数量, 即每种食物的克重
# %%
# 计算每个食物的总克重
def calculate_total_grams(df):
    """
    :param df: 男/女生数据的Dataframe
    :return: 返回各食物的数量
    """
    print("--- 1.1 统计食物数量, 即每种食物的克重 ---")
    df['食物重量(克)'] = df['可食部（克/份）'] * df['食用份数']
    food_quantities_summary = df.groupby('食物名称')['食物重量(克)'].sum().reset_index()
    print(food_quantities_summary)
    return food_quantities_summary

# %% md
# ### 1.2 分析五大类别食物是否齐全
# %%
def get_food_categories(df):
    # 定义一个函数，根据食物编码获取其所属的五大类别名称或标记为“其他类别”
    def get_major_food_group_from_code(food_code, code_to_group_map):
        """
        根据食物编码的前两位查找对应的五大类别名称。
        非五大类别，则返回 '其他类别'。
        """
        code = food_code[:2]
        # 使用 字典的.get() 方法，如果在映射中找不到前缀，返回 '其他类别'
        return code_to_group_map.get(code, '其他类别')

    print(f"--- 1.2 分析{df.name}每日食谱五大类别食物是否齐全 ---")
    # 应用函数，创建 '食物类别' 新列
    df['食物类别'] = df['食物编码'].apply(lambda x: get_major_food_group_from_code(x, code_to_group_map))
    # 获取食谱中实际包含的五大类别（排除“其他类别”）
    categories_present = df[df['食物类别'] != '其他类别']['食物类别'].unique().tolist()

    # 检查哪些五大类别是包含的，哪些是不包含的
    print("五大类别食物包含情况:")
    missing_categories = []
    for group_name in five_major_food_names:
        is_present = group_name in categories_present
        print(f"   - {group_name}: {'包含 ✅' if is_present else '不包含 ❌'}")
        if not is_present:
            missing_categories.append(group_name)

    # 判断是否五大类别齐全
    all_five_present = len(missing_categories) == 0
    print(f"五大类别是否齐全: {'是 ✅' if all_five_present else '否 ❌'}")

    # 输出缺少的类别（如果存在）
    if missing_categories:
        print(f"缺少的五大类别: {', '.join(missing_categories)}")
    else:
        print("所有五大类别都已包含。")

    # 检查是否有食物被归类到“其他类别”
    other_category_items = df[df['食物类别'] == '其他类别']['主要成分'].unique().tolist()
    if other_category_items:
        print("-" * 50)
        print(f"以下主要成分未能归入五大类别，被标记为 '其他类别':\n {', '.join(other_category_items)}")

# %%
get_food_categories(df_man)

# %% md
# ### 1.3 食物种类是否大于12种
# %%
def count_food_types(df):
    print(f"--- 1.3 {df.name}每日食谱食物种类数量分析 ---")
    unique_food_types_count = df['食物名称'].nunique()
    print(f"食物种类数量: {unique_food_types_count} 种")
    print(f"（要求日食谱 > 12 种）")
    if unique_food_types_count > 12:
        print("食物种类数量达标 ✅")
    else:
        print("每日食物种类数量不达标 ❌")

# %%
count_food_types(df_man)


# %% md
# ## 2. 计算食谱的主要营养素含量
#
# 查出每100克可食部食物所含主要营养素的数量，从而算出食谱中各种主要营养素的含量
#
# 主要营养素: 碳水化合物、脂肪、蛋白质、矿物质、维生素、水
#
# 产能营养素: 碳水化合物、脂肪、蛋白质
# %%
def calculate_nutrient_intakes(df):
    """
    :param df:
    :return: intick_dict Dict（一日各营养素摄入量及能量总量）
    :return: df_meal DataFrame（餐次的各营养素摄入量及能量总量）
    """

    weight_col = '食物重量(克)'
    if not weight_col in df.columns:
        df[weight_col] = df['可食部（克/份）'] * df['食用份数']

    # --- 2.1 计算食谱的主要营养素摄入量 ---
    print(f"--- 2.1 计算{df.name}食谱的主要营养素含量 ---")

    # 定义需要计算摄入量的营养素列名列表
    nutrient_cols_to_calculate = df_man_origin.columns.to_list()[6:]

    for nutrient_col_100g in nutrient_cols_to_calculate:
        # 提取营养素名称和单位 (例如 '蛋白质', 'g')
        parts = nutrient_col_100g.replace(')', '').split('(')
        # 营养素名字
        nutrient_name = parts[0].strip()
        # 单位名称
        unit_info = parts[1].strip()  # 例如 'g/100g', 'mg/100g'
        # 摄入单位
        intake_unit = unit_info.split('/')[0]  # 例如 'g', 'mg'
        # 构建新的摄入量列名
        intake_col_name = f'{nutrient_name}摄入量 ({intake_unit})'

        # 使用向量化计算： (总克重 / 100) * 每100克含量
        # 创建新列 列名: 营养素名称
        df[intake_col_name] = (df[weight_col] / 100) * df[nutrient_col_100g]

    # --- 2.2 计算一日总营养素摄入量 ---
    print(f"\n--- 计算{df.name}一日总营养素摄入量 ---")

    dict_intake = {}

    # 添加所有新计算的列的列名称为列表
    intake_cols = [col for col in df.columns if '摄入量 (' in col and col.endswith(')')]

    for intake_col in intake_cols:
        # 计算列摄入量总和
        total_intake = df[intake_col].sum()
        # 创建字典 营养素名: 每日营养素摄入总含量
        dict_intake[intake_col] = total_intake
        # 提取单位进行打印，例如 '蛋白质摄入量 (g)' -> g

        # 取出str中的单位
        unit = intake_col.split('(')[-1].replace(')', '')

        print(f"  {intake_col.split('摄入量')[0].strip()} 总摄入量: {total_intake:.2f} {unit}")

    # --- 2.3 计算总能量 ---
    energy_conversion = {'蛋白质': 4, '脂肪': 9, '碳水化合物': 4}  # kcal/g

    # energy_conversion = {'蛋白质': 4, '脂肪': 9, '碳水化合物': 4, '膳食纤维': 2}
    # 宏量营养素的总能量
    total_calculated_energy_kcal = 0

    for substance in energy_conversion.keys():
        # 获取宏量营养素的摄入量
        total_g = dict_intake.get(substance + '摄入量 (g)', 0)

        # 计算宏量营养素的能量
        energy_kcal = total_g * energy_conversion[substance]
        # 创建对应的列
        df[substance + '能量摄入量 (kcal)'] = energy_kcal
        total_calculated_energy_kcal += energy_kcal

    # 将总能量添加到日摄入量字典中
    dict_intake['总能量摄入量 (kcal)'] = total_calculated_energy_kcal

    print(f"\n一日总能量摄入量: {total_calculated_energy_kcal:.2f} kcal")

    # --- 2.4 计算每餐总营养素摄入量及能量 ---
    print("\n--- 计算一日每餐次总能量摄入量 ---")
    energy_substance = [col + '摄入量 (g)' for col in energy_conversion.keys()]
    df_meal = df.groupby('餐次')[energy_substance].sum()
    df_meal['总能量摄入量 (kcal)'] = df_meal.sum(axis=1)
    print(df_meal.round(5)[['总能量摄入量 (kcal)']])
    return dict_intake, df_meal


calculate_nutrient_intakes(df_man)
calculate_nutrient_intakes(df_woman)
# %% md
# ## 3. 评价食谱提供的能量、餐次比及非产能主要营养素含量
# 根据
# - 每日能量摄入目标
# - 餐次比参考值
# - 以及非产能主要营养素钙、铁、锌、维生素A、维生素B1、维生素B2、维生素C的参考摄入量
#
# 对食谱进行评价。
#






