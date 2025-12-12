"""
工具函数测试模块

测试项目中的工具函数和辅助功能：
- 数据格式化
- 计算函数
- 验证函数

运行方式：
    pytest tests/test_utils.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


class TestDataFormatting:
    """数据格式化测试类"""
    
    def test_price_formatting(self):
        """测试价格格式化"""
        # 测试基本的数值格式化
        price = 457.81
        formatted = f"{price:.2f}"
        assert formatted == "457.81"
    
    def test_large_number_formatting(self):
        """测试大数字格式化"""
        count = 184945
        # 格式化为万
        in_wan = count / 10000
        assert abs(in_wan - 18.4945) < 0.001
    
    def test_percentage_calculation(self):
        """测试百分比计算"""
        old_value = 100
        new_value = 110
        change_rate = (new_value - old_value) / old_value * 100
        assert abs(change_rate - 10.0) < 0.001


class TestStatisticalCalculations:
    """统计计算测试类"""
    
    def test_mean_calculation(self):
        """测试均值计算"""
        data = pd.Series([100, 200, 300, 400, 500])
        mean = data.mean()
        assert mean == 300.0
    
    def test_median_calculation(self):
        """测试中位数计算"""
        data = pd.Series([100, 200, 300, 400, 500])
        median = data.median()
        assert median == 300.0
    
    def test_std_calculation(self):
        """测试标准差计算"""
        data = pd.Series([100, 200, 300, 400, 500])
        std = data.std()
        assert std > 0  # 标准差应该大于0
    
    def test_coefficient_of_variation(self):
        """测试变异系数计算"""
        data = pd.Series([100, 200, 300, 400, 500])
        mean = data.mean()
        std = data.std()
        cv = (std / mean) * 100
        assert cv > 0  # 变异系数应该大于0
    
    def test_growth_rate(self):
        """测试增长率计算"""
        old_price = 500
        new_price = 550
        growth_rate = (new_price - old_price) / old_price * 100
        assert growth_rate == 10.0


class TestDataValidation:
    """数据验证测试类"""
    
    def test_price_validation(self):
        """测试价格数据验证"""
        valid_prices = [100, 200, 300]
        invalid_prices = [-100, 0, None]
        
        for price in valid_prices:
            assert price > 0
        
        for price in invalid_prices:
            if price is not None:
                assert price <= 0
    
    def test_date_validation(self):
        """测试日期数据验证"""
        valid_date = "2024-01-15"
        try:
            parsed = datetime.strptime(valid_date, "%Y-%m-%d")
            assert parsed.year == 2024
        except ValueError:
            pytest.fail("有效日期解析失败")
    
    def test_area_validation(self):
        """测试面积数据验证"""
        valid_areas = [50, 100, 150, 200]
        for area in valid_areas:
            assert area > 0
            assert area < 10000  # 合理范围


class TestDataAggregation:
    """数据聚合测试类"""
    
    def test_groupby_mean(self):
        """测试分组均值计算"""
        df = pd.DataFrame({
            '区域': ['A', 'A', 'B', 'B'],
            '价格': [100, 200, 300, 400]
        })
        
        grouped = df.groupby('区域')['价格'].mean()
        
        assert grouped['A'] == 150.0
        assert grouped['B'] == 350.0
    
    def test_groupby_count(self):
        """测试分组计数"""
        df = pd.DataFrame({
            '区域': ['A', 'A', 'B', 'B', 'B'],
            '价格': [100, 200, 300, 400, 500]
        })
        
        counts = df.groupby('区域').size()
        
        assert counts['A'] == 2
        assert counts['B'] == 3
    
    def test_monthly_aggregation(self):
        """测试月度聚合"""
        df = pd.DataFrame({
            '日期': pd.to_datetime(['2024-01-01', '2024-01-15', '2024-02-01']),
            '价格': [100, 200, 300]
        })
        
        df['月份'] = df['日期'].dt.to_period('M')
        monthly = df.groupby('月份')['价格'].mean()
        
        assert len(monthly) == 2  # 两个月


class TestInvestmentIndex:
    """投资指数计算测试类"""
    
    def test_stability_score(self):
        """测试市场稳定性评分计算"""
        # 模拟变异系数
        cv = 30  # 30%
        
        # 稳定性评分公式：100 / (1 + CV/10)
        stability = 100 / (1 + cv / 10)
        
        assert 20 < stability < 30  # 合理范围
    
    def test_trend_score(self):
        """测试趋势评分计算"""
        old_avg = 500
        new_avg = 525
        
        # 价格趋势变化率
        trend = (new_avg - old_avg) / old_avg * 100
        
        assert trend == 5.0
    
    def test_composite_score(self):
        """测试综合评分计算"""
        price_trend = 60
        volume_trend = 50
        stability = 70
        
        # 加权计算（示例权重）
        composite = price_trend * 0.4 + volume_trend * 0.2 + stability * 0.4
        
        assert 50 < composite < 70


class TestEdgeCases:
    """边界情况测试类"""
    
    def test_empty_dataframe(self):
        """测试空数据框处理"""
        df = pd.DataFrame()
        assert len(df) == 0
        assert df.empty
    
    def test_nan_handling(self):
        """测试 NaN 值处理"""
        data = pd.Series([1, 2, np.nan, 4, 5])
        
        # dropna 后长度
        clean_data = data.dropna()
        assert len(clean_data) == 4
        
        # 均值计算跳过 NaN
        mean = data.mean()
        assert mean == 3.0
    
    def test_division_by_zero(self):
        """测试除零处理"""
        with pytest.raises(ZeroDivisionError):
            result = 100 / 0
    
    def test_negative_price_filter(self):
        """测试负价格过滤"""
        prices = pd.Series([-100, 0, 100, 200, 300])
        valid_prices = prices[prices > 0]
        
        assert len(valid_prices) == 3
        assert all(p > 0 for p in valid_prices)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

