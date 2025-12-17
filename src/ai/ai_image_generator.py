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
        🏠 根据用户画像生成「梦想之家」效果图（优化版：更详细的提示词）
        这是AI生图最有价值的应用 - 用户输入预算、需求，AI生成未来家的想象图
        """
        budget = user_profile.get('budget', 500)
        area = user_profile.get('preferred_area', 100)
        style = user_profile.get('style', 'modern')
        family = user_profile.get('family_type', 'young_couple')
        city = user_profile.get('city', 'Beijing')
        tags = user_profile.get('tags', [])
        custom_prompt = user_profile.get('custom_prompt', '')
        
        # 详细的风格映射（添加更多描述）
        style_map = {
            'modern': 'sleek modern minimalist with clean lines, neutral color palette, premium materials like marble and brushed metal',
            'chinese': 'elegant new Chinese style blending traditional elements (lattice screens, tea corners) with contemporary comfort, warm wood tones, cultural sophistication',
            'european': 'European classical luxury with ornate moldings, chandeliers, marble floors, rich textures, timeless elegance',
            'japanese': 'Japanese zen minimalist with natural materials, tatami influences, shoji-inspired elements, harmonious simplicity, connection to nature',
            'industrial': 'urban industrial loft with exposed brick, concrete, metal beams, Edison bulbs, raw yet refined aesthetic'
        }
        
        # 增强的关键词映射（更具体的视觉描述）
        tag_prompts = {
            '落地窗': 'floor-to-ceiling panoramic windows with slim black frames',
            '城市景观': 'breathtaking city skyline view with skyscrapers and urban landscape',
            '开放厨房': 'open concept kitchen with marble island, built-in appliances, pendant lights',
            '书房角落': 'cozy reading nook with floor-to-ceiling bookshelves and comfortable armchair',
            '阳台花园': 'green balcony garden with potted plants, herbs, and outdoor seating',
            '大客厅': 'spacious open-plan living room with high ceilings and generous space',
            '步入式衣帽间': 'luxurious walk-in closet with organized shelving visible through door',
            '智能家居': 'smart home features with touch panels and modern tech integration',
            '温馨灯光': 'layered warm ambient lighting with dimmers and accent lamps',
            '木质元素': 'natural oak or walnut wood accents in flooring, furniture, and wall paneling'
        }
        
        # 构建关键词描述
        tag_descriptions = [tag_prompts.get(tag, tag) for tag in tags if tag in tag_prompts]
        tag_str = ', '.join(tag_descriptions) if tag_descriptions else 'comfortable and well-designed living space'
        
        # 根据预算调整质感描述
        quality_tier = {
            'luxury': 'premium designer furniture, imported materials, high-end finishes, bespoke details',
            'mid-range': 'quality furniture, good materials, tasteful styling, well-curated decor',
            'affordable': 'smart affordable design, IKEA-style efficiency, practical yet stylish, good value aesthetics'
        }
        tier = 'luxury' if budget > 800 else 'mid-range' if budget > 400 else 'affordable'
        
        # 根据家庭类型调整氛围
        family_atmosphere = {
            'young_couple': 'intimate and romantic atmosphere, couples lifestyle',
            'family_with_kids': 'family-friendly with playful touches, child-safe design',
            'single': 'personal sanctuary feel, bachelor/bachelorette pad sophistication',
            'elderly': 'comfortable and accessible design, mature elegance'
        }
        atmosphere = family_atmosphere.get(family, 'welcoming and comfortable atmosphere')
        
        prompt = f"""
Professional architectural interior visualization of dream home in {city}, China:

STYLE & AESTHETICS:
- Primary style: {style_map.get(style, 'modern minimalist design')}
- Quality level: {quality_tier[tier]}
- Target demographic: {atmosphere}

SPACE SPECIFICATIONS:
- Approximate size: {area} square meters
- Main view: Living room with open sightlines to dining area and kitchen
- Key features integrated: {tag_str}

COMPOSITION & FRAMING:
- Wide angle interior shot (24mm equivalent)
- Eye-level perspective, slightly elevated (1.5m height)
- Balanced composition with rule of thirds
- Foreground: Elegant sofa/seating area
- Midground: Dining table or kitchen island
- Background: Large windows with stunning view

