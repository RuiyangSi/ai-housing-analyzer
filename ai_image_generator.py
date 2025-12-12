"""
AI 图像生成模块
使用 SiliconFlow API 生成创意房产相关图像
专注于无法用代码绘制的创意内容
"""

import requests
import json
from typing import Optional, Dict, Any

class AIImageGenerator:
    """AI 图像生成器 - 创意图像专用"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.siliconflow.cn/v1"):
        self.api_key = api_key
        self.api_url = api_url
        self.default_model = "black-forest-labs/FLUX.1-schnell"
        
    def generate_image(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        size: str = "1024x1024",
        steps: int = 4
    ) -> Dict[str, Any]:
        """生成图像"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model or self.default_model,
            'prompt': prompt,
            'image_size': size,
            'num_inference_steps': steps
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=120
            )
            result = response.json()
            
            if 'images' in result and len(result['images']) > 0:
                return {
                    'success': True,
                    'image_url': result['images'][0].get('url'),
                    'model': model or self.default_model
                }
            elif 'data' in result and len(result['data']) > 0:
                return {
                    'success': True,
                    'image_url': result['data'][0].get('url'),
                    'model': model or self.default_model
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', '图像生成失败')
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': '请求超时，请稍后重试'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 创意应用场景 ====================
    
    def generate_dream_home(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        🏠 根据用户画像生成「梦想之家」效果图
        这是AI生图最有价值的应用 - 用户输入预算、需求，AI生成未来家的想象图
        """
        budget = user_profile.get('budget', 500)
        area = user_profile.get('preferred_area', 100)
        style = user_profile.get('style', 'modern')
        family = user_profile.get('family_type', 'young_couple')
        city = user_profile.get('city', 'Beijing')
        tags = user_profile.get('tags', [])
        custom_prompt = user_profile.get('custom_prompt', '')
        
        style_map = {
            'modern': 'sleek modern minimalist',
            'chinese': 'elegant Chinese traditional with modern touches',
            'european': 'European classical luxury',
            'japanese': 'Japanese zen minimalist',
            'industrial': 'urban industrial loft'
        }
        
        # 关键词映射
        tag_prompts = {
            '落地窗': 'floor-to-ceiling windows',
            '城市景观': 'stunning city skyline view',
            '开放厨房': 'open concept kitchen with island',
            '书房角落': 'cozy reading nook with bookshelves',
            '阳台花园': 'balcony garden with plants',
            '大客厅': 'spacious living room',
            '步入式衣帽间': 'walk-in closet',
            '智能家居': 'smart home features',
            '温馨灯光': 'warm ambient lighting',
            '木质元素': 'natural wood accents'
        }
        
        # 构建关键词描述
        tag_descriptions = [tag_prompts.get(tag, tag) for tag in tags if tag in tag_prompts]
        tag_str = ', '.join(tag_descriptions) if tag_descriptions else 'comfortable living space'
        
        prompt = f"""
        Architectural visualization of a dream home in {city}, China:
        - Style: {style_map.get(style, 'modern minimalist')}
        - Size: approximately {area} square meters
        - Budget tier: {'luxury' if budget > 800 else 'mid-range' if budget > 400 else 'affordable'}
        - Key features: {tag_str}
        - Interior view showing living room and partial kitchen
        - Large windows with city/nature view
        - Warm afternoon lighting
        - Photorealistic architectural rendering
        - High-end real estate marketing quality
        - 8K ultra detailed
        {f'- Additional details: {custom_prompt}' if custom_prompt else ''}
        """
        
        return self.generate_image(prompt)
    
    def generate_neighborhood_vision(self, district: str, city: str, features: list) -> Dict[str, Any]:
        """
        🏘️ 生成社区/区域未来发展愿景图
        帮助用户想象该区域5-10年后的样子
        """
        feature_desc = ', '.join(features[:5]) if features else 'parks, shops, schools'
        
        prompt = f"""
        Futuristic urban development vision for {district}, {city}:
        - Aerial/bird's eye view of the neighborhood
        - Modern residential towers with green terraces
        - Key amenities visible: {feature_desc}
        - Lush green spaces and tree-lined streets
        - Smart city elements (solar panels, EV charging)
        - People enjoying public spaces
        - Golden hour lighting
        - Utopian but realistic urban planning visualization
        - Architectural concept art style
        - Magazine cover quality
        """
        
        return self.generate_image(prompt)
    
    def generate_lifestyle_scene(self, lifestyle_type: str, city: str) -> Dict[str, Any]:
        """
        🌟 生成生活方式场景图
        展示在该城市购房后的美好生活想象
        """
        scenes = {
            'family_morning': f"""
                Warm family morning scene in a modern {city} apartment:
                - Parents preparing breakfast in open kitchen
                - Child doing homework at dining table
                - Sunlight streaming through floor-to-ceiling windows
                - City skyline visible in background
                - Cozy, lived-in but stylish interior
                - Coffee and toast on counter
                - Lifestyle photography style
                - Warm color grading
            """,
            'weekend_relax': f"""
                Weekend relaxation scene in a {city} high-rise apartment:
                - Person reading on comfortable sofa
                - Afternoon tea on coffee table
                - Panoramic city view through large windows
                - Indoor plants and modern decor
                - Soft natural lighting
                - Peaceful, aspirational atmosphere
                - Editorial lifestyle photography
            """,
            'home_office': f"""
                Modern home office setup in {city} apartment:
                - Sleek desk with dual monitors
                - Ergonomic chair by window with city view
                - Plants and personal touches
                - Natural light workspace
                - Video call setup visible
                - Professional yet cozy atmosphere
                - Work-from-home lifestyle
            """,
            'rooftop_party': f"""
                Rooftop gathering at a {city} residential building:
                - Friends gathered on rooftop terrace
                - City lights twinkling in background
                - String lights and lounge furniture
                - Drinks and appetizers
                - Sunset/dusk atmosphere
                - Urban social lifestyle
                - Instagram-worthy scene
            """
        }
        
        prompt = scenes.get(lifestyle_type, scenes['family_morning'])
        return self.generate_image(prompt)
    
    def generate_before_after_renovation(self, room_type: str, style: str) -> Dict[str, Any]:
        """
        🔨 生成装修前后对比的「After」效果图
        用户上传旧房照片，AI生成装修后的想象图
        """
        room_prompts = {
            'living_room': 'spacious living room with sofa, TV wall, and accent lighting',
            'bedroom': 'cozy master bedroom with king bed, walk-in closet, and ensuite bathroom door visible',
            'kitchen': 'modern open kitchen with island, built-in appliances, and pendant lights',
            'bathroom': 'spa-like bathroom with rain shower, freestanding tub, and marble finishes'
        }
        
        style_prompts = {
            'modern': 'clean lines, neutral colors with bold accents, minimalist furniture',
            'scandinavian': 'light wood, white walls, hygge atmosphere, functional beauty',
            'luxury': 'marble, gold accents, designer furniture, chandelier lighting',
            'japanese': 'tatami elements, shoji screens, natural materials, zen garden view'
        }
        
        prompt = f"""
        Interior design rendering - renovated {room_prompts.get(room_type, 'living room')}:
        - Style: {style_prompts.get(style, 'modern minimalist')}
        - Professional interior design photography
        - Warm inviting atmosphere
        - Staged with tasteful decor
        - Natural and artificial lighting blend
        - Real estate listing quality
        - Magazine editorial standard
        - 8K photorealistic
        """
        
        return self.generate_image(prompt)
    
    def generate_investment_story(self, scenario: str, city: str) -> Dict[str, Any]:
        """
        📈 生成投资故事场景图
        可视化投资成功的场景
        """
        scenarios = {
            'rental_income': f"""
                Happy landlord scene in {city}:
                - Professional person reviewing documents on tablet
                - Modern apartment interior visible
                - Notification showing rental payment received
                - Coffee shop or home office setting
                - Successful investor aesthetic
                - Warm, prosperous atmosphere
                - Business lifestyle photography
            """,
            'property_appreciation': f"""
                Property value growth celebration:
                - Family looking at their apartment building
                - Real estate price chart overlay (subtle)
                - Modern cityscape of {city}
                - Sunset golden hour lighting
                - Achievement and pride emotion
                - Aspirational family portrait style
            """,
            'passive_income': f"""
                Financial freedom lifestyle scene:
                - Person working remotely by the beach/cafe
                - Laptop showing property management dashboard
                - Relaxed, successful aesthetic
                - Digital nomad with real estate portfolio
                - Aspirational passive income lifestyle
            """
        }
        
        prompt = scenarios.get(scenario, scenarios['rental_income'])
        return self.generate_image(prompt)
    
    def generate_seasonal_home(self, season: str, home_type: str) -> Dict[str, Any]:
        """
        🌸 生成不同季节的家的氛围图
        展示四季变换中家的温馨
        """
        prompt = f"""
        {season.capitalize()} atmosphere in a {home_type} home:
        - {'Cherry blossoms visible through window, fresh spring morning light' if season == 'spring' else ''}
        - {'Summer sunshine, plants thriving, light airy curtains' if season == 'summer' else ''}
        - {'Autumn foliage view, warm orange lighting, cozy blankets' if season == 'autumn' else ''}
        - {'Snowfall outside, warm interior lighting, fireplace glow' if season == 'winter' else ''}
        - Cozy lived-in atmosphere
        - Family home feeling
        - Editorial interior photography
        - Warm color palette
        - Magazine quality
        """
        
        return self.generate_image(prompt)

