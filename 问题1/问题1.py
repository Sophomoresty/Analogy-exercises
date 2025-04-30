#%%
import pandas as pd
import numpy as np
#%%
man_data_file_path = r'../处理后的数据/附件1_处理_final.xlsx'
woman_data_file_path = r'../处理后的数据/附件2_处理_final.xlsx'
#%%
df_man = pd.read_excel(man_data_file_path)
df_woman = pd.read_excel(woman_data_file_path)
df_man.name = '男学生'
df_woman.name = '女学生'
#%%
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
#%% md
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
#%%
five_major_food_names = ["谷、薯类", "蔬菜、菌藻、水果类", "畜、禽、鱼、蛋类及制品", "奶、干豆、坚果、种子类及制品", "植物油类"]

five_major_food_groups = [
    {"谷类及制品": "01", "薯类、淀粉及制品": "02"},
    {"蔬菜类及制品": "04", "菌藻类": "05", "水果类及制品": "06"},
    {"畜肉类及制品": "08", "禽肉类及制品": "09", "鱼虾蟹贝类": "12", "蛋类及制品": "11"},
    {"乳类及制品": "10", "干豆类及制品": "03", "坚果、种子类": "07"},
    {"植物油类": "18"}
]

five_major_food_groups_dict = {
    "names": five_major_food_names,
    "code": five_major_food_groups,
}
#%%
# 建立编号和组名的映射
code_to_group_map = {}
for i, group_codes_dict in enumerate(five_major_food_groups):
    group_name = five_major_food_names[i]

    for _, code in group_codes_dict.items():
        code_to_group_map[code] = group_name
code_to_group_map
#%% md
# 代码思路:
# 
# 读取男女生的表,
# 
# 按照食物编码进行统计数量, 怎么得出每一种的数量?
# 
# 将男女生的食物编码进行拆分, 保留前两个数字, 设为新列, 即为类别编码,
# 
# 
#%% md
# ### 1.1 统计食物数量, 即每种食物的克重
#%%
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


food_quantities_summary_man = calculate_total_grams(df_man)
food_quantities_summary_woman = calculate_total_grams(df_woman)
# print(food_quantities_summary_man)
#%% md
# ### 1.2 分析五大类别食物是否齐全，
#%%
def get_food_categories(df):
    # 定义一个函数，根据食物编码获取其所属的五大类别名称或标记为“其他类别”
    def get_major_food_group_from_code(food_code, code_to_group_map):
        """
        根据食物编码的前两位查找对应的五大类别名称。
        如果找不到匹配的前缀，则返回 '其他类别'。
        """
        code = food_code[:2]
        # 使用 字典的.get() 方法，如果在映射中找不到前缀，返回 '其他类别'
        return code_to_group_map.get(code, '其他类别')

    print("--- 1.2 分析五大类别食物是否齐全 ---")

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
#%%
get_food_categories(df_man)
#%% md
# ### 1.3 食物种类是否大于12种
#%%
def count_food_types(df):
    print("--- 1.3 每日食谱食物种类数量分析 ---")
    unique_food_types_count = df['食物名称'].nunique()
    print(f"食物种类数量: {unique_food_types_count} 种")
    print(f"（要求日食谱 > 12 种）")
    if unique_food_types_count > 12:
        print("食物种类数量达标 ✅")
    else:
        print("每日食物种类数量不达标 ❌")
