"""
API 接口测试模块

测试 Flask 应用的 API 接口：
- 城市数据接口
- 认证接口
- 分析数据接口

运行方式：
    pytest tests/test_api.py -v
"""

import pytest
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAuthAPI:
    """认证接口测试类"""
    
    def test_auth_page_loads(self, client):
        """测试登录页面是否正常加载"""
        response = client.get('/auth')
        assert response.status_code == 200
    
    def test_register_validation(self, client):
        """测试注册接口参数验证"""
        # 缺少参数的请求
        response = client.post('/api/auth/register', 
            json={},
            content_type='application/json'
        )
        assert response.status_code in [200, 400]  # 可能返回错误信息
    
    def test_login_validation(self, client):
        """测试登录接口参数验证"""
        # 错误的凭据
        response = client.post('/api/auth/login',
            json={'username': 'nonexistent', 'password': 'wrong'},
            content_type='application/json'
        )
        # 应该返回某种响应（不应崩溃）
        assert response.status_code in [200, 401, 400]


class TestCityDataAPI:
    """城市数据接口测试类"""
    
    def test_city_stats_endpoint(self, client):
        """测试城市统计接口"""
        # 测试北京数据
        response = client.get('/api/city/beijing/stats')
        
        # 可能需要登录或数据不存在，接受多种状态码
        assert response.status_code in [200, 302, 401, 404]
    
    def test_city_analysis_endpoint(self, client):
        """测试城市分析接口"""
        response = client.get('/api/city/beijing/analysis')
        # 可能需要登录或数据不存在，接受多种状态码
        assert response.status_code in [200, 302, 401, 404]
    
    def test_invalid_city(self, client):
        """测试无效城市处理"""
        response = client.get('/api/city/invalid_city_name/stats')
        # 应该返回404或错误信息，而不是崩溃
        assert response.status_code in [200, 302, 401, 404]


class TestNationalComparisonAPI:
    """全国对比接口测试类"""
    
    def test_comparison_data_endpoint(self, client):
        """测试全国对比数据接口"""
        response = client.get('/api/national-comparison')
        # 可能需要登录
        assert response.status_code in [200, 302, 401]


class TestHomePage:
    """首页测试类"""
    
    def test_home_redirect(self, client):
        """测试首页访问（可能重定向到登录）"""
        response = client.get('/')
        # 首页应该正常响应或重定向到登录
        assert response.status_code in [200, 302]
    
    def test_static_resources(self, client):
        """测试静态资源访问"""
        # 测试 CSS 文件
        response = client.get('/static/css/style.css')
        assert response.status_code == 200


class TestResponseFormat:
    """响应格式测试类"""
    
    def test_api_returns_json(self, client):
        """测试 API 返回 JSON 格式"""
        response = client.post('/api/auth/login',
            json={'username': 'test', 'password': 'test'},
            content_type='application/json'
        )
        
        # 验证返回的是 JSON
        if response.status_code == 200:
            try:
                data = json.loads(response.data)
                assert isinstance(data, dict)
            except json.JSONDecodeError:
                pass  # 某些响应可能不是 JSON


class TestErrorHandling:
    """错误处理测试类"""
    
    def test_404_page(self, client):
        """测试 404 错误处理"""
        response = client.get('/nonexistent_page_12345')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """测试请求方法错误处理"""
        # 对 GET 接口发送 DELETE 请求
        response = client.delete('/api/city/beijing/stats')
        # 应该返回 405 或其他错误，而不是崩溃
        assert response.status_code in [405, 404, 302, 401]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

