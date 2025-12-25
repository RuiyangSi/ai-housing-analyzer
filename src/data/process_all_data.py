#!/usr/bin/env python3
"""
统一数据处理脚本
功能：
1. 处理所有省市的CSV数据
2. 按省份组织数据（一个省的不同市合并）
3. 筛选2023-2025年的数据
4. 生成统一格式的输出
"""

import pandas as pd
import os
import json
from datetime import datetime

def clean_unit_price(price_str):
    """清理单价字符串"""
    if pd.isna(price_str):
        return None
    if isinstance(price_str, (int, float)):
        return price_str
    price_str = str(price_str).replace('元', '').replace(',', '').replace('*', '').strip()
    try:
        return float(price_str)
    except:
        return None

def clean_total_price(price_str):
    """清理总价字符串"""
    if pd.isna(price_str):
        return None
    if isinstance(price_str, (int, float)):
        return price_str
    price_str = str(price_str).replace('*', '').strip()
    try:
        return float(price_str)
    except:
        return None

def clean_data(df, province_name):
    """
    数据清洗函数
    1. 一致性校验：成交价 ≈ 单价 × 面积 / 10000
    2. 异常值过滤：删除极端价格
    3. 去重处理：删除重复记录
    """
    original_len = len(df)
    print(f"     🔧 开始数据清洗...")
    
    # 1. 一致性校验：计算预期成交价，检查误差
    # 预期成交价 = 单价 × 面积 / 10000 (转换为万元)
    df['预期成交价'] = df['成交单价（元）'] * df['面积（m²）'] / 10000
    
    # 计算误差比例：|实际 - 预期| / 预期
    df['价格误差'] = abs(df['成交价（万元）'] - df['预期成交价']) / df['预期成交价']
    
    # 删除误差超过50%的记录（价格不一致）
    before_consistency = len(df)
    df = df[df['价格误差'] <= 0.5]
    consistency_removed = before_consistency - len(df)
    if consistency_removed > 0:
        print(f"     ⚠️  一致性校验: 删除 {consistency_removed:,} 条价格不一致记录")
    
    # 2. 异常值过滤
    # 成交价范围：10万 - 5000万（合理的住宅价格范围）
    before_outlier = len(df)
    df = df[(df['成交价（万元）'] >= 10) & (df['成交价（万元）'] <= 5000)]
    outlier_removed = before_outlier - len(df)
    if outlier_removed > 0:
        print(f"     ⚠️  异常值过滤: 删除 {outlier_removed:,} 条极端价格记录")
    
    # 单价范围：1000元/㎡ - 300000元/㎡
    before_unit_outlier = len(df)
    df = df[(df['成交单价（元）'] >= 1000) & (df['成交单价（元）'] <= 300000)]
    unit_outlier_removed = before_unit_outlier - len(df)
    if unit_outlier_removed > 0:
        print(f"     ⚠️  单价异常过滤: 删除 {unit_outlier_removed:,} 条单价异常记录")
    
    # 面积范围：10㎡ - 500㎡
    before_area_outlier = len(df)
    df = df[(df['面积（m²）'] >= 10) & (df['面积（m²）'] <= 500)]
    area_outlier_removed = before_area_outlier - len(df)
    if area_outlier_removed > 0:
        print(f"     ⚠️  面积异常过滤: 删除 {area_outlier_removed:,} 条面积异常记录")
    
    # 3. 去重处理（基于小区、户型、面积、成交日期、成交价）
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['小区', '户型', '面积（m²）', '成交日期', '成交价（万元）'])
    dedup_removed = before_dedup - len(df)
    if dedup_removed > 0:
        print(f"     ⚠️  去重处理: 删除 {dedup_removed:,} 条重复记录")
    
    # 删除临时列
    df = df.drop(columns=['预期成交价', '价格误差'])
    
    total_removed = original_len - len(df)
    print(f"     ✅ 清洗完成: 共删除 {total_removed:,} 条 ({total_removed/original_len*100:.1f}%), 剩余 {len(df):,} 条")
    
    return df

