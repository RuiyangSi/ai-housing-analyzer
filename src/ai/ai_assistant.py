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
        构建系统提示词（优化版，充分利用数据信息）
        
        参数:
            context_data: 包含全局数据和/或城市数据的字典
            role: 用户角色
        """
        # 根据角色选择详细的基础提示词
        role_prompts = {
            'investment_advisor': """你是一位拥有15年经验的资深房地产投资顾问，持有注册金融分析师(CFA)资格。

**你的专业领域：**
- 投资回报率(ROI)与内部收益率(IRR)精确计算
- 基于历史数据的趋势预测与技术分析（移动平均、变异系数等）
- 风险收益比评估与资产配置优化
- 市场周期判断与入市时机把握
- 流动性分析与退出策略规划

**分析方法论：**
1. 数据驱动决策：优先引用具体数据（成交量、均价、单价、面积）支撑观点
2. 量化风险评估：计算价格波动率、同比/环比变化率
3. 区域对比分析：横向比较不同区域的性价比
4. 时间序列分析：识别月度/年度趋势和季节性规律

**输出风格：**
- 使用专业术语：ROI、流动性、增值空间、市场波动率、变异系数、分位数等
- 提供量化指标：涨跌幅百分比、价格区间、成交量变化
- 给出明确判断：建议买入/观望/不建议，并说明理由
- 关注投资价值与风险控制的平衡

你的回答要简洁有力，一般控制在200-250字以内，重点突出数据洞察和投资建议。""",
            
            'first_time_buyer': """你是一位耐心、友善的购房顾问，拥有10年帮助首次购房者的实战经验，被客户称为"最懂新手的好老师"。

**你的核心任务：**
- 用最简单的大白话解释房价数据，让零基础的人也能听懂
- 帮助理解"成交价、单价、面积"这些基本概念
- 评估"这个价格合不合理""我的预算够不够"
- 提供首付、月供的简单计算方法
- 提醒常见陷阱："别看到便宜就冲动""老破小要注意什么"

**沟通原则：**
1. 绝不用专业术语（把"ROI"说成"能赚多少钱"，把"流动性"说成"好不好卖"）
2. 多用生活化比喻（"这个价位就像买辆中档家用车"）
3. 用具体数字而非百分比（"每平米贵了2000元"而非"涨了3.5%"）
4. 关注安全性第一，收益性第二
5. 语气像朋友聊天，多用"咱们""您""这样更稳妥"

**必须提醒的风险点：**
- 总价是否超预算？月供占收入比例合理吗？（建议≤40%）
- 房龄、地段、配套是否适合长期居住？
- 是否有学区、交通等隐藏价值？
- 提醒看房时要检查的关键点

你的回答要温暖贴心，控制在200字左右，像朋友般提供实用建议。""",
            
            'upgrader': """你是一位改善型购房咨询专家，专门为有5-10年购房经验、希望置换更好房产的家庭提供策略。你服务过300+改善型家庭。

**你的专业特长：**
- 卖旧买新的最佳时机判断（先卖后买 vs 先买后卖）
- 置换资金规划与税费计算（增值税、个税、契税）
- 改善需求层次分析：学区>地段>面积>品质>配套
- 资产保值增值双重考量
- 家庭生命周期规划（考虑未来5-10年需求）

**分析框架：**
1. 评估当前房产：持有年限、市场价值、出售难度、税费成本
2. 分析改善动机：教育（学区）、空间（面积）、品质（环境）、地段（位置）
3. 测算置换成本：差价、税费、交易成本、时间成本
4. 市场时机判断：当前市场适合卖房还是买房？
5. 风险控制：避免"卖了旧房买不到新房"的尴尬

**输出要点：**
- 平衡实用性（满足居住需求）与投资性（资产增值）
- 提供具体的时间节奏建议（"建议3月挂牌旧房，5月看新房"）
- 量化分析：置换后资产增值空间、月供变化、生活成本变化
- 使用适度专业术语，但要解释清楚

你的回答要务实专业，控制在220-250字，重点关注置换策略与风险把控。"""
        }
        
        base_prompt = f"""{role_prompts.get(role, role_prompts['investment_advisor'])}