#%%
count_food_types(df_man)
#%% md
# ## 2. 计算食谱的主要营养素含量
# 
# 查出每100克可食部食物所含主要营养素的数量，从而算出食谱中各种主要营养素的含量
# 
# 主要营养素: 碳水化合物、脂肪、蛋白质、矿物质、维生素、水
# 
# 产能营养素: 碳水化合物、脂肪、蛋白质
#%%
def calculate_nutrient_intakes(
        df:pd.DataFrame,
):
    """
    :param df:
    :return: daily_nutrient_intake Dict（一日各营养素摄入量及能量总量）
    :return: meal_nutrient_intake DataFrame（餐次的各营养素摄入量及能量总量）

    """
    student_id = df.name
    weight_col = '食物重量(克)'
    if not weight_col in df.columns:
        df[weight_col] = df['可食部（克/份）'] * df['食用份数']

    # --- 2.1 计算食谱的主要营养素含量 ---
    print(f"--- 2.1 计算{student_id}食谱的主要营养素含量 ---")
    # 定义需要计算摄入量的营养素列名列表

    nutrient_cols_to_calculate = ['碳水化合物 (g/100g)',
                                  '蛋白质 (g/100g)', '脂肪 (g/100g)',
                                  '钙 (mg/100g)', '铁 (mg/100g)', '锌 (mg/100g)',
                                  '维生素A (μg/100g)', '维生素B1 (mg/100g)', '维生素B2 (mg/100g)', '维生素C (mg/100g)',
                                  '异亮氨酸 (g/100g)', '亮氨酸 (g/100g)', '赖氨酸 (g/100g)', '含硫氨基酸 (g/100g)',
                                  '芳香族氨基酸 (g/100g)',
                                  '苏氨酸 (g/100g)', '色氨酸 (g/100g)', '缬氨酸 (g/100g)']
    # 创建一个新的 DataFrame 来存储每行的营养素摄入量，或者直接添加到 df
    # 这里直接添加到 df 中，创建新的列
    # 新列的命名格式例如：'蛋白质摄入量 (g)', '钙摄入量 (mg)'

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
        # 检查必需的列是否存在且是数值类型
        if weight_col in df.columns and\
                pd.api.types.is_numeric_dtype(df[weight_col]) and \
                pd.api.types.is_numeric_dtype(df[nutrient_col_100g]):

            # 使用向量化计算： (总克重 / 100) * 每100克含量
            df[intake_col_name] = (df[weight_col] / 100) * df[nutrient_col_100g]

        else:
            print(f"警告：计算 '{nutrient_name}' 摄入量所需列缺失或非数值类型。跳过计算。")
            df[intake_col_name] = 0  # 或者 pd.NA


    # --- 2.2 计算一日总营养素摄入量 ---
    print(f"\n--- 计算{student_id}一日总营养素摄入量 ---")
    daily_nutrient_intake = {}

    # 找到所有新创建的摄入量列
    intake_cols = [col for col in df.columns if '摄入量 (' in col and col.endswith(')')]

    for intake_col in intake_cols:
        total_intake = df[intake_col].sum()
        daily_nutrient_intake[intake_col] = total_intake
        # 提取单位进行打印，例如 '蛋白质摄入量 (g)' -> g

        # 单位
        unit = intake_col.split('(')[-1].replace(')', '')

        print(f"  {intake_col.split('摄入量')[0].strip()} 总摄入量: {total_intake:.2f} {unit}")

    # --- 2.3 计算总能量 ---

    energy_conversion = {'蛋白质': 4, '脂肪': 9, '碳水化合物': 4, '膳食纤维': 2}  # kcal/g

    # 获取计算能量所需的宏量营养素总摄入量 (确保单位是克 g)
    protein_total_g = daily_nutrient_intake.get('蛋白质摄入量 (g)', 0)
    fat_total_g = daily_nutrient_intake.get('脂肪摄入量 (g)', 0)
    carb_total_g = daily_nutrient_intake.get('碳水化合物摄入量 (g)', 0)
    # fiber_total_g = daily_nutrient_intake.get('膳食纤维摄入量 (g)', 0)

    # 计算各自的能量贡献 (kcal)
    protein_energy_kcal = protein_total_g * energy_conversion['蛋白质']
    fat_energy_kcal = fat_total_g * energy_conversion['脂肪']
    carb_energy_kcal = carb_total_g * energy_conversion['碳水化合物']

    # fiber_energy_kcal = fiber_total_g * energy_conversion['膳食纤维']

    # 计算总能量摄入 (包含膳食纤维的能量)
    total_calculated_energy_kcal = protein_energy_kcal + fat_energy_kcal + carb_energy_kcal

    # 将总能量添加到日摄入量字典中
    daily_nutrient_intake['总能量摄入量 (kcal)'] = total_calculated_energy_kcal

    print(f"\n一日总能量摄入量: {total_calculated_energy_kcal:.2f} kcal")

    # --- 2.4 计算每餐总营养素摄入量及能量 ---
    print("\n--- 计算一日每餐次总能量摄入量 ---")

    # 使用 groupby('餐次') 对所有摄入量列求和
    meal_nutrient_intake = df_man.groupby('餐次')[intake_cols].sum()
    # 如果没有直接能量列，且需要精确计算每餐能量：
    # 需要按餐汇总蛋白质、脂肪、碳水化合物、膳食纤维的克重，再乘以能量转换系数
    meal_energy_kcal = (meal_nutrient_intake.get('蛋白质摄入量 (g)', 0) * energy_conversion['蛋白质'] +
                        meal_nutrient_intake.get('脂肪摄入量 (g)', 0) * energy_conversion['脂肪'] +
                        meal_nutrient_intake.get('碳水化合物摄入量 (g)', 0) * energy_conversion['碳水化合物'] +
                        meal_nutrient_intake.get('膳食纤维摄入量 (g)', 0) * energy_conversion['膳食纤维'])
    meal_nutrient_intake['总能量摄入量 (kcal)'] = meal_energy_kcal
    print(meal_nutrient_intake.round(5)[['总能量摄入量 (kcal)']])
    return daily_nutrient_intake,meal_nutrient_intake
