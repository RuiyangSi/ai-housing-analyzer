"""
AI 助手模块
提供房价数据智能问答功能
"""

import requests
import json
from typing import List, Dict, Any, Optional

class AIAssistant:
    """AI 助手类"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "deepseek-ai/DeepSeek-V3"):
        """
        初始化 AI 助手
        
        参数:
            api_url: API 地址
            api_key: API 密钥
            model: 使用的模型名称（默认使用DeepSeek-V3）
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
        
    def build_system_prompt(self, context_data: Optional[Dict[str, Any]] = None, role: str = 'investment_advisor') -> str:
        """
        构建系统提示词
        
        参数:
            context_data: 包含全局数据和/或城市数据的字典
            role: 用户角色
        """
        # 根据角色选择基础提示词
        role_prompts = {
            'investment_advisor': """你是一位拥有15年经验的资深房地产投资顾问。擅长使用专业术语（ROI、流动性、增值空间、市场波动率等）分析投资价值和风险控制。""",
            'first_time_buyer': """你是一位耐心、友善的购房顾问，正在帮助首次购房的新手。用通俗易懂的语言解释房价数据，避免专业术语，关注安全性和可负担性。""",
            'upgrader': """你是一位改善型购房咨询专家，专门为有换房需求的家庭提供建议。关注置换策略、资金规划和改善型需求匹配。"""
        }
        
        base_prompt = f"""{role_prompts.get(role, role_prompts['investment_advisor'])}

你的任务是帮助用户理解和分析2023-2025年的房价数据。回答要简洁明了，一般控制在200字以内。"""

        if context_data:
            # 添加全局数据上下文
            global_data = context_data.get('global_data', {})
            if global_data:
                provinces = global_data.get('provinces', [])
                total_records = global_data.get('total_records', 0)
                
                data_context = f"""

【系统数据概览】
- 覆盖省份数：{len(provinces)} 个
- 总数据量：{total_records:,} 条真实成交数据
- 数据年份：2023-2025年

省份分布："""
                
                for prov in provinces:
                    data_context += f"""
- {prov['name']}：{prov['count']:,}套（{prov['cities_count']}个城市）"""
                
                base_prompt += data_context
            
            # 添加城市数据上下文
            city_data = context_data.get('city_data', {})
            if city_data:
                overall = city_data.get('overall', {})
                yearly = city_data.get('yearly', [])
                
                city_context = f"""

【当前查看的城市数据】
- 城市：{city_data.get('city_name', '未知')}
- 总成交量：{overall.get('total_count', 0):,} 套
- 平均成交价：{overall.get('avg_price', 0):.2f} 万元
- 平均单价：{overall.get('avg_unit_price', 0):.2f} 元/m²
- 平均面积：{overall.get('avg_area', 0):.2f} m²"""
                
                base_prompt += city_context
        
        return base_prompt
    
    def chat(self, user_message: str, context_data: Optional[Dict[str, Any]] = None, 
             temperature: float = 0.7, max_tokens: int = 500, role: str = 'investment_advisor') -> Dict[str, Any]:
        """
        与 AI 对话
        
        参数:
            user_message: 用户消息
            context_data: 上下文数据（包含全局数据和/或城市数据）
            temperature: 温度参数（0-1，越高越随机）
            max_tokens: 最大token数
            role: 角色ID
            
        返回:
            包含回复内容和状态的字典
        """
        try:
            # 构建消息列表
            messages = [
                {"role": "system", "content": self.build_system_prompt(context_data, role)}
            ]
            
            # 添加历史对话（最近5轮）
            messages.extend(self.conversation_history[-10:])
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用 API
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    ai_message = result['choices'][0]['message']['content']
                    
                    # 保存到对话历史
                    self.conversation_history.append({"role": "user", "content": user_message})
                    self.conversation_history.append({"role": "assistant", "content": ai_message})
                    
                    return {
                        'success': True,
                        'message': ai_message,
                        'model': self.model
                    }
                else:
                    return {
                        'success': False,
                        'error': '未收到有效回复'
                    }
            else:
                return {
                    'success': False,
                    'error': f'API 错误：{response.status_code}',
                    'details': response.text[:200]
                }
                
        except requests.Timeout:
            return {
                'success': False,
                'error': '请求超时，请重试'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'发生错误：{str(e)}'
            }
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def build_role_system_prompt(self, role: str = 'investment_advisor') -> str:
        """
        根据角色构建系统提示词
        
        参数:
            role: 角色ID（investment_advisor / first_time_buyer / upgrader）
        """
        role_prompts = {
            'investment_advisor': """你是一位拥有15年经验的资深房地产投资顾问。

你的专业领域：
- 投资回报率（ROI）评估
- 市场趋势预判和技术分析
- 风险收益比分析
- 资产配置策略建议
- 市场时机把握

分析风格：
- 使用专业术语：ROI、流动性、增值空间、市场波动率、变异系数等
- 关注投资价值和风险控制
- 提供量化指标和数据支撑
- 给出明确的投资建议（买入/观望/不建议）

请用专业但清晰的语言分析，重点关注投资价值。""",
            
            'first_time_buyer': """你是一位耐心、友善的购房顾问，正在帮助首次购房的新手。

你的任务：
- 用通俗易懂的语言解释房价数据
- 帮助理解购房流程和注意事项
- 评估房价是否合理
- 提供首付和贷款建议
- 提醒常见陷阱和风险

沟通风格：
- 避免使用专业术语（如ROI、流动性等）
- 用生活化的比喻和例子
- 关注安全性和可负担性
- 语气亲切，像朋友聊天一样
- 重点提醒"要注意什么"

请用简单的语言，帮助首次购房者做出明智决策。""",
            
            'upgrader': """你是一位改善型购房咨询专家，专门为有换房需求的家庭提供建议。

你的专长：
- 卖旧买新的最佳时机判断
- 置换策略和资金规划
- 改善型需求匹配（学区、地段、面积、环境）
- 资产保值增值分析
- 家庭生命周期规划

分析重点：
- 评估当前房产价值和市场行情
- 分析换房的时机（先卖后买 vs 先买后卖）
- 考虑改善需求的优先级
- 税费和资金成本计算
- 平衡实用性和投资价值

请平衡专业性和实用性，重点关注换房策略和资产优化。"""
        }
        
        return role_prompts.get(role, role_prompts['investment_advisor'])
    
    def chat_stream(self, user_message: str, context_data: Optional[Dict[str, Any]] = None, 
             temperature: float = 0.7, max_tokens: int = 500, role: str = 'investment_advisor'):
        """
        与 AI 对话（流式输出）
        
        参数:
            user_message: 用户消息
            context_data: 上下文数据（包含全局数据和/或城市数据）
            temperature: 温度参数（0-1，越高越随机）
            max_tokens: 最大token数
            role: 角色ID（investment_advisor / first_time_buyer / upgrader）
            
        返回:
            生成器，逐步yield AI回复的文本片段
        """
        try:
            # 构建系统提示词（包含角色和数据上下文）
            system_prompt = self.build_system_prompt(context_data, role)
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史对话（最近5轮）
            messages.extend(self.conversation_history[-10:])
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用 API（流式）
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True  # 开启流式输出
                },
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                full_response = ''
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        full_response += content
                                        yield content
                            except json.JSONDecodeError:
                                continue
                
                # 保存到对话历史
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": full_response})
            else:
                yield "抱歉，AI服务暂时不可用。"
                
        except Exception as e:
            print(f"AI Stream Error: {e}")
            yield "抱歉，发生了错误。请稍后重试。"
    
    def get_quick_answer(self, question_type: str, city_data: Dict[str, Any]) -> str:
        """
        获取快速回答（预设问题）
        
        参数:
            question_type: 问题类型
            city_data: 城市数据
        """
        overall = city_data.get('overall', {})
        yearly = city_data.get('yearly', [])
        city_name = city_data.get('city_name', '该城市')
        
        if question_type == 'trend':
            if len(yearly) >= 2:
                first_year = yearly[0]
                last_year = yearly[-1]
                price_change = last_year['avg_price'] - first_year['avg_price']
                change_percent = (price_change / first_year['avg_price']) * 100
                
                if price_change > 0:
                    trend = "上涨"
                    emoji = "📈"
                else:
                    trend = "下降"
                    emoji = "📉"
                
                return f"{emoji} {city_name}在{first_year['year']}-{last_year['year']}年间，平均房价{trend}了{abs(price_change):.2f}万元，涨幅约{abs(change_percent):.1f}%。"
            else:
                return "数据不足，无法分析趋势。"
        
        elif question_type == 'recommend':
            avg_price = overall.get('avg_price', 0)
            avg_unit_price = overall.get('avg_unit_price', 0)
            
            return f"根据{city_name}的数据，平均成交价为{avg_price:.2f}万元，平均单价{avg_unit_price:.2f}元/m²。建议关注性价比高的区域，并结合自身需求和预算做出选择。"
        
        elif question_type == 'market':
            total = overall.get('total_count', 0)
            return f"{city_name}在2023-2025年间共成交{total:,}套房产，市场较为活跃。从成交量可以看出市场需求稳定。"
        
        else:
            return "抱歉，我不太理解这个问题类型。"


