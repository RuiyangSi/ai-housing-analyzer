"""
智能分析服务模块
使用 AI 大模型对房价数据进行深度分析和解读
"""

import requests
import json
from typing import Dict, Any, Optional


class IntelligentAnalyzer:
    """智能分析器 - 使用AI大模型分析房价数据"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "deepseek-ai/DeepSeek-V3"):
        """
        初始化智能分析器
        
        参数:
            api_url: API地址
            api_key: API密钥
            model: 使用的模型名称
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
    
    def _call_ai(self, prompt: str, max_tokens: int = 500) -> str:
        """
        调用AI模型（非流式）
        
        参数:
            prompt: 提示词
            max_tokens: 最大token数
        
        返回:
            AI生成的文本
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的房地产市场分析师，擅长解读房价数据，用简洁易懂的语言为用户提供有价值的洞察。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
            
            return "AI分析暂时不可用，请稍后再试。"
            
        except Exception as e:
            print(f"AI调用错误: {e}")
            return "AI分析暂时不可用，请稍后再试。"
    
    def _call_ai_stream(self, prompt: str, max_tokens: int = 500):
        """
        调用AI模型（流式）
        
        参数:
            prompt: 提示词
            max_tokens: 最大token数
        
        返回:
            生成器，逐步返回AI生成的文本片段
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的房地产市场分析师，擅长解读房价数据，用简洁易懂的语言为用户提供有价值的洞察。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": True  # 开启流式输出
            }
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]  # 去掉 "data: " 前缀
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                yield "AI分析暂时不可用，请稍后再试。"
                
        except Exception as e:
            print(f"AI流式调用错误: {e}")
            yield "AI分析暂时不可用，请稍后再试。"
    
    def analyze_national_overview(self, comparison_data: Dict[str, Any]) -> str:
        """
        生成全国对比的AI概览分析
        
        参数:
            comparison_data: 全国对比数据
        
        返回:
            AI生成的概览分析文本
        """
        overview = comparison_data.get('overview', {})
        price_comp = comparison_data.get('price_comparison', {})
        growth = comparison_data.get('growth_rates', {})
        investment = comparison_data.get('investment_scores', {})
        
        prompt = f"""请分析以下全国房价对比数据，用3-4段文字（每段80-100字）概括关键发现：

**市场概况：**
- 总成交量：{overview.get('total_transactions_all', 0)}套
- 价格最高城市：{overview.get('highest_price_city', '')}
- 价格最低城市：{overview.get('lowest_price_city', '')}
- 最活跃城市：{overview.get('most_active_city', '')}

**价格差距：**
- 价格差距：{price_comp.get('price_gap', 0)}万元
- 价格倍数：{price_comp.get('price_ratio', 0)}倍
- 差距评级：{price_comp.get('price_disparity_level', '')}

**增长趋势：**
- 整体趋势：{growth.get('overall_trend', '')}
- 最佳表现：{growth.get('best_performer', '')} ({growth.get('best_growth_rate', 0)}%)
- 最差表现：{growth.get('worst_performer', '')} ({growth.get('worst_growth_rate', 0)}%)

**投资价值：**
{json.dumps(investment.get('scores', [])[:3], ensure_ascii=False, indent=2)}

请提供：
1. 市场整体特征（城市分化程度、价格水平等）
2. 增长趋势分析（哪些城市表现好/差，原因可能是什么）
3. 投资建议（不同类型购房者应关注什么）

要求：语言简洁专业，每段80-100字，总共不超过350字。"""

        return self._call_ai(prompt, max_tokens=600)
    
    def analyze_city_overview(self, city_name: str, analysis_data: Dict[str, Any]) -> str:
        """
        生成单城市分析的AI概览
        
        参数:
            city_name: 城市名称
            analysis_data: 城市分析数据
        
        返回:
            AI生成的概览文本
        """
        basic = analysis_data.get('basic_statistics', {})
        investment = analysis_data.get('investment_index', {})
        volatility = analysis_data.get('volatility_analysis', {})
        
        prompt = f"""请分析{city_name}的房价数据（2023-2025年），用2-3段文字（每段60-80字）总结关键信息：

**基本统计：**
- 总成交量：{basic.get('total_transactions', 0)}套
- 平均价格：{basic.get('price', {}).get('mean', 0):.2f}万元
- 平均单价：{basic.get('unit_price', {}).get('mean', 0):.2f}元/m²
- 平均面积：{basic.get('area', {}).get('mean', 0):.2f}m²

**投资指数：**
- 综合评分：{investment.get('index_score', 0):.1f}分
- 投资等级：{investment.get('investment_level', '')}
- 市场稳定性：{volatility.get('stability_level', '')}

**市场特征：**
- 变异系数：{volatility.get('coefficient_of_variation', 0):.2f}%
- 价格范围：{volatility.get('price_range_percent', 0):.2f}%

请提供：
1. 市场定位（高端/中端/经济型，价格水平如何）
2. 投资价值评估（适合哪类购房者）
3. 风险提示（市场稳定性如何）

要求：简洁有力，每段60-80字，总共不超过250字。"""

        return self._call_ai(prompt, max_tokens=400)
    
    def analyze_chart(self, chart_type: str, chart_data: Dict[str, Any], context: str = "") -> str:
        """
        分析图表数据
        
        参数:
            chart_type: 图表类型（如"price_trend", "yoy_comparison"等）
            chart_data: 图表的数据
            context: 额外的上下文信息
        
        返回:
            AI生成的图表分析文本
        """
        prompt = f"""请分析以下图表数据，用100-150字简洁说明：

**图表类型：**{chart_type}

**数据：**
{json.dumps(chart_data, ensure_ascii=False, indent=2)[:1000]}

{f"**上下文：**{context}" if context else ""}

请提供：
1. 数据的主要趋势或特征（2-3句话）
2. 值得关注的异常点或关键发现（1-2句话）
3. 对购房者的实际意义（1句话）

要求：专业但易懂，100-150字。"""

        return self._call_ai(prompt, max_tokens=300)
    
    def analyze_price_trend(self, monthly_data: list) -> str:
        """
        分析价格趋势图
        
        参数:
            monthly_data: 月度价格数据
        
        返回:
            AI分析文本
        """
        return self.analyze_chart(
            "月度价格趋势",
            {"monthly_prices": monthly_data},
            f"时间跨度：{monthly_data[0]['month']} 至 {monthly_data[-1]['month']}" if monthly_data else ""
        )
    
    def analyze_yoy_comparison(self, yoy_data: list) -> str:
        """
        分析同比数据
        
        参数:
            yoy_data: 同比数据
        
        返回:
            AI分析文本
        """
        return self.analyze_chart(
            "年度同比对比",
            {"yearly_comparison": yoy_data},
            "关注各年度的同比增长率变化"
        )
    
    def analyze_district_comparison(self, district_data: list) -> str:
        """
        分析区域对比数据
        
        参数:
            district_data: 区域对比数据
        
        返回:
            AI分析文本
        """
        return self.analyze_chart(
            "区域价格对比",
            {"districts": district_data[:10]},  # 只发送前10个区域
            "关注高价区域和性价比区域的差异"
        )
    
    def analyze_investment_comparison(self, cities_scores: list) -> str:
        """
        分析城市投资价值对比
        
        参数:
            cities_scores: 城市投资评分数据
        
        返回:
            AI分析文本
        """
        return self.analyze_chart(
            "城市投资价值对比",
            {"investment_scores": cities_scores},
            "综合考虑价格趋势、稳定性等多维度指标"
        )
    
    def simplify_table_data(self, table_data: Dict[str, Any], table_name: str) -> str:
        """
        简化复杂表格数据，生成易读的文字总结
        
        参数:
            table_data: 表格数据
            table_name: 表格名称
        
        返回:
            AI生成的简化总结
        """
        prompt = f"""请将以下表格数据用简洁的文字总结（3-4个要点，每个20-30字）：

**表格名称：**{table_name}

**数据：**
{json.dumps(table_data, ensure_ascii=False, indent=2)[:1500]}

要求：
- 提取3-4个最重要的数据点
- 每个要点20-30字
- 总字数不超过120字
- 使用项目符号格式"""

        return self._call_ai(prompt, max_tokens=250)
    
    def generate_purchase_advice(self, user_profile: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """
        根据用户画像和市场数据生成购房建议
        
        参数:
            user_profile: 用户画像（预算、需求等）
            market_data: 市场数据
        
        返回:
            个性化购房建议
        """
        prompt = f"""根据以下信息，为购房者提供专业建议（150-200字）：

**购房者情况：**
{json.dumps(user_profile, ensure_ascii=False, indent=2)}

**市场情况：**
{json.dumps(market_data, ensure_ascii=False, indent=2)}

请提供：
1. 是否是入市的好时机（2-3句话）
2. 推荐关注的区域或价位段（2-3句话）
3. 风险提示和注意事项（1-2句话）

要求：专业、客观、实用，150-200字。"""

        return self._call_ai(prompt, max_tokens=350)

