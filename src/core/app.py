"""
AI 驱动的智能房价分析系统 - Flask 主应用

本模块是系统的核心入口，负责：
1. Flask 应用初始化和配置
2. 数据管理器初始化
3. AI 模块集成（对话、分析、预测、图像生成）
4. 用户认证和会话管理
5. API 路由定义

主要组件：
- DataManager: 城市房价数据管理
- AIAssistant: AI 对话助手
- PricePredictor: 房价预测引擎
- AIImageGenerator: AI 图像生成
- StrategyAnalyzer: 购房策略分析

技术栈：
- Flask 3.1.2: Web 框架
- Pandas 2.3.3: 数据处理
- SQLite: 用户数据存储
- DeepSeek-V3: AI 大语言模型

作者: Python 课程大作业
日期: 2024-2025
"""

from flask import Flask, render_template, jsonify, request, Response, stream_with_context, session, redirect, url_for
import pandas as pd
import json
import os
import logging
import sqlite3
import hashlib
from datetime import datetime
from functools import wraps

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai.ai_assistant import AIAssistant
from src.analysis.housing_analyzer import HousingAnalyzer
from src.analysis.national_comparator import NationalComparator
from src.ai.intelligent_analyzer import IntelligentAnalyzer
from src.ai.strategy_analyzer import StrategyAnalyzer
from src.ai.ai_image_generator import AIImageGenerator
from src.analysis.price_predictor import PricePredictor

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
app = Flask(__name__, 
            template_folder=str(PROJECT_ROOT / 'templates'),
            static_folder=str(PROJECT_ROOT / 'static'))

# Session配置
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production-2024')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时

# ============== SQLite 数据库配置 ==============
DATABASE = str(PROJECT_ROOT / 'users.db')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

def hash_password(password):
    """密码哈希（简单版，生产环境建议使用 bcrypt）"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash

# 初始化数据库
init_db()

# ============== AI 配置（使用环境变量）==============
AI_CONFIG = {
    'api_url': os.getenv('AI_API_URL', 'https://api.siliconflow.cn/v1'),
    'api_key': os.getenv('DEEPSEEK_API_KEY', ''),  # 从环境变量读取，默认为空
    'model': os.getenv('AI_MODEL', 'deepseek-ai/DeepSeek-V3')
}

# 检查 API Key 是否配置
if not AI_CONFIG['api_key']:
    logger.warning("⚠️ 警告: DEEPSEEK_API_KEY 环境变量未设置，AI 功能将不可用")
    logger.warning("请设置环境变量: export DEEPSEEK_API_KEY='your-api-key'")

# 初始化 AI 助手
ai_assistant = AIAssistant(
    api_url=AI_CONFIG['api_url'],
    api_key=AI_CONFIG['api_key'],
    model=AI_CONFIG['model']
)

# 初始化智能分析器
intelligent_analyzer = IntelligentAnalyzer(
    api_url=AI_CONFIG['api_url'],
    api_key=AI_CONFIG['api_key'],
    model=AI_CONFIG['model']
)

# 初始化策略分析器
strategy_analyzer = StrategyAnalyzer(ai_assistant)

# 初始化AI图像生成器
ai_image_generator = AIImageGenerator(
    api_key=AI_CONFIG['api_key'],
    api_url=AI_CONFIG['api_url']
)

class DataManager:
    """数据管理器：负责加载和管理城市数据"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = str(PROJECT_ROOT / 'src' / 'core' / 'config.json')
        self.config_path = config_path
        self.config = self.load_config()
        self.data_cache = {}
        
    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def reload_config(self):
        """重新加载配置（用于动态添加城市）"""
        self.config = self.load_config()
        self.data_cache = {}  # 清空缓存
    
    def get_enabled_provinces(self):
        """获取启用的省份列表"""
        return [province for province in self.config.get('provinces', []) if province['enabled']]
    
    def get_enabled_cities(self):
        """获取启用的城市列表（兼容旧版本）"""
        # 如果配置中有provinces，返回provinces
        if 'provinces' in self.config:
            return self.get_enabled_provinces()
        # 否则返回cities（兼容旧版本）
        return [city for city in self.config.get('cities', []) if city['enabled']]
    
    def load_city_data(self, province_name_en):
        """加载指定省份/城市的数据"""
        # 检查缓存
        if province_name_en in self.data_cache:
            return self.data_cache[province_name_en]
        
        # 查找省份配置（兼容新旧版本）
        province_config = None
        config_list = self.config.get('provinces', self.config.get('cities', []))
        
        for item in config_list:
            if item['name_en'] == province_name_en and item['enabled']:
                province_config = item
                break
        
        if not province_config:
            return None
        
        # 加载数据
        data_dir = self.config.get('data_directory', str(PROJECT_ROOT / 'data' / 'processed'))
        data_path = os.path.join(data_dir, province_config['data_file'])
        if not os.path.exists(data_path):
            return None
        
        df = pd.read_csv(data_path, encoding='utf-8-sig')
        df['成交日期'] = pd.to_datetime(df['成交日期'])
        
        # 缓存数据
        self.data_cache[province_name_en] = df
        return df
    
    def get_city_statistics(self, province_name_en):
        """获取省份/城市统计数据"""
        df = self.load_city_data(province_name_en)
        if df is None or len(df) == 0:
            return None
        
        # 按年份统计
        df['年份'] = df['成交日期'].dt.year
        yearly_stats = []
        
        for year in sorted(df['年份'].unique()):
            year_data = df[df['年份'] == year]
            yearly_stats.append({
                'year': int(year),
                'count': int(len(year_data)),
                'avg_price': round(float(year_data['成交价（万元）'].mean()), 2),
                'avg_unit_price': round(float(year_data['成交单价（元）'].mean()), 2),
                'total_volume': round(float(year_data['成交价（万元）'].sum()), 2),
                'avg_area': round(float(year_data['面积（m²）'].mean()), 2)
            })
        
        # 按月份统计（用于趋势图）
        df['年月'] = df['成交日期'].dt.to_period('M').astype(str)
        monthly_stats = df.groupby('年月').agg({
            '成交价（万元）': 'mean',
            '成交单价（元）': 'mean',
            '面积（m²）': 'count'
        }).reset_index()
        
        monthly_data = []
        for _, row in monthly_stats.iterrows():
            monthly_data.append({
                'month': row['年月'],
                'avg_price': round(float(row['成交价（万元）']), 2),
                'avg_unit_price': round(float(row['成交单价（元）']), 2),
                'count': int(row['面积（m²）'])
            })
        
        # 区域统计（包含城市信息）
        # 先检查是否有城市字段
        if '城市' in df.columns:
            # 按城市和区域分组
            district_stats = df.groupby(['城市', '区域']).agg({
                '成交价（万元）': 'mean',
                '成交单价（元）': 'mean',
                '面积（m²）': 'count'
            }).reset_index().sort_values('成交单价（元）', ascending=False).head(10)
            
            district_data = []
            for _, row in district_stats.iterrows():
                # 格式化显示：城市 - 区域
                district_label = f"{row['城市']} - {row['区域']}" if pd.notna(row['城市']) else row['区域']
                district_data.append({
                    'district': district_label,
                    'city': row['城市'] if pd.notna(row['城市']) else '',
                    'area': row['区域'],
                    'avg_price': round(float(row['成交价（万元）']), 2),
                    'avg_unit_price': round(float(row['成交单价（元）']), 2),
                    'count': int(row['面积（m²）'])
                })
        else:
            # 兼容旧数据格式（没有城市字段）
            district_stats = df.groupby('区域').agg({
                '成交价（万元）': 'mean',
                '成交单价（元）': 'mean',
                '面积（m²）': 'count'
            }).reset_index().sort_values('成交单价（元）', ascending=False).head(10)
            
            district_data = []
            for _, row in district_stats.iterrows():
                district_data.append({
                    'district': row['区域'],
                    'city': '',
                    'area': row['区域'],
                    'avg_price': round(float(row['成交价（万元）']), 2),
                    'avg_unit_price': round(float(row['成交单价（元）']), 2),
                    'count': int(row['面积（m²）'])
                })
        
        # 总体统计
        overall_stats = {
            'total_count': int(len(df)),
            'avg_price': round(float(df['成交价（万元）'].mean()), 2),
            'median_price': round(float(df['成交价（万元）'].median()), 2),
            'avg_unit_price': round(float(df['成交单价（元）'].mean()), 2),
            'median_unit_price': round(float(df['成交单价（元）'].median()), 2),
            'avg_area': round(float(df['面积（m²）'].mean()), 2),
            'min_price': round(float(df['成交价（万元）'].min()), 2),
            'max_price': round(float(df['成交价（万元）'].max()), 2)
        }
        
        return {
            'overall': overall_stats,
            'yearly': yearly_stats,
            'monthly': monthly_data,
            'district': district_data
        }

