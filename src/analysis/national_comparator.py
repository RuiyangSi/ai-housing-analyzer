"""
全国城市对比分析模块
对比多个城市的房价数据，提供横向分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from src.analysis.housing_analyzer import HousingAnalyzer

class NationalComparator:
    """全国城市对比分析器"""
    
    def __init__(self, cities_data: Dict[str, pd.DataFrame]):
        """
        初始化对比分析器
        
        参数:
            cities_data: {城市名: DataFrame} 字典
        """
        self.cities_data = cities_data
        self.analyzers = {
            city: HousingAnalyzer(df, city) 
            for city, df in cities_data.items()
        }
    
    def get_comprehensive_comparison(self) -> Dict[str, Any]:
        """获取全面对比分析"""
        return {
            'overview': self.compare_overview(),
            'price_comparison': self.compare_prices(),
            'market_scale': self.compare_market_scale(),
            'growth_rates': self.compare_growth_rates(),
            'volatility': self.compare_volatility(),
            'affordability': self.compare_affordability(),
            'investment_scores': self.compare_investment_scores(),
            'regional_characteristics': self.analyze_regional_characteristics(),
            'house_type_comparison': self.compare_house_types(),  # 新增：户型对比
            'recommendations': self.generate_recommendations()
        }
    
    def compare_overview(self) -> Dict[str, Any]:
        """总体对比"""
        comparisons = []
        
        for city, analyzer in self.analyzers.items():
            stats = analyzer.analyze_basic_statistics()
            comparisons.append({
                'city': city,
                'total_transactions': stats['total_transactions'],
                'avg_price': stats['price']['mean'],
                'avg_unit_price': stats['unit_price']['mean'],
                'avg_area': stats['area']['mean'],
                'price_range': f"{stats['price']['min']}-{stats['price']['max']}"
            })
        
        # 排名
        comparisons_sorted_by_price = sorted(comparisons, key=lambda x: x['avg_price'], reverse=True)
        for idx, item in enumerate(comparisons_sorted_by_price, 1):
            item['price_rank'] = idx
        
        comparisons_sorted_by_volume = sorted(comparisons, key=lambda x: x['total_transactions'], reverse=True)
        for idx, item in enumerate(comparisons_sorted_by_volume, 1):
            item['volume_rank'] = idx
        
        return {
            'cities': comparisons,
            'total_transactions_all': sum(c['total_transactions'] for c in comparisons),
            'highest_price_city': max(comparisons, key=lambda x: x['avg_price'])['city'],
            'lowest_price_city': min(comparisons, key=lambda x: x['avg_price'])['city'],
            'most_active_city': max(comparisons, key=lambda x: x['total_transactions'])['city']
        }
    
    def compare_prices(self) -> Dict[str, Any]:
        """价格对比分析"""
        price_data = []
        unit_price_data = []
        
        for city, analyzer in self.analyzers.items():
            stats = analyzer.analyze_basic_statistics()
            price_data.append({
                'city': city,
                'mean': stats['price']['mean'],
                'median': stats['price']['median'],
                'std': stats['price']['std'],
                'q25': stats['price']['q25'],
                'q75': stats['price']['q75']
            })
            unit_price_data.append({
                'city': city,
                'mean': stats['unit_price']['mean'],
                'median': stats['unit_price']['median'],
                'std': stats['unit_price']['std']
            })
        
        # 计算价格差距
        prices = [p['mean'] for p in price_data]
        price_gap = max(prices) - min(prices)
        price_ratio = max(prices) / min(prices) if min(prices) > 0 else 0
        
        return {
            'price_comparison': price_data,
            'unit_price_comparison': unit_price_data,
            'price_gap': round(price_gap, 2),
            'price_ratio': round(price_ratio, 2),
            'price_disparity_level': self._assess_price_disparity(price_ratio)
        }
    
    def _assess_price_disparity(self, ratio: float) -> str:
        """评估价格差距水平"""
        if ratio < 1.5:
            return '差距较小'
        elif ratio < 2:
            return '差距中等'
        elif ratio < 3:
            return '差距较大'
        else:
            return '差距悬殊'
    
    def compare_market_scale(self) -> Dict[str, Any]:
        """市场规模对比"""
        scale_data = []
        
        for city, df in self.cities_data.items():
            total_volume = len(df)
            total_value = df['成交价（万元）'].sum()
            avg_monthly = total_volume / df['成交日期'].dt.to_period('M').nunique()
            avg_daily = total_volume / ((df['成交日期'].max() - df['成交日期'].min()).days + 1)
            
            scale_data.append({
                'city': city,
                'total_transactions': int(total_volume),
                'total_volume': int(total_volume),  # 为前端兼容性
                'total_value': round(float(total_value), 2),
                'avg_monthly_volume': round(float(avg_monthly), 2),
                'avg_daily_volume': round(float(avg_daily), 2),
                'market_share': 0  # 待计算
            })
        
        # 计算市场份额
        total_transactions = sum(s['total_transactions'] for s in scale_data)
        for item in scale_data:
            item['market_share'] = round((item['total_transactions'] / total_transactions) * 100, 2)
        
        return {
            'scale_comparison': scale_data,
            'scale_data': sorted(scale_data, key=lambda x: x['total_value'], reverse=True),  # 为前端兼容性
            'total_market_value': sum(s['total_value'] for s in scale_data),
            'dominant_city': max(scale_data, key=lambda x: x['market_share'])['city'],
            'largest_market': max(scale_data, key=lambda x: x['total_value'])['city']
        }
    
    def compare_growth_rates(self) -> Dict[str, Any]:
        """增长率对比"""
        growth_data = []
        
        for city, analyzer in self.analyzers.items():
            trend = analyzer.analyze_price_trend()
            overall = trend['overall_trend']
            yoy = analyzer.analyze_year_over_year()['yearly_comparison']
            
            growth_data.append({
                'city': city,
                'total_change_percent': overall['total_change_percent'],
                'trend_direction': overall['trend_direction'],
                'first_price': overall['first_price'],
                'last_price': overall['last_price'],
                'avg_annual_growth': overall['total_change_percent'],
                'growth_stability': '稳定' if abs(overall['total_change_percent']) < 10 else '波动',
                'yearly_details': yoy
            })
        
        # 找出表现最好和最差的城市
        best_performer = max(growth_data, key=lambda x: x['total_change_percent'])
        worst_performer = min(growth_data, key=lambda x: x['total_change_percent'])
        
        return {
            'growth_comparison': growth_data,
            'growth_data': growth_data,  # 为前端兼容性
            'best_performer': best_performer['city'],
            'best_growth_rate': best_performer['total_change_percent'],
            'worst_performer': worst_performer['city'],
            'worst_growth_rate': worst_performer['total_change_percent'],
            'overall_trend': self._determine_overall_trend(growth_data)
        }
    
    def _determine_overall_trend(self, growth_data: List[Dict]) -> str:
        """判断整体趋势"""
        avg_growth = sum(g['total_change_percent'] for g in growth_data) / len(growth_data)
        positive_count = sum(1 for g in growth_data if g['total_change_percent'] > 0)
        
        if positive_count == len(growth_data):
            return '全面上涨'
        elif positive_count == 0:
            return '全面下跌'
        elif avg_growth > 0:
            return '整体上涨，局部分化'
        else:
            return '整体下跌，局部分化'
    
    def compare_volatility(self) -> Dict[str, Any]:
        """波动性对比"""
        volatility_data = []
        
        for city, analyzer in self.analyzers.items():
            vol = analyzer.analyze_volatility()
            cv = vol['coefficient_of_variation']
            volatility_data.append({
                'city': city,
                'coefficient_of_variation': cv,
                'cv': cv,  # 为前端兼容性
                'stability_level': vol['stability_level'],
                'stability': vol['stability_level'],  # 为前端兼容性
                'price_range_percent': vol['price_range_percent'],
                'risk_level': self._assess_risk_level(cv)
            })
        
        # 找出最稳定和最波动的城市
        most_stable = min(volatility_data, key=lambda x: x['coefficient_of_variation'])
        most_volatile = max(volatility_data, key=lambda x: x['coefficient_of_variation'])
        
        return {
            'volatility_comparison': volatility_data,
            'volatility_data': volatility_data,  # 为前端兼容性
            'most_stable_city': most_stable['city'],
            'most_stable_cv': most_stable['coefficient_of_variation'],
            'most_volatile_city': most_volatile['city'],
            'most_volatile_cv': most_volatile['coefficient_of_variation'],
            'safest_city': most_stable['city'],
            'riskiest_city': most_volatile['city']
        }
    
    def _assess_risk_level(self, cv: float) -> str:
        """评估风险等级"""
        if cv < 10:
            return '低风险'
        elif cv < 15:
            return '中低风险'
        elif cv < 20:
            return '中等风险'
        else:
            return '较高风险'
    
    def compare_affordability(self) -> Dict[str, Any]:
        """购买力/可负担性对比"""
        affordability_data = []
        
        for city, df in self.cities_data.items():
            # 计算不同价位段的占比
            affordable = len(df[df['成交价（万元）'] <= 200])
            mid_range = len(df[(df['成交价（万元）'] > 200) & (df['成交价（万元）'] <= 500)])
            high_end = len(df[df['成交价（万元）'] > 500])
            total = len(df)
            
            avg_price = df['成交价（万元）'].mean()
            affordable_pct = (affordable / total) * 100
            
            affordability_data.append({
                'city': city,
                'affordable_percent': round(affordable_pct, 2),
                'mid_range_percent': round((mid_range / total) * 100, 2),
                'high_end_percent': round((high_end / total) * 100, 2),
                'median_price': round(float(df['成交价（万元）'].median()), 2),
                'avg_down_payment': round(float(avg_price * 0.3), 2),
                'affordability_level': self._rate_affordability(affordable_pct)
            })
        
        # 找出最可负担的城市
        most_affordable = max(affordability_data, key=lambda x: x['affordable_percent'])
        
        return {
            'affordability_comparison': affordability_data,
            'affordability_data': affordability_data,  # 为前端兼容性
            'most_affordable_city': most_affordable['city'],
            'most_affordable_percent': most_affordable['affordable_percent'],
            'most_affordable': most_affordable['city']
        }
    
    def _rate_affordability(self, percent: float) -> str:
        """评级可负担性"""
        if percent > 70:
            return '高可负担性'
        elif percent > 50:
            return '中等可负担性'
        elif percent > 30:
            return '低可负担性'
        else:
            return '较难负担'
    
    def compare_investment_scores(self) -> Dict[str, Any]:
        """投资指数对比"""
        scores_data = []
        
        for city, analyzer in self.analyzers.items():
            index = analyzer.calculate_investment_index()
            scores_data.append({
                'city': city,
                'investment_score': index['index_score'],
                'total_score': index['index_score'],  # 为前端兼容性
                'investment_level': index['investment_level'],
                'level': index['investment_level'],  # 为前端兼容性
                'price_trend_score': index['price_trend_score'],
                'price_trend': index['price_trend_score'],  # 为前端兼容性
                'stability_score': index['stability_score'],
                'stability': index['stability_score'],  # 为前端兼容性
                'volume_trend_score': index.get('volume_trend_score', 50),
                'volume_trend': index.get('volume_trend_score', 50),  # 为前端兼容性
                'recommendation': index.get('recommendation', '')
            })
        
        # 排名
        scores_sorted = sorted(scores_data, key=lambda x: x['investment_score'], reverse=True)
        for idx, item in enumerate(scores_sorted, 1):
            item['rank'] = idx
        
        return {
            'investment_comparison': scores_sorted,
            'scores': scores_sorted,  # 为前端兼容性
            'best_investment': scores_sorted[0]['city'],
            'best_score': scores_sorted[0]['investment_score']
        }
    
    def analyze_regional_characteristics(self) -> Dict[str, Any]:
        """区域特征分析"""
        characteristics = []
        
        for city, df in self.cities_data.items():
            # 主力户型
            area_ranges = [
                (0, 90, '刚需型'),
                (90, 140, '改善型'),
                (140, float('inf'), '豪宅型')
            ]
            
            type_stats = []
            for min_a, max_a, label in area_ranges:
                count = len(df[(df['面积（m²）'] >= min_a) & (df['面积（m²）'] < max_a)])
                type_stats.append({
                    'type': label,
                    'percentage': round((count / len(df)) * 100, 2)
                })
            
            main_type = max(type_stats, key=lambda x: x['percentage'])
            
            # 价格分层
            high_price_districts = df.groupby('区域')['成交单价（元）'].mean().nlargest(3)
            low_price_districts = df.groupby('区域')['成交单价（元）'].mean().nsmallest(3)
            active_districts = df.groupby('区域').size().nlargest(5)
            
            characteristics.append({
                'city': city,
                'main_property_type': main_type['type'],
                'main_type_percentage': main_type['percentage'],
                'avg_area': round(float(df['面积（m²）'].mean()), 2),
                'characteristics': self._describe_city_characteristics(city, df, main_type['type']),
                'high_price_areas': [
                    {'district': idx, 'unit_price': round(float(val), 2)}
                    for idx, val in high_price_districts.items()
                ],
                'low_price_areas': [
                    {'district': idx, 'unit_price': round(float(val), 2)}
                    for idx, val in low_price_districts.items()
                ],
                'most_active_areas': [
                    {'district': idx, 'volume': int(val)}
                    for idx, val in active_districts.items()
                ],
                'district_count': int(df['区域'].nunique())
            })
        
        return {
            'regional_characteristics': characteristics,
            'characteristics': characteristics  # 为前端兼容性
        }
    
    def _describe_city_characteristics(self, city: str, df: pd.DataFrame, main_type: str) -> str:
        """描述城市特征"""
        avg_price = df['成交价（万元）'].mean()
        avg_unit_price = df['成交单价（元）'].mean()
        
        if avg_price > 400:
            price_level = '高价'
        elif avg_price > 200:
            price_level = '中高价'
        else:
            price_level = '相对亲民'
        
        return f"{city}以{main_type}为主，整体{price_level}，适合对应人群。"
    
    def generate_recommendations(self) -> Dict[str, Any]:
        """生成投资建议"""
        recommendations = {
            'for_first_time_buyers': [],
            'for_upgraders': [],
            'for_investors': []
        }
        
        # 获取各城市的关键指标
        city_metrics = {}
        for city, analyzer in self.analyzers.items():
            stats = analyzer.analyze_basic_statistics()
            investment = analyzer.calculate_investment_index()
            volatility = analyzer.analyze_volatility()
            
            city_metrics[city] = {
                'avg_price': stats['price']['mean'],
                'investment_score': investment['index_score'],
                'cv': volatility['coefficient_of_variation']
            }
        
        # 刚需购房者建议（低价+稳定）
        for_first_time = sorted(city_metrics.items(), key=lambda x: x[1]['avg_price'])
        recommendations['for_first_time_buyers'] = [
            {
                'city': city,
                'reason': f"平均价格{metrics['avg_price']:.2f}万元，相对可负担",
                'priority': idx
            }
            for idx, (city, metrics) in enumerate(for_first_time[:2], 1)
        ]
        
        # 改善型购房者建议（投资指数+稳定性）
        for_upgraders = sorted(
            city_metrics.items(),
            key=lambda x: (x[1]['investment_score'], -x[1]['cv']),
            reverse=True
        )
        recommendations['for_upgraders'] = [
            {
                'city': city,
                'reason': f"投资指数{metrics['investment_score']:.1f}分，市场较稳定",
                'priority': idx
            }
            for idx, (city, metrics) in enumerate(for_upgraders[:2], 1)
        ]
        
        # 投资者建议（投资指数最高）
        for_investors = sorted(city_metrics.items(), key=lambda x: x[1]['investment_score'], reverse=True)
        recommendations['for_investors'] = [
            {
                'city': city,
                'reason': f"投资价值评分{metrics['investment_score']:.1f}，潜力较大",
                'priority': idx
            }
            for idx, (city, metrics) in enumerate(for_investors[:2], 1)
        ]
        
        return recommendations
    
    def compare_house_types(self) -> Dict[str, Any]:
        """
        全国户型对比分析
        
        对比各城市的户型分布、主流户型和户型价格差异
        """
        house_type_comparison = {
            'cities_data': [],
            'summary': {
                'cities_with_data': 0,
                'total_house_types': set(),
                'common_types': [],
                'price_leaders': {}
            }
        }
        
        all_house_types = set()
        cities_with_data = 0
        
        # 收集各城市户型数据
        for city, analyzer in self.analyzers.items():
            house_type_data = analyzer.analyze_house_type()
            
            if house_type_data and house_type_data.get('available', False):
                cities_with_data += 1
                
                # 提取主要信息
                city_info = {
                    'city': city,
                    'main_type': house_type_data['summary']['main_type'],
                    'main_percentage': house_type_data['summary']['main_percentage'],
                    'total_types': house_type_data['summary']['total_types'],
                    'data_coverage': house_type_data['summary']['data_coverage'],
                    'most_expensive_type': house_type_data['summary'].get('most_expensive_type', ''),
                    'most_expensive_unit_price': house_type_data['summary'].get('most_expensive_unit_price', 0),
                    'distribution': house_type_data['distribution'][:5],  # 只取前5种
                    'room_statistics': house_type_data['room_statistics']
                }
                
                house_type_comparison['cities_data'].append(city_info)
                
                # 收集所有户型
                for item in house_type_data['distribution']:
                    all_house_types.add(item['house_type'])
        
        # 统计信息
        house_type_comparison['summary']['cities_with_data'] = cities_with_data
        house_type_comparison['summary']['total_house_types'] = len(all_house_types)
        
        if cities_with_data == 0:
            house_type_comparison['available'] = False
            house_type_comparison['message'] = '所有城市均无户型数据'
            return house_type_comparison
        
        house_type_comparison['available'] = True
        
        # 找出最常见的户型（在各城市中出现频率最高）
        type_frequency = {}
        for city_data in house_type_comparison['cities_data']:
            main_type = city_data['main_type']
            type_frequency[main_type] = type_frequency.get(main_type, 0) + 1
        
        common_types = sorted(type_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        house_type_comparison['summary']['common_types'] = [
            {'type': t, 'cities_count': count} for t, count in common_types
        ]
        
        # 分析各户型的价格领先城市
        common_house_types = ['2室1厅', '2室2厅', '3室1厅', '3室2厅']
        for house_type in common_house_types:
            city_prices = []
            for city_data in house_type_comparison['cities_data']:
                for dist_item in city_data['distribution']:
                    if dist_item['house_type'] == house_type:
                        city_prices.append({
                            'city': city_data['city'],
                            'avg_price': dist_item['avg_price'],
                            'avg_unit_price': dist_item['avg_unit_price']
                        })
                        break
            
            if city_prices:
                highest = max(city_prices, key=lambda x: x['avg_unit_price'])
                lowest = min(city_prices, key=lambda x: x['avg_unit_price'])
                house_type_comparison['summary']['price_leaders'][house_type] = {
                    'highest': highest,
                    'lowest': lowest,
                    'price_gap': highest['avg_unit_price'] - lowest['avg_unit_price'],
                    'cities_count': len(city_prices)
                }
        
        # 按室数对比分析
        room_comparison = {}
        for city_data in house_type_comparison['cities_data']:
            for room_stat in city_data['room_statistics']:
                room_label = room_stat['label']
                if room_label not in room_comparison:
                    room_comparison[room_label] = []
                
                room_comparison[room_label].append({
                    'city': city_data['city'],
                    'count': room_stat['count'],
                    'percentage': room_stat['percentage'],
                    'avg_price': room_stat['avg_price'],
                    'avg_unit_price': room_stat['avg_unit_price']
                })
        
        # 计算每种室数的全国平均价格
        room_national_avg = {}
        for room_label, cities in room_comparison.items():
            avg_price = sum(c['avg_price'] for c in cities) / len(cities)
            avg_unit_price = sum(c['avg_unit_price'] for c in cities) / len(cities)
            room_national_avg[room_label] = {
                'avg_price': round(float(avg_price), 2),
                'avg_unit_price': round(float(avg_unit_price), 2),
                'cities_count': len(cities)
            }
        
        house_type_comparison['room_comparison'] = room_comparison
        house_type_comparison['room_national_avg'] = room_national_avg
        
        return house_type_comparison