#%%
daily_nutrient_intake_man,meal_nutrient_intake_man = calculate_nutrient_intakes(df_man)
#%% md
# ## 3. 评价食谱提供的能量、餐次比及非产能主要营养素含量
# 根据
# - 每日能量摄入目标
# - 餐次比参考值
# - 以及非产能主要营养素钙、铁、锌、维生素A、维生素B1、维生素B2、维生素C的参考摄入量
# 
# 对食谱进行评价。
# 
#%%
import pandas as pd


# 假设 standards 字典已在您的代码开头定义，包含以下结构：
# standards = {
#     'energy_target': {'男': 2400, '女': 1900}, # kcal/d
#     'meal_ratio_range': {'早餐': (0.25, 0.35), '午餐': (0.30, 0.40), '晚餐': (0.30, 0.40)}, # 注意这里使用附件4评价原则中的范围
#     'micro_target': { # RNI/AI
#         '男': {'钙': 800, '铁': 12, '锌': 12.5, '维生素A': 800, '维生素B1': 1.4, '维生素B2': 1.4, '维生素C': 100}, # mg/d 或 μgRE/d
#         '女': {'钙': 800, '铁': 20, '锌': 7.5, '维生素A': 700, '维生素B1': 1.2, '维生素B2': 1.2, '维生素C': 100}
#     },
#     'rounding_decimals': 5 # 或者根据附件4要求设置为 2
#     # ... 其他标准 ...
# }

# 确保您在 Problem 1.1 Step 2 计算得到的 daily_intake 字典中包含如下键：
# '总能量摄入量 (kcal)'
# '钙摄入量 (mg)', '铁摄入量 (mg)', '锌摄入量 (mg)', '维生素A摄入量 (μg)', '维生素B1摄入量 (mg)', '维生素B2摄入量 (mg)', '维生素C摄入量 (mg)'
# 注意单位要匹配！如果计算出来的维生素A单位是 μg，但标准是 μgRE，可能需要根据食物成分表转换系数进行转换，或者在评价时说明假设 μg = μgRE。
# 如果您的食物成分表提供的营养素单位与 standards 不一致，需要进行单位转换，或者调整 standards。
# 这里假设 daily_intake 字典中的单位与 standards['micro_target'] 中的目标值单位是一致的。

# 确保您在 Problem 1.1 Step 2 计算得到的 meal_intake DataFrame 中包含如下列：
# '总能量摄入量 (kcal)'

# --- 评价函数：评价能量 (Problem 1.1 步骤 3.1) ---