def test_assistant():
    """测试 AI 助手"""
    print("=" * 60)
    print("AI 助手测试")
    print("=" * 60)
    
    # 初始化助手
    assistant = AIAssistant(
        api_url="https://api3.apifans.com/v1",
        api_key="sk-bu6GTEtgqeTb2UQkD95fD3B04d2a48488f1a8b3395Ff667e"
    )
    
    # 测试数据
    test_city_data = {
        'city_name': '北京',
        'overall': {
            'total_count': 184945,
            'avg_price': 457.81,
            'avg_unit_price': 54931.62,
            'avg_area': 83.35
        },
        'yearly': [
            {'year': 2023, 'count': 65000, 'avg_price': 450.0, 'avg_unit_price': 53000.0},
            {'year': 2024, 'count': 70000, 'avg_price': 460.0, 'avg_unit_price': 55000.0},
            {'year': 2025, 'count': 49945, 'avg_price': 463.0, 'avg_unit_price': 56000.0}
        ]
    }
    
    # 测试问题
    test_questions = [
        "北京的房价趋势如何？",
        "现在适合在北京买房吗？",
        "北京哪个区域的房价比较合理？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        result = assistant.chat(question, test_city_data)
        
        if result['success']:
            print(f"✅ AI 回复: {result['message']}")
        else:
            print(f"❌ 错误: {result['error']}")
        
        print("-" * 60)
    
    # 测试快速回答
    print("\n测试快速回答:")
    print("趋势分析:", assistant.get_quick_answer('trend', test_city_data))
    print("购房建议:", assistant.get_quick_answer('recommend', test_city_data))
    print("市场分析:", assistant.get_quick_answer('market', test_city_data))


if __name__ == '__main__':
    test_assistant()

