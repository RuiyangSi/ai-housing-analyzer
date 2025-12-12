"""
购房策略分析器
基于用户画像和历史数据，生成个性化购房策略
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from ai_assistant import AIAssistant


class StrategyAnalyzer:
    """购房策略分析器"""
    
    def __init__(self, ai_assistant: AIAssistant):
        """
        初始化策略分析器
        
        参数:
            ai_assistant: AI助手实例
        """
        self.ai_assistant = ai_assistant
    
    def analyze_affordability(self, budget: float, city_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析购买力
        
        参数:
            budget: 预算（万元）
            city_data: 城市数据DataFrame
        
        返回:
            购买力分析结果
        """
        # 计算在预算内可以买到的面积
        avg_unit_price = city_data['成交单价（元）'].mean()
        affordable_area = (budget * 10000) / avg_unit_price
        
        # 找出预算范围内的房源占比
        budget_range = city_data[
            (city_data['成交价（万元）'] >= budget * 0.8) & 
            (city_data['成交价（万元）'] <= budget * 1.2)
        ]
        
        availability_rate = len(budget_range) / len(city_data) * 100
        
        # 分析预算在市场中的位置（分位数）
        budget_percentile = (city_data['成交价（万元）'] <= budget).sum() / len(city_data) * 100
        
        return {
            'affordable_area': round(float(affordable_area), 1),
            'avg_unit_price': round(float(avg_unit_price), 2),
            'availability_rate': round(float(availability_rate), 2),
            'budget_percentile': round(float(budget_percentile), 1),
            'market_position': self._get_budget_level(budget_percentile),
            'suitable_properties_count': int(len(budget_range))
        }
    
    def _get_budget_level(self, percentile: float) -> str:
        """根据预算分位数判断购买力水平"""
        if percentile < 25:
            return '经济型（入门级）'
        elif percentile < 50:
            return '标准型（中低端）'
        elif percentile < 75:
            return '舒适型（中高端）'
        else:
            return '高端型（高端市场）'
    
    def recommend_districts(self, budget: float, city_data: pd.DataFrame, 
                          preferred_district: Optional[str] = None, 
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """
        推荐区域
        
        参数:
            budget: 预算（万元）
            city_data: 城市数据
            preferred_district: 期望区域（可选）
            top_n: 返回前N个推荐
        
        返回:
            推荐区域列表
        """
        # 按区域统计
        district_stats = city_data.groupby('区域').agg({
            '成交价（万元）': ['mean', 'median', 'count'],
            '成交单价（元）': 'mean',
            '面积（m²）': 'mean'
        }).reset_index()
        
        district_stats.columns = ['区域', '平均价格', '中位价格', '成交量', '平均单价', '平均面积']
        
        # 计算性价比评分（预算可买面积）
        district_stats['可买面积'] = (budget * 10000) / district_stats['平均单价']
        
        # 筛选有足够成交量的区域（至少100套）
        district_stats = district_stats[district_stats['成交量'] >= 100]
        
        # 如果指定了期望区域，优先推荐
        if preferred_district:
            district_stats['优先级'] = district_stats['区域'].apply(
                lambda x: 1 if preferred_district in x else 0
            )
            district_stats = district_stats.sort_values(['优先级', '可买面积'], ascending=[False, False])
        else:
            # 按可买面积排序
            district_stats = district_stats.sort_values('可买面积', ascending=False)
        
        # 转换为推荐列表
        recommendations = []
        for _, row in district_stats.head(top_n).iterrows():
            # 计算该区域的价格趋势（简化版）
            district_data = city_data[city_data['区域'] == row['区域']]
            district_data = district_data.sort_values('成交日期')
            
            if len(district_data) > 10:
                recent_price = district_data.tail(int(len(district_data) * 0.3))['成交价（万元）'].mean()
                earlier_price = district_data.head(int(len(district_data) * 0.3))['成交价（万元）'].mean()
                trend_pct = ((recent_price - earlier_price) / earlier_price) * 100
            else:
                trend_pct = 0
            
            recommendations.append({
                'district': row['区域'],
                'avg_price': round(float(row['平均价格']), 2),
                'median_price': round(float(row['中位价格']), 2),
                'avg_unit_price': round(float(row['平均单价']), 2),
                'affordable_area': round(float(row['可买面积']), 1),
                'transaction_volume': int(row['成交量']),
                'trend': '上涨' if trend_pct > 0 else '下跌' if trend_pct < 0 else '持平',
                'trend_percent': round(float(trend_pct), 1),
                'is_preferred': preferred_district and preferred_district in row['区域']
            })
        
        return recommendations
    
    def calculate_loan_plan(self, budget: float, down_payment_ratio: float = 0.3, 
                           loan_years: int = 30, annual_rate: float = 0.042) -> Dict[str, Any]:
        """
        计算贷款方案
        
        参数:
            budget: 总价（万元）
            down_payment_ratio: 首付比例
            loan_years: 贷款年限
            annual_rate: 年利率
        
        返回:
            贷款方案详情
        """
        total_price = budget * 10000  # 转换为元
        down_payment = total_price * down_payment_ratio
        loan_amount = total_price - down_payment
        
        # 计算月供（等额本息）
        monthly_rate = annual_rate / 12
        total_months = loan_years * 12
        
        if monthly_rate > 0:
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** total_months) / \
                            ((1 + monthly_rate) ** total_months - 1)
        else:
            monthly_payment = loan_amount / total_months
        
        total_interest = monthly_payment * total_months - loan_amount
        total_repayment = loan_amount + total_interest
        
        return {
            'total_price': round(float(total_price), 2),
            'down_payment': round(float(down_payment), 2),
            'down_payment_ratio': down_payment_ratio * 100,
            'loan_amount': round(float(loan_amount), 2),
            'loan_years': loan_years,
            'annual_rate': annual_rate * 100,
            'monthly_payment': round(float(monthly_payment), 2),
            'total_interest': round(float(total_interest), 2),
            'total_repayment': round(float(total_repayment), 2)
        }
    
    def assess_market_timing(self, city_data: pd.DataFrame) -> Dict[str, Any]:
        """
        评估市场时机
        
        参数:
            city_data: 城市数据
        
        返回:
            市场时机评估
        """
        # 按日期排序
        city_data = city_data.sort_values('成交日期')
        
        # 计算最近3个月vs之前3个月的价格变化
        recent_3m = city_data.tail(int(len(city_data) * 0.25))
        previous_3m = city_data.head(int(len(city_data) * 0.25))
        
        recent_avg = recent_3m['成交价（万元）'].mean()
        previous_avg = previous_3m['成交价（万元）'].mean()
        
        price_change = ((recent_avg - previous_avg) / previous_avg) * 100
        
        # 计算成交量变化
        recent_volume = len(recent_3m)
        previous_volume = len(previous_3m)
        volume_change = ((recent_volume - previous_volume) / max(previous_volume, 1)) * 100
        
        # 计算价格波动性
        price_std = city_data['成交价（万元）'].std()
        price_mean = city_data['成交价（万元）'].mean()
        volatility = (price_std / price_mean) * 100
        
        # 综合评分
        timing_score = 50  # 基准分
        
        # 价格趋势影响（-20到+20）
        if price_change < -5:
            timing_score += 20  # 价格下跌，买入时机好
        elif price_change > 5:
            timing_score -= 20  # 价格上涨，买入时机一般
        else:
            timing_score += 10  # 价格平稳，买入时机较好
        
        # 成交量影响（-10到+10）
        if volume_change < -10:
            timing_score += 10  # 成交量下降，议价空间大
        elif volume_change > 10:
            timing_score -= 10  # 成交量上升，竞争激烈
        
        # 波动性影响（-10到+10）
        if volatility < 10:
            timing_score += 10  # 市场稳定
        elif volatility > 20:
            timing_score -= 10  # 市场波动大
        
        return {
            'timing_score': round(float(timing_score), 1),
            'timing_level': self._get_timing_level(timing_score),
            'price_change': round(float(price_change), 2),
            'volume_change': round(float(volume_change), 2),
            'volatility': round(float(volatility), 2),
            'recommendation': self._get_timing_recommendation(timing_score)
        }
    
    def _get_timing_level(self, score: float) -> str:
        """根据时机评分判断入市时机"""
        if score >= 70:
            return '极佳时机'
        elif score >= 60:
            return '较好时机'
        elif score >= 50:
            return '适中时机'
        elif score >= 40:
            return '需谨慎'
        else:
            return '建议观望'
    
    def _get_timing_recommendation(self, score: float) -> str:
        """根据时机评分给出建议"""
        if score >= 70:
            return '市场处于有利买入窗口，建议积极看房，遇到合适房源可果断出手'
        elif score >= 60:
            return '当前市场较为稳定，可以开始看房，但不必过于着急'
        elif score >= 50:
            return '市场处于平衡状态，可以边看边等，选择性价比高的房源'
        elif score >= 40:
            return '市场存在一定风险，建议多观察，谨慎决策'
        else:
            return '市场风险较高，建议暂缓购房，等待更好时机'
    
    def generate_action_plan(self, user_profile: Dict[str, Any], 
                            recommendations: List[Dict[str, Any]],
                            timing: Dict[str, Any]) -> List[str]:
        """
        生成行动计划
        
        参数:
            user_profile: 用户画像
            recommendations: 推荐区域
            timing: 市场时机
        
        返回:
            行动步骤列表
        """
        plan = []
        
        # 第一步：明确目标
        top_district = recommendations[0]['district'] if recommendations else '目标区域'
        plan.append(f"📍 第一步：明确目标区域为 {top_district}，预算范围 {user_profile['budget']*0.9:.0f}-{user_profile['budget']*1.1:.0f}万")
        
        # 第二步：线上筛选
        plan.append(f"💻 第二步：在贝壳/链家APP搜索关键词：{top_district}、{user_profile['budget']:.0f}万左右")
        
        # 第三步：看房计划
        urgency = user_profile.get('urgency', 'moderate')
        if urgency == 'urgent':
            plan.append("🏠 第三步：本周内安排看房，至少看3-5套进行对比")
        elif urgency == 'moderate':
            plan.append("🏠 第三步：未来2周内安排看房，建议看5-8套做充分比较")
        else:
            plan.append("🏠 第三步：1个月内持续看房，可以看10套以上，不着急出手")
        
        # 第四步：议价策略
        if timing['timing_score'] >= 60:
            plan.append("💰 第四步：当前市场适合买入，报价可比业主挂牌价低3-5万试探")
        else:
            plan.append("💰 第四步：当前可多观察，报价建议比业主挂牌价低5-8万，争取更大优惠")
        
        # 第五步：贷款准备
        plan.append("🏦 第五步：提前准备好征信报告、收入证明等贷款材料，缩短流程时间")
        
        # 第六步：注意事项
        if user_profile.get('has_kid'):
            plan.append("⚠️ 第六步：重点查看学区信息、周边儿童设施，确保满足教育需求")
        else:
            plan.append("⚠️ 第六步：重点关注交通便利性、生活配套，确保居住舒适度")
        
        return plan
    
    def generate_comprehensive_strategy(self, user_profile: Dict[str, Any], 
                                       city_data: pd.DataFrame,
                                       city_name: str) -> Dict[str, Any]:
        """
        生成综合购房策略
        
        参数:
            user_profile: 用户画像
            city_data: 城市数据
            city_name: 城市名称
        
        返回:
            完整的购房策略
        """
        budget = user_profile['budget']
        
        # 1. 购买力分析
        affordability = self.analyze_affordability(budget, city_data)
        
        # 2. 区域推荐
        recommendations = self.recommend_districts(
            budget, 
            city_data, 
            user_profile.get('preferred_district')
        )
        
        # 3. 贷款方案
        loan_plan = self.calculate_loan_plan(budget)
        
        # 4. 市场时机
        timing = self.assess_market_timing(city_data)
        
        # 5. 行动计划
        action_plan = self.generate_action_plan(user_profile, recommendations, timing)
        
        # 6. AI生成个性化建议
        ai_advice = self._generate_ai_advice(
            user_profile, 
            city_name,
            affordability, 
            recommendations, 
            timing
        )
        
        return {
            'city_name': city_name,
            'user_profile': user_profile,
            'affordability': affordability,
            'recommendations': recommendations,
            'loan_plan': loan_plan,
            'timing': timing,
            'action_plan': action_plan,
            'ai_advice': ai_advice
        }
    
    def _generate_ai_advice(self, user_profile: Dict[str, Any],
                           city_name: str,
                           affordability: Dict[str, Any],
                           recommendations: List[Dict[str, Any]],
                           timing: Dict[str, Any]) -> str:
        """
        使用AI生成个性化建议
        """
        # 构建prompt
        purpose_map = {
            'self_living': '自住',
            'investment': '投资',
            'education': '学区'
        }
        
        urgency_map = {
            'urgent': '急迫（3个月内）',
            'moderate': '适中（半年内）',
            'relaxed': '不急（1年内）'
        }
        
        prompt = f"""请为以下购房者提供专业的购房策略建议（250-300字）：

**购房者信息：**
- 城市：{city_name}
- 预算：{user_profile['budget']:.0f}万元
- 购房目的：{purpose_map.get(user_profile['purpose'], user_profile['purpose'])}
- 家庭人数：{user_profile['family_size']}人
- 有无小孩：{'有' if user_profile.get('has_kid') else '无'}
- 急迫程度：{urgency_map.get(user_profile['urgency'], user_profile['urgency'])}

**市场分析：**
- 购买力水平：{affordability['market_position']}
- 可购买面积：约{affordability['affordable_area']:.0f}㎡
- 预算范围内房源占比：{affordability['availability_rate']:.1f}%
- 市场时机评分：{timing['timing_score']:.0f}分（{timing['timing_level']}）
- 价格趋势：近期{timing['price_change']:+.1f}%

**推荐区域TOP3：**
1. {recommendations[0]['district']}（均价{recommendations[0]['avg_unit_price']:.0f}元/㎡，可买{recommendations[0]['affordable_area']:.0f}㎡）
2. {recommendations[1]['district'] if len(recommendations) > 1 else '暂无'}
3. {recommendations[2]['district'] if len(recommendations) > 2 else '暂无'}

请提供：
1. 综合购房建议（考虑预算、市场时机、购房目的）
2. 户型和面积选择建议（基于家庭人数和实际需求）
3. 风险提示和注意事项

要求：语言专业但易懂，250-300字。"""

        # 调用AI
        result = self.ai_assistant.chat(prompt, None, temperature=0.7, max_tokens=500)
        
        if result.get('success'):
            return result['message']
        else:
            return "AI分析暂时不可用，请参考上述数据分析结果。"

