"""
数据管理器测试模块

测试 DataManager 类的核心功能：
- 配置文件加载
- 城市数据加载
- 数据有效性验证

运行方式：
    pytest tests/test_data_manager.py -v
"""

import pytest
import pandas as pd
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import data_manager


class TestDataManager:
    """数据管理器测试类"""
    
    def test_config_loaded(self):
        """测试配置文件是否正确加载"""
        cities = data_manager.get_enabled_cities()
        assert cities is not None, "城市配置不应为空"
        assert len(cities) > 0, "至少应有一个城市配置"
    
    def test_city_names(self):
        """测试城市名称配置"""
        cities = data_manager.get_enabled_cities()
        city_names_en = [city['name_en'] for city in cities]
        
        # 验证至少包含一个预期城市
        expected_cities = ['beijing', 'wuhan', 'xiamen']
        for expected in expected_cities:
            if expected in city_names_en:
                assert True
                return
        
        # 如果没有预期城市，至少确认有城市数据
        assert len(city_names_en) > 0, "应至少有一个城市"
    
    def test_load_city_data(self):
        """测试城市数据加载"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        # 加载第一个城市的数据
        city = cities[0]
        df = data_manager.load_city_data(city['name_en'])
        
        assert df is not None, f"城市 {city['name']} 数据加载失败"
        assert len(df) > 0, f"城市 {city['name']} 数据为空"
    
    def test_data_columns(self):
        """测试数据字段完整性"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None:
            pytest.skip("数据加载失败")
        
        # 必须字段
        required_columns = ['成交价（万元）', '区域']
        
        for col in required_columns:
            assert col in df.columns, f"缺少必须字段: {col}"
    
    def test_data_types(self):
        """测试数据类型正确性"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None:
            pytest.skip("数据加载失败")
        
        # 检查成交价是数值类型
        if '成交价（万元）' in df.columns:
            assert pd.api.types.is_numeric_dtype(df['成交价（万元）']), \
                "成交价应为数值类型"
    
    def test_data_no_all_null(self):
        """测试数据不全为空值"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None:
            pytest.skip("数据加载失败")
        
        # 检查至少有一行有效数据
        assert not df.empty, "数据不应为空"


class TestDataStatistics:
    """数据统计测试类"""
    
    def test_price_range(self):
        """测试价格数据范围合理性"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None or '成交价（万元）' not in df.columns:
            pytest.skip("数据不可用")
        
        prices = df['成交价（万元）'].dropna()
        
        # 价格应该是正数
        assert prices.min() > 0, "价格应大于0"
        # 价格应该在合理范围（0-10000万）
        assert prices.max() < 10000, "价格应在合理范围内"
    
    def test_district_diversity(self):
        """测试区域多样性"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None or '区域' not in df.columns:
            pytest.skip("数据不可用")
        
        districts = df['区域'].dropna().unique()
        
        # 应该有多个区域
        assert len(districts) >= 2, "应至少有2个区域"
    
    def test_mean_price_calculation(self):
        """测试平均价格计算"""
        cities = data_manager.get_enabled_cities()
        
        if len(cities) == 0:
            pytest.skip("没有可用的城市数据")
        
        df = data_manager.load_city_data(cities[0]['name_en'])
        
        if df is None or '成交价（万元）' not in df.columns:
            pytest.skip("数据不可用")
        
        mean_price = df['成交价（万元）'].mean()
        
        # 平均价格应该是有效数值
        assert pd.notna(mean_price), "平均价格计算应有效"
        assert mean_price > 0, "平均价格应大于0"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

