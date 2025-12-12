#!/usr/bin/env python3
"""
数据处理脚本
功能：
1. 将Excel文件转换为CSV格式
2. 筛选2023-2025年的数据
3. 清理和标准化数据
"""

import pandas as pd
import sys
import os
from datetime import datetime

def process_city_data(excel_file, city_name, output_file, start_year=2023, end_year=2025):
    """
    处理单个城市的数据
    
    参数:
        excel_file: Excel文件路径
        city_name: 城市名称
        output_file: 输出CSV文件名
        start_year: 开始年份（默认2023）
        end_year: 结束年份（默认2025）
    """
    print(f"\n{'='*60}")
    print(f"处理 {city_name} 数据...")
    print(f"{'='*60}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"❌ 错误：文件 {excel_file} 不存在")
        return False
    
    try:
        # 读取数据
        print(f"📖 读取文件: {excel_file}")
        df = pd.read_excel(excel_file)
        print(f"✓ 原始数据: {len(df):,} 条")
        
        # 转换日期格式
        df['成交日期'] = pd.to_datetime(df['成交日期'], format='%Y.%m.%d')
        
        # 筛选年份范围的数据
        start_date = f'{start_year}-01-01'
        end_date = f'{end_year}-12-31'
        df_filtered = df[(df['成交日期'] >= start_date) & (df['成交日期'] <= end_date)]
        print(f"✓ {start_year}-{end_year}年数据: {len(df_filtered):,} 条")
        
        if len(df_filtered) == 0:
            print(f"⚠️  警告：没有找到 {start_year}-{end_year} 年的数据")
            return False
        
        # 选择需要保留的列
        columns_to_keep = [
            '成交日期', '城市', '区域', '商圈', '小区', 
            '户型', '面积（m²）', '挂牌价（万元）', 
            '成交价（万元）', '成交单价（元）'
        ]
        
        # 检查列是否存在
        missing_columns = [col for col in columns_to_keep if col not in df_filtered.columns]
        if missing_columns:
            print(f"❌ 错误：缺少列 {missing_columns}")
            return False
        
        df_final = df_filtered[columns_to_keep].copy()
        
        # 数据清理：删除缺失值
        original_len = len(df_final)
        df_final = df_final.dropna()
        if len(df_final) < original_len:
            print(f"✓ 清理缺失值: 删除了 {original_len - len(df_final)} 条记录")
        
        # 保存为CSV
        df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存到: {output_file}")
        
        # 显示统计信息
        print(f"\n📊 数据统计:")
        print(f"  • 成交量: {len(df_final):,} 套")
        print(f"  • 平均成交价: {df_final['成交价（万元）'].mean():.2f} 万元")
        print(f"  • 中位数成交价: {df_final['成交价（万元）'].median():.2f} 万元")
        print(f"  • 平均单价: {df_final['成交单价（元）'].mean():.2f} 元/m²")
        print(f"  • 平均面积: {df_final['面积（m²）'].mean():.2f} m²")
        print(f"  • 价格范围: {df_final['成交价（万元）'].min():.2f} - {df_final['成交价（万元）'].max():.2f} 万元")
        
        # 按年份统计
        df_final['年份'] = df_final['成交日期'].dt.year
        yearly_counts = df_final['年份'].value_counts().sort_index()
        print(f"\n📅 年度成交量:")
        for year, count in yearly_counts.items():
            print(f"  • {year}年: {count:,} 套")
        
        print(f"\n✅ {city_name} 数据处理完成!\n")
        return True
        
    except Exception as e:
        print(f"❌ 错误：处理数据时发生异常")
        print(f"   {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("房价数据处理工具")
    print("="*60)
    
    # 预定义的城市数据
    cities = [
        {
            'name': '北京',
            'excel_file': 'data/raw/北京成交数据(435008条_2018.04.04-2025.08.01).xlsx',
            'output_file': 'data/processed/data_beijing_2023_2025.csv'
        },
        {
            'name': '厦门',
            'excel_file': 'data/raw/厦门成交数据(38238条_2018.04.02-2025.07.30).xlsx',
            'output_file': 'data/processed/data_xiamen_2023_2025.csv'
        },
        {
            'name': '武汉',
            'excel_file': 'data/raw/武汉成交数据(241506条_2018.04.01-2025.08.01).xlsx',
            'output_file': 'data/processed/data_wuhan_2023_2025.csv'
        }
    ]
    
    # 处理所有城市数据
    success_count = 0
    for city in cities:
        if process_city_data(city['excel_file'], city['name'], city['output_file']):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"处理完成! 成功: {success_count}/{len(cities)}")
    print("="*60 + "\n")
    
    if success_count < len(cities):
        sys.exit(1)

if __name__ == '__main__':
    main()