def evaluate_energy(daily_intake: dict, standards: dict, gender: str, rounding_decimals: int) -> dict:
    """
    评价一日总能量摄入量是否符合个体需要 (根据附件4评价原则1)。

    Args:
        daily_intake: 包含一日总营养素摄入量的字典（需包含 '总能量摄入量 (kcal)' 键）。
        standards: 包含能量目标 ('energy_target' 键) 的评价标准的字典。
        gender: 学生性别 ('男' 或 '女')。
        rounding_decimals: 结果中百分比和实际摄入量保留的小数位数。

    Returns:
        包含能量评价结果的字典：actual_kcal, target_kcal, percentage_of_target, comment。
    """

    evaluation_results = {}
    # 从 daily_intake 字典中获取实际总能量，如果不存在则为 0
    actual_energy_kcal = daily_intake.get('总能量摄入量 (kcal)', 0)
    # 从 standards 字典中获取该性别的能量目标，如果不存在则为 None
    target_energy_kcal = standards['energy_target'].get(gender)

    # 存储实际摄入量，并进行四舍五入
    evaluation_results['actual_kcal'] = round(actual_energy_kcal, rounding_decimals)

    # 打印评价头部信息
    print("\n--- 能量评价 ---")

    if target_energy_kcal is None:
        # 如果标准缺失
        evaluation_results['target_kcal'] = None
        evaluation_results['percentage_of_target'] = None
        evaluation_results['comment'] = "标准缺失"
        print("  评价: 标准缺失，无法评价。")
    else:
        # 存储目标摄入量
        evaluation_results['target_kcal'] = target_energy_kcal
        print(f"  目标: {target_energy_kcal:.2f} kcal") # 目标通常打印2位小数

        if target_energy_kcal > 0:
            # 计算实际摄入占目标的百分比
            percentage = (actual_energy_kcal / target_energy_kcal) * 100
            # 存储并四舍五入百分比
            evaluation_results['percentage_of_target'] = round(percentage, rounding_decimals)

            print(f"  实际: {actual_energy_kcal:.{rounding_decimals}f} kcal") # 实际摄入量按指定小数位打印
            print(f"  占目标比例: {percentage:.2f}%") # 百分比通常打印2位小数

            # --- 评价结论 (根据附件4评价原则1：符合个体需要) ---
            # 这里简单判断是否达到或超过目标
            if percentage >= 100:
                 evaluation_results['comment'] = "达标或偏高"
                 print("  评价: 达标或偏高 ✅")
            else: # percentage < 100
                 evaluation_results['comment'] = "偏低"
                 print("  评价: 偏低 ❌")

        else:
            # 如果目标为零，通常是数据错误或标准设置问题
            evaluation_results['percentage_of_target'] = None
            evaluation_results['comment'] = "目标为零，无法评价"
            print("  评价: 目标为零，无法评价。")

    return evaluation_results

# --- 评价函数：评价餐次比 (Problem 1.1 步骤 3.2) ---