def process_all_data(data_dir='data/raw', output_dir='data/processed', start_year=2023, end_year=2025):
    """处理所有城市数据"""
    print("\n" + "="*80)
    print("全国房价数据统一处理工具")
    print("="*80)
    
    # 特殊文件名映射（文件名 -> (省份, 城市)）
    # 根据原始数据URL中的城市代码确定实际城市
    special_mappings = {
        'anhui_deals': ('安徽', '合肥市'),           # hf.esf.fang.com
        'hebei_all_deals_merged': ('河北', '保定市'), # bd.esf.fang.com
        'heilongjiang_deals': ('黑龙江', '哈尔滨市'), # hrb.esf.fang.com
        'jiangsu_deals': ('江苏', '无锡市'),         # wuxi.esf.fang.com
        'jilin_deals': ('吉林', '长春市'),           # changchun
        'liaoning_deals': ('辽宁', '沈阳市'),        # sy
        'shanxi_deals': ('山西', '太原市'),          # taiyuan.esf.fang.com (旧数据)
        'shanxi_taiyuan_deals': ('山西', '太原市'),  # 新增太原数据
        'shanxi_datong_deals': ('山西', '大同市'),   # 新增大同数据
        'zhejiang_deals': ('浙江', '宁波市'),        # nb.esf.fang.com
        '厦门': ('福建', '厦门市'),                  # xm.esf.fang.com (新增大数据集)
        '重庆': ('重庆', '重庆市'),                  # cq.esf.fang.com (直辖市)
        '云南昆明': ('云南', '昆明市'),              # 新增云南昆明
        '四川成都': ('四川', '成都市'),              # 新增四川成都
        '四川绵阳': ('四川', '绵阳市'),              # 新增四川绵阳
        '广东广州': ('广东', '广州市'),              # 新增广东广州
        '广东深圳': ('广东', '深圳市'),              # 新增广东深圳
        '贵州贵阳': ('贵州', '贵阳市'),              # 新增贵州贵阳
        '贵州遵义': ('贵州', '遵义市'),              # 新增贵州遵义
    }
    
    # 扫描所有CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"\n📁 发现 {len(csv_files)} 个数据文件")
        
    # 按省份组织文件
    province_cities = {}
    for filename in sorted(csv_files):
        file_key = filename.replace('.csv', '')
        
        # 检查是否是特殊文件名
        if file_key in special_mappings:
            province, city = special_mappings[file_key]
        elif '-' in filename:
            # 格式: "省份-城市.csv"
            parts = filename.replace('.csv', '').split('-')
            province = parts[0]
            city = parts[1]
        else:
            # 直辖市格式: "城市.csv"
            city = filename.replace('.csv', '')
            if city in ['北京市', '上海市', '天津市', '重庆市']:
                province = city.replace('市', '')
            else:
                province = city.replace('市', '')
        
        if province not in province_cities:
            province_cities[province] = []
        province_cities[province].append({'filename': filename, 'city': city})
    
    print(f"\n🗺️  覆盖省份: {len(province_cities)} 个")
    for province, cities in province_cities.items():
        city_names = ', '.join([c['city'] for c in cities])
        print(f"  • {province}: {city_names}")
    
    # 处理每个省份的数据
    all_results = []
    summary_stats = {}
    
    for province, cities in province_cities.items():
        print(f"\n{'='*80}")
        print(f"处理 {province} 数据...")
        print(f"{'='*80}")
        
        province_data = []
        province_total_count = 0
        
        for city_info in cities:
            filename = city_info['filename']
            city_name = city_info['city']
            file_path = os.path.join(data_dir, filename)
            
            print(f"\n  📖 读取: {filename}")
            
            try:
                # 读取CSV
                df = pd.read_csv(file_path, low_memory=False)
                print(f"     原始数据: {len(df):,} 条")
                
                # 转换日期
                df['成交日期'] = pd.to_datetime(df['deal_date'], format='mixed', errors='coerce')
                
                # 筛选年份
                start_date = f'{start_year}-01-01'
                end_date = f'{end_year}-12-31'
                df_filtered = df[(df['成交日期'] >= start_date) & (df['成交日期'] <= end_date)]
                print(f"     {start_year}-{end_year}年数据: {len(df_filtered):,} 条")
                
                if len(df_filtered) == 0:
                    print(f"     ⚠️  警告：没有 {start_year}-{end_year} 年的数据")
                    continue
                
                # 数据转换
                df_processed = pd.DataFrame()
                df_processed['成交日期'] = df_filtered['成交日期']
                df_processed['省份'] = province
                df_processed['城市'] = city_name
                df_processed['区域'] = df_filtered['district']
                df_processed['商圈'] = df_filtered['business_area']
                df_processed['小区'] = df_filtered['community']
                df_processed['户型'] = df_filtered['room_type']
                df_processed['面积（m²）'] = pd.to_numeric(df_filtered['area'], errors='coerce')
                df_processed['挂牌价（万元）'] = None
                df_processed['成交价（万元）'] = df_filtered['total_price'].apply(clean_total_price)
                df_processed['成交单价（元）'] = df_filtered['unit_price'].apply(clean_unit_price)
                
                # 清理缺失值
                original_len = len(df_processed)
                df_processed = df_processed.dropna(subset=['成交日期', '成交价（万元）', '面积（m²）', '成交单价（元）'])
                removed = original_len - len(df_processed)
                if removed > 0:
                    print(f"     清理缺失值: 删除了 {removed} 条记录")
                
                if len(df_processed) > 0:
                    province_data.append(df_processed)
                    province_total_count += len(df_processed)
                    
                    # 统计
                    avg_price = df_processed['成交价（万元）'].mean()
                    avg_unit_price = df_processed['成交单价（元）'].mean()
                    print(f"     ✓ 有效数据: {len(df_processed):,} 条")
                    print(f"     ✓ 平均成交价: {avg_price:.2f} 万元")
                    print(f"     ✓ 平均单价: {avg_unit_price:.2f} 元/m²")
                
            except Exception as e:
                print(f"     ❌ 错误: {str(e)}")
                continue
        
        # 合并省份数据
        if province_data:
            province_df = pd.concat(province_data, ignore_index=True)
            
            # 数据清洗
            province_df = clean_data(province_df, province)
            
            if len(province_df) == 0:
                print(f"     ⚠️  警告：{province} 清洗后无有效数据")
                continue
            
            # 保存省份数据
            output_file = os.path.join(output_dir, f'data_{province}_2023_2025.csv')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            province_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            # 统计信息
            stats = {
                'province': province,
                'cities': [c['city'] for c in cities],
                'total_count': int(len(province_df)),
                'avg_price': round(float(province_df['成交价（万元）'].mean()), 2),
                'median_price': round(float(province_df['成交价（万元）'].median()), 2),
                'avg_unit_price': round(float(province_df['成交单价（元）'].mean()), 2),
                'avg_area': round(float(province_df['面积（m²）'].mean()), 2),
                'min_price': round(float(province_df['成交价（万元）'].min()), 2),
                'max_price': round(float(province_df['成交价（万元）'].max()), 2)
            }
            summary_stats[province] = stats
            
            print(f"\n  ✅ {province} 数据处理完成!")
            print(f"     总成交量: {len(province_df):,} 套")
            print(f"     平均成交价: {stats['avg_price']:.2f} 万元")
            print(f"     平均单价: {stats['avg_unit_price']:.2f} 元/m²")
            print(f"     保存到: {output_file}")
            
            all_results.append({
                'province': province,
                'count': len(province_df),
                'output_file': output_file
            })
    
    # 保存汇总统计
    summary_file = os.path.join(output_dir, 'data_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    
    # 打印总结
    print(f"\n{'='*80}")
    print("处理完成!")
    print(f"{'='*80}")
    
    total_records = sum([r['count'] for r in all_results])
    print(f"\n📊 总体统计:")
    print(f"  • 处理省份: {len(all_results)} 个")
    print(f"  • 总数据量: {total_records:,} 条")
    print(f"  • 汇总文件: {summary_file}")
    
    print(f"\n📋 各省数据量:")
    for result in sorted(all_results, key=lambda x: x['count'], reverse=True):
        percentage = (result['count'] / total_records * 100) if total_records > 0 else 0
        print(f"  • {result['province']}: {result['count']:,} 条 ({percentage:.1f}%)")
    
    return all_results, summary_stats

if __name__ == '__main__':
    results, stats = process_all_data()