LIGHTING DESIGN:
- Golden hour natural light streaming through windows (late afternoon, 4-5pm)
- Soft warm glow (2700K-3000K color temperature)
- Layered lighting: ambient + accent + natural
- Gentle shadows adding depth and dimension
- Sun rays creating atmospheric volumetric lighting

MATERIALS & TEXTURES:
- Rich material variety: wood grain, fabric weaves, smooth surfaces
- Photorealistic material rendering with proper reflections
- Tactile quality evident in close-up elements

ATMOSPHERE & MOOD:
- Aspirational yet achievable lifestyle
- Clean and uncluttered but lived-in feel
- Warm, inviting, and emotionally resonant
- Sense of space, light, and comfort

VIEW THROUGH WINDOWS:
- {city} cityscape or nature depending on location
- Slightly defocused background (subtle depth of field)
- Blue sky with soft clouds

STYLING & DETAILS:
- Coffee table book, decorative bowl, or small plant as styling
- Fresh flowers or greenery adding life
- Throws, cushions for texture and comfort
- Art piece on wall (abstract or landscape)
- No clutter - curated minimalism

TECHNICAL QUALITY:
- Photorealistic architectural rendering
- High-end real estate marketing photography quality
- Sharp focus on foreground, slight depth of field
- 8K resolution, ultra-detailed textures
- Professional color grading (slightly desaturated, elevated blacks)
- Cinematic quality comparable to Architectural Digest or Dwell magazine

REFERENCE STYLES:
- Similar to work by architectural photographers: Hufton+Crow, Iwan Baan
- Interior design magazine editorial quality
- Luxury real estate listing photography standard

{f'ADDITIONAL CUSTOMIZATION: {custom_prompt}' if custom_prompt else ''}

