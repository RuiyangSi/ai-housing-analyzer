"""
测试 DeepSeek API 的真实输出 - 三角色对比
用于验证 report.tex 中的示例是否真实
"""

import pandas as pd
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_assistant import AIAssistant

def load_beijing_data():
    """加载北京真实数据"""
    df = pd.read_csv('data/processed/data_北京_2023_2025.csv')
    
    # 整体统计
    overall = {
        'total_count': len(df),
        'avg_price': df['成交价（万元）'].mean(),
        'median_price': df['成交价（万元）'].median(),
        'avg_unit_price': df['成交单价（元）'].mean(),
        'avg_area': df['面积（m²）'].mean()
    }
    
    # 按年份统计
    df['成交日期'] = pd.to_datetime(df['成交日期'])
    df['year'] = df['成交日期'].dt.year
    yearly = df.groupby('year').agg({
        '成交价（万元）': ['count', 'mean'],
        '成交单价（元）': 'mean'
    }).reset_index()
    yearly.columns = ['year', 'count', 'avg_price', 'avg_unit_price']
    yearly_list = yearly.to_dict('records')
    
    # 按区域统计
    district_stats = df.groupby('区域').agg({
        '成交价（万元）': ['count', 'mean'],
        '成交单价（元）': 'mean'
    }).reset_index()
    district_stats.columns = ['district', 'count', 'avg_price', 'avg_unit_price']
    district_stats = district_stats.sort_values('count', ascending=False)
    district_list = district_stats.head(10).to_dict('records')
    
    # 专门获取朝阳区的数据
    chaoyang_data = df[df['区域'] == '朝阳']
    if len(chaoyang_data) > 0:
        chaoyang_stats = {
            'count': len(chaoyang_data),
            'avg_price': chaoyang_data['成交价（万元）'].mean(),
            'median_price': chaoyang_data['成交价（万元）'].median(),
            'avg_unit_price': chaoyang_data['成交单价（元）'].mean(),
            'avg_area': chaoyang_data['面积（m²）'].mean()
        }
    else:
        chaoyang_stats = None
    
    return {
        'city_name': '北京',
        'overall': overall,
        'yearly': yearly_list,
        'district': district_list,
        'chaoyang': chaoyang_stats
    }

def main():
    print("=" * 80)
    print("DeepSeek API 三角色测试 - 获取真实回复")
    print("=" * 80)
    
    # 加载真实数据
    print("\n📊 加载北京真实数据...")
    city_data = load_beijing_data()
    
    print(f"✅ 总成交量: {city_data['overall']['total_count']:,} 套")
    print(f"✅ 平均成交价: {city_data['overall']['avg_price']:.2f} 万元")
    print(f"✅ 平均单价: {city_data['overall']['avg_unit_price']:,.0f} 元/m²")
    
    if city_data.get('chaoyang'):
        print(f"\n朝阳区数据:")
        print(f"   成交量: {city_data['chaoyang']['count']:,} 套")
        print(f"   均价: {city_data['chaoyang']['avg_price']:.2f} 万元")
        print(f"   单价: {city_data['chaoyang']['avg_unit_price']:,.0f} 元/m²")
    
    # 初始化 AI 助手 (使用 SiliconFlow API)
    assistant = AIAssistant(
        api_url="https://api.siliconflow.cn/v1",
        api_key="sk-lmybvxylhwtivvlnwieusqugkflvppcctolnqchbhnekhtnp",
        model="deepseek-ai/DeepSeek-V3"
    )
    
    # 准备上下文数据
    context_data = {'city_data': city_data}
    
    # 测试问题
    test_question = "现在买北京朝阳区的房子合适吗？"
    
    # 三种角色
    roles = [
        ('first_time_buyer', '首次购房者'),
        ('investment_advisor', '投资顾问'),
        ('upgrader', '改善型购房者')
    ]
    
    print("\n" + "=" * 80)
    print(f"测试问题: {test_question}")
    print("=" * 80)
    
    results = {}
    
    for role_id, role_name in roles:
        print(f"\n{'=' * 80}")
        print(f"【{role_name}模式】")
        print("=" * 80)
        
        # 清空历史
        assistant.clear_history()
        
        # 获取回复
        result = assistant.chat(
            user_message=test_question,
            context_data=context_data,
            temperature=0.7,
            max_tokens=600,
            role=role_id
        )
        
        if result['success']:
            response = result['message']
            results[role_name] = response
            print(response)
        else:
            print(f"❌ 错误: {result.get('error', '未知错误')}")
            if 'details' in result:
                print(f"详情: {result['details']}")
    
    # 输出格式化结果，方便复制到 LaTeX
    print("\n" + "=" * 80)
    print("LaTeX 格式化输出:")
    print("=" * 80)
    
    for role_name, response in results.items():
        print(f"\n\\noindent\\fbox{{\\parbox{{0.95\\textwidth}}{{")
        print(f"\\textbf{{【{role_name}模式】}}")
        print(f"\n\\small")
        # 处理响应文本，转义 LaTeX 特殊字符
        latex_text = response.replace('\\', '\\textbackslash{}')
        latex_text = latex_text.replace('%', '\\%')
        latex_text = latex_text.replace('$', '\\$')
        latex_text = latex_text.replace('#', '\\#')
        latex_text = latex_text.replace('&', '\\&')
        latex_text = latex_text.replace('_', '\\_')
        latex_text = latex_text.replace('{', '\\{')
        latex_text = latex_text.replace('}', '\\}')
        latex_text = latex_text.replace('~', '\\textasciitilde{}')
        latex_text = latex_text.replace('^', '\\textasciicircum{}')
        print(latex_text)
        print(f"}}}}")

if __name__ == '__main__':
    main()