# 初始化数据管理器
data_manager = DataManager()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function

# 认证相关路由
@app.route('/auth')
def auth_page():
    """登录/注册页面"""
    # 如果已登录，跳转到首页
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('auth.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    # 验证
    if not username or not password or not role:
        return jsonify({'success': False, 'error': '请填写完整信息'})
    
    # 检查用户名是否已存在
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': '用户名已存在'})
    
    # 保存用户到数据库（密码哈希存储）
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, hash_password(password), role)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        logger.error(f"注册失败: {str(e)}")
        return jsonify({'success': False, 'error': '注册失败，请重试'})
    
    # 自动登录
    session['user'] = {
        'username': username,
        'role': role
    }
    session.permanent = True
    
    logger.info(f"用户注册成功: {username}, 角色: {role}")
    return jsonify({'success': True})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '请填写完整信息'})
    
    # 从数据库验证用户
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username, password_hash, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'error': '用户名不存在'})
    
    if not verify_password(password, user['password_hash']):
        return jsonify({'success': False, 'error': '密码错误'})
    
    # 登录成功
    session['user'] = {
        'username': user['username'],
        'role': user['role']
    }
    session.permanent = True
    
    logger.info(f"用户登录成功: {username}")
    return jsonify({'success': True})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/auth/current-user')
def get_current_user():
    """获取当前用户信息"""
    if 'user' in session:
        return jsonify({'success': True, 'user': session['user']})
    return jsonify({'success': False})

@app.route('/')
@login_required
def index():
    """主页"""
    provinces = data_manager.get_enabled_provinces()
    user = session.get('user', {})
    
    # 计算总数据量和每个省份的数据量
    total_records = 0
    province_data_stats = []
    
    for province in provinces:
        try:
            df = data_manager.load_city_data(province['name_en'])
            if df is not None:
                province_count = len(df)
                total_records += province_count
                province_data_stats.append({
                    'name': province['name'],
                    'name_en': province['name_en'],
                    'count': province_count,
                    'icon': province.get('icon', '🏙️')
                })
            else:
                province_data_stats.append({
                    'name': province['name'],
                    'name_en': province['name_en'],
                    'count': 0,
                    'icon': province.get('icon', '🏙️')
                })
        except Exception as e:
            logger.warning(f"加载 {province['name']} 数据失败: {e}")
            province_data_stats.append({
                'name': province['name'],
                'name_en': province['name_en'],
                'count': 0,
                'icon': province.get('icon', '🏙️')
            })
    
    # 计算占比
    for province_stat in province_data_stats:
        if total_records > 0:
            province_stat['percentage'] = round((province_stat['count'] / total_records) * 100, 1)
        else:
            province_stat['percentage'] = 0
    
    # 格式化数据量（以万为单位）
    total_records_display = f"{int(total_records / 10000)}万+" if total_records >= 10000 else str(total_records)
    
    return render_template('home.html', cities=provinces, user=user, active_page='home', 
                         total_records=total_records_display, city_count=len(provinces),
                         city_data_stats=province_data_stats)

@app.route('/api/cities')
def get_cities():
    """获取城市列表"""
    cities = data_manager.get_enabled_cities()
    return jsonify({'cities': cities})

@app.route('/api/city/<city_name_en>/statistics')
def get_city_statistics(city_name_en):
    """获取城市统计数据"""
    stats = data_manager.get_city_statistics(city_name_en)
    if stats is None:
        return jsonify({'error': '数据未找到'}), 404
    return jsonify(stats)

