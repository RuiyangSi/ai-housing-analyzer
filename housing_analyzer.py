"""
房价深度分析模块
提供专业的房价数据分析功能
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

class HousingAnalyzer:
    """房价专业分析器"""
    
    def __init__(self, df: pd.DataFrame, city_name: str):
        """
        初始化分析器
        
        参数:
            df: 房价数据 DataFrame
            city_name: 城市名称
        """
        self.df = df.copy()
        self.city_name = city_name
        self.df['成交日期'] = pd.to_datetime(self.df['成交日期'])
        self.df['年份'] = self.df['成交日期'].dt.year
        self.df['月份'] = self.df['成交日期'].dt.month
        self.df['季度'] = self.df['成交日期'].dt.quarter
        self.df['年月'] = self.df['成交日期'].dt.to_period('M')
        
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        获取综合分析报告
        """
        return {
            'basic_stats': self.analyze_basic_statistics(),
            'price_trend': self.analyze_price_trend(),
            'volatility': self.analyze_volatility(),
            'market_activity': self.analyze_market_activity(),
            'area_analysis': self.analyze_area_distribution(),
            'price_range': self.analyze_price_range(),
            'seasonal': self.analyze_seasonality(),
            'yoy_comparison': self.analyze_year_over_year(),
            'district_deep': self.analyze_district_deep(),
            'investment_index': self.calculate_investment_index(),
            'violin_data': self.analyze_price_violin_data(),
            'heatmap_data': self.analyze_district_heatmap_data(),
            'waterfall_data': self.analyze_price_waterfall_data(),
            'house_type_analysis': self.analyze_house_type()  # 新增：户型分析
        }
    
    def analyze_basic_statistics(self) -> Dict[str, Any]:
        """基础统计分析"""
        return {
            'total_transactions': int(len(self.df)),
            'date_range': {
                'start': self.df['成交日期'].min().strftime('%Y-%m-%d'),
                'end': self.df['成交日期'].max().strftime('%Y-%m-%d')
            },
            'price': {
                'mean': round(float(self.df['成交价（万元）'].mean()), 2),
                'median': round(float(self.df['成交价（万元）'].median()), 2),
                'std': round(float(self.df['成交价（万元）'].std()), 2),
                'min': round(float(self.df['成交价（万元）'].min()), 2),
                'max': round(float(self.df['成交价（万元）'].max()), 2),
                'q25': round(float(self.df['成交价（万元）'].quantile(0.25)), 2),
                'q75': round(float(self.df['成交价（万元）'].quantile(0.75)), 2)
            },
            'unit_price': {
                'mean': round(float(self.df['成交单价（元）'].mean()), 2),
                'median': round(float(self.df['成交单价（元）'].median()), 2),
                'std': round(float(self.df['成交单价（元）'].std()), 2),
                'min': round(float(self.df['成交单价（元）'].min()), 2),
                'max': round(float(self.df['成交单价（元）'].max()), 2)
            },
            'area': {
                'mean': round(float(self.df['面积（m²）'].mean()), 2),
                'median': round(float(self.df['面积（m²）'].median()), 2),
                'std': round(float(self.df['面积（m²）'].std()), 2)
            }
        }
    
    def analyze_price_trend(self) -> Dict[str, Any]:
        """价格趋势分析"""
        monthly = self.df.groupby('年月').agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean'
        }).reset_index()
        
        monthly['年月'] = monthly['年月'].astype(str)
        
        # 计算环比增长率，并替换NaN为0
        monthly['价格环比'] = monthly['成交价（万元）'].pct_change() * 100
        monthly['单价环比'] = monthly['成交单价（元）'].pct_change() * 100
        monthly['价格环比'] = monthly['价格环比'].fillna(0)
        monthly['单价环比'] = monthly['单价环比'].fillna(0)
        
        # 整体趋势
        first_price = monthly['成交价（万元）'].iloc[0]
        last_price = monthly['成交价（万元）'].iloc[-1]
        total_change = ((last_price - first_price) / first_price) * 100
        
        return {
            'monthly_data': monthly.to_dict('records'),
            'overall_trend': {
                'first_month': monthly['年月'].iloc[0],
                'last_month': monthly['年月'].iloc[-1],
                'first_price': round(float(first_price), 2),
                'last_price': round(float(last_price), 2),
                'total_change_percent': round(float(total_change), 2),
                'trend_direction': '上涨' if total_change > 0 else '下跌' if total_change < 0 else '持平'
            },
            'peak_month': monthly.loc[monthly['成交价（万元）'].idxmax(), '年月'],
            'peak_price': round(float(monthly['成交价（万元）'].max()), 2),
            'lowest_month': monthly.loc[monthly['成交价（万元）'].idxmin(), '年月'],
            'lowest_price': round(float(monthly['成交价（万元）'].min()), 2)
        }
    
    def analyze_volatility(self) -> Dict[str, Any]:
        """波动性分析"""
        monthly_prices = self.df.groupby('年月')['成交价（万元）'].mean()
        
        # 计算变异系数（CV）
        cv = (monthly_prices.std() / monthly_prices.mean()) * 100
        
        # 计算价格波动范围
        price_range = monthly_prices.max() - monthly_prices.min()
        price_range_pct = (price_range / monthly_prices.mean()) * 100
        
        return {
            'coefficient_of_variation': round(float(cv), 2),
            'price_range': round(float(price_range), 2),
            'price_range_percent': round(float(price_range_pct), 2),
            'stability_level': self._get_stability_level(cv),
            'volatility_description': self._describe_volatility(cv)
        }
    
    def _get_stability_level(self, cv: float) -> str:
        """根据变异系数判断稳定性"""
        if cv < 5:
            return '非常稳定'
        elif cv < 10:
            return '稳定'
        elif cv < 15:
            return '一般'
        elif cv < 20:
            return '波动较大'
        else:
            return '波动剧烈'
    
    def _describe_volatility(self, cv: float) -> str:
        """描述波动性"""
        if cv < 10:
            return '市场价格波动小，显示出较强的稳定性，适合长期持有。'
        elif cv < 20:
            return '市场价格有一定波动，但在合理范围内，需要关注市场动态。'
        else:
            return '市场价格波动较大，存在一定风险，建议谨慎投资。'
    
    def analyze_market_activity(self) -> Dict[str, Any]:
        """市场活跃度分析"""
        monthly_volume = self.df.groupby('年月').size()
        yearly_volume = self.df.groupby('年份').size()
        
        return {
            'monthly_average': round(float(monthly_volume.mean()), 2),
            'monthly_max': int(monthly_volume.max()),
            'monthly_min': int(monthly_volume.min()),
            'yearly_data': [
                {
                    'year': int(year),
                    'volume': int(vol),
                    'market_share': round(float((vol / len(self.df)) * 100), 2)
                }
                for year, vol in yearly_volume.items()
            ],
            'most_active_month': monthly_volume.idxmax().strftime('%Y-%m'),
            'least_active_month': monthly_volume.idxmin().strftime('%Y-%m'),
            'activity_level': self._assess_activity_level(monthly_volume.mean())
        }
    
    def _assess_activity_level(self, avg_monthly: float) -> str:
        """评估市场活跃度"""
        if avg_monthly > 5000:
            return '高度活跃'
        elif avg_monthly > 3000:
            return '活跃'
        elif avg_monthly > 1000:
            return '一般'
        else:
            return '相对平淡'
    
    def analyze_area_distribution(self) -> Dict[str, Any]:
        """面积分布分析"""
        area_ranges = [
            (0, 50, '小户型（<50㎡）'),
            (50, 90, '中小户型（50-90㎡）'),
            (90, 120, '中户型（90-120㎡）'),
            (120, 150, '中大户型（120-150㎡）'),
            (150, 200, '大户型（150-200㎡）'),
            (200, float('inf'), '豪宅（>200㎡）')
        ]
        
        distribution = []
        for min_area, max_area, label in area_ranges:
            count = len(self.df[(self.df['面积（m²）'] >= min_area) & (self.df['面积（m²）'] < max_area)])
            avg_price = self.df[(self.df['面积（m²）'] >= min_area) & (self.df['面积（m²）'] < max_area)]['成交价（万元）'].mean()
            
            distribution.append({
                'category': label,
                'count': int(count),
                'percentage': round(float((count / len(self.df)) * 100), 2),
                'avg_price': round(float(avg_price), 2) if not pd.isna(avg_price) else 0
            })
        
        # 主流户型
        main_category = max(distribution, key=lambda x: x['count'])
        
        return {
            'distribution': distribution,
            'main_category': main_category['category'],
            'main_percentage': main_category['percentage']
        }
    
    def analyze_price_range(self) -> Dict[str, Any]:
        """价格区间分析"""
        price_ranges = [
            (0, 100, '100万以下'),
            (100, 200, '100-200万'),
            (200, 300, '200-300万'),
            (300, 500, '300-500万'),
            (500, 800, '500-800万'),
            (800, 1000, '800-1000万'),
            (1000, float('inf'), '1000万以上')
        ]
        
        distribution = []
        for min_price, max_price, label in price_ranges:
            count = len(self.df[(self.df['成交价（万元）'] >= min_price) & (self.df['成交价（万元）'] < max_price)])
            
            distribution.append({
                'range': label,
                'count': int(count),
                'percentage': round(float((count / len(self.df)) * 100), 2)
            })
        
        # 主流价格段
        main_range = max(distribution, key=lambda x: x['count'])
        
        return {
            'distribution': distribution,
            'main_range': main_range['range'],
            'main_percentage': main_range['percentage']
        }
    
    def analyze_seasonality(self) -> Dict[str, Any]:
        """季节性分析"""
        seasonal = self.df.groupby(['年份', '季度']).agg({
            '成交价（万元）': 'mean',
            '面积（m²）': 'count'
        }).reset_index()
        
        seasonal.columns = ['年份', '季度', '平均价格', '成交量']
        
        # 各季度平均表现
        quarter_avg = self.df.groupby('季度').agg({
            '成交价（万元）': 'mean',
            '面积（m²）': 'count'
        }).reset_index()
        
        return {
            'quarterly_data': seasonal.to_dict('records'),
            'quarter_averages': [
                {
                    'quarter': f'Q{int(q)}',
                    'avg_price': round(float(p), 2),
                    'avg_volume': round(float(v), 2)
                }
                for q, p, v in zip(quarter_avg['季度'], quarter_avg['成交价（万元）'], quarter_avg['面积（m²）'])
            ]
        }
    
    def analyze_year_over_year(self) -> Dict[str, Any]:
        """同比分析"""
        yearly = self.df.groupby('年份').agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean',
            '面积（m²）': ['mean', 'count']
        }).reset_index()
        
        yearly.columns = ['年份', '平均价格', '平均单价', '平均面积', '成交量']
        
        # 计算同比增长
        yoy_data = []
        for i in range(len(yearly)):
            data = {
                'year': int(yearly.iloc[i]['年份']),
                'avg_price': round(float(yearly.iloc[i]['平均价格']), 2),
                'avg_unit_price': round(float(yearly.iloc[i]['平均单价']), 2),
                'volume': int(yearly.iloc[i]['成交量'])
            }
            
            if i > 0:
                prev_price = yearly.iloc[i-1]['平均价格']
                data['yoy_price_change'] = round(float(((yearly.iloc[i]['平均价格'] - prev_price) / prev_price) * 100), 2)
                
                prev_volume = yearly.iloc[i-1]['成交量']
                data['yoy_volume_change'] = round(float(((yearly.iloc[i]['成交量'] - prev_volume) / prev_volume) * 100), 2)
            
            yoy_data.append(data)
        
        return {'yearly_comparison': yoy_data}
    
    def analyze_district_deep(self) -> Dict[str, Any]:
        """区域深度分析"""
        district_stats = self.df.groupby('区域').agg({
            '成交价（万元）': ['mean', 'median', 'std', 'count'],
            '成交单价（元）': ['mean', 'median'],
            '面积（m²）': 'mean'
        }).reset_index()
        
        district_stats.columns = ['区域', '平均价格', '中位价格', '价格标准差', '成交量', '平均单价', '中位单价', '平均面积']
        
        # 排序并取前15
        district_stats = district_stats.sort_values('平均单价', ascending=False).head(15)
        
        districts = []
        for _, row in district_stats.iterrows():
            districts.append({
                'district': row['区域'],
                'avg_price': round(float(row['平均价格']), 2),
                'median_price': round(float(row['中位价格']), 2),
                'price_std': round(float(row['价格标准差']), 2),
                'volume': int(row['成交量']),
                'avg_unit_price': round(float(row['平均单价']), 2),
                'avg_area': round(float(row['平均面积']), 2),
                'price_stability': '稳定' if row['价格标准差'] < row['平均价格'] * 0.3 else '波动较大'
            })
        
        return {'top_districts': districts}
    
    def analyze_price_violin_data(self) -> Dict[str, Any]:
        """价格分布数据（用于小提琴图）"""
        import numpy as np
        
        prices = self.df['成交价（万元）'].dropna()
        
        # 基本统计
        stats = {
            'min': float(prices.min()),
            'q1': float(prices.quantile(0.25)),
            'median': float(prices.quantile(0.50)),
            'q3': float(prices.quantile(0.75)),
            'max': float(prices.max()),
            'mean': float(prices.mean()),
            'std': float(prices.std())
        }
        
        # 计算密度估计（简化版，不需要scipy）
        # 使用直方图来估计密度
        hist, bin_edges = np.histogram(prices, bins=30, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        return {
            'stats': stats,
            'density': {
                'values': bin_centers.tolist(),
                'density': hist.tolist()
            },
            'samples': prices.sample(min(500, len(prices))).tolist()  # 采样用于显示
        }
    
    def analyze_district_heatmap_data(self) -> Dict[str, Any]:
        """区域-时间价格热力图数据"""
        # 按区域和月份聚合
        self.df['年月'] = self.df['成交日期'].dt.to_period('M').astype(str)
        
        heatmap_data = self.df.groupby(['区域', '年月'])['成交单价（元）'].mean().reset_index()
        
        # 获取所有区域和月份
        districts = sorted(heatmap_data['区域'].unique())
        months = sorted(heatmap_data['年月'].unique())
        
        # 构建矩阵
        matrix = []
        for district in districts:
            row = []
            for month in months:
                value = heatmap_data[
                    (heatmap_data['区域'] == district) & 
                    (heatmap_data['年月'] == month)
                ]['成交单价（元）'].values
                row.append(float(value[0]) if len(value) > 0 else 0)
            matrix.append(row)
        
        return {
            'districts': districts,
            'months': months,
            'data': matrix,
            'min_price': float(heatmap_data['成交单价（元）'].min()),
            'max_price': float(heatmap_data['成交单价（元）'].max())
        }
    
    def analyze_price_waterfall_data(self) -> Dict[str, Any]:
        """价格变化瀑布图数据"""
        # 计算价格变化的各个因素
        overall = self.analyze_price_trend()
        
        if 'overall_trend' not in overall:
            return {'factors': []}
        
        trend = overall['overall_trend']
        first_price = trend.get('first_price', 0)
        last_price = trend.get('last_price', 0)
        total_change = last_price - first_price
        
        # 分解价格变化因素（简化版）
        factors = [
            {
                'name': '起始价格',
                'value': first_price,
                'type': 'start'
            },
            {
                'name': '市场趋势',
                'value': total_change * 0.4,  # 假设40%归因于市场趋势
                'type': 'increase' if total_change > 0 else 'decrease'
            },
            {
                'name': '区域发展',
                'value': total_change * 0.3,  # 30%归因于区域发展
                'type': 'increase' if total_change > 0 else 'decrease'
            },
            {
                'name': '政策影响',
                'value': total_change * 0.2,  # 20%归因于政策
                'type': 'increase' if total_change > 0 else 'decrease'
            },
            {
                'name': '其他因素',
                'value': total_change * 0.1,  # 10%其他
                'type': 'increase' if total_change > 0 else 'decrease'
            },
            {
                'name': '当前价格',
                'value': last_price,
                'type': 'end'
            }
        ]
        
        return {
            'factors': factors,
            'total_change': total_change,
            'total_change_percent': trend.get('total_change_percent', 0)
        }
    
    def calculate_investment_index(self) -> Dict[str, Any]:
        """
        计算投资指数
        
        【计算方法说明】
        
        1. 价格趋势分数（40%权重）
           - 对比最近6个月与之前6个月的均价变化率
           - 公式：(最近6月均价 - 之前6月均价) / 之前6月均价 × 100
           - 正值=上涨，负值=下跌
        
        2. 成交量趋势分数（20%权重）
           - 对比最近6个月与之前6个月的成交量变化率
           - 公式：(最近6月成交量 - 之前6月成交量) / 之前6月成交量 × 100
           - 正值=活跃度提升，负值=活跃度下降
        
        3. 市场稳定性分数（40%权重）**已修复**
           - 基于价格变异系数(CV)计算
           - CV = 标准差/均值 × 100%，反映价格波动程度
           - 公式：100 / (1 + CV/10)
           - CV=0时为100分(完全稳定)，CV=100时约9分(波动极大)
        
        4. 综合投资指数
           - 加权平均：趋势×0.4 + 成交量×0.2 + 稳定性×0.4
           - 归一化到0-100分
           - 评级：80-100优秀，60-79良好，40-59一般，0-39较差
        """
        recent_6m = self.df[self.df['成交日期'] >= self.df['成交日期'].max() - pd.DateOffset(months=6)]
        prev_6m = self.df[(self.df['成交日期'] >= self.df['成交日期'].max() - pd.DateOffset(months=12)) & 
                          (self.df['成交日期'] < self.df['成交日期'].max() - pd.DateOffset(months=6))]
        
        # 价格趋势
        if len(prev_6m) > 0:
            recent_avg = recent_6m['成交价（万元）'].mean()
            prev_avg = prev_6m['成交价（万元）'].mean()
            price_trend_score = ((recent_avg - prev_avg) / prev_avg) * 100
        else:
            recent_avg = recent_6m['成交价（万元）'].mean()
            prev_avg = recent_avg
            price_trend_score = 0
        
        # 成交量趋势
        volume_trend_score = ((len(recent_6m) - len(prev_6m)) / max(len(prev_6m), 1)) * 100
        
        # 价格稳定性（变异系数越低越好）**修复BUG**
        cv = (self.df['成交价（万元）'].std() / self.df['成交价（万元）'].mean()) * 100
        # 新公式：使用反比例函数，避免出现0分
        stability_score = 100 / (1 + cv / 10)
        
        # 综合投资指数（0-100）
        investment_index = (
            price_trend_score * 0.4 +  # 价格趋势权重40%
            volume_trend_score * 0.2 +  # 成交量趋势权重20%
            stability_score * 0.4        # 稳定性权重40%
        )
        
        # 归一化到0-100
        investment_index = max(0, min(100, 50 + investment_index))
        
        return {
            'index_score': round(float(investment_index), 2),
            'price_trend_score': round(float(price_trend_score), 2),
            'volume_trend_score': round(float(volume_trend_score), 2),
            'stability_score': round(float(stability_score), 2),
            'coefficient_of_variation': round(float(cv), 2),  # 添加CV值供参考
            'investment_level': self._get_investment_level(investment_index),
            'recommendation': self._get_investment_recommendation(investment_index),
            'calculation_details': {  # 添加计算详情
                'recent_avg_price': round(float(recent_avg), 2),
                'prev_avg_price': round(float(prev_avg), 2),
                'recent_volume': int(len(recent_6m)),
                'prev_volume': int(len(prev_6m)),
                'cv_percentage': round(float(cv), 2),
                'stability_level': '稳定' if cv < 30 else '一般' if cv < 50 else '波动较大'
            }
        }
    
    def _get_investment_level(self, score: float) -> str:
        """投资等级"""
        if score >= 80:
            return '优秀'
        elif score >= 70:
            return '良好'
        elif score >= 60:
            return '一般'
        elif score >= 50:
            return '较差'
        else:
            return '不建议'
    
    def _get_investment_recommendation(self, score: float) -> str:
        """投资建议"""
        if score >= 80:
            return '市场表现优异，价格趋势向好，成交活跃，适合投资。'
        elif score >= 70:
            return '市场表现良好，整体向好，可以考虑投资，建议选择优质区域。'
        elif score >= 60:
            return '市场表现一般，需要谨慎评估，建议深入研究后决策。'
        elif score >= 50:
            return '市场表现欠佳，存在一定风险，不建议短期投资。'
        else:
            return '市场表现较差，风险较高，建议观望或考虑其他城市。'
    
    def analyze_house_type(self) -> Dict[str, Any]:
        """
        户型分析（几室几厅）
        
        分析内容：
        1. 户型分布（各种户型的占比）
        2. 不同户型的价格统计
        3. 户型与面积的关系
        4. 户型的价格趋势
        5. 主流户型分析
        """
        if '户型' not in self.df.columns or self.df['户型'].isna().all():
            return {
                'available': False,
                'message': '该城市数据中没有户型信息'
            }
        
        # 清洗户型数据（去除空值）
        df_with_type = self.df[self.df['户型'].notna()].copy()
        
        if len(df_with_type) == 0:
            return {
                'available': False,
                'message': '该城市数据中没有有效的户型信息'
            }
        
        # 1. 户型分布统计
        type_distribution = df_with_type['户型'].value_counts()
        distribution_data = []
        
        for house_type, count in type_distribution.head(15).items():  # 取前15种户型
            percentage = (count / len(df_with_type)) * 100
            avg_price = df_with_type[df_with_type['户型'] == house_type]['成交价（万元）'].mean()
            avg_unit_price = df_with_type[df_with_type['户型'] == house_type]['成交单价（元）'].mean()
            avg_area = df_with_type[df_with_type['户型'] == house_type]['面积（m²）'].mean()
            
            distribution_data.append({
                'house_type': house_type,
                'count': int(count),
                'percentage': round(float(percentage), 2),
                'avg_price': round(float(avg_price), 2),
                'avg_unit_price': round(float(avg_unit_price), 2),
                'avg_area': round(float(avg_area), 2)
            })
        
        # 2. 主流户型分析
        main_type = type_distribution.index[0] if len(type_distribution) > 0 else '未知'
        main_percentage = (type_distribution.values[0] / len(df_with_type)) * 100 if len(type_distribution) > 0 else 0
        
        # 3. 按室数统计（提取"X室"）
        df_with_type['室数'] = df_with_type['户型'].str.extract(r'(\d+)室')[0]
        df_with_type['室数'] = pd.to_numeric(df_with_type['室数'], errors='coerce')
        
        room_stats = []
        for room_num in sorted(df_with_type['室数'].dropna().unique()):
            room_data = df_with_type[df_with_type['室数'] == room_num]
            room_stats.append({
                'room_count': int(room_num),
                'label': f'{int(room_num)}室',
                'count': int(len(room_data)),
                'percentage': round(float((len(room_data) / len(df_with_type)) * 100), 2),
                'avg_price': round(float(room_data['成交价（万元）'].mean()), 2),
                'avg_unit_price': round(float(room_data['成交单价（元）'].mean()), 2),
                'avg_area': round(float(room_data['面积（m²）'].mean()), 2),
                'price_range': [
                    round(float(room_data['成交价（万元）'].quantile(0.25)), 2),
                    round(float(room_data['成交价（万元）'].quantile(0.75)), 2)
                ]
            })
        
        # 4. 户型价格趋势（按月）
        type_trend_data = []
        top_types = type_distribution.head(5).index.tolist()  # 分析前5种户型
        
        for house_type in top_types:
            monthly_trend = df_with_type[df_with_type['户型'] == house_type].groupby('年月').agg({
                '成交价（万元）': 'mean',
                '成交单价（元）': 'mean'
            }).reset_index()
            
            monthly_trend['年月'] = monthly_trend['年月'].astype(str)
            
            type_trend_data.append({
                'house_type': house_type,
                'trend': [
                    {
                        'month': row['年月'],
                        'avg_price': round(float(row['成交价（万元）']), 2),
                        'avg_unit_price': round(float(row['成交单价（元）']), 2)
                    }
                    for _, row in monthly_trend.iterrows()
                ]
            })
        
        # 5. 户型与面积的关系分析
        type_area_relation = []
        for house_type in type_distribution.head(10).index:
            type_data = df_with_type[df_with_type['户型'] == house_type]
            type_area_relation.append({
                'house_type': house_type,
                'min_area': round(float(type_data['面积（m²）'].min()), 2),
                'avg_area': round(float(type_data['面积（m²）'].mean()), 2),
                'max_area': round(float(type_data['面积（m²）'].max()), 2),
                'area_std': round(float(type_data['面积（m²）'].std()), 2)
            })
        
        # 6. 总结分析
        summary = {
            'total_types': int(len(type_distribution)),
            'main_type': main_type,
            'main_percentage': round(float(main_percentage), 2),
            'data_coverage': round(float((len(df_with_type) / len(self.df)) * 100), 2),
            'most_expensive_type': distribution_data[0]['house_type'] if distribution_data else '未知',
            'most_expensive_avg_price': distribution_data[0]['avg_price'] if distribution_data else 0
        }
        
        # 找出最贵的户型（按平均单价）
        sorted_by_price = sorted(distribution_data, key=lambda x: x['avg_unit_price'], reverse=True)
        if sorted_by_price:
            summary['most_expensive_type'] = sorted_by_price[0]['house_type']
            summary['most_expensive_unit_price'] = sorted_by_price[0]['avg_unit_price']
        
        return {
            'available': True,
            'distribution': distribution_data,
            'room_statistics': room_stats,
            'type_trends': type_trend_data,
            'type_area_relation': type_area_relation,
            'summary': summary
        }