def evaluate_meal_ratio(meal_intake: pd.DataFrame, daily_intake: dict, standards: dict, rounding_decimals: int) -> dict:
    """
    评价三餐供能比是否在推荐范围内 (根据附件4评价原则2)。

    Args:
        meal_intake: 包含每餐总营养素摄入量的 DataFrame（需包含 '总能量摄入量 (kcal)' 列）。
        daily_intake: 包含一日总能量的字典（需包含 '总能量摄入量 (kcal)' 键）。
        standards: 包含餐次比范围 ('meal_ratio_range' 键) 的评价标准的字典。例如: {'早餐': (0.25, 0.35), ...}。
        rounding_decimals: 结果中百分比和实际摄入量保留的小数位数。

    Returns:
        包含每餐供能比评价结果的字典。'meal_ratios' 键下是各餐次的评价结果，还有 'total_daily_energy' 和 'overall_comment'。
    """
    evaluation_results = {}
    # 获取一日总能量，如果不存在或为0则无法计算餐次比
    total_daily_energy = daily_intake.get('总能量摄入量 (kcal)', 0)
    meal_energy_col = '总能量摄入量 (kcal)' # 每餐总能量在 meal_intake 中的列名
    # 获取餐次比目标范围字典
    meal_ratio_ranges = standards.get('meal_ratio_range')

    print("\n--- 餐次比评价 ---")

    # --- 安全性检查：确保计算所需数据和标准存在 ---
    if total_daily_energy <= 0:
         evaluation_results['comment'] = "日总能量为零或缺失，无法计算餐次比"
         print("  评价: 日总能量为零或缺失，无法计算餐次比。")
         return evaluation_results
    if meal_energy_col not in meal_intake.columns or meal_intake.empty:
         evaluation_results['comment'] = "每餐能量数据缺失或为空，无法计算餐次比"
         print("  评价: 每餐能量数据缺失或为空，无法计算餐次比。")
         evaluation_results['total_daily_energy'] = round(total_daily_energy, rounding_decimals) # 仍然存储日总能量
         return evaluation_results
    if meal_ratio_ranges is None or not isinstance(meal_ratio_ranges, dict):
         evaluation_results['comment'] = "餐次比标准缺失或格式不正确，无法评价"
         print("  评价: 餐次比标准缺失或格式不正确，无法评价。")
         evaluation_results['total_daily_energy'] = round(total_daily_energy, rounding_decimals)
         return evaluation_results


    evaluation_results['total_daily_energy'] = round(total_daily_energy, rounding_decimals)
    evaluation_results['meal_ratios'] = {}
    evaluation_results['overall_comment'] = "达标 ✅" # 乐观初始化整体评价

    # 定义常见的餐次顺序，以便按顺序打印和评价
    meal_order = ['早餐', '午餐', '晚餐'] # 根据附件表格顺序

    # --- 遍历每餐进行评价 ---
    for meal in meal_order:
        # 从 meal_intake DataFrame 中获取该餐的能量，如果该餐不存在则为 0
        meal_energy = meal_intake.loc[meal, meal_energy_col] if meal in meal_intake.index and meal_energy_col in meal_intake.columns else 0
        # 计算该餐能量占日总能量的百分比 (转换为 0-1 范围的小数)
        meal_percentage = (meal_energy / total_daily_energy) if total_daily_energy > 0 else 0
        # 获取该餐的推荐范围 (0-1 范围的小数对)
        target_range = meal_ratio_ranges.get(meal)

        meal_eval = {
            'actual_kcal': round(meal_energy, rounding_decimals), # 存储实际能量
            'actual_percentage': round(meal_percentage * 100, rounding_decimals), # 存储实际百分比 (0-100)
            'target_range_percent': None, # 存储目标范围百分比 (0-100)
            'comment': "标准缺失" # 初始化评价结论
        }
        evaluation_results['meal_ratios'][meal] = meal_eval # 将单餐评价结果添加到字典中


        print(f"  {meal} 供能:")

        if target_range is None:
             # 如果该餐的标准缺失
             print("    标准缺失，无法评价。")
             # 整体评价更新为部分标准缺失
             if evaluation_results['overall_comment'] == "达标 ✅": # 避免覆盖已有偏离警告
                  evaluation_results['overall_comment'] = "部分餐次标准缺失"
        elif not (isinstance(target_range, tuple) and len(target_range) == 2 and isinstance(target_range[0], (int, float)) and isinstance(target_range[1], (int, float))):
             # 如果标准格式不正确
             print("    标准格式错误，无法评价。")
             meal_eval['comment'] = "标准格式错误"
             if evaluation_results['overall_comment'] == "达标 ✅":
                  evaluation_results['overall_comment'] = "部分餐次标准格式错误"
        else:
            # 如果标准存在且格式正确
            target_min_percent = target_range[0] * 100 # 转换为 0-100 范围的百分比
            target_max_percent = target_range[1] * 100 # 转换为 0-100 范围的百分比
            meal_eval['target_range_percent'] = (round(target_min_percent, 2), round(target_max_percent, 2)) # 存储目标范围 (保留2位)

            print(f"    实际供能: {meal_energy:.{rounding_decimals}f} kcal ({meal_eval['actual_percentage']:.2f}%)") # 打印实际百分比，保留2位
            print(f"    目标范围: {target_min_percent:.0f}% - {target_max_percent:.0f}%") # 打印目标范围，不带小数

            # --- 评价结论 (判断是否在目标范围内) ---
            if target_range[0] <= meal_percentage <= target_range[1]:
                meal_eval['comment'] = "达标"
                print("    评价: 达标 ✅")
            elif meal_percentage < target_range[0]:
                meal_eval['comment'] = "偏低"
                print("    评价: 偏低 ❌")
                # 如果有任何一餐偏离，整体评价就不是“达标”了
                if evaluation_results['overall_comment'] == "达标 ✅":
                     evaluation_results['overall_comment'] = "部分餐次比偏离"
            else: # meal_percentage > target_range[1]
                meal_eval['comment'] = "偏高"
                print("    评价: 偏高 ❌")
                if evaluation_results['overall_comment'] == "达标 ✅":
                     evaluation_results['overall_comment'] = "部分餐次比偏离"

    # 可选：对不在 meal_order 列表中的餐次进行处理或提示
    evaluated_meals = list(evaluation_results['meal_ratios'].keys())
    all_present_in_data = all(meal in meal_intake.index for meal in meal_order)
    if not all_present_in_data:
        missing_data_meals = [meal for meal in meal_order if meal not in meal_intake.index]
        print(f"警告：数据中缺少以下餐次的数据，无法进行评价: {', '.join(missing_data_meals)}")
        if evaluation_results['overall_comment'] == "达标 ✅":
             evaluation_results['overall_comment'] = "部分餐次数据缺失"


    return evaluation_results