@app.route('/api/reload')
def reload_data():
    """重新加载配置和数据"""
    data_manager.reload_config()
    return jsonify({'message': '配置已重新加载'})

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI 助手聊天接口"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': '缺少消息内容'}), 400
    
    user_message = data['message']
    city_name_en = data.get('city')
    
    # 获取城市数据（如果指定了城市）
    city_data = None
    if city_name_en:
        stats = data_manager.get_city_statistics(city_name_en)
        if stats:
            # 查找城市中文名
            city_name = None
            for city in data_manager.get_enabled_cities():
                if city['name_en'] == city_name_en:
                    city_name = city['name']
                    break
            
            city_data = {
                'city_name': city_name or city_name_en,
                **stats
            }
    
    # 调用 AI 助手
    result = ai_assistant.chat(user_message, city_data)
    
    return jsonify(result)

@app.route('/api/ai/chat-stream', methods=['POST'])
def ai_chat_stream():
    """AI 助手聊天接口（流式）"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': '缺少消息内容'}), 400
    
    user_message = data['message']
    city_name_en = data.get('city')
    
    # 获取用户角色
    user = session.get('user', {})
    role = user.get('role', 'investment_advisor')
    
    # 获取全局数据概览
    global_data = data.get('global_data')
    
    # 获取城市数据（如果指定了城市）
    city_data = None
    if city_name_en:
        stats = data_manager.get_city_statistics(city_name_en)
        if stats:
            # 查找城市中文名
            city_name = None
            for city in data_manager.get_enabled_cities():
                if city['name_en'] == city_name_en:
                    city_name = city['name']
                    break
            
            city_data = {
                'city_name': city_name or city_name_en,
                **stats
            }
    
    # 合并全局数据和城市数据
    context_data = {}
    if global_data:
        context_data['global_data'] = global_data
    if city_data:
        context_data['city_data'] = city_data
    
    def generate():
        try:
            # 调用 AI 助手的流式方法（传递用户角色）
            for chunk in ai_assistant.chat_stream(user_message, context_data if context_data else None, role=role):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

# ==================== AI 图像生成 API ====================

@app.route('/api/ai/generate-image', methods=['POST'])
@login_required
def generate_image():
    """AI 创意图像生成接口"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': '缺少参数'}), 400
    
    image_type = data.get('type', 'dream_home')
    city_name = data.get('city', '北京')  # 直接使用中文城市名
    style = data.get('style', 'modern')
    tags = data.get('tags', [])
    custom_prompt = data.get('custom_prompt', '')
    
    try:
        if image_type == 'dream_home':
            # 🏠 梦想之家 - 根据用户画像生成
            user_profile = {
                'budget': data.get('budget', 500),
                'preferred_area': data.get('area', 100),
                'style': style,
                'family_type': data.get('family', 'young_couple'),
                'city': city_name,
                'tags': tags,
                'custom_prompt': custom_prompt
            }
            result = ai_image_generator.generate_dream_home(user_profile)
            
        elif image_type == 'neighborhood':
            # 🏘️ 社区愿景图
            district = data.get('district', '朝阳区')
            features = tags if tags else ['公园', '商场', '学校', '地铁']
            result = ai_image_generator.generate_neighborhood_vision(district, city_name, features)
            
        elif image_type == 'lifestyle':
            # 🌟 生活方式场景
            lifestyle = data.get('lifestyle', 'family_morning')
            result = ai_image_generator.generate_lifestyle_scene(lifestyle, city_name)
            
        elif image_type == 'renovation':
            # 🔨 装修效果图
            room = data.get('room', 'living_room')
            result = ai_image_generator.generate_before_after_renovation(room, style)
            
        elif image_type == 'investment':
            # 📈 投资故事
            scenario = data.get('scenario', 'rental_income')
            result = ai_image_generator.generate_investment_story(scenario, city_name)
            
        elif image_type == 'seasonal':
            # 🌸 季节氛围
            season = data.get('season', 'autumn')
            home_type = data.get('home_type', 'modern apartment')
            result = ai_image_generator.generate_seasonal_home(season, home_type)
            
        elif image_type == 'custom':
            # 自定义提示词
            prompt = data.get('prompt', f'{city_name}的温馨家庭生活')
            result = ai_image_generator.generate_image(prompt)
        else:
            return jsonify({'success': False, 'error': '不支持的图像类型'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"图像生成错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/quick-answer', methods=['POST'])
def ai_quick_answer():
    """AI 快速回答接口"""
    data = request.get_json()
    
    if not data or 'type' not in data or 'city' not in data:
        return jsonify({'error': '缺少参数'}), 400
    
    question_type = data['type']
    city_name_en = data['city']
    
    # 获取城市数据
    stats = data_manager.get_city_statistics(city_name_en)
    if not stats:
        return jsonify({'error': '城市数据未找到'}), 404
    
    # 查找城市中文名
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    city_data = {
        'city_name': city_name or city_name_en,
        **stats
    }
    
    # 获取快速回答
    answer = ai_assistant.get_quick_answer(question_type, city_data)
    
    return jsonify({'success': True, 'message': answer})

@app.route('/api/ai/clear-history', methods=['POST'])
def ai_clear_history():
    """清空 AI 对话历史"""
    ai_assistant.clear_history()
    return jsonify({'success': True, 'message': '对话历史已清空'})

@app.route('/analysis/<city_name_en>')
@login_required
def analysis_page(city_name_en):
    """专业分析报告页面"""
    # 查找城市信息
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    if not city_name:
        return "城市未找到", 404
    
    user = session.get('user', {})
    return render_template('analysis.html', city_name=city_name, city_name_en=city_name_en, user=user, active_page=f'analysis_{city_name_en}')

@app.route('/analysis-simple/<city_name_en>')
def analysis_simple_page(city_name_en):
    """简化测试页面"""
    # 查找城市信息
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    if not city_name:
        return "城市未找到", 404
    
    return render_template('analysis_simple.html', city_name=city_name, city_name_en=city_name_en)

@app.route('/api/city/<city_name_en>/deep-analysis')
def get_deep_analysis(city_name_en):
    """获取城市深度分析数据"""
    import numpy as np
    
    # 加载城市数据
    df = data_manager.load_city_data(city_name_en)
    if df is None or len(df) == 0:
        return jsonify({'error': '数据未找到'}), 404
    
    # 查找城市中文名
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    # 创建分析器并进行分析
    analyzer = HousingAnalyzer(df, city_name or city_name_en)
    analysis_result = analyzer.get_comprehensive_analysis()
    
    # 将NaN和Infinity转换为None
    cleaned_result = clean_data(analysis_result)
    
    return jsonify({
        'success': True,
        'city': city_name or city_name_en,
        'analysis': cleaned_result
    })

@app.route('/national-comparison')
@login_required
def national_comparison():
    """全国对比分析页面"""
    cities = data_manager.get_enabled_cities()
    user = session.get('user', {})
    return render_template('national_comparison.html', cities=cities, user=user, active_page='national')

@app.route('/api/national-comparison')
def get_national_comparison():
    """获取全国对比分析数据"""
    import numpy as np
    
    # 加载所有启用的城市数据
    cities_data = {}
    for city in data_manager.get_enabled_cities():
        df = data_manager.load_city_data(city['name_en'])
        if df is not None and len(df) > 0:
            cities_data[city['name']] = df
    
    if not cities_data:
        return jsonify({'error': '没有可用的城市数据'}), 404
    
    # 创建对比分析器
    comparator = NationalComparator(cities_data)
    comparison_result = comparator.get_comprehensive_comparison()
    
    # 清理数据
    cleaned_result = clean_data(comparison_result)
    
    return jsonify({
        'success': True,
        'comparison': cleaned_result
    })

@app.route('/api/national-comparison/ai-overview')
def get_national_ai_overview():
    """获取全国对比的AI智能概览分析"""
    # 加载所有启用的城市数据
    cities_data = {}
    for city in data_manager.get_enabled_cities():
        df = data_manager.load_city_data(city['name_en'])
        if df is not None and len(df) > 0:
            cities_data[city['name']] = df
    
    if not cities_data:
        return jsonify({'error': '没有可用的城市数据'}), 404
    
    # 创建对比分析器
    comparator = NationalComparator(cities_data)
    comparison_result = comparator.get_comprehensive_comparison()
    
    # 使用AI生成概览分析
    ai_overview = intelligent_analyzer.analyze_national_overview(comparison_result)
    
    return jsonify({
        'success': True,
        'ai_overview': ai_overview
    })

@app.route('/api/national-comparison/ai-overview-stream')
def get_national_ai_overview_stream():
    """获取全国对比的AI智能概览分析（流式）"""
    # 在generate()外部获取role参数
    role = request.args.get('role', 'investment_advisor')
    
    def generate():
        try:
            # 加载所有启用的城市数据
            cities_data = {}
            for city in data_manager.get_enabled_cities():
                df = data_manager.load_city_data(city['name_en'])
                if df is not None and len(df) > 0:
                    cities_data[city['name']] = df
            
            if not cities_data:
                yield f"data: {json.dumps({'error': '没有可用的城市数据'})}\n\n"
                return
            
            # 创建对比分析器
            comparator = NationalComparator(cities_data)
            comparison_result = comparator.get_comprehensive_comparison()
            
            # 构建prompt（根据角色定制）
            overview = comparison_result.get('overview', {})
            price_comp = comparison_result.get('price_comparison', {})
            growth = comparison_result.get('growth_rates', {})
            investment = comparison_result.get('investment_scores', {})
            
            # 基础数据（所有角色共用）
            base_data = f"""**市场概况：**
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
- 最差表现：{growth.get('worst_performer', '')} ({growth.get('worst_growth_rate', 0)}%)"""
            
            # 根据角色定制prompt
            if role == 'first_time_buyer':
                # 首次购房者：通俗语言，关注哪里适合买
                prompt = f"""请分析全国房价对比数据，用通俗易懂的语言（就像跟朋友聊天）告诉首次购房者：

{base_data}

请用3-4段话（每段70-90字）说明：

1. **各城市房价差别大不大？**（哪个城市最贵？哪个最便宜？相差多少倍？）
2. **哪些城市房价在涨？哪些在跌？**（最近表现好的和不好的城市）
3. **首次购房者适合在哪里买？**（价格合理、稳定的城市推荐）
4. **要注意什么？**（不同城市买房的风险和建议）

要求：
- 不要用"投资"、"ROI"等专业词
- 用"房价稳不稳定"代替"市场波动"
- 用"价格合理"代替"投资价值"
- 总共不超过320字"""
            
            elif role == 'upgrader':
                # 改善型购房者：换房视角，哪里适合换房
                prompt = f"""请从换房者视角分析全国房价对比数据：

{base_data}

请用3-4段话（每段80-100字）分析：

1. **市场分化情况**（城市间差异大不大？对换房有什么影响？）
2. **换房机会分析**（哪些城市适合卖旧房？哪些适合买新房？）
3. **跨城换房建议**（要不要考虑换个城市？哪里性价比高？）
4. **时机与策略**（现在是换房的好时机吗？要注意什么？）

要求：平衡专业性和实用性，每段80-100字，总共不超过350字"""
            
            else:  # investment_advisor
                # 投资顾问：专业投资分析
                prompt = f"""请分析全国房价对比数据，用专业视角评估投资价值：

{base_data}

**投资价值排名：**
{json.dumps(investment.get('scores', [])[:3], ensure_ascii=False, indent=2)}

请用3-4段专业分析（每段80-100字）：

1. **市场整体特征**（城市分化程度、价格梯队、投资机会分布）
2. **增长趋势研判**（哪些城市表现好/差？背后的逻辑和驱动因素？）
3. **投资价值评估**（基于数据推荐投资城市，分析ROI和风险）
4. **投资建议**（配置策略、入市时机、风险控制）

要求：使用专业术语，数据支撑，每段80-100字，总共不超过350字"""
            
            # 流式生成（使用ai_assistant的角色系统）
            for chunk in ai_assistant.chat_stream(prompt, None, role=role):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/city/<city_name_en>/ai-overview')
def get_city_ai_overview(city_name_en):
    """获取单城市的AI智能概览分析"""
    df = data_manager.load_city_data(city_name_en)
    if df is None or len(df) == 0:
        return jsonify({'error': '数据未找到'}), 404
    
    # 查找城市中文名
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    # 创建分析器并进行分析
    analyzer = HousingAnalyzer(df, city_name or city_name_en)
    analysis_result = analyzer.get_comprehensive_analysis()
    
    # 使用AI生成概览分析
    ai_overview = intelligent_analyzer.analyze_city_overview(
        city_name or city_name_en, 
        analysis_result
    )
    
    return jsonify({
        'success': True,
        'ai_overview': ai_overview
    })

@app.route('/api/city/<city_name_en>/ai-overview-stream')
def get_city_ai_overview_stream(city_name_en):
    """获取单城市的AI智能概览分析（流式）"""
    # 在generate()外部获取role参数
    role = request.args.get('role', 'investment_advisor')
    
    def generate():
        try:
            df = data_manager.load_city_data(city_name_en)
            if df is None or len(df) == 0:
                yield f"data: {json.dumps({'error': '数据未找到'})}\n\n"
                return
            
            # 查找城市中文名
            city_name = None
            for city in data_manager.get_enabled_cities():
                if city['name_en'] == city_name_en:
                    city_name = city['name']
                    break
            
            # 创建分析器并进行分析
            analyzer = HousingAnalyzer(df, city_name or city_name_en)
            analysis_result = analyzer.get_comprehensive_analysis()
            
            # 构建prompt（根据角色定制）
            basic = analysis_result.get('basic_stats', {})
            investment = analysis_result.get('investment_index', {})
            volatility = analysis_result.get('volatility', {})
            
            # 基础数据部分（所有角色共用）
            base_data = f"""**{city_name or city_name_en}房价数据（2023-2025年）：**
- 总成交量：{basic.get('total_transactions', 0)}套
- 平均价格：{basic.get('price', {}).get('mean', 0):.2f}万元
- 平均单价：{basic.get('unit_price', {}).get('mean', 0):.2f}元/m²
- 平均面积：{basic.get('area', {}).get('mean', 0):.2f}m²
- 价格波动范围：{volatility.get('price_range', 0):.2f}万元
- 稳定性等级：{volatility.get('stability_level', '')}"""
            
            # 根据角色定制prompt
            if role == 'first_time_buyer':
                # 首次购房者：不提投资，关注实用性
                prompt = f"""{base_data}

请用通俗易懂的语言（就像跟朋友聊天一样），用2-3段话告诉首次购房者：

1. **价格水平**：这个城市的房价在什么水平？贵不贵？是高端还是普通住宅为主？
2. **是否适合买**：现在适合买房吗？价格稳不稳定？要不要再等等？
3. **注意事项**：买房时要特别注意什么？有什么风险或陷阱需要警惕？

要求：
- 不要用"投资"、"ROI"、"流动性"这些专业词汇
- 用"房子稳不稳定"代替"市场波动率"
- 用"价格合理"代替"投资价值"
- 每段50-70字，亲切友好，总共不超过220字"""
            
            elif role == 'upgrader':
                # 改善型购房者：关注换房策略
                prompt = f"""{base_data}

**投资指标：**
- 综合评分：{investment.get('index_score', 0):.1f}分
- 投资等级：{investment.get('investment_level', '')}
- 市场稳定性：{investment.get('stability_score', 0):.1f}分

请从换房者视角，用2-3段话分析：

1. **换房时机**：当前市场适合卖旧房还是买新房？是先卖后买还是先买后卖？
2. **市场行情**：价格趋势如何？对换房有利还是不利？要把握什么时机？
3. **资金建议**：换房要准备多少资金？税费成本如何？有什么省钱技巧？

要求：平衡专业性和实用性，每段60-80字，总共不超过250字"""
            
            else:  # investment_advisor（默认）
                # 投资顾问：专业分析
                prompt = f"""{base_data}

**投资指数：**
- 综合评分：{investment.get('index_score', 0):.1f}分
- 投资等级：{investment.get('investment_level', '')}
- 市场稳定性评分：{investment.get('stability_score', 0):.1f}分
- 变异系数：{volatility.get('coefficient_of_variation', 0):.2f}%

请用专业视角，用2-3段话分析：

1. **市场定位**：高端/中端/经济型，价格水平如何？目标客群是谁？
2. **投资价值**：ROI如何？流动性怎样？适合长持还是短炒？投资风险等级？
3. **投资建议**：当前是买入、观望还是不建议？给出明确的投资建议和理由。

要求：使用专业术语，数据支撑，每段60-80字，总共不超过250字"""
            
            # 流式生成（使用ai_assistant的角色系统，role通过闭包访问）
            for chunk in ai_assistant.chat_stream(prompt, None, role=role):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/ai-analyze-chart', methods=['POST'])
def ai_analyze_chart():
    """AI分析图表数据"""
    data = request.json
    chart_type = data.get('chart_type', '')
    chart_data = data.get('chart_data', {})
    context = data.get('context', '')
    
    # 使用AI分析图表
    analysis = intelligent_analyzer.analyze_chart(chart_type, chart_data, context)
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/api/ai/quick-insight-stream/<city_name_en>', methods=['GET'])
def quick_insight_stream(city_name_en):
    """一键AI洞察 - 流式返回整体分析"""
    # ✅ 在generate()外部获取role参数
    role = request.args.get('role', 'investment_advisor')
    
    def generate():
        try:
            
            # 获取城市DataFrame和中文名
            df = data_manager.load_city_data(city_name_en)
            if df is None or len(df) == 0:
                yield f"data: {json.dumps({'error': '城市数据未找到'}, ensure_ascii=False)}\n\n"
                return
                
            city_name = next((city['name'] for city in data_manager.get_enabled_cities() if city['name_en'] == city_name_en), city_name_en)
            
            # 创建分析器并获取数据
            analyzer = HousingAnalyzer(df, city_name)
            analysis_data = analyzer.get_comprehensive_analysis()
            
            # 根据角色构建不同的分析报告prompt
            # 基础数据（所有角色共用）
            base_data = f"""
## 基本市场数据
- 平均成交价: {analysis_data['basic_stats']['price']['mean']}万元
- 中位数价格: {analysis_data['basic_stats']['price']['median']}万元
- 价格区间: {analysis_data['basic_stats']['price']['min']}-{analysis_data['basic_stats']['price']['max']}万元
- 总成交量: {analysis_data['basic_stats']['total_transactions']}套
- 月均成交量: {analysis_data['market_activity']['monthly_average']}套

## 价格趋势
- 整体趋势: {analysis_data['price_trend']['overall_trend']['trend_direction']}
- 总体变化: {analysis_data['price_trend']['overall_trend']['total_change_percent']}%
- 起始价格: {analysis_data['price_trend']['overall_trend']['first_price']}万元 ({analysis_data['price_trend']['overall_trend']['first_month']})
- 当前价格: {analysis_data['price_trend']['overall_trend']['last_price']}万元 ({analysis_data['price_trend']['overall_trend']['last_month']})

## 市场稳定性
- 稳定性等级: {analysis_data['volatility']['stability_level']}
- 价格波动幅度: {analysis_data['volatility']['price_range']}万元

## 主流户型
- 主流面积段: {analysis_data['area_analysis']['main_category']}
- 占比: {analysis_data['area_analysis']['main_percentage']}%
"""
            
            if role == 'first_time_buyer':
                # 首次购房者：不提投资，关注实用性
                context = f"""请为首次购房者提供{city_name}的购房分析报告，用通俗易懂的语言。

{base_data}

# 请提供以下分析（用大白话，就像跟朋友聊天）

1. **这个城市房价怎么样？**（2-3段，每段80-100字）
   - 房价是贵还是便宜？属于什么档次？
   - 大部分房子卖多少钱？（讲讲价格范围）
   - 跟我的预算合适吗？

2. **现在适合买房吗？**（2-3段）
   - 房价是涨还是跌？稳不稳定？
   - 现在买还是再等等？
   - 市场活不活跃？好不好出手？

3. **买房要注意什么？**（2-3段）
   - 要看哪些方面？（地段、配套、交通等）
   - 什么户型比较好？多大面积合适？
   - 有什么陷阱和风险要警惕？

4. **具体建议**（1-2段）
   - 推荐看什么价位的房子？
   - 什么时候买比较合适？
   - 还有什么要特别提醒的？

要求：
- 不要用"投资"、"ROI"、"流动性"等专业词
- 用"房子稳不稳定"代替"市场波动"
- 用"价格合理"代替"投资价值"
- 每段开头用小标题（加粗），总字数800-1000字
"""
            
            elif role == 'upgrader':
                # 改善型购房者：关注换房策略
                context = f"""请为换房者提供{city_name}的换房策略分析报告。

{base_data}

## 投资参考数据
- 综合评分: {analysis_data['investment_index']['index_score']}/100
- 价格趋势得分: {analysis_data['investment_index']['price_trend_score']:.1f}
- 市场稳定性: {analysis_data['investment_index']['stability_score']:.1f}

# 请提供以下分析

1. **换房时机研判**（2-3段，每段80-100字）
   - 当前市场适合卖旧房还是买新房？
   - 先卖后买 vs 先买后卖，哪个更合适？
   - 把握什么样的时间窗口？

2. **市场行情分析**（2-3段）
   - 价格趋势对换房有利还是不利？
   - 旧房好不好卖？新房选择多不多？
   - 交易活跃度如何？成交周期多长？

3. **资金规划建议**（2-3段）
   - 换房需要准备多少资金？
   - 税费成本大概多少？
   - 如何降低资金压力？有什么省钱技巧？

4. **换房策略**（2-3段）
   - 推荐什么价位和户型？
   - 改善重点应该放在哪里？（学区/地段/面积/环境）
   - 要注意哪些风险和问题？

要求：平衡专业性和实用性，每段开头用小标题（加粗），总字数800-1000字
"""
            
            else:  # investment_advisor
                # 投资顾问：专业投资分析
                context = f"""请为投资者提供{city_name}的房地产市场专业投资分析报告。

{base_data}

## 投资指数
- 综合投资指数: {analysis_data['investment_index']['index_score']}/100
- 投资等级: {analysis_data['investment_index']['investment_level']}
- 价格趋势得分: {analysis_data['investment_index']['price_trend_score']:.1f}
- 成交量趋势得分: {analysis_data['investment_index']['volume_trend_score']:.1f}
- 市场稳定性得分: {analysis_data['investment_index']['stability_score']:.1f}
- 变异系数: {analysis_data['volatility']['coefficient_of_variation']}%

# 请提供以下专业分析

1. **市场定位分析**（2-3段，每段80-100字）
   - 该城市房地产市场的整体定位
   - 与其他一线/二线城市的对比
   - 目标客群和市场容量

2. **投资价值评估**（3-4段）
   - 基于投资指数的综合评价
   - ROI预期和增值潜力
   - 市场流动性分析
   - 风险收益比评估

3. **市场趋势研判**（2-3段）
   - 近期价格走势和成交量变化
   - 市场信号和技术指标
   - 未来3-6个月市场预判

4. **投资建议**（2-3段）
   - 明确的投资建议（买入/观望/不建议）
   - 推荐的投资策略（长持/短炒）
   - 推荐的户型和价格区间
   - 入市时机判断

5. **风险提示**（1-2段）
   - 主要风险点和应对策略
   - 需要关注的关键指标

要求：使用专业术语，数据支撑，每段开头用小标题（加粗），总字数800-1000字
"""
            
            # 调用AI分析（流式输出，传递role参数）
            for chunk in ai_assistant.chat_stream(context, None, role=role):
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Quick insight stream error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/ai/analyze-chart-stream', methods=['POST'])
def ai_analyze_chart_stream():
    """AI分析图表数据（流式）"""
    data = request.json
    chart_type = data.get('chart_type', '')
    chart_data = data.get('chart_data', {})
    city = data.get('city', '')
    context = data.get('context', '')
    role = data.get('role', 'investment_advisor')  # 使用标准角色ID
    
    def generate():
        try:
            # 根据角色定制prompt
            if role == 'first_time_buyer':
                # 首次购房者：通俗易懂，关注实用性
                prompt = f"""分析以下图表数据：

**图表类型**: {chart_type}
**城市**: {city}
**背景**: {context}

**数据**: {json.dumps(chart_data, ensure_ascii=False)}

请用通俗易懂的语言（就像跟朋友聊天），提供2-3段分析（每段50-70字）：
1. 这个图表告诉我们什么？（用大白话解释）
2. 对买房有什么影响？（价格贵不贵？稳不稳定？）
3. 买房时要注意什么？（有什么风险或建议？）

要求：
- 不要用"投资"、"ROI"等专业词
- 用"房子稳不稳定"代替"市场波动"
- 总共不超过180字，通俗易懂"""
            
            elif role == 'upgrader':
                # 改善型购房者：从换房角度分析
                prompt = f"""分析以下图表数据：

**图表类型**: {chart_type}
**城市**: {city}
**背景**: {context}

**数据**: {json.dumps(chart_data, ensure_ascii=False)}

请从换房者视角，提供2-3段分析（每段60-80字）：
1. 数据关键特征和趋势
2. 对换房时机的启示（适合卖旧房还是买新房？）
3. 换房建议（要注意什么？如何规划？）

要求：平衡专业性和实用性，总共不超过200字"""
            
            else:  # investment_advisor
                # 投资顾问：专业分析
                prompt = f"""分析以下图表数据：

**图表类型**: {chart_type}
**城市**: {city}
**背景**: {context}

**数据**: {json.dumps(chart_data, ensure_ascii=False)}

请提供2-3段专业分析（每段60-80字），包括：
1. 数据关键特征和趋势
2. 市场含义和投资信号
3. 对投资者的启示（投资价值、风险、时机）

要求：使用专业术语，突出重点，总共不超过200字"""
            
            # 流式生成分析（使用ai_assistant的角色系统）
            for chunk in ai_assistant.chat_stream(prompt, None, role=role):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/strategy-planner')
@login_required
def strategy_planner():
    """购房策略规划器页面"""
    cities = data_manager.get_enabled_cities()
    user = session.get('user', {})
    return render_template('strategy_planner.html', cities=cities, user=user, active_page='strategy')

@app.route('/ai-image-studio')
@login_required
def ai_image_studio():
    """AI创意图像工作室页面"""
    user = session.get('user', {})
    return render_template('ai_image_studio.html', user=user, active_page='ai_studio')

@app.route('/price-prediction')
@login_required
def price_prediction():
    """AI房价预测页面"""
    cities = data_manager.get_enabled_cities()
    user = session.get('user', {})
    return render_template('price_prediction.html', cities=cities, user=user, active_page='prediction')

@app.route('/api/city/<city_name_en>/districts')
def get_city_districts(city_name_en):
    """获取城市区域列表"""
    df = data_manager.load_city_data(city_name_en)
    if df is None or '区域' not in df.columns:
        return jsonify({'districts': []})
    
    districts = df['区域'].unique().tolist()
    return jsonify({'districts': sorted(districts)})

@app.route('/api/prediction/stats', methods=['POST'])
@login_required
def get_prediction_stats():
    """获取统计预测数据"""
    data = request.get_json()
    city = data.get('city', 'beijing')
    months = data.get('months', 6)
    district = data.get('district', '')
    
    df = data_manager.load_city_data(city)
    if df is None:
        return jsonify({'success': False, 'error': '数据未找到'})
    
    # 查找城市名称
    city_name = city
    for c in data_manager.get_enabled_cities():
        if c['name_en'] == city:
            city_name = c['name']
            break
    
    try:
        predictor = PricePredictor(df, city_name)
        
        historical = predictor.get_historical_trend()
        factors = predictor.calculate_prediction_factors()
        predictions = predictor.generate_simple_prediction(months)
        districts_data = predictor.get_district_trends()
        
        return jsonify({
            'success': True,
            'historical': historical['data'][-12:],  # 最近12个月
            'factors': factors,
            'predictions': predictions,
            'districts': districts_data['districts']
        })
    except Exception as e:
        logger.error(f"预测错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/prediction/ai-stream')
@login_required
def get_ai_prediction_stream():
    """AI预测流式接口"""
    city = request.args.get('city', 'beijing')
    months = int(request.args.get('months', 6))
    district = request.args.get('district', '')
    role = request.args.get('role', 'investment_advisor')
    
    def generate():
        try:
            df = data_manager.load_city_data(city)
            if df is None:
                yield f"data: {json.dumps({'error': '数据未找到'})}\n\n"
                return
            
            # 查找城市名称
            city_name = city
            for c in data_manager.get_enabled_cities():
                if c['name_en'] == city:
                    city_name = c['name']
                    break
            
            predictor = PricePredictor(df, city_name)
            prompt = predictor.build_ai_prompt(months, district if district else None, role)
            
            # 调用 AI 流式接口
            import requests
            headers = {
                'Authorization': f'Bearer {AI_CONFIG["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': AI_CONFIG['model'],
                'messages': [
                    {'role': 'system', 'content': '你是一位专业的房地产分析师，擅长基于数据进行房价预测分析。请严格按照用户要求的格式输出，先输出JSON数据块，再输出分析文字。'},
                    {'role': 'user', 'content': prompt}
                ],
                'stream': True,
                'max_tokens': 2000
            }
            
            response = requests.post(
                f"{AI_CONFIG['api_url']}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            yield "data: [DONE]\n\n"
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield f"data: {json.dumps({'content': content})}\n\n"
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"AI预测错误: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/prediction/ai-data', methods=['POST'])
@login_required
def get_ai_prediction_data():
    """获取 AI 预测的结构化数据（非流式，用于图表）"""
    from price_predictor import AIResponseExtractor
    
    data = request.get_json()
    city = data.get('city', 'beijing')
    months = data.get('months', 6)
    district = data.get('district', '')
    
    try:
        df = data_manager.load_city_data(city)
        if df is None:
            return jsonify({'success': False, 'error': '数据未找到'})
        
        # 查找城市名称
        city_name = city
        for c in data_manager.get_enabled_cities():
            if c['name_en'] == city:
                city_name = c['name']
                break
        
        predictor = PricePredictor(df, city_name)
        prompt = predictor.build_ai_prompt_for_extraction(months, district if district else None)
        
        # 调用 AI 接口（非流式）
        import requests
        headers = {
            'Authorization': f'Bearer {AI_CONFIG["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': AI_CONFIG['model'],
            'messages': [
                {'role': 'system', 'content': '你是一位房地产数据分析专家，只输出JSON格式的预测数据，不要任何其他文字。'},
                {'role': 'user', 'content': prompt}
            ],
            'stream': False,
            'max_tokens': 1000
        }
        
        response = requests.post(
            f"{AI_CONFIG['api_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_response = result['choices'][0]['message']['content']
            
            # 使用 Extractor 提取数据
            extracted = AIResponseExtractor.extract_predictions(ai_response)
            
            if extracted['success']:
                return jsonify({
                    'success': True,
                    'ai_predictions': extracted['predictions'],
                    'trend': extracted['trend'],
                    'confidence': extracted['confidence'],
                    'risk_level': extracted['risk_level'],
                    'key_factors': extracted.get('key_factors', []),
                    'recommendation': extracted.get('recommendation', ''),
                    'raw_response': ai_response
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '无法解析AI预测数据',
                    'raw_response': ai_response
                })
        else:
            return jsonify({'success': False, 'error': 'AI响应异常'})
            
    except Exception as e:
        logger.error(f"AI预测数据获取错误: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/3d-map/<city_name_en>')
@login_required
def map_3d(city_name_en):
    """3D房价地图页面"""
    # 查找城市信息
    city_name = None
    for city in data_manager.get_enabled_cities():
        if city['name_en'] == city_name_en:
            city_name = city['name']
            break
    
    if not city_name:
        return "城市未找到", 404
    
    user = session.get('user', {})
    return render_template('map_3d.html', city_name=city_name, city_name_en=city_name_en, user=user, active_page=f'3d_{city_name_en}')

@app.route('/api/city/<city_name_en>/map-data')
def get_map_data(city_name_en):
    """获取3D地图数据（按区域和时间聚合）"""
    import numpy as np
    
    df = data_manager.load_city_data(city_name_en)
    if df is None or len(df) == 0:
        return jsonify({'error': '数据未找到'}), 404
    
    # 添加时间字段
    df['年月'] = df['成交日期'].dt.to_period('M').astype(str)
    df['年份'] = df['成交日期'].dt.year
    
    # 按区域和月份聚合
    monthly_district = df.groupby(['区域', '年月']).agg({
        '成交价（万元）': 'mean',
        '成交单价（元）': 'mean',
        '面积（m²）': 'count'
    }).reset_index()
    
    monthly_district.columns = ['区域', '年月', '平均价格', '平均单价', '成交量']
    
    # 转换为前端需要的格式
    map_data = []
    for _, row in monthly_district.iterrows():
        map_data.append({
            'district': row['区域'],
            'month': row['年月'],
            'avg_price': round(float(row['平均价格']), 2),
            'avg_unit_price': round(float(row['平均单价']), 2),
            'volume': int(row['成交量'])
        })
    
    # 获取所有区域列表
    districts = sorted(df['区域'].unique().tolist())
    
    # 获取所有月份列表
    months = sorted(df['年月'].unique().tolist())
    
    # 计算每个区域的总体统计
    district_stats = df.groupby('区域').agg({
        '成交价（万元）': ['mean', 'min', 'max'],
        '成交单价（元）': ['mean', 'min', 'max'],
        '面积（m²）': 'count'
    }).reset_index()
    
    district_stats.columns = ['区域', '平均价格', '最低价格', '最高价格', '平均单价', '最低单价', '最高单价', '总成交量']
    
    district_summary = []
    for _, row in district_stats.iterrows():
        # 计算价格变化趋势
        district_data = df[df['区域'] == row['区域']].sort_values('成交日期')
        if len(district_data) > 10:
            recent_price = district_data.tail(int(len(district_data) * 0.3))['成交单价（元）'].mean()
            earlier_price = district_data.head(int(len(district_data) * 0.3))['成交单价（元）'].mean()
            trend_pct = ((recent_price - earlier_price) / earlier_price) * 100
        else:
            trend_pct = 0
        
        district_summary.append({
            'district': row['区域'],
            'avg_price': round(float(row['平均价格']), 2),
            'avg_unit_price': round(float(row['平均单价']), 2),
            'total_volume': int(row['总成交量']),
            'trend_percent': round(float(trend_pct), 2),
            'price_range': [round(float(row['最低价格']), 2), round(float(row['最高价格']), 2)]
        })
    
    return jsonify({
        'success': True,
        'districts': districts,
        'months': months,
        'data': map_data,
        'summary': district_summary
    })

@app.route('/api/strategy/analyze', methods=['POST'])
def analyze_strategy():
    """分析购房策略"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['city', 'budget', 'purpose', 'family_size', 'urgency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数：{field}'}), 400
        
        city_name_en = data['city']
        
        # 加载城市数据
        df = data_manager.load_city_data(city_name_en)
        if df is None or len(df) == 0:
            return jsonify({'error': '城市数据未找到'}), 404
        
        # 获取城市中文名
        city_name = None
        for city in data_manager.get_enabled_cities():
            if city['name_en'] == city_name_en:
                city_name = city['name']
                break
        
        if not city_name:
            return jsonify({'error': '城市未找到'}), 404
        
        # 构建用户画像
        user_profile = {
            'budget': float(data['budget']),
            'purpose': data['purpose'],
            'family_size': int(data['family_size']),
            'urgency': data['urgency'],
            'preferred_district': data.get('preferred_district', ''),
            'has_kid': data.get('has_kid', False),
            'work_location': data.get('work_location', '')
        }
        
        # 生成策略
        strategy = strategy_analyzer.generate_comprehensive_strategy(
            user_profile, 
            df, 
            city_name
        )
        
        # 清理数据
        strategy_cleaned = clean_data(strategy)
        
        return jsonify({
            'success': True,
            'strategy': strategy_cleaned
        })
        
    except Exception as e:
        logger.error(f"策略分析错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'分析失败：{str(e)}'
        }), 500

def clean_data(obj):
    """清理数据中的NaN和Infinity"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(item) for item in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return 0  # 转换为0而不是None，更适合前端处理
        return obj
    elif hasattr(obj, 'item'):  # numpy类型
        return clean_data(obj.item())
    return obj

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
