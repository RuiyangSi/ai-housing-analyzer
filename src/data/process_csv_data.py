#!/usr/bin/env python3
"""
CSV数据处理脚本（用于处理上海和天津数据）
功能：
1. 将CSV格式数据转换为统一格式
2. 筛选2023-2025年的数据
3. 清理和标准化数据
"""

import pandas as pd
import sys
import os
from datetime import datetime
import re

def clean_unit_price(price_str):
    """
    清理单价字符串，提取数字
    例如: "36775元" -> 36775
    """
    if pd.isna(price_str):
        return None
    if isinstance(price_str, (int, float)):
        return price_str
    # 移除"元"字符和其他非数字字符（保留小数点）
    price_str = str(price_str).replace('元', '').replace(',', '').strip()
    try:
        return float(price_str)
    except:
        return None

def process_csv_city_data(csv_file, city_name, output_file, start_year=2023, end_year=2025):
    """
    处理CSV格式的城市数据（上海、天津）
    
    参数:
        csv_file: CSV文件路径
        city_name: 城市名称
        output_file: 输出CSV文件名
        start_year: 开始年份（默认2023）
        end_year: 结束年份（默认2025）
    """
    print(f"\n{'='*60}")
    print(f"处理 {city_name} 数据...")
    print(f"{'='*60}")
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"❌ 错误：文件 {csv_file} 不存在")
        return False
    
    try:
        # 读取数据
        print(f"📖 读取文件: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"✓ 原始数据: {len(df):,} 条")
        
        # 显示原始列名
        print(f"📋 原始列名: {list(df.columns)}")
        
        # 数据映射和转换
        # 原始列: community,district,business_area,title,room_type,area,orientation,floor_info,total_price,unit_price,deal_date,source,url
        # 目标列: 成交日期,城市,区域,商圈,小区,户型,面积（m²）,挂牌价（万元）,成交价（万元）,成交单价（元）
        
        df_processed = pd.DataFrame()
        
        # 1. 成交日期 - 使用混合格式解析，处理不同的日期格式
        df_processed['成交日期'] = pd.to_datetime(df['deal_date'], format='mixed', errors='coerce')
        
        # 2. 城市
        df_processed['城市'] = city_name
        
        # 3. 区域
        df_processed['区域'] = df['district']
        
        # 4. 商圈
        df_processed['商圈'] = df['business_area']
        
        # 5. 小区
        df_processed['小区'] = df['community']
        
        # 6. 户型
        df_processed['户型'] = df['room_type']
        
        # 7. 面积（m²）
        df_processed['面积（m²）'] = pd.to_numeric(df['area'], errors='coerce')
        
        # 8. 挂牌价（万元）- CSV数据中没有此字段，设为空
        df_processed['挂牌价（万元）'] = None
        
        # 9. 成交价（万元）
        df_processed['成交价（万元）'] = pd.to_numeric(df['total_price'], errors='coerce')
        
        # 10. 成交单价（元）- 需要清理"元"字符
        df_processed['成交单价（元）'] = df['unit_price'].apply(clean_unit_price)
        
        # 筛选年份范围的数据
        start_date = f'{start_year}-01-01'
        end_date = f'{end_year}-12-31'
        df_filtered = df_processed[(df_processed['成交日期'] >= start_date) & (df_processed['成交日期'] <= end_date)]
        print(f"✓ {start_year}-{end_year}年数据: {len(df_filtered):,} 条")
        
        if len(df_filtered) == 0:
            print(f"⚠️  警告：没有找到 {start_year}-{end_year} 年的数据")
            # 显示数据中的日期范围
            print(f"   数据日期范围: {df_processed['成交日期'].min()} 到 {df_processed['成交日期'].max()}")
            return False
        
        # 数据清理：删除关键字段的缺失值
        original_len = len(df_filtered)
        # 只删除关键字段（成交日期、成交价、面积、单价）的缺失值
        df_filtered = df_filtered.dropna(subset=['成交日期', '成交价（万元）', '面积（m²）', '成交单价（元）'])
        if len(df_filtered) < original_len:
            print(f"✓ 清理缺失值: 删除了 {original_len - len(df_filtered)} 条记录")
        
        if len(df_filtered) == 0:
            print(f"❌ 错误：清理后没有有效数据")
            return False
        
        # 保存为CSV
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存到: {output_file}")
        
        # 显示统计信息
        print(f"\n📊 数据统计:")
        print(f"  • 成交量: {len(df_filtered):,} 套")
        print(f"  • 平均成交价: {df_filtered['成交价（万元）'].mean():.2f} 万元")
        print(f"  • 中位数成交价: {df_filtered['成交价（万元）'].median():.2f} 万元")
        print(f"  • 平均单价: {df_filtered['成交单价（元）'].mean():.2f} 元/m²")
        print(f"  • 平均面积: {df_filtered['面积（m²）'].mean():.2f} m²")
        print(f"  • 价格范围: {df_filtered['成交价（万元）'].min():.2f} - {df_filtered['成交价（万元）'].max():.2f} 万元")
        print(f"  • 单价范围: {df_filtered['成交单价（元）'].min():.0f} - {df_filtered['成交单价（元）'].max():.0f} 元/m²")
        
        # 按年份统计
        df_filtered['年份'] = df_filtered['成交日期'].dt.year
        yearly_counts = df_filtered['年份'].value_counts().sort_index()
        print(f"\n📅 年度成交量:")
        for year, count in yearly_counts.items():
            print(f"  • {year}年: {count:,} 套")
        
        # 按区域统计前10
        district_counts = df_filtered['区域'].value_counts().head(10)
        print(f"\n🏘️  主要区域成交量 (Top 10):")
        for district, count in district_counts.items():
            avg_price = df_filtered[df_filtered['区域'] == district]['成交单价（元）'].mean()
            print(f"  • {district}: {count:,} 套 (均价: {avg_price:.0f} 元/m²)")
        
        print(f"\n✅ {city_name} 数据处理完成!\n")
        return True
        
    except Exception as e:
        print(f"❌ 错误：处理数据时发生异常")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("房价CSV数据处理工具 (上海、天津)")
    print("="*60)
    
    # 预定义的城市数据
    cities = [
        {
            'name': '上海',
            'csv_file': 'data/raw/上海.csv',
            'output_file': 'data/processed/data_shanghai_2023_2025.csv'
        },
        {
            'name': '天津',
            'csv_file': 'data/raw/天津.csv',
            'output_file': 'data/processed/data_tianjin_2023_2025.csv'
        }
    ]
    
    # 处理所有城市数据
    success_count = 0
    for city in cities:
        if process_csv_city_data(city['csv_file'], city['name'], city['output_file']):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"处理完成! 成功: {success_count}/{len(cities)}")
    print("="*60 + "\n")
    
    if success_count < len(cities):
        sys.exit(1)

if __name__ == '__main__':
    main()