# --- 评价函数：评价非产能主要营养素 (Problem 1.1 步骤 3.3) ---

def evaluate_micronutrients(daily_intake: dict, standards: dict, gender: str, rounding_decimals: int) -> dict:
    """
    评价非产能主要营养素摄入量是否达到 RNI/AI 标准 (根据附件4评价原则3)。

    Args:
        daily_intake: 包含一日总营养素摄入量的字典。键应为 '营养素名称摄入量 (单位)' 格式。
        standards: 包含非产能营养素目标 (RNI/AI) ('micro_target' 键) 的评价标准的字典。
                   'micro_target' 键下应有性别键，再下是营养素名称键，值为目标量 (数值)。
                   例如: standards['micro_target']['男']['钙'] = 800。
                   假设 standards 中的目标单位与 daily_intake 中的摄入量单位一致。
        gender: 学生性别 ('男' 或 '女')。
        rounding_decimals: 结果中百分比和实际摄入量保留的小数位数。

    Returns:
        包含非产能营养素评价结果的字典。'micronutrients' 键下是每个营养素的评价详情，还有 'overall_comment'。
    """
    evaluation_results = {}
    # 获取该性别的非产能营养素目标字典
    micronutrient_targets = standards['micro_target'].get(gender)

    print("\n--- 非产能主要营养素评价 (RNI/AI) ---")

    # --- 安全性检查：确保标准存在 ---
    if micronutrient_targets is None:
        evaluation_results['comment'] = "标准缺失，无法评价"
        print("  评价: 标准缺失，无法评价。")
        return evaluation_results # Return if no standards
    if not isinstance(micronutrient_targets, dict) or not micronutrient_targets:
         evaluation_results['comment'] = "非产能营养素标准格式不正确或为空，无法评价"
         print("  评价: 非产能营养素标准格式不正确或为空，无法评价。")
         return evaluation_results


    evaluation_results['micronutrients'] = {}
    evaluation_results['overall_comment'] = "基本达标 😊" # 乐观初始化整体评价

    # 需要评价的非产能营养素名称列表，从该性别的标准中获取
    micros_to_evaluate = list(micronutrient_targets.keys())

    # --- 遍历每个非产能营养素进行评价 ---
    for micro_name in micros_to_evaluate:
        target_amount = micronutrient_targets.get(micro_name) # 获取该营养素的目标量

        # 从 daily_intake 字典中查找该营养素的实际摄入量。
        # 键名匹配规则：以 '营养素名称摄入量 (' 开头
        actual_intake_item = next(
            (key, value) for key, value in daily_intake.items()
            if key.startswith(f'{micro_name}摄入量 (')
        , (None, None)) # 查找第一个匹配项，如果没找到返回 (None, None)

        actual_intake_col_name = actual_intake_item[0] # 实际摄入量的键名 (如 '钙摄入量 (mg)')
        actual_intake = actual_intake_item[1] # 实际摄入量的值

        micro_eval = {
             'actual_intake': None,
             'target_amount': target_amount,
             'unit': None, # 实际摄入量单位
             'percentage_of_rni_ai': None,
             'comment': "数据缺失或标准缺失" # 初始化评价结论
        }
        evaluation_results['micronutrients'][micro_name] = micro_eval # 将单营养素评价结果添加到字典中


        print(f"  {micro_name} 摄入量 (目标: {target_amount:.2f} ?):") # 打印目标，单位待定

        # --- 评价结论 (根据附件4评价原则3：达到 RNI/AI) ---

        if target_amount is None or not isinstance(target_amount, (int, float)):
            # 如果目标标准缺失或不是数字
            print("    标准缺失或格式错误，无法评价。")
            micro_eval['comment'] = "标准缺失或格式错误"
            # 整体评价更新为部分标准缺失
            if evaluation_results['overall_comment'] == "基本达标 😊":
                 evaluation_results['overall_comment'] = "部分非产能营养素标准缺失"

        elif actual_intake_col_name is None or actual_intake is None:
             # 如果实际摄入量数据缺失 (未计算或键名不匹配)
             print("    数据缺失，无法评价。")
             micro_eval['comment'] = "数据缺失"
             # 整体评价更新为部分数据缺失
             if evaluation_results['overall_comment'] == "基本达标 😊":
                  evaluation_results['overall_comment'] = "部分非产能营养素数据缺失"

        else:
            # 标准和数据都存在，进行评价
            micro_eval['actual_intake'] = round(actual_intake, rounding_decimals)
            # 提取实际摄入量单位
            actual_unit_match = actual_intake_col_name.split('(')[-1].replace(')', '').strip()
            micro_eval['unit'] = actual_unit_match

            print(f"    实际: {actual_intake:.{rounding_decimals}f} {actual_unit_match}")
            print(f"    目标: {target_amount:.2f} {actual_unit_match} (假设单位一致)") # 打印目标，假设单位一致

            if target_amount > 0:
                # 计算占目标比例
                percentage = (actual_intake / target_amount) * 100
                micro_eval['percentage_of_rni_ai'] = round(percentage, rounding_decimals)
                print(f"    占目标比例: {percentage:.2f}%")

                # 评价结论 (达到或超过 RNI/AI 为达标，否则不足)
                if percentage >= 100:
                    micro_eval['comment'] = "达标或偏高"
                    print("    评价: 达标或偏高 ✅")
                else: # percentage < 100
                    micro_eval['comment'] = "不足"
                    print("    评价: 不足 ❌")
                    # 如果有任何一个不足，整体评价就不是“基本达标”了
                    if evaluation_results['overall_comment'] == "基本达标 😊":
                         evaluation_results['overall_comment'] = "部分非产能营养素摄入不足"

            else:
                # 如果目标为零，通常是标准设置问题
                micro_eval['comment'] = "目标为零，无法评价"
                print("    评价: 目标为零，无法评价。")
                if evaluation_results['overall_comment'] == "基本达标 😊":
                     evaluation_results['overall_comment'] = "部分非产能营养素标准为零"


    # --- 细化整体评价 (可选) ---
    # 如果整体评价仍是“基本达标”，但实际上所有标准都缺失或数据缺失，可以进一步调整
    # 例如，如果所有营养素都是“数据缺失”或“标准缺失”，整体评价不应该是“基本达标”
    if evaluation_results['overall_comment'] == "基本达标 😊" and all(e['comment'] in ["数据缺失", "标准缺失", "标准格式错误", "目标为零，无法评价"] for e in evaluation_results['micronutrients'].values()):
         evaluation_results['overall_comment'] = "未能进行有效评价，数据或标准问题"


    return evaluation_results

