# -*- coding: utf-8 -*-
# @time    : 2025/5/1 23:49
# @Author  : Sophomores
# @File    : evaluator.py
# @Software: PyCharm


# diet_analyzer/evaluator.py
import matplotlib.pyplot as plt
import pandas as pd


# --- Helper function to get major food group from code (used in Step 1) ---
def get_major_food_group_from_code(food_code, code_to_group_map):
    """
    根据食物编码的前两位查找对应的五大类别名称。
    非五大类别，则返回 '其他类别'。
    Assumes food_code is not NaN and is string-like.
    """
    if pd.isna(food_code) or not isinstance(food_code, str):
        return '其他类别'
    if len(food_code) < 2:
        return '其他类别'
    code = food_code[:2]
    return code_to_group_map.get(code, '其他类别')


# --- Helper function to count unique food types (used in Step 1) ---
def count_food_types(df: pd.DataFrame) -> int:
    """
    统计 DataFrame 中 '食物名称' 列的不重复数量。
    """
    if '食物名称' in df.columns:
        return df['食物名称'].nunique()
    return 0


# --- Evaluation Class (Finalized based on user requirements) ---

class Evaluation:
    def __init__(self, df: pd.DataFrame, display_flag: bool = True, rounding_decimals: int = 2):
        self.df = df.copy()
        self.gender = getattr(df, 'name', '食堂')

        self.display_flag = display_flag
        self.rounding_decimals = rounding_decimals

        # --- Standards (Comprehensive) ---
        self.standards = {
            'daily_variety_min': 12,
            'energy_target': {'男': 2400, '女': 1900},
            'energy_acceptable_range_percent': 10,
            'meal_ratio_range': {'早餐': (0.25, 0.35), '午餐': (0.30, 0.40), '晚餐': (0.30, 0.40)},
            'micro_target': {
                '男': {'钙': 800, '铁': 12, '锌': 12.5, '维生素A': 800, '维生素B1': 1.4, '维生素B2': 1.4,
                       '维生素C': 100},
                '女': {'钙': 800, '铁': 20, '锌': 7.5, '维生素A': 700, '维生素B1': 1.2, '维生素B2': 1.2, '维生素C': 100}
            },
            'macro_ratio_range': {'蛋白质': (0.10, 0.15), '脂肪': (0.20, 0.30), '碳水化合物': (0.50, 0.65)},
            'energy_conversion': {'蛋白质': 4, '脂肪': 9, '碳水化合物': 4},  # No Fiber
            'aas_ref_pattern': {
                '异亮氨酸': 40, '亮氨酸': 70, '赖氨酸': 55, '含硫氨基酸': 35,
                '芳香族氨基酸': 60, '苏氨酸': 40, '色氨酸': 10, '缬氨酸': 50,
            },
            'aas_eval_criteria': {
                '不合理': (0, 60), '不够合理': (60, 80), '比较合理': (80, 90), '合理': (90, float('inf')),
            },
            'five_major_food_names': ["谷、薯类", "蔬菜、菌藻、水果类", "畜、禽、鱼、蛋类及制品", "奶、干豆、坚果、种子类及制品",
                                      "植物油类"],
            'code_prefix_to_major_group': self._build_code_to_group_map(),
            'nutrient_cols_per_100g': self._get_nutrient_cols_per_100g(df),  # Excludes Fiber
            'weight_col': '食物重量(克)',
            'meal_col': '餐次',
            'meal_order': ['早餐', '午餐', '晚餐'],
        }

        self.evaluation_results = {
            'gender': self.gender
        }

        import matplotlib.pyplot as plt

        font_config = {
            'font.family': ['LXGW WenKai GB Screen R', 'JetBrains Mono NL'],  # 设置中英文字体
            'font.size': 10,  # 设置字体大小
            "mathtext.fontset": 'stix',  # 设置公式字体, 这是matplotlib自带的
            "font.serif": 'SimSun',  # 设置衬线字体
            "font.sans-serif": 'SimHei',  # 设置非衬线字体
            'axes.unicode_minus': False,  # 解决负号'-'显示为方块的问题
        }

        plt.rcParams.update(font_config)

    def plot_five_food_groups_pie(self,food_structure_dict):
        from collections import defaultdict
        import matplotlib.pyplot as plt

        if not food_structure_dict:
            print("无食物结构信息，无法绘制五大类图")
            return

        food_summary = food_structure_dict.get('food_quantities_summary')
        if not food_summary or not isinstance(food_summary, list):
            print("无食物重量汇总数据，无法绘制五大类图")
            return

        # 汇总五大类的总重量（依赖 '食物类别'）
        group_weights = defaultdict(float)
        for item in food_summary:
            category = item.get('食物类别', '未分类')
            weight = item.get('食物重量(克)', 0)
            group_weights[category] += weight

        labels = list(group_weights.keys())
        sizes = list(group_weights.values())

        if not sizes or sum(sizes) == 0:
            print("所有食物重量为 0，无法绘图")
            return

        plt.figure(figsize=(7, 7))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("五大类食物重量分布")
        plt.tight_layout()
        plt.savefig(f'./Image/{self.gender}学生 五大类食物分布 - 饼图.png', dpi=500)
        plt.close()

    def plot_macro_energy_ratio(self, df_intake):
        labels = ['蛋白质', '脂肪', '碳水化合物']
        energy_values = []

        # 读取能量值
        for label in labels:
            col_name = f'{label}摄入量 (g)'
            if col_name in df_intake.columns:
                if label == '蛋白质':
                    kcal = df_intake[col_name].values[0] * 4
                elif label == '脂肪':
                    kcal = df_intake[col_name].values[0] * 9
                else:
                    kcal = df_intake[col_name].values[0] * 4
                energy_values.append(kcal)
            else:
                energy_values.append(0)

        plt.figure(figsize=(6, 6))
        plt.pie(energy_values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("宏量营养素供能占比")
        plt.axis('equal')
        plt.tight_layout()

        plt.savefig(f'./Image/{self.gender}学生 宏量营养素供能比 - 饼图', dpi=500)
        plt.close()

    def plot_meal_energy_bar(self,df_meal):
        import matplotlib.pyplot as plt

        if df_meal.empty or '总能量摄入量 (kcal)' not in df_meal.columns:
            print("无餐次能量数据可绘图")
            return

        df_plot = df_meal['总能量摄入量 (kcal)'].reindex(['早餐', '午餐', '晚餐']).fillna(0)
        total_energy = df_plot.sum()
        if total_energy <= 0:
            print("总能量为 0，无法绘图")
            return

        percentages = (df_plot / total_energy * 100).round(1)

        plt.figure(figsize=(8, 5))
        bars = plt.bar(df_plot.index, df_plot.values, color='skyblue')

        # 添加每根柱子的能量值和百分比
        for i, (bar, percent) in enumerate(zip(bars, percentages)):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 5,
                     f"{height:.0f} kcal\n({percent:.1f}%)",
                     ha='center', va='bottom', fontsize=9)

        # 推荐范围标注
        ranges = {
            '早餐': (0.25, 0.35),
            '午餐': (0.30, 0.40),
            '晚餐': (0.30, 0.40),
        }

        for i, meal in enumerate(['早餐', '午餐', '晚餐']):
            lower = total_energy * ranges[meal][0]
            upper = total_energy * ranges[meal][1]
            plt.hlines([lower, upper], i - 0.4, i + 0.4,
                       colors='red', linestyles='dashed', linewidth=1)
            plt.fill_between([i - 0.4, i + 0.4], lower, upper,
                             color='red', alpha=0.1, label='推荐范围' if i == 0 else None)

        plt.ylabel("能量 (kcal)")
        plt.title("三餐能量分布（含推荐区间）")
        plt.xticks(rotation=0)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'./Image/{self.gender}学生 三餐能量占比 - 条形图（含推荐区间）.png', dpi=500)
        plt.close()

    def plot_micronutrient_adequacy(self,micronutrients_data):

        names = []
        percentages = []
        for k, v in micronutrients_data.items():
            if v.get('percentage_of_rni_ai') is not None:
                names.append(k)
                percentages.append(v['percentage_of_rni_ai'])

        plt.figure(figsize=(8, 5))
        plt.barh(names, percentages, color='orange')
        plt.axvline(100, color='red', linestyle='--', label='推荐摄入量 100%')
        plt.xlabel('达标率 (%)')
        plt.title('非产能营养素摄入达标情况')
        plt.legend()
        plt.tight_layout()

        plt.savefig(f'./Image/{self.gender}学生 非产能营养素达标率 - 水平条形图', dpi=500)
        plt.close()

    def plot_meal_aas_scores(self,aas_data):
        meals = []
        scores = []
        for meal, info in aas_data.items():
            if info.get('aas') is not None:
                meals.append(meal)
                scores.append(info['aas'])

        plt.figure(figsize=(6, 4))
        plt.bar(meals, scores, color='green')
        plt.axhline(60, color='red', linestyle='--', label='最低合格线')
        plt.ylabel("AAS 分值")
        plt.title("三餐蛋白质氨基酸评分")
        plt.legend()
        plt.tight_layout()

        plt.savefig(f'./Image/{self.gender}学生 AAS 分值 - 折线图 条形图', dpi=500)
        plt.close()

    @staticmethod
    def _build_code_to_group_map():
        """ 构建食物编码前缀到五大类别的映射字典。"""
        five_major_food_groups_source = [
            {"谷类及制品": "01", "薯类、淀粉及制品": "02"},
            {"蔬菜类及制品": "04", "菌藻类": "05", "水果类及制品": "06"},
            {"畜肉类及制品": "08", "禽肉类及制品": "09", "鱼虾蟹贝类": "12", "蛋类及制品": "11"},
            {"乳类及制品": "10", "干豆类及制品": "03", "坚果、种子类": "07"},
            {"植物油类": "19"}
        ]
        five_major_food_names_source = ["谷、薯类", "蔬菜、菌藻、水果类", "畜、禽、鱼、蛋类及制品",
                                        "奶、干豆、坚果、种子类及制品", "植物油类"]

        code_to_group_map = {}
        for i, group_codes_dict in enumerate(five_major_food_groups_source):
            group_name = five_major_food_names_source[i]
            for sub_group_name, code_prefix in group_codes_dict.items():
                code_to_group_map[code_prefix] = group_name
        return code_to_group_map

    @staticmethod
    def _get_nutrient_cols_per_100g(df: pd.DataFrame) -> list[str]:
        """
        从 DataFrame 的列名中识别出每100g营养成分列。
        不包含膳食纤维。
        """
        nutrient_patterns = {
            '碳水化合物': 'g/100g', '蛋白质': 'g/100g', '脂肪': 'g/100g',
            # '膳食纤维': 'g/100g', # Excluded
            '钙': 'mg/100g', '铁': 'mg/100g', '锌': 'mg/100g',
            '维生素A': 'μg/100g', '维生素B1': 'mg/100g', '维生素B2': 'mg/100g', '维生素C': 'mg/100g',
            '异亮氨酸': 'g/100g', '亮氨酸': 'g/100g', '赖氨酸': 'g/100g',
            '含硫氨基酸': 'g/100g', '芳香族氨基酸': 'g/100g',
            '苏氨酸': 'g/100g', '色氨酸': 'g/100g', '缬氨酸': 'g/100g',
        }

        nutrient_cols = []
        for name, unit_pattern in nutrient_patterns.items():
            col_name = f'{name} ({unit_pattern})'
            if col_name in df.columns:
                nutrient_cols.append(col_name)

        return nutrient_cols

    #  --- 1 分析食物结构 ---
    def analyze_food_structure(self) -> pd.DataFrame:
        """ 分析食谱中的食物结构，结果存储在 self.evaluation_results['food_structure']。 """
        df = self.df
        standards = self.standards

        if '食物类别' not in df.columns:
            df['食物类别'] = df['食物编码'].apply(
                lambda x: get_major_food_group_from_code(x, standards['code_prefix_to_major_group'])
            )

        categories_present = df[df['食物类别'] != '其他类别']['食物类别'].unique().tolist()
        missing_categories = [cat for cat in standards['five_major_food_names'] if cat not in categories_present]
        all_five_present = len(missing_categories) == 0

        unique_food_types_count = count_food_types(df)
        daily_variety_met = unique_food_types_count > standards['daily_variety_min']

        other_category_items = df[df['食物类别'] == '其他类别']['主要成分'].unique().tolist()

        food_quantities_summary = None
        weight_col = standards.get('weight_col', '食物重量(克)')
        df[weight_col] = df['可食部（克/份）'] * df['食用份数']
        food_quantities_summary_df = (
            df.groupby(['食物名称', '食物类别'])[weight_col]
            .sum()
            .reset_index()
        )
        food_quantities_summary = food_quantities_summary_df.to_dict('records')

        self.evaluation_results['food_structure'] = {
            'categories_present': categories_present,
            'missing_categories': missing_categories,
            'all_five_present': all_five_present,
            'unique_food_types_count': unique_food_types_count,
            'daily_variety_met': daily_variety_met,
            'other_category_items': other_category_items,
            'food_quantities_summary': food_quantities_summary,
        }
        # 返回添加了食物类别的df
        return df

    #  --- 2 计算主要营养素含量 ---
    def calculate_nutrient_intakes(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        计算日食谱的日总和每餐总营养素摄入量及能量。
        结果存储在 self.evaluation_results['nutrient_intake']。
        不包含膳食纤维的能量计算。

        Returns:
            一个元组，包含：
            - df_intake: DataFrame（一日各营养素摄入量及能量总量，1行）
            - df_meal: DataFrame（餐次的各营养素摄入量及能量总量）
        """
        df = self.df

        weight_col = self.standards.get('weight_col', '食物重量(克)')
        meal_col = self.standards.get('meal_col', '餐次')
        energy_conversion = self.standards.get('energy_conversion', {})  # No Fiber
        nutrient_cols_per_100g = self.standards.get('nutrient_cols_per_100g', [])  # No Fiber

        if weight_col not in df.columns:
            df[weight_col] = df['可食部（克/份）'].fillna(0) * df['食用份数'].fillna(0)

        intake_cols = []
        for nutrient_col_100g in nutrient_cols_per_100g:
            parts = nutrient_col_100g.replace(')', '').split('(')
            if len(parts) == 2:
                nutrient_name = parts[0].strip()
                unit_info = parts[1].strip()
                intake_unit = unit_info.split('/')[0].strip()
                intake_col_name = f'{nutrient_name}摄入量 ({intake_unit})'

                if nutrient_col_100g in df.columns and weight_col in df.columns:
                    df[intake_col_name] = (df[weight_col].fillna(0) / 100) * df[nutrient_col_100g].fillna(0)
                    intake_cols.append(intake_col_name)

        # --- Calculate per-row energy contribution from macros (P, F, C) ---
        per_row_energy_contribution_cols = []
        macro_names_for_energy = ['蛋白质', '脂肪', '碳水化合物']  # Based on energy_conversion keys
        for substance in macro_names_for_energy:
            intake_col_g = f'{substance}摄入量 (g)'
            energy_col_name = f'{substance}能量贡献 (kcal)'
            if intake_col_g in df.columns and energy_conversion.get(substance) is not None:
                df[energy_col_name] = df[intake_col_g].fillna(0) * energy_conversion.get(substance, 0)
                per_row_energy_contribution_cols.append(energy_col_name)

        # --- 2.2 计算一日总营养素摄入量 ---

        existing_intake_cols_for_daily = [col for col in intake_cols if col in df.columns]
        daily_nutrient_intake_dict: dict = {}
        if existing_intake_cols_for_daily:
            for intake_col in existing_intake_cols_for_daily:
                daily_nutrient_intake_dict[intake_col] = df[intake_col].sum()

        # --- 2.3 计算总能量 (日总) ---
        # Calculate total daily energy ONLY from P, F, C intake grams
        protein_total_g = daily_nutrient_intake_dict.get('蛋白质摄入量 (g)', 0)
        fat_total_g = daily_nutrient_intake_dict.get('脂肪摄入量 (g)', 0)
        carb_total_g = daily_nutrient_intake_dict.get('碳水化合物摄入量 (g)', 0)

        total_calculated_energy_kcal = (protein_total_g * energy_conversion.get('蛋白质', 0) +
                                        fat_total_g * energy_conversion.get('脂肪', 0) +
                                        carb_total_g * energy_conversion.get('碳水化合物', 0))

        daily_nutrient_intake_dict['总能量摄入量 (kcal)'] = total_calculated_energy_kcal

        df_intake = pd.DataFrame([daily_nutrient_intake_dict])

        cols_to_sum_per_meal = intake_cols + per_row_energy_contribution_cols

        existing_cols_to_sum_per_meal = [col for col in cols_to_sum_per_meal if col in df.columns]

        if meal_col not in df.columns:
            df_meal = pd.DataFrame()
        elif df.empty:
            df_meal = pd.DataFrame()
        elif not existing_cols_to_sum_per_meal:
            df_meal = pd.DataFrame()
        else:
            df_meal = df.groupby(meal_col)[existing_cols_to_sum_per_meal].sum()

            existing_per_meal_energy_cols = [col for col in per_row_energy_contribution_cols if col in df_meal.columns]
            if existing_per_meal_energy_cols:
                df_meal['总能量摄入量 (kcal)'] = df_meal[existing_per_meal_energy_cols].sum(axis=1)
            else:
                df_meal['总能量摄入量 (kcal)'] = 0

        self.evaluation_results['nutrient_intake'] = {
            'daily_totals_df': df_intake,
            'meal_totals_df': df_meal
        }

        return df_intake, df_meal

    #  --- 3 评价各项指标 ---

    # --- 3.1 评价能量 ---
    def evaluate_energy(self, df_intake: pd.DataFrame) -> None:
        """
        评价一日总能量摄入量是否符合个体需要 (根据附件4评价原则1)。
        结果存储在 self.evaluation_results['evaluation_energy']。
        """
        gender = self.evaluation_results['gender']
        rounding_decimals = self.rounding_decimals

        energy_evaluation = {}

        actual_energy_kcal = df_intake.get('总能量摄入量 (kcal)', pd.Series([0])).values[0]
        target_energy_kcal = self.standards['energy_target'].get(gender)
        acceptable_range_percent = self.standards.get('energy_acceptable_range_percent')

        energy_evaluation['actual_kcal'] = round(actual_energy_kcal, rounding_decimals)
        energy_evaluation['target_kcal'] = target_energy_kcal

        comment = "标准缺失或数据缺失"
        percentage_of_target = None
        acceptable_range_kcal = None

        if target_energy_kcal is not None and target_energy_kcal > 0:
            percentage_of_target = (actual_energy_kcal / target_energy_kcal) * 100

            if acceptable_range_percent is not None and isinstance(acceptable_range_percent, (int, float)):
                lower_bound = target_energy_kcal * (1 - acceptable_range_percent / 100)
                upper_bound = target_energy_kcal * (1 + acceptable_range_percent / 100)
                acceptable_range_kcal = (round(lower_bound, 2), round(upper_bound, 2))

                if lower_bound <= actual_energy_kcal <= upper_bound:
                    comment = "适宜"
                elif actual_energy_kcal < lower_bound:
                    comment = "偏低"
                else:  # actual_energy_kcal > upper_bound
                    comment = "偏高"
            else:
                comment = "适宜 (范围标准缺失)" if actual_energy_kcal >= target_energy_kcal else "偏低 (范围标准缺失)"

        elif target_energy_kcal == 0:
            comment = "目标为零，无法评价"

        energy_evaluation['percentage_of_target'] = round(percentage_of_target,
                                                          rounding_decimals) if percentage_of_target is not None else None
        energy_evaluation['acceptable_range_kcal'] = acceptable_range_kcal
        energy_evaluation['comment'] = comment

        self.evaluation_results['evaluation_energy'] = energy_evaluation

    # --- 3.2 评价餐次比 ---
    def evaluate_meal_ratio(self, df_intake: pd.DataFrame, df_meal: pd.DataFrame) -> None:
        """
        评价三餐供能比是否在推荐范围内 (根据附件4评价原则2)。
        结果存储在 self.evaluation_results['evaluation_meal_ratio']。
        """
        rounding_decimals = self.rounding_decimals
        meal_ratio_evaluation = {}

        meal_energy_col = '总能量摄入量 (kcal)'
        total_daily_energy = df_intake.get(meal_energy_col, pd.Series([0])).values[0]

        meal_ratio_ranges = self.standards.get('meal_ratio_range')

        meal_ratio_evaluation['meal_ratios'] = {}
        overall_comment = "达标 ✅"

        meal_order = self.standards.get('meal_order')

        if total_daily_energy <= 0 or meal_energy_col not in df_meal.columns or df_meal.empty or meal_ratio_ranges is None:
            overall_comment = "总能量为零、每餐能量数据缺失或标准缺失，无法评价"
        else:
            for meal in meal_order:
                meal_energy = df_meal.loc[
                    meal, meal_energy_col] if meal in df_meal.index and meal_energy_col in df_meal.columns else 0
                meal_percentage = (meal_energy / total_daily_energy) if total_daily_energy > 0 else 0
                target_range = meal_ratio_ranges.get(meal)

                meal_eval = {
                    'actual_kcal': round(meal_energy, rounding_decimals),
                    'actual_percentage': round(meal_percentage * 100, rounding_decimals),
                    'target_range_percent': None,
                    'comment': "标准缺失或数据缺失"
                }
                meal_ratio_evaluation['meal_ratios'][meal] = meal_eval

                if target_range is not None and isinstance(target_range, tuple) and len(
                        target_range) == 2 and isinstance(target_range[0], (int, float)) and isinstance(target_range[1],
                                                                                                        (int, float)):
                    target_min_percent = target_range[0] * 100
                    target_max_percent = target_range[1] * 100
                    meal_eval['target_range_percent'] = (round(target_min_percent, 2), round(target_max_percent, 2))

                    if target_range[0] <= meal_percentage <= target_range[1]:
                        meal_eval['comment'] = "达标"
                    else:
                        meal_eval['comment'] = "偏低" if meal_percentage < target_range[0] else "偏高"
                        if overall_comment == "达标 ✅":
                            overall_comment = "部分餐次比偏离"
                else:
                    if overall_comment == "达标 ✅":
                        overall_comment = "部分餐次比标准问题"

        meal_ratio_evaluation['overall_comment'] = overall_comment
        self.evaluation_results['evaluation_meal_ratio'] = meal_ratio_evaluation

    # --- 3.3 评价非产能主要营养素 ---
    def evaluate_micronutrients(self, df_intake: pd.DataFrame) -> None:
        """
        评价非产能主要营养素摄入量是否达到标准 (根据附件4评价原则3)。
        结果存储在 self.evaluation_results['evaluation_micronutrients']。
        """
        gender = self.evaluation_results['gender']
        rounding_decimals = self.rounding_decimals
        micronutrients_evaluation = {}

        micronutrient_targets = self.standards['micro_target'].get(gender)

        micronutrients_evaluation['micronutrients'] = {}
        overall_comment = "基本达标 😊"

        if micronutrient_targets is None or not isinstance(micronutrient_targets, dict) or not micronutrient_targets:
            overall_comment = "标准缺失，无法评价"
        else:
            micros_to_evaluate = list(micronutrient_targets.keys())

            for micro_name in micros_to_evaluate:
                target_amount = micronutrient_targets.get(micro_name)

                actual_intake_col_name = next(
                    (col for col in df_intake.columns if col.startswith(f'{micro_name}摄入量 (')),
                    None
                )
                actual_intake = df_intake[actual_intake_col_name].values[
                    0] if actual_intake_col_name in df_intake.columns and not df_intake.empty else 0

                micro_eval = {
                    'actual_intake': None,
                    'target_amount': target_amount,
                    'unit': None,
                    'percentage_of_rni_ai': None,
                    'comment': "计算失败或标准缺失"
                }
                micronutrients_evaluation['micronutrients'][micro_name] = micro_eval

                if target_amount is None or not isinstance(target_amount, (int, float)):
                    micro_eval['comment'] = "标准缺失或格式错误"
                    if overall_comment == "基本达标 😊": overall_comment = "部分非产能营养素标准问题"
                elif actual_intake_col_name is None:
                    micro_eval['comment'] = "数据列缺失"
                    if overall_comment == "基本达标 😊": pass
                    overall_comment = "部分未达标，需改进"
                else:
                    micro_eval['actual_intake'] = round(actual_intake, rounding_decimals)
                    actual_unit_match = actual_intake_col_name.split('(')[-1].replace(')',
                                                                                      '').strip() if '(' in actual_intake_col_name else '?'
                    micro_eval['unit'] = actual_unit_match

                    if target_amount > 0:
                        percentage = (actual_intake / target_amount) * 100
                        micro_eval['percentage_of_rni_ai'] = round(percentage, rounding_decimals)

                        if percentage >= 100:
                            micro_eval['comment'] = "达标或偏高"
                        else:
                            micro_eval['comment'] = "不足"
                            if overall_comment == "基本达标 😊":
                                overall_comment = "部分非产能营养素摄入不足"
                            overall_comment = "部分未达标，需改进"
                    else:
                        micro_eval['comment'] = "目标为零，无法评价"
                        if overall_comment == "基本达标 😊": overall_comment = "部分非产能营养素标准为零"
                        overall_comment = "部分未达标，需改进"

        micronutrients_evaluation['overall_comment'] = overall_comment
        self.evaluation_results['evaluation_micronutrients'] = micronutrients_evaluation

    # --- 4 评价宏量营养素供能比 ---
    # Adjusted for no fiber energy
    def evaluate_macro_ratios(self, df_intake: pd.DataFrame) -> None:
        """
        评价一日食谱的宏量营养素供能比是否在推荐范围内 (根据附件4评价原则4)。
        结果存储在 self.evaluation_results['evaluation_macro_ratios']。
        能量计算不包含膳食纤维。
        """
        rounding_decimals = self.rounding_decimals
        macro_ratios_evaluation = {}

        total_daily_energy = df_intake.get('总能量摄入量 (kcal)', pd.Series([0])).values[0]
        protein_g = df_intake.get('蛋白质摄入量 (g)', pd.Series([0])).values[0]
        fat_g = df_intake.get('脂肪摄入量 (g)', pd.Series([0])).values[0]
        carb_g = df_intake.get('碳水化合物摄入量 (g)', pd.Series([0])).values[0]

        macro_ratio_ranges = self.standards.get('macro_ratio_range')
        energy_conversion = self.standards.get('energy_conversion', {})  # No Fiber

        macro_ratios_evaluation['macro_ratios'] = {}
        overall_comment = "达标 ✅"

        if total_daily_energy <= 0 or \
                macro_ratio_ranges is None or \
                not isinstance(macro_ratio_ranges, dict) or \
                not macro_ratio_ranges or \
                energy_conversion is None or \
                not isinstance(energy_conversion, dict) or \
                not energy_conversion:
            overall_comment = "日总能量为零、标准缺失或格式不正确，无法评价"
        else:
            protein_kcal = protein_g * energy_conversion.get('蛋白质', 0)
            fat_kcal = fat_g * energy_conversion.get('脂肪', 0)
            carb_kcal = carb_g * energy_conversion.get('碳水化合物', 0)

            macro_energy_dict = {'蛋白质': protein_kcal, '脂肪': fat_kcal, '碳水化合物': carb_kcal}

            macros_to_evaluate = ['蛋白质', '脂肪', '碳水化合物']
            for macro_name in macros_to_evaluate:
                actual_kcal = macro_energy_dict.get(macro_name, 0)
                actual_ratio = (actual_kcal / total_daily_energy) if total_daily_energy > 0 else 0
                target_range = macro_ratio_ranges.get(macro_name)

                macro_eval = {
                    'actual_kcal': round(actual_kcal, rounding_decimals),
                    'actual_ratio': round(actual_ratio, rounding_decimals),
                    'actual_percentage': round(actual_ratio * 100, rounding_decimals),
                    'target_range': target_range,
                    'target_range_percent': None,
                    'comment': "标准缺失或格式错误"
                }
                macro_ratios_evaluation['macro_ratios'][macro_name] = macro_eval

                if target_range is not None and isinstance(target_range, tuple) and len(
                        target_range) == 2 and isinstance(target_range[0], (int, float)) and isinstance(target_range[1],
                                                                                                        (int, float)):
                    target_min_percent = target_range[0] * 100
                    target_max_percent = target_range[1] * 100
                    macro_eval['target_range_percent'] = (round(target_min_percent, 2), round(target_max_percent, 2))

                    if target_range[0] <= actual_ratio <= target_range[1]:
                        macro_eval['comment'] = "达标"
                    else:
                        macro_eval['comment'] = "偏低" if actual_ratio < target_range[0] else "偏高"
                        if overall_comment == "达标 ✅":
                            overall_comment = "部分宏量比偏离"
                else:
                    if overall_comment == "达标 ✅":
                        overall_comment = "部分宏量比标准问题"

            # Check consistency of P+F+C energy sum vs total daily energy (calculated without fiber)
            sum_pfc_kcal = protein_kcal + fat_kcal + carb_kcal
            if total_daily_energy > 0 and abs(sum_pfc_kcal - total_daily_energy) / total_daily_energy > 0.01:
                if overall_comment == "达标 ✅":
                    overall_comment += " (计算警告: PFC能量总和与日总量不符)"

        macro_ratios_evaluation['overall_comment'] = overall_comment
        self.evaluation_results['evaluation_macro_ratios'] = macro_ratios_evaluation

    # --- 5 计算并评价每餐的蛋白质氨基酸评分 (AAS) ---
    def calculate_and_evaluate_per_meal_aas(self, df_meal: pd.DataFrame) -> None:
        """
        计算并评价每餐的蛋白质氨基酸评分 (AAS) (根据附件4评价原则5)。
        结果存储在 self.evaluation_results['evaluation_aas']。
        """
        rounding_decimals = self.rounding_decimals
        aas_evaluation = {}
        # 毎克参考蛋白质中必须氨基酸含量(mg/g)
        aas_ref_pattern = self.standards.get('aas_ref_pattern')

        aas_eval_criteria = self.standards.get('aas_eval_criteria')

        aas_evaluation['meal_aas'] = {}
        overall_comment = "达标 ✅"

        if df_meal.empty:
            overall_comment = "每餐数据为空，无法计算 AAS"
        else:
            protein_intake_col_g = '蛋白质摄入量 (g)'
            # 氨基酸名字
            essential_aa_names = list(aas_ref_pattern.keys())
            # 实际在df_meal中氨基酸的列名 列表
            essential_aa_intake_cols = []

            for aa_name in essential_aa_names:
                col_mg = f'{aa_name}摄入量 (mg)'
                col_g = f'{aa_name}摄入量 (g)'
                if col_mg in df_meal.columns:
                    essential_aa_intake_cols.append(col_mg)
                elif col_g in df_meal.columns:
                    essential_aa_intake_cols.append(col_g)

            if protein_intake_col_g not in df_meal.columns:
                overall_comment = f"缺少蛋白质摄入量列 '{protein_intake_col_g}'，无法计算 AAS"

            elif len(essential_aa_intake_cols) < len(essential_aa_names):
                missing_aa_cols = [f'{aa_name}摄入量 (g/mg)' for aa_name in essential_aa_names if
                                   f'{aa_name}摄入量 (mg)' not in essential_aa_intake_cols and f'{aa_name}摄入量 (g)' not in essential_aa_intake_cols]
                overall_comment = f"缺少部分必需氨基酸摄入量列 ({', '.join(missing_aa_cols)})，无法计算 AAS"

            else:
                meal_order = self.standards.get('meal_order')
                overall_aas_sufficient = True

                for meal in meal_order:
                    meal_eval_default = {'comment': '数据缺失', 'aas': None, 'limiting_aa': None, 'protein_g': None}

                    if meal not in df_meal.index:
                        aas_evaluation['meal_aas'][meal] = meal_eval_default
                        overall_aas_sufficient = False
                        continue

                    meal_protein_g = df_meal.loc[
                        meal, protein_intake_col_g] if protein_intake_col_g in df_meal.columns else 0

                    if meal_protein_g <= 0:
                        meal_eval_default['comment'] = '蛋白质摄入为零，无法计算 AAS'
                        aas_evaluation['meal_aas'][meal] = meal_eval_default
                        overall_aas_sufficient = False
                        continue

                    limiting_aa = None
                    min_ratio = float('inf')
                    aa_ratios = {}

                    calculation_successful = True

                    for aa_intake_col in essential_aa_intake_cols:
                        # 氨基酸名字
                        aa_name = aa_intake_col.split('摄入量')[0].strip()
                        # 氨基酸单位
                        aa_unit = aa_intake_col.split('(')[-1].replace(')', '').strip()
                        # 氨基酸摄入量
                        aa_intake_amount = df_meal.loc[meal, aa_intake_col] if aa_intake_col in df_meal.columns else 0
                        # 换算单位,只有g和mg两种, 不是g即mg则不懂
                        aa_intake_mg = aa_intake_amount * 1000 if aa_unit.lower() == 'g' else aa_intake_amount
                        # 获取参考氨基酸
                        ref_amount_mg_per_g_protein = aas_ref_pattern.get(aa_name)

                        if ref_amount_mg_per_g_protein is None or ref_amount_mg_per_g_protein <= 0:
                            calculation_successful = False
                            break

                        ratio = aa_intake_mg / (meal_protein_g * ref_amount_mg_per_g_protein) if (
                                meal_protein_g > 0 and ref_amount_mg_per_g_protein > 0) else 0
                        aa_ratios[aa_name] = round(ratio, rounding_decimals)

                        if ratio < min_ratio:
                            min_ratio = ratio
                            limiting_aa = aa_name

                    meal_eval = {
                        'protein_g': round(meal_protein_g, rounding_decimals),
                        'aas': None,
                        'limiting_aa': None,
                        'comment': "计算失败",
                    }

                    if calculation_successful and min_ratio != float('inf'):
                        aas_score = round(min_ratio * 100, rounding_decimals)
                        meal_eval['aas'] = aas_score
                        meal_eval['limiting_aa'] = limiting_aa

                        meal_aas_comment = "未知等级"
                        is_current_meal_sufficient = False
                        sorted_criteria = sorted(aas_eval_criteria.items(), key=lambda item: item[1][0])

                        for comment, range_tuple in sorted_criteria:
                            range_tuple: tuple
                            if range_tuple[0] <= aas_score < range_tuple[1]:
                                meal_aas_comment = comment
                                if comment in ['合理', '比较合理']:
                                    is_current_meal_sufficient = True
                                break

                        meal_eval['comment'] = meal_aas_comment

                        if not is_current_meal_sufficient:
                            overall_aas_sufficient = False

                    else:
                        overall_aas_sufficient = False

                    aas_evaluation['meal_aas'][meal] = meal_eval

                if overall_aas_sufficient:
                    overall_comment = "所有餐次 AAS 达标 ✅"
                else:
                    overall_comment = "部分餐次 AAS 不足或计算/数据缺失 ❌"

        aas_evaluation['overall_comment'] = overall_comment
        self.evaluation_results['evaluation_aas'] = aas_evaluation

    # --- 6 综合所有评价结果，生成整体评价和膳食建议 ---
    def generate_overall_evaluation_and_suggestions(self) -> str:
        """
        综合所有评价结果，生成整体评价和膳食建议。
        格式化输出，评价总结子项前用50个-号分隔，评价和建议之间用50个#号分隔。
        """
        evaluation_results = self.evaluation_results
        standards = self.standards
        gender = evaluation_results.get('gender', '未知')
        rounding_decimals = self.rounding_decimals

        # Use gender in the main title
        overall_summary = f"\n--- {gender} 学生食谱整体评价与建议 ---\n"

        # --- 总结各项评价 ---
        overall_summary += "\n各项评价总结:\n"

        # 1. 食物结构总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        fs_eval: dict = evaluation_results.get('food_structure', {})
        overall_summary += "  食物结构:\n"
        if fs_eval:
            overall_summary += f"    种类数量: {fs_eval.get('unique_food_types_count', 'N/A')} 种 (目标 > {standards.get('daily_variety_min', 'N/A')} 种) - 评价: {'达标 ✅' if fs_eval.get('daily_variety_met', False) else '不足 ❌'}\n"
            overall_summary += f"    五大类包含: {'齐全 ✅' if fs_eval.get('all_five_present', False) else '不齐全 ❌'}\n"
            if fs_eval.get('missing_categories'):
                overall_summary += f"    缺少的类别: {', '.join(fs_eval['missing_categories'])}\n"
            if fs_eval.get('other_category_items'):
                overall_summary += f"    未归类食物: {', '.join(fs_eval['other_category_items'])}\n"
        else:
            overall_summary += "    食物结构评价数据缺失。\n"

        # 3.1 能量摄入总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        energy_eval: dict = evaluation_results.get('evaluation_energy', {})
        overall_summary += "  能量摄入:\n"
        if energy_eval:
            actual_energy_kcal = energy_eval.get('actual_kcal', 'N/A')
            target_energy_kcal = energy_eval.get('target_kcal')
            percentage = energy_eval.get('percentage_of_target', 'N/A')
            acceptable_range_kcal = energy_eval.get('acceptable_range_kcal', 'N/A')

            summary_line = f"    总能量: {actual_energy_kcal:.{rounding_decimals}f} kcal"
            if target_energy_kcal is not None:
                summary_line += f" (目标 {target_energy_kcal:.0f} kcal"
                if acceptable_range_kcal != 'N/A':
                    summary_line += f", 适宜范围 {acceptable_range_kcal[0]:.0f}-{acceptable_range_kcal[1]:.0f} kcal"
                summary_line += f", 占目标 {percentage:.1f}%)"
            summary_line += f" - 评价: {energy_eval.get('comment', 'N/A')}\n"
            overall_summary += summary_line
        else:
            overall_summary += "    能量评价数据缺失。\n"

        # 3.2 餐次比总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        meal_ratio_eval: dict = evaluation_results.get('evaluation_meal_ratio', {})
        overall_summary += "  餐次供能比:\n"
        if meal_ratio_eval and meal_ratio_eval.get('meal_ratios'):
            for meal, eval_data in meal_ratio_eval['meal_ratios'].items():
                summary_line = f"    {meal}: {eval_data.get('actual_percentage', 'N/A'):.1f}%"
                if eval_data.get('target_range_percent'):
                    summary_line += f" (目标 {eval_data['target_range_percent'][0]:.0f}%-{eval_data['target_range_percent'][1]:.0f}%)"
                summary_line += f" - 评价: {eval_data.get('comment', 'N/A')}\n"
                overall_summary += summary_line
            overall_summary += f"  餐次比整体评价: {meal_ratio_eval.get('overall_comment', 'N/A')}\n"
        else:
            overall_summary += "    餐次比评价数据缺失。\n"

        # 4. 宏量营养素供能比总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        macro_eval: dict = evaluation_results.get('evaluation_macro_ratios', {})
        overall_summary += "  宏量供能比:\n"
        if macro_eval and macro_eval.get('macro_ratios'):
            for macro, eval_data in macro_eval['macro_ratios'].items():
                summary_line = f"    {macro}: {eval_data.get('actual_percentage', 'N/A'):.1f}%"
                if eval_data.get('target_range_percent'):
                    summary_line += f" (目标 {eval_data['target_range_percent'][0]:.0f}%-{eval_data['target_range_percent'][1]:.0f}%)"
                summary_line += f" - 评价: {eval_data.get('comment', 'N/A')}\n"
                overall_summary += summary_line
            overall_summary += f"  宏量供能比整体评价: {macro_eval.get('overall_comment', 'N/A')}\n"
        else:
            overall_summary += "    宏量营养素供能比评价数据缺失。\n"

        # 3.3 非产能主要营养素总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        micro_eval: dict = evaluation_results.get('evaluation_micronutrients', {})
        overall_summary += "  非产能营养素:\n"
        if micro_eval and micro_eval.get('micronutrients'):
            for micro, eval_data in micro_eval['micronutrients'].items():
                summary_line = f"    {micro}: {eval_data.get('actual_intake', 'N/A'):.{rounding_decimals}f}{eval_data.get('unit', '?')}"
                if eval_data.get('target_amount') is not None:
                    summary_line += f" (目标 {eval_data['target_amount']:.0f}{eval_data.get('unit', '?')}, 占目标 {eval_data.get('percentage_of_rni_ai', 'N/A'):.1f}%)"
                summary_line += f" - 评价: {eval_data.get('comment', 'N/A')}\n"
                overall_summary += summary_line
            overall_summary += f"  非产能营养素整体评价: {micro_eval.get('overall_comment', 'N/A')}\n"
        else:
            overall_summary += "    非产能主要营养素评价数据缺失。\n"

        # 5. AAS 总结
        overall_summary += "-" * 50 + "\n"  # Add separator before this section
        aas_eval: dict = evaluation_results.get('evaluation_aas', {})
        overall_summary += "  每餐 AAS:\n"
        if aas_eval and aas_eval.get('meal_aas'):
            for meal, eval_data in aas_eval['meal_aas'].items():
                summary_line = f"    {meal}: AAS {eval_data.get('aas', 'N/A'):.1f}"
                if eval_data.get('limiting_aa'):
                    summary_line += f" (限制性氨基酸: {eval_data['limiting_aa']})"
                summary_line += f" - 评价: {eval_data.get('comment', 'N/A')}\n"
                overall_summary += summary_line
            overall_summary += f"  每餐 AAS 整体评价: {aas_eval.get('overall_comment', 'N/A')}\n"
        else:
            overall_summary += "    每餐 AAS 评价数据缺失或计算失败。\n"

        # --- Separator between Evaluation Summary and Suggestions ---
        overall_summary += "\n" + "#" * 50 + "\n"

        # --- Comprehensive Evaluation Conclusions and Dietary Suggestions ---
        # The "综合评价结论:" header comes before suggestions list
        overall_summary += "综合评价结论:\n"

        suggestions = []  # Collect suggestions

        # --- Generate specific suggestions based on evaluation results ---
        # Food Structure Suggestions
        if fs_eval and not fs_eval.get('daily_variety_met', False):
            suggestions.append(
                f"食谱种类不足，建议增加每日食物种类数量，目标 > {standards.get('daily_variety_min', 'N/A')} 种，以增加食物多样性。")
        if fs_eval and not fs_eval.get('all_five_present', False):
            suggestions.append(
                f"食谱包含的食物类别不全，建议增加 {', '.join(fs_eval.get('missing_categories', []))} 等五大类食物的摄入。")

        # Energy Suggestions
        energy_comment = energy_eval.get('comment')
        if energy_comment == '偏低':
            suggestions.append(
                f"总能量摄入偏低 ({energy_eval.get('actual_kcal', 'N/A'):.0f} kcal)，建议适量增加食物摄入总量。")
        elif energy_comment == '偏高':
            suggestions.append(
                f"总能量摄入偏高 ({energy_eval.get('actual_kcal', 'N/A'):.0f} kcal)，建议适量减少食物摄入总量。")

        # Meal Ratio Suggestions
        if meal_ratio_eval and meal_ratio_eval.get('overall_comment') == '部分餐次比偏离':
            for meal, eval_data in meal_ratio_eval.get('meal_ratios', {}).items():
                meal_comment = eval_data.get('comment')
                if meal_comment == '偏低':
                    suggestions.append(
                        f"{meal} 供能比偏低 ({eval_data.get('actual_percentage', 'N/A'):.1f}%)，建议增加 {meal} 的食物摄入量，以使供能更均衡。")
                elif meal_comment == '偏高':
                    suggestions.append(
                        f"{meal} 供能比偏高 ({eval_data.get('actual_percentage', 'N/A'):.1f}%)，建议减少 {meal} 的食物摄入量，并合理分配到其他餐次。")

        # Macro Ratio Suggestions
        if macro_eval and macro_eval.get('overall_comment') == '部分宏量比偏离':
            for macro, eval_data in macro_eval.get('macro_ratios', {}).items():
                macro_comment = eval_data.get('comment')
                if macro_comment == '偏低':
                    suggestions.append(
                        f"{macro} 供能比偏低 ({eval_data.get('actual_percentage', 'N/A'):.1f}%)，建议增加富含 {macro} 的食物摄入，如{'全谷物、薯类' if macro == '碳水化合物' else ('鱼禽蛋瘦肉、豆制品' if macro == '蛋白质' else '优质植物油、坚果')}等。")
                elif macro_comment == '偏高':
                    suggestions.append(
                        f"{macro} 供能比偏高 ({eval_data.get('actual_percentage', 'N/A'):.1f}%)，建议减少富含 {macro} 的食物摄入。")

        # Micronutrient Suggestions (focus on '不足')
        if micro_eval and micro_eval.get('overall_comment') in ['部分非产能营养素摄入不足', '部分未达标，需改进']:
            suggestions.append("食谱中部分非产能主要营养素摄入不足，需重点改进：")
            for micro, eval_data in micro_eval.get('micronutrients', {}).items():
                micro_comment = eval_data.get('comment')
                if micro_comment in ['不足', '严重不足']:
                    suggestion_text = f"  {micro}: 摄入量不足 (占目标 {eval_data.get('percentage_of_rni_ai', 'N/A'):.1f}%)，建议增加富含 {micro} 的食物。"
                    if micro == '钙':
                        suggestion_text += " (如奶制品、豆制品、深绿色蔬菜)"
                    elif micro == '铁':
                        suggestion_text += " (如瘦肉、动物肝脏、木耳)"
                    elif micro == '锌':
                        suggestion_text += " (如贝壳类海产品、红色肉类)"
                    elif micro == '维生素A':
                        suggestion_text += " (如动物肝脏、胡萝卜、深绿色蔬菜)"
                    elif micro == '维生素B1':
                        suggestion_text += " (如全谷物、豆类、瘦猪肉)"
                    elif micro == '维生素B2':
                        suggestion_text += " (如奶制品、动物内脏、蛋类)"
                    elif micro == '维生素C':
                        suggestion_text += " (如新鲜蔬菜水果，特别是深色蔬菜和柑橘类水果)"
                    suggestions.append(suggestion_text)

        # AAS Suggestions (focus on '不合理', '不够合理')
        if aas_eval and aas_eval.get('overall_comment') == '部分餐次 AAS 不足或计算/数据缺失 ❌':
            suggestions.append("部分餐次蛋白质质量（AAS）不理想，需注意食物搭配：")
            for meal, eval_data in aas_eval.get('meal_aas', {}).items():
                aas_comment = eval_data.get('comment')
                if aas_comment in ['不合理', '不够合理']:
                    suggestion_text = f"  {meal}: AAS 不理想 ({eval_data.get('aas', 'N/A'):.1f})，建议在该餐次搭配不同来源的蛋白质食物"
                    if eval_data.get('limiting_aa'):
                        suggestion_text += f" (限制性氨基酸: {eval_data['limiting_aa']})"
                    suggestion_text += "，如谷类和豆类同食，或增加优质动物蛋白。"
                    suggestions.append(suggestion_text)

        # --- Generate Final Report ---
        overall_summary += "\n膳食建议:\n"
        # Add separator before the list of suggestions if there are suggestions
        if suggestions:
            overall_summary += "-" * 50 + "\n"  # Add separator before the list starts
            for i, suggestion in enumerate(suggestions):
                overall_summary += f"  {i + 1}. {suggestion}\n"
        else:
            overall_summary += "  食谱评价基本符合要求，请继续保持均衡膳食。\n"

        overall_summary += f"\n--- {gender} 学生食谱整体评价与建议结束 ---\n"

        # Print the generated summary

        return overall_summary

    # --- 主函数 ---
    def main(self):
        """
        执行食谱的全部评价流程：分析结构、计算营养素、各项评价、生成总结和建议。
        不使用 student_id，只使用 gender。
        """
        gender = self.evaluation_results['gender']  # Use gender

        # Use gender in the start message

        # 1. 分析食物结构
        self.analyze_food_structure()

        # 2. 计算主要营养素含量 (获取日总和每餐总)
        df_intake, df_meal = self.calculate_nutrient_intakes()

        # 3.1 评价能量
        self.evaluate_energy(df_intake)

        # 3.2 评价餐次比
        self.evaluate_meal_ratio(df_intake, df_meal)

        # 3.3 评价非产能主要营养素
        self.evaluate_micronutrients(df_intake)

        # 4. 评价宏量营养素供能比
        self.evaluate_macro_ratios(df_intake)

        # 5. 评价每餐的蛋白质氨基酸评分 (AAS)
        self.calculate_and_evaluate_per_meal_aas(df_meal)
        food_structure_dict = self.evaluation_results['food_structure']
        # 6. 综合评价和建议 (Prints the final summary)
        aas_data = self.evaluation_results['evaluation_aas']['meal_aas']
        overall_summary = self.generate_overall_evaluation_and_suggestions()
        micronutrients_data = self.evaluation_results['evaluation_micronutrients']['micronutrients']
        if self.display_flag:
            print(f"\n--- 开始评价 {gender} 学生 的食谱 ---")
            print(overall_summary)
            # Use gender in the end message
            print(f"\n--- {gender} 学生 食谱评价全部完成 ---")

        self.plot_macro_energy_ratio(df_intake)
        self.plot_meal_energy_bar(df_meal)
        self.plot_meal_aas_scores(aas_data)
        self.plot_micronutrient_adequacy(micronutrients_data)
        self.plot_five_food_groups_pie(food_structure_dict)
