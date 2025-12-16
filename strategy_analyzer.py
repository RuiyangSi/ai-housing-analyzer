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
        
        prompt = f"""作为资深房产顾问，请基于以下真实数据为购房者制定个性化策略（280-320字）：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 【购房者画像】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 目标城市：{city_name}
• 购房预算：{user_profile['budget']:.0f}万元
• 核心诉求：{purpose_map.get(user_profile['purpose'], user_profile['purpose'])}
• 家庭结构：{user_profile['family_size']}人家庭，{'有学龄儿童' if user_profile.get('has_kid') else '无小孩'}
• 时间计划：{urgency_map.get(user_profile['urgency'], user_profile['urgency'])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 【数据驱动的市场分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 购买力评估：
   • 市场定位：{affordability['market_position']}（超过{affordability.get('budget_percentile', 50):.0f}%的在售房源）
   • 可买面积：约{affordability['affordable_area']:.0f}㎡（按市场均价{affordability['avg_unit_price']:,.0f}元/㎡计算）
   • 匹配房源：预算±20%范围内有{affordability.get('suitable_properties_count', 0)}套房源可选
   • 房源占比：{affordability['availability_rate']:.1f}%（{'选择余地充足' if affordability['availability_rate'] > 10 else '房源较少，需扩大范围' if affordability['availability_rate'] > 5 else '房源稀缺，建议调整预算'}）

⏰ 市场时机：
   • 综合评分：{timing['timing_score']:.0f}/100分 → {timing['timing_level']}
   • 价格走势：近期{'上涨' if timing['price_change'] > 0 else '下跌'}{abs(timing['price_change']):.1f}%（{'需尽快锁定' if timing['price_change'] > 3 else '可从容选择' if timing['price_change'] < -3 else '市场平稳'}）
   • 成交热度：{'量价齐升，竞争激烈' if timing['volume_change'] > 10 and timing['price_change'] > 0 else '量价齐跌，议价空间大' if timing['volume_change'] < -10 and timing['price_change'] < 0 else '市场平衡'}
   • 波动性：{timing['volatility']:.1f}%（{'价格稳定' if timing['volatility'] < 15 else '波动较大，需谨慎'}）

🗺️ 推荐区域（按性价比排序）：
   1️⃣ {recommendations[0]['district']}
      • 单价：{recommendations[0]['avg_unit_price']:,.0f}元/㎡（中位价{recommendations[0]['median_price']:.2f}万）
      • 可购面积：{recommendations[0]['affordable_area']:.0f}㎡
      • 成交活跃度：{recommendations[0]['transaction_volume']}套/年
      • 趋势：{recommendations[0]['trend']}{abs(recommendations[0]['trend_percent']):.1f}%
      {'⭐ 匹配期望区域' if recommendations[0].get('is_preferred') else ''}
   
   2️⃣ {recommendations[1]['district'] if len(recommendations) > 1 else '暂无其他推荐'}
      {f"• 单价：{recommendations[1]['avg_unit_price']:,.0f}元/㎡，可买{recommendations[1]['affordable_area']:.0f}㎡" if len(recommendations) > 1 else ''}
   
   3️⃣ {recommendations[2]['district'] if len(recommendations) > 2 else '（建议重点关注前2个区域）'}
      {f"• 单价：{recommendations[2]['avg_unit_price']:,.0f}元/㎡，可买{recommendations[2]['affordable_area']:.0f}㎡" if len(recommendations) > 2 else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 【请提供专业建议】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于上述真实数据，请从以下4个维度提供建议：

1️⃣ 综合购房策略（100字）：
   - 结合预算定位、市场时机、购房目的，给出是否适合现在入手的判断
   - 如果目的是投资，重点分析增值潜力；如果是自住，关注居住舒适度；如果是学区，突出教育配套
   - 引用具体数据支持你的判断

2️⃣ 户型面积建议（80字）：
   - 根据家庭人数推荐合理户型（{user_profile['family_size']}人家庭建议几室几厅）
   - 结合可买面积{affordability['affordable_area']:.0f}㎡，说明是宽裕还是紧张
   - 如果有小孩，考虑预留成长空间

3️⃣ 区域选择指导（80字）：
   - 在推荐的3个区域中，哪个最适合该用户？为什么？
   - 对比价格、趋势、成交量等数据
   - 如果用户时间{'紧迫' if user_profile['urgency'] == 'urgent' else '充裕'}，建议优先看哪个区域

4️⃣ 风险提示（60字）：
   - 基于市场波动性{timing['volatility']:.1f}%和价格趋势，有什么风险
   - 预算{affordability['availability_rate']:.1f}%房源占比意味着什么风险
   - 需要提醒的关键注意事项

要求：
✅ 必须引用数据中的具体数字支撑观点
✅ 语言专业但易懂，避免空洞的套话
✅ 给出可执行的具体建议，不只是原则性意见
✅ 总字数280-320字，分4段输出，每段有小标题"""

        # 调用AI
        result = self.ai_assistant.chat(prompt, None, temperature=0.7, max_tokens=500)
        
        if result.get('success'):
            return result['message']
        else:
            return "AI分析暂时不可用，请参考上述数据分析结果。"