# --- 更新 calculate_and_display_nutrient_intakes 函数来调用这些评价函数 ---

# 假设 calculate_and_display_nutrient_intakes 函数已在代码开头定义
# 在其中计算完 daily_intake 和 meal_intake 后，添加对这些评价函数的调用：

# def calculate_and_display_nutrient_intakes(df: pd.DataFrame, student_id: str, weight_col: str, meal_col: str, nutrient_cols_per_100g: list, energy_conversion_dict: dict, rounding_decimals: int, standards: dict) -> tuple[dict, pd.in
    # ... (前面的代码：获取 student_id，定义配置，计算每行摄入量，计算日总量 daily_intake，计算每餐总量 meal_intake) ...
    # 注意：这里需要将 standards 字典也作为参数传入 calculate_and_display_nutrient_intakes

#    # --- 打印计算结果摘要 ---
#    # ... (打印 daily_intake 和 meal_intake 摘要的代码) ...

    print(f"\n--- {student_id} 食谱评价 (Problem 1.1 Step 3) ---")

    # --- Problem 1.1 - Step 3: 评价能量、餐次比及非产能主要营养素含量 ---

    # 评价能量
    energy_eval = evaluate_energy(daily_intake, standards, student_id.replace('学生', ''), standards['rounding_decimals']) # 假设 student_id 是 '男学生'/'女学生'
    # 您可以将评价结果存储在 daily_intake 或一个新的 evaluation_results 字典中
    # 建议在主调函数 process_and_evaluate_diet 中存储所有评价结果
    # For now, let's just print the results returned by the evaluation functions

    # 评价餐次比
    meal_ratio_eval = evaluate_meal_ratio(meal_intake, daily_intake, standards, standards['rounding_decimals'])
    # 存储或处理 meal_ratio_eval

    # 评价非产能主要营养素
    micronutrient_eval = evaluate_micronutrients(daily_intake, standards, student_id.replace('学生', ''), standards['rounding_decimals']) # 假设 student_id 是 '男学生'/'女学生'
    # 存储或处理 micronutrient_eval