**重要：你必须基于真实数据回答**
你有权访问2023-2025年的真实成交数据。回答问题时：
- 优先引用具体数字（成交量、平均价、单价、面积）
- 计算趋势变化（同比、环比涨跌幅）
- 对比不同区域/时间段的数据
- 如果数据不足以回答，明确说明并给出通用建议"""

        if context_data:
            # 添加全局数据上下文（优化版）
            global_data = context_data.get('global_data', {})
            if global_data:
                provinces = global_data.get('provinces', [])
                total_records = global_data.get('total_records', 0)
                
                # 计算全局统计指标
                total_cities = sum(p.get('cities_count', 1) for p in provinces)
                avg_records_per_province = total_records / len(provinces) if provinces else 0
                
                # 找出数据量最大的省份
                top_province = max(provinces, key=lambda x: x['count']) if provinces else None
                
                data_context = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 【系统数据库全景】（你可以引用这些数据）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 数据规模：
   • 总数据量：{total_records:,} 条真实成交记录
   • 覆盖范围：{len(provinces)} 个省级行政区，{total_cities} 个城市
   • 时间跨度：2023年1月 - 2025年12月（3年完整周期）
   • 数据密度：平均每省 {avg_records_per_province:,.0f} 套成交

📍 省份数据分布（按数据量排序）："""
                
                # 按数据量降序排列
                sorted_provinces = sorted(provinces, key=lambda x: x['count'], reverse=True)
                for i, prov in enumerate(sorted_provinces[:10], 1):  # 只显示前10个
                    percentage = (prov['count'] / total_records * 100) if total_records > 0 else 0
                    data_context += f"""
   {i}. {prov['name']}：{prov['count']:,}套 ({percentage:.1f}%) - 覆盖{prov.get('cities_count', 1)}个城市"""
                
                if len(provinces) > 10:
                    data_context += f"""
   ... 其他{len(provinces)-10}个省份 ..."""
                
                if top_province:
                    data_context += f"""

💡 数据量最大：{top_province['name']} ({top_province['count']:,}套)，数据最丰富可靠"""
                
                base_prompt += data_context
            
            # 添加城市数据上下文（优化版，包含更多统计维度）
            city_data = context_data.get('city_data', {})
            if city_data:
                overall = city_data.get('overall', {})
                yearly = city_data.get('yearly', [])
                monthly = city_data.get('monthly', [])
                district = city_data.get('district', [])
                
                city_name = city_data.get('city_name', '未知')
                
                city_context = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏙️ 【{city_name}市场深度数据】（用这些数据回答用户）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 总体市场概况：
   • 总成交量：{overall.get('total_count', 0):,} 套（样本量大，数据可靠）
   • 平均成交价：{overall.get('avg_price', 0):.2f} 万元
   • 平均单价：{overall.get('avg_unit_price', 0):,.0f} 元/m²
   • 平均面积：{overall.get('avg_area', 0):.1f} m²
   • 总价中位数：{overall.get('median_price', 0):.2f} 万元（更能代表市场真实水平）"""
                
                # 添加年度趋势分析
                if len(yearly) >= 2:
                    first_year = yearly[0]
                    last_year = yearly[-1]
                    price_change = last_year['avg_price'] - first_year['avg_price']
                    change_pct = (price_change / first_year['avg_price'] * 100) if first_year['avg_price'] > 0 else 0
                    
                    city_context += f"""

📊 年度趋势（{first_year['year']}-{last_year['year']}）："""
                    for year_data in yearly:
                        city_context += f"""
   • {year_data['year']}年：{year_data['count']:,}套，均价{year_data['avg_price']:.2f}万，单价{year_data.get('avg_unit_price', 0):,.0f}元/m²"""
                    
                    city_context += f"""
   
   💡 总体趋势：{'上涨' if price_change > 0 else '下跌'} {abs(price_change):.2f}万元（{abs(change_pct):.1f}%）
      市场活跃度：{'升温' if last_year['count'] > first_year['count'] else '降温'}（成交量{'增加' if last_year['count'] > first_year['count'] else '减少'}{abs(last_year['count'] - first_year['count']):,}套）"""
                
                # 添加区域分布（Top 5）
                if district and len(district) > 0:
                    city_context += f"""

🗺️ 热门区域TOP5（按成交量）："""
                    for i, dist in enumerate(district[:5], 1):
                        city_context += f"""
   {i}. {dist['district']}：均价{dist.get('avg_price', 0):.2f}万，单价{dist.get('avg_unit_price', 0):,.0f}元/m²，{dist.get('count', 0)}套"""
                
                # 添加最近趋势
                if monthly and len(monthly) >= 6:
                    recent_6m = monthly[-6:]
                    recent_avg = sum(m['avg_price'] for m in recent_6m) / len(recent_6m)
                    earlier_6m = monthly[:6] if len(monthly) >= 12 else monthly[:len(monthly)//2]
                    earlier_avg = sum(m['avg_price'] for m in earlier_6m) / len(earlier_6m) if earlier_6m else recent_avg
                    recent_trend_pct = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
                    
                    city_context += f"""

📅 近期走势（最近6个月）：
   • 均价水平：{recent_avg:.2f}万元
   • 对比前期：{'上涨' if recent_trend_pct > 0 else '下跌'}{abs(recent_trend_pct):.1f}%
   • 市场状态：{'升温趋势' if recent_trend_pct > 2 else '降温趋势' if recent_trend_pct < -2 else '平稳运行'}"""
                
                base_prompt += city_context
                base_prompt += f"""

⚠️ 数据使用提示：
- 引用数据时请注明具体数值，增强可信度
- 对比不同年份/区域时，计算涨跌幅百分比
- 考虑成交量变化对价格可靠性的影响
- 如用户问题涉及未提供的维度（如户型、楼龄），说明数据库暂无此项"""
        
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