NEGATIVE PROMPT (what to avoid):
- No people visible in the scene
- No cartoon or illustration style
- No unrealistic proportions or perspectives
- No cluttered or messy spaces
- No dated or old-fashioned furniture
- No harsh or unflattering lighting
- No dark, dim, or gloomy atmosphere
- No visible branding or logos
- No outdoor-only shots
"""
        
        return self.generate_image(prompt.strip())
    
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
        🌟 生成生活方式场景图（优化版：更真实、更有情感共鸣）
        展示在该城市购房后的美好生活想象
        """
        scenes = {
            'family_morning': f"""
Cinematic lifestyle photography - Warm family morning in modern {city} apartment:

SCENE SETUP:
- Location: Open concept living-dining-kitchen area, modern Chinese family home
- Time: 7:30 AM, weekday morning, soft golden morning light
- Season: Spring/early summer, comfortable temperature

HUMAN ELEMENTS (natural, candid):
- Mother (30s) preparing breakfast at kitchen island, wearing casual home clothes, gentle smile
- Father (30s) helping child with backpack near dining table, morning routine interaction
- Child (6-8 years) eating breakfast at table, school uniform, natural child behavior
- Natural family dynamics, authentic moment not posed, tender interactions

COMPOSITION & FRAMING:
- Shot from living room perspective looking toward kitchen
- Medium-wide angle (35mm equivalent)
- Eye level, documentary photography style
- Foreground: Partial view of living room sofa/coffee table
- Midground: Dining table with child, father nearby
- Background: Kitchen island with mother, windows beyond

LIGHTING (natural, realistic):
- Soft warm morning sunlight streaming through floor-to-ceiling windows (east-facing)
- Golden hour quality but softer (early morning, not sunset)
- Gentle shadows, no harsh contrast
- Kitchen pendant lights slightly on, creating warm ambiance layer
- Overall warm color temperature (3500K)

INTERIOR DETAILS:
- Modern Chinese family home: clean, organized, but lived-in feel
- Kitchen: open concept with marble island, breakfast items visible
- Dining table: bamboo or wood, simple breakfast spread (congee, eggs, milk, fruit)
- Coffee machine, toaster on counter (middle-class family details)
- Fresh flowers in vase, morning newspaper, keys on console table
- Child's backpack, lunchbox visible - authentic family life details
- Indoor plant near window (pothos or fiddle leaf fig)

ATMOSPHERE & EMOTION:
- Warm, loving, authentic family connection
- Busy but peaceful morning routine
- Sense of comfort, security, and belonging
- Aspirational but relatable lifestyle
- "This could be your life" feeling

TECHNICAL SPECS:
- Lifestyle editorial photography quality (like Kinfolk or Cereal magazine)
- Slightly desaturated color grading with warm tones
- Natural grain/texture for authentic feel
- Sharp focus on family members, slight depth of field
- 4K resolution, photojournalistic quality
- Reference: Lifestyle work by photographers like Tec Petaja, Luisa Brimble

CITY CONTEXT:
- {city} cityscape visible through windows (subtle, not dominant)
- Modern residential building setting
- Urban family lifestyle

NEGATIVE (avoid):
- No overly staged or fake-looking poses
- No harsh lighting or dark shadows
- No cluttered or messy environment
- No dated furniture or outdated design
- No visible faces looking directly at camera (candid, natural moments)
- No excessive product placement feeling
            """,
            
            'weekend_relax': f"""
Serene lifestyle photography - Weekend relaxation in {city} high-rise apartment:

SCENE SETUP:
- Location: Living room with panoramic city view, luxury apartment
- Time: Saturday afternoon, 3:00 PM, soft natural light
- Season: Autumn, comfortable indoor temperature

HUMAN ELEMENT (peaceful, intimate):
- Person (late 20s-30s, gender neutral) curled up on modern sofa with book
- Wearing comfortable weekend loungewear (knit sweater, soft pants)
- Natural reading posture, genuinely relaxed
- Bare feet or fuzzy socks, casual comfort
- Peaceful facial expression, absorbed in reading

COMPOSITION:
- Shot from side angle, person in mid-ground
- Wide angle view showing full living room and windows
- Person occupying left or right third of frame (rule of thirds)
- Emphasis on space, light, and tranquility

LIGHTING:
- Soft diffused afternoon light through large windows
- No direct harsh sunlight
- Gentle ambient glow
- Warm color temperature (3200K)
- Peaceful, meditative quality

INTERIOR STYLING:
- Modern minimalist aesthetic
- Quality sofa (fabric or leather) with plush cushions and throw blanket
- Wooden or marble coffee table with carefully styled items:
  * Ceramic teapot and cup with steam rising
  * Small plate with pastries or fruit
  * Reading glasses case
  * Small succulent or simple flower arrangement
- Area rug adding texture and warmth
- Floor lamp providing accent lighting
- Bookshelf visible in background with curated books
- Art piece on wall (abstract or landscape painting)

WINDOW VIEW:
- Panoramic {city} skyline visible but slightly defocused
- High-rise perspective (15-25 floor level)
- Urban landscape adding context without dominating
- Slight haze/atmosphere in distance

ATMOSPHERE:
- Ultimate weekend relaxation and self-care
- Quiet luxury and personal sanctuary
- Sense of escape and peace
- "This is the life you deserve" aspiration
- Mindful living and intentional downtime

TECHNICAL QUALITY:
- High-end lifestyle magazine photography
- Slightly desaturated, elevated blacks
- Soft focus on distant elements, sharp on person
- Natural grain for warmth
- Editorial quality like Elle Decor or Kinfolk

NEGATIVE:
- No busy or cluttered feeling
- No cold or sterile atmosphere
- No harsh shadows or bright highlights
- No technology visible (no phones, laptops)
- No multiple people (focus on solitary peace)
            """,
            
            'home_office': f"""
Professional lifestyle photography - Modern home office in {city} apartment:

SCENE SETUP:
- Location: Dedicated home office or study corner with city view
- Time: 10:00 AM weekday, productive morning work session
- Context: Remote work / entrepreneurship lifestyle

HUMAN ELEMENT:
- Professional (30-35 years) working at desk, seen from side/back angle
- Business casual attire (nice shirt/blouse, could be video call ready)
- Natural working posture, typing or in video call
- Productive, focused energy
- Successful work-from-home lifestyle representation

WORKSPACE COMPOSITION:
- Desk positioned by window with {city} view as background
- Shot from door/room entry perspective
- Wide enough to show full workspace context
- Balanced composition: desk centered, windows in background

WORKSPACE DETAILS (organized, premium):
- Modern desk: wood or minimalist white, spacious surface
- Dual monitor setup or laptop with external display
- Ergonomic office chair (Herman Miller style)
- Desk lamp providing task lighting
- Organized stationery holder with pens, notepad
- Coffee mug (half full, realistic detail)
- Indoor plant (small pothos or succulent)
- Wireless keyboard and mouse
- Notebook or planner open
- Headphones on desk stand
- Minimal cables, clean setup

TECHNOLOGY & SETUP:
- One screen showing video call grid (blurred faces)
- Ring light or webcam visible
- Professional home office aesthetic
- Smart, efficient use of space

LIGHTING:
- Natural light from window (primary light source)
- Desk lamp providing warm accent light
- Balanced exposure, not too bright or dim
- Professional video call lighting quality
- Color temperature: 4000K (neutral, productive)

BACKGROUND & CONTEXT:
- Bookshelf with professional books, awards, or decor
- Framed certificates or motivational art
- {city} skyline visible through window
- Height: mid-to-high floor apartment view
- Plants adding life and productivity vibes

ATMOSPHERE:
- Professional yet comfortable
- Work-life balance achieved
- Successful remote career lifestyle
- Productive and inspiring workspace
- "Career goals" aspiration

TECHNICAL SPECS:
- Corporate lifestyle photography quality
- Clean, sharp, professional look
- Slight desaturation, elevated contrast
- Focus on person and desk, slight depth of field on background
- Reference: LinkedIn, WeWork, modern office lifestyle photography

NEGATIVE:
- No messy or disorganized appearance
- No old or outdated equipment
- No dark or poorly lit space
- No cramped or uncomfortable setup
- No visible personal clutter
            """,
            
            'rooftop_party': f"""
Vibrant lifestyle photography - Rooftop social gathering at {city} residential building:

SCENE SETUP:
- Location: Modern rooftop terrace of high-rise residential building
- Time: Golden hour into blue hour (7:30-8:00 PM)
- Season: Late spring or early autumn, perfect outdoor weather
- Event: Casual friends gathering, weekend social

HUMAN ELEMENTS (natural, candid):
- Small group of 4-6 friends (diverse, late 20s-30s)
- Casual upscale attire (smart casual, stylish)
- Natural interactions: conversing, laughing, toasting
- Standing/sitting around high-top table or lounge seating
- Genuine social dynamics, not posed
- Mix of seated and standing positions

ROOFTOP SETTING:
- Modern rooftop terrace design
- Wooden deck or stone tiles flooring
- Contemporary outdoor furniture (lounge seating, high-top tables)
- String lights or market lights overhead (glowing warm)
- Planters with greenery creating cozy zones
- Glass railings with safety (unobstructed view)
- Outdoor heaters or fire pit (for ambiance)

FOOD & DRINK SETUP:
- High-top table with appetizers and drinks
- Wine bottles, cocktail glasses
- Charcuterie board or small plates
- Casual but elevated presentation
- Realistic party details

LIGHTING (magical hour):
- Golden hour sunlight fading (warm glow from horizon)
- Blue hour sky beginning (deep blue with orange gradient)
- String lights creating warm overhead glow
- City lights beginning to twinkle in background
- Candles or lanterns on tables
- Multi-layered lighting creating magical atmosphere

CITYSCAPE:
- {city} skyline panoramic view in background
- High-rise perspective (20-30 floor level)
- City lights starting to illuminate
- Iconic buildings visible if applicable
- Urban landscape adding premium context

COMPOSITION:
- Shot from corner perspective capturing group and view
- Wide angle showing terrace space and skyline
- Foreground: Friends gathered
- Midground: Terrace furnishings and details
- Background: Spectacular city view

ATMOSPHERE:
- Vibrant, social, aspirational lifestyle
- Urban sophistication and young professional energy
- "This is the life" feeling
- Community and friendship in the city
- Luxury urban living experience

TECHNICAL QUALITY:
- High-end lifestyle editorial photography
- Warm, rich color grading (golden and blue tones)
- Sharp focus on people, slight depth of field on city
- Natural grain for warmth
- Reference: Airbnb Experiences, luxury lifestyle magazines
- Cinematic quality, slightly stylized but realistic

NEGATIVE:
- No overcrowded or cluttered scene
- No dark or poorly lit faces
- No cheap or plastic party decorations
- No messy or trashy party appearance
- No excessive alcohol focus
- No unsafe behavior near railings
            """
        }
        
        prompt = scenes.get(lifestyle_type, scenes['family_morning'])
        return self.generate_image(prompt.strip())
    
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