#    # --- Problem 1.1 - Step 4: 评价食谱的能量来源 (宏量营养素占比) ---
#    # ... (这里将调用 evaluate_macro_ratios 函数，待实现) ...
#
#    # --- Problem 1.1 - Step 5: 评价每餐的蛋白质氨基酸评分 (AAS) ---
#    # ... (这里将调用 calculate_and_evaluate_per_meal_aas 函数，待实现) ...
#
#    # --- Problem 1.1 - Step 6: 整体评价及建议 ---
#    # ... (这里将调用 generate_overall_evaluation_and_suggestions 函数，待实现) ...


#    print(f"\n--- {student_id} 营养素含量计算和初步评价完成 ---") # 修改完成信息

#    return daily_intake, meal_intake # 返回计算结果，评价结果可以存储在外部字典


# --- 主流程中调用 calculate_and_display_nutrient_intakes (需要传入 standards) ---
# Assume df_man, df_female, standards are loaded/defined

# print("--- 开始计算和初步评价男女学生食谱 ---")
#
# daily_intake_man, meal_intake_man = calculate_and_display_nutrient_intakes(
#     df=df_man,
#     student_id='男学生',
#     weight_col=standards['weight_col'],
#     meal_col=standards['meal_col'],
#     nutrient_cols_per_100g=standards['nutrient_cols_per_100g'],
#     energy_conversion_dict=standards['energy_conversion'],
#     rounding_decimals=standards['rounding_decimals'],
#     standards=standards # Pass the standards dictionary
# )
#
# daily_intake_female, meal_intake_female = calculate_and_display_nutrient_intakes(
#     df=df_female,
#     student_id='女学生',
#     weight_col=standards['weight_col'],
#     meal_col=standards['meal_col'],
#     nutrient_cols_per_100g=standards['nutrient_cols_per_100g'],
#     energy_conversion_dict=standards['energy_conversion'],
#     rounding_decimals=standards['rounding_decimals'],
#     standards=standards # Pass the standards dictionary
# )
#
# print("\n--- 男女学生食谱计算和初步评价全部完成 ---")