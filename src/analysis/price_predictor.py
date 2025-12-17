"""
AI 房价预测模块
基于历史数据和 AI 语言模型进行房价趋势预测
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import re


class AIResponseExtractor:
    """从 AI 响应中提取结构化预测数据"""
    
    @staticmethod
    def extract_predictions(ai_response: str) -> Dict[str, Any]:
        """
        从 AI 文本响应中提取预测数据
        
        参数:
            ai_response: AI 的完整文本响应
            
        返回:
            提取的结构化数据
        """
        result = {
            'success': False,
            'predictions': [],
            'trend': 'stable',
            'confidence': 60,
            'key_factors': [],
            'recommendation': '',
            'risk_level': 'medium'
        }
        
        try:
            # 尝试提取 JSON 块
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', ai_response)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                
                # 提取预测数据
                if 'predictions' in parsed:
                    result['predictions'] = parsed['predictions']
                    result['success'] = True
                    
                if 'trend' in parsed:
                    result['trend'] = parsed['trend']
                if 'confidence' in parsed:
                    result['confidence'] = parsed['confidence']
                if 'key_factors' in parsed:
                    result['key_factors'] = parsed['key_factors']
                if 'recommendation' in parsed:
                    result['recommendation'] = parsed['recommendation']
                if 'risk_level' in parsed:
                    result['risk_level'] = parsed['risk_level']
                    
                return result
            
            # 如果没有 JSON，尝试从文本中提取数字
            result['predictions'] = AIResponseExtractor._extract_from_text(ai_response)
            if result['predictions']:
                result['success'] = True
                
            # 提取趋势判断
            if '上涨' in ai_response or '增长' in ai_response or '走高' in ai_response:
                result['trend'] = 'up'
            elif '下跌' in ai_response or '下降' in ai_response or '走低' in ai_response:
                result['trend'] = 'down'
            else:
                result['trend'] = 'stable'
                
            # 提取风险等级
            if '高风险' in ai_response or '风险较大' in ai_response:
                result['risk_level'] = 'high'
            elif '低风险' in ai_response or '风险较小' in ai_response:
                result['risk_level'] = 'low'
                
        except Exception as e:
            print(f"提取预测数据失败: {e}")
            
        return result
    
    @staticmethod
    def _extract_from_text(text: str) -> List[Dict]:
        """从纯文本中提取预测数据"""
        predictions = []
        
        # 匹配类似 "2025年7月: 405万" 或 "7月份：405万元" 的模式
        patterns = [
            r'(\d{4})年(\d{1,2})月[：:]\s*(\d+(?:\.\d+)?)\s*万',
            r'(\d{1,2})月[份]?[：:]\s*(\d+(?:\.\d+)?)\s*万',
            r'预计[到]?(\d{4})年(\d{1,2})月.*?(\d+(?:\.\d+)?)\s*万'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    year, month, price = match
                    predictions.append({
                        'month': f'{year}-{int(month):02d}',
                        'price': float(price)
                    })
                elif len(match) == 2:
                    month, price = match
                    # 假设是当前年或下一年
                    year = datetime.now().year
                    if int(month) < datetime.now().month:
                        year += 1
                    predictions.append({
                        'month': f'{year}-{int(month):02d}',
                        'price': float(price)
                    })
        
        # 去重并排序
        seen = set()
        unique_predictions = []
        for p in predictions:
            if p['month'] not in seen:
                seen.add(p['month'])
                unique_predictions.append(p)
        
        return sorted(unique_predictions, key=lambda x: x['month'])


class PricePredictor:
    """AI 房价预测器"""
    
    def __init__(self, df: pd.DataFrame, city_name: str):
        """
        初始化预测器
        
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
        self.df['年月'] = self.df['成交日期'].dt.to_period('M').astype(str)
        
    def get_historical_trend(self) -> Dict[str, Any]:
        """获取历史趋势数据"""
        monthly = self.df.groupby('年月').agg({
            '成交价（万元）': ['mean', 'median', 'count', 'std'],
            '成交单价（元）': ['mean', 'median'],
            '面积（m²）': 'mean'
        }).reset_index()
        
        monthly.columns = ['年月', '均价', '中位价', '成交量', '价格标准差', 
                          '单价均价', '单价中位', '平均面积']
        
        # 计算变化率
        monthly['价格环比'] = monthly['均价'].pct_change() * 100
        monthly['成交量环比'] = monthly['成交量'].pct_change() * 100
        
        # 填充 NaN
        monthly = monthly.fillna(0)
        
        return {
            'data': monthly.to_dict('records'),
            'summary': {
                'total_months': len(monthly),
                'avg_price': round(float(monthly['均价'].mean()), 2),
                'avg_volume': round(float(monthly['成交量'].mean()), 0),
                'price_volatility': round(float(monthly['均价'].std() / monthly['均价'].mean() * 100), 2),
                'latest_price': round(float(monthly['均价'].iloc[-1]), 2),
                'latest_month': monthly['年月'].iloc[-1]
            }
        }
    
    def get_district_trends(self) -> Dict[str, Any]:
        """获取各区域趋势数据"""
        if '区域' not in self.df.columns:
            return {'districts': []}
        
        # 按区域和年月聚合
        district_monthly = self.df.groupby(['区域', '年月']).agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean'
        }).reset_index()
        
        # 获取各区域最新数据和历史对比
        districts = []
        for district in self.df['区域'].unique():
            d_data = district_monthly[district_monthly['区域'] == district].sort_values('年月')
            if len(d_data) >= 2:
                latest = d_data.iloc[-1]
                first = d_data.iloc[0]
                prev = d_data.iloc[-2]
                
                total_change = ((latest['成交价（万元）'] - first['成交价（万元）']) / first['成交价（万元）']) * 100
                mom_change = ((latest['成交价（万元）'] - prev['成交价（万元）']) / prev['成交价（万元）']) * 100
                
                districts.append({
                    'name': district,
                    'latest_price': round(float(latest['成交价（万元）']), 2),
                    'latest_unit_price': round(float(latest['成交单价（元）']), 0),
                    'total_change': round(float(total_change), 2),
                    'mom_change': round(float(mom_change), 2),
                    'trend': 'up' if total_change > 0 else 'down' if total_change < 0 else 'stable'
                })
        
        # 按最新价格排序
        districts.sort(key=lambda x: x['latest_price'], reverse=True)
        
        return {'districts': districts[:15]}  # 返回前15个区域
    
    def get_seasonality_pattern(self) -> Dict[str, Any]:
        """分析季节性模式"""
        seasonal = self.df.groupby('月份').agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean'
        }).reset_index()
        
        avg_price = seasonal['成交价（万元）'].mean()
        seasonal['季节性指数'] = (seasonal['成交价（万元）'] / avg_price - 1) * 100
        
        # 找出最佳/最差月份
        best_month = seasonal.loc[seasonal['成交价（万元）'].idxmin(), '月份']
        worst_month = seasonal.loc[seasonal['成交价（万元）'].idxmax(), '月份']
        
        return {
            'monthly_pattern': seasonal.to_dict('records'),
            'best_buy_month': int(best_month),
            'peak_price_month': int(worst_month),
            'seasonality_strength': round(float(seasonal['季节性指数'].std()), 2)
        }
    
    def calculate_prediction_factors(self) -> Dict[str, Any]:
        """计算预测因子"""
        monthly = self.df.groupby('年月').agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean'
        }).reset_index()
        
        # 近期趋势（最近6个月）
        recent = monthly.tail(6)
        if len(recent) >= 2:
            recent_trend = ((recent['成交价（万元）'].iloc[-1] - recent['成交价（万元）'].iloc[0]) 
                           / recent['成交价（万元）'].iloc[0]) * 100
        else:
            recent_trend = 0
        
        # 长期趋势（整体）
        if len(monthly) >= 2:
            long_trend = ((monthly['成交价（万元）'].iloc[-1] - monthly['成交价（万元）'].iloc[0]) 
                         / monthly['成交价（万元）'].iloc[0]) * 100
        else:
            long_trend = 0
        
        # 波动性
        volatility = monthly['成交价（万元）'].std() / monthly['成交价（万元）'].mean() * 100
        
        # 成交量趋势（使用平均值比较，避免极端值）
        volume_by_month = self.df.groupby('年月').size()
        if len(volume_by_month) >= 6:
            recent_volume = volume_by_month.tail(6)
            # 使用前3个月平均 vs 后3个月平均，更稳定
            early_avg = recent_volume.iloc[:3].mean() if len(recent_volume) >= 3 else recent_volume.iloc[0]
            late_avg = recent_volume.iloc[-3:].mean() if len(recent_volume) >= 3 else recent_volume.iloc[-1]
            if early_avg > 0:
                volume_trend = ((late_avg - early_avg) / early_avg) * 100
            else:
                volume_trend = 0
            # 限制在合理范围内
            volume_trend = max(min(volume_trend, 200), -80)
        else:
            volume_trend = 0
        
        # 市场热度指标
        market_heat = 50  # 基准值
        if recent_trend > 5:
            market_heat += 20
        elif recent_trend > 0:
            market_heat += 10
        elif recent_trend < -5:
            market_heat -= 20
        elif recent_trend < 0:
            market_heat -= 10
            
        if volume_trend > 10:
            market_heat += 15
        elif volume_trend < -10:
            market_heat -= 15
            
        market_heat = max(0, min(100, market_heat))
        
        return {
            'recent_trend': round(float(recent_trend), 2),
            'long_trend': round(float(long_trend), 2),
            'volatility': round(float(volatility), 2),
            'volume_trend': round(float(volume_trend), 2),
            'market_heat': int(market_heat),
            'stability_score': max(0, 100 - int(volatility * 2))
        }
    
    def generate_simple_prediction(self, months: int = 6) -> Dict[str, Any]:
        """
        生成简单的统计预测（作为 AI 预测的参考基准）
        
        参数:
            months: 预测月数
        """
        monthly = self.df.groupby('年月').agg({
            '成交价（万元）': 'mean'
        }).reset_index()
        monthly['年月'] = monthly['年月'].astype(str)
        
        # 使用简单移动平均和趋势
        recent_prices = monthly['成交价（万元）'].tail(6).values
        
        # 计算简单趋势
        if len(recent_prices) >= 2:
            avg_change = np.mean(np.diff(recent_prices))
            trend_pct = avg_change / recent_prices[-1] * 100
        else:
            avg_change = 0
            trend_pct = 0
        
        # 生成预测
        last_price = recent_prices[-1]
        last_month = monthly['年月'].iloc[-1]
        
        predictions = []
        current_price = last_price
        
        # 解析最后月份
        year, month = map(int, last_month.split('-'))
        
        for i in range(1, months + 1):
            # 计算下一个月
            month += 1
            if month > 12:
                month = 1
                year += 1
            
            # 预测价格（加入一些随机波动模拟不确定性）
            change = avg_change * (1 + np.random.uniform(-0.3, 0.3))
            current_price = max(current_price + change, current_price * 0.9)  # 防止大幅下跌
            
            predictions.append({
                'month': f'{year}-{month:02d}',
                'predicted_price': round(float(current_price), 2),
                'confidence': max(40, 90 - i * 8),  # 置信度随时间递减
                'range_low': round(float(current_price * 0.95), 2),
                'range_high': round(float(current_price * 1.05), 2)
            })
        
        return {
            'base_price': round(float(last_price), 2),
            'base_month': last_month,
            'trend_direction': 'up' if trend_pct > 1 else 'down' if trend_pct < -1 else 'stable',
            'trend_pct': round(float(trend_pct), 2),
            'predictions': predictions
        }
    
    def get_prediction_context(self, target_district: Optional[str] = None) -> Dict[str, Any]:
        """
        获取完整的预测上下文（供 AI 使用）
        
        参数:
            target_district: 目标区域（可选）
        """
        historical = self.get_historical_trend()
        districts = self.get_district_trends()
        seasonality = self.get_seasonality_pattern()
        factors = self.calculate_prediction_factors()
        simple_pred = self.generate_simple_prediction(12)
        
        context = {
            'city': self.city_name,
            'historical_summary': historical['summary'],
            'recent_trend': {
                'months': historical['data'][-6:] if len(historical['data']) >= 6 else historical['data'],
                'trend_direction': simple_pred['trend_direction'],
                'trend_pct': simple_pred['trend_pct']
            },
            'districts_summary': {
                'total_districts': len(districts['districts']),
                'top_3': districts['districts'][:3] if districts['districts'] else [],
                'bottom_3': districts['districts'][-3:] if len(districts['districts']) >= 3 else []
            },
            'seasonality': {
                'best_buy_month': seasonality['best_buy_month'],
                'peak_price_month': seasonality['peak_price_month'],
                'strength': seasonality['seasonality_strength']
            },
            'market_factors': factors,
            'statistical_forecast': simple_pred
        }
        
        # 如果指定了区域
        if target_district and '区域' in self.df.columns:
            district_data = self.df[self.df['区域'] == target_district]
            if len(district_data) > 0:
                d_monthly = district_data.groupby('年月').agg({
                    '成交价（万元）': 'mean',
                    '成交单价（元）': 'mean'
                }).reset_index()
                d_monthly['年月'] = d_monthly['年月'].astype(str)
                
                context['target_district'] = {
                    'name': target_district,
                    'avg_price': round(float(district_data['成交价（万元）'].mean()), 2),
                    'transaction_count': len(district_data),
                    'recent_months': d_monthly.tail(6).to_dict('records')
                }
        
        return context
    
    def build_ai_prompt(self, prediction_months: int = 6, 
                        target_district: Optional[str] = None,
                        user_role: str = 'investment_advisor') -> str:
        """
        构建 AI 预测提示词
        
        参数:
            prediction_months: 预测月数
            target_district: 目标区域
            user_role: 用户角色
        """
        context = self.get_prediction_context(target_district)
        
        # 根据角色定制语言风格
        if user_role == 'first_time_buyer':
            style_guide = """
请用通俗易懂的语言，就像跟朋友聊天一样。
- 不要使用专业术语，或者用括号解释
- 重点告诉我：现在适不适合买？要等吗？
- 给出实际可操作的建议
- 提醒可能的风险"""
        elif user_role == 'upgrader':
            style_guide = """
请从换房角度分析：
- 现在卖旧买新是否划算？
- 置换时机如何把握？
- 区域选择建议
- 预算规划建议"""
        else:  # investment_advisor
            style_guide = """
请提供专业投资分析：
- 使用专业指标和术语
- 分析投资回报率和风险
- 给出量化的预测数据
- 提供多情景分析"""
        
        prompt = f"""请基于以下{self.city_name}房价数据，预测未来{prediction_months}个月的房价走势。

## 历史数据摘要
- 平均成交价：{context['historical_summary']['avg_price']}万元
- 最新成交价：{context['historical_summary']['latest_price']}万元（{context['historical_summary']['latest_month']}）
- 月均成交量：{context['historical_summary']['avg_volume']}套
- 价格波动率：{context['historical_summary']['price_volatility']}%

## 近期趋势（最近6个月）
- 趋势方向：{'上涨' if context['recent_trend']['trend_direction'] == 'up' else '下跌' if context['recent_trend']['trend_direction'] == 'down' else '平稳'}
- 变化幅度：{context['recent_trend']['trend_pct']}%
- 月度数据：
"""
        
        for m in context['recent_trend']['months']:
            prompt += f"  {m['年月']}: {m.get('均价', m.get('成交价（万元）', 'N/A'))}万元\n"
        
        prompt += f"""
## 市场因素分析
- 近期趋势得分：{context['market_factors']['recent_trend']}%
- 长期趋势得分：{context['market_factors']['long_trend']}%
- 成交量趋势：{context['market_factors']['volume_trend']}%
- 市场热度指数：{context['market_factors']['market_heat']}/100
- 价格稳定性：{context['market_factors']['stability_score']}/100

## 季节性特征
- 最佳购房月份：{context['seasonality']['best_buy_month']}月
- 价格高峰月份：{context['seasonality']['peak_price_month']}月

## 区域分析
热门区域前3：
"""
        for d in context['districts_summary']['top_3']:
            prompt += f"- {d['name']}: {d['latest_price']}万元 ({'+' if d['total_change'] > 0 else ''}{d['total_change']}%)\n"
        
        if target_district and 'target_district' in context:
            td = context['target_district']
            prompt += f"""
## 目标区域：{td['name']}
- 平均价格：{td['avg_price']}万元
- 成交量：{td['transaction_count']}套
"""

        prompt += f"""
## 统计模型参考预测
- 基准价格：{context['statistical_forecast']['base_price']}万元
- 预测趋势：{'上涨' if context['statistical_forecast']['trend_direction'] == 'up' else '下跌' if context['statistical_forecast']['trend_direction'] == 'down' else '平稳'}
- 月均变化：{context['statistical_forecast']['trend_pct']}%

---

{style_guide}

## 重要：请严格按以下格式输出

首先，输出你的预测数据（JSON格式，用于图表绑定）：

```json
{{
  "predictions": [
    {{"month": "YYYY-MM", "price": 数字, "low": 数字, "high": 数字}},
    ... （共{prediction_months}个月）
  ],
  "trend": "up/down/stable",
  "confidence": 0-100的数字,
  "risk_level": "low/medium/high",
  "key_factors": ["因素1", "因素2", "因素3"],
  "recommendation": "一句话购房建议"
}}
```

然后，用自然语言详细分析：

1. **整体预测**：未来{prediction_months}个月的价格走势预判
2. **价格区间**：预计价格范围（最低-最高）
3. **关键因素**：影响价格的主要因素
4. **时机建议**：何时是较好的买入/卖出时机
5. **风险提示**：需要注意的风险因素

请基于数据给出合理预测，month格式必须是YYYY-MM（如2025-07），price/low/high单位是万元。"""

        return prompt
    
    def build_ai_prompt_for_extraction(self, prediction_months: int = 6,
                                       target_district: Optional[str] = None) -> str:
        """
        构建专门用于数据提取的 AI 提示词（纯 JSON 输出）
        """
        context = self.get_prediction_context(target_district)
        base_price = context['statistical_forecast']['base_price']
        base_month = context['statistical_forecast']['base_month']
        trend_pct = context['statistical_forecast']['trend_pct']
        
        # 计算预测月份列表
        year, month = map(int, base_month.split('-'))
        future_months = []
        for i in range(1, prediction_months + 1):
            month += 1
            if month > 12:
                month = 1
                year += 1
            future_months.append(f"{year}-{month:02d}")
        
        prompt = f"""你是一位房地产数据分析专家。基于以下{self.city_name}的房价数据，预测未来{prediction_months}个月的价格。

## 关键数据
- 当前均价：{base_price}万元（{base_month}）
- 近期趋势：月均变化 {trend_pct}%
- 市场热度：{context['market_factors']['market_heat']}/100
- 价格波动率：{context['historical_summary']['price_volatility']}%

## 最近6个月价格
"""
        for m in context['recent_trend']['months']:
            price = m.get('均价', m.get('成交价（万元）', 0))
            prompt += f"- {m['年月']}: {price:.1f}万元\n"

        prompt += f"""
## 任务
请预测以下月份的房价：{', '.join(future_months)}

## 输出要求
只输出 JSON，不要其他任何文字：

```json
{{
  "predictions": [
    {{"month": "{future_months[0]}", "price": 预测价格, "low": 最低预估, "high": 最高预估}},
    {{"month": "{future_months[1]}", "price": 预测价格, "low": 最低预估, "high": 最高预估}},
    ... 依此类推，共{prediction_months}条
  ],
  "trend": "up或down或stable",
  "confidence": 置信度0-100,
  "risk_level": "low或medium或high",
  "summary": "一句话总结预测"
}}
```

注意：
1. 价格单位是万元，保留1位小数
2. low 约等于 price×0.93，high 约等于 price×1.07
3. 基于趋势合理推断，不要简单线性外推
4. 只输出JSON，不要其他解释"""

        return prompt

