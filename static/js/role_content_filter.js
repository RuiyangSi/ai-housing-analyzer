/**
 * AI角色内容过滤器
 * 根据选择的角色显示/隐藏不同的内容板块
 */

// 内容板块配置
const CONTENT_CONFIG = {
    'investment_advisor': {
        name: '投资顾问',
        showSections: ['all'],  // 显示所有内容
        hideKeywords: []
    },
    'first_time_buyer': {
        name: '首次购房者',
        showSections: ['basic', 'trend', 'price_range', 'area', 'district'],  // 只显示基础内容
        hideSections: ['investment_index', 'volatility', 'yoy'],  // 隐藏专业指标
        replaceTerms: {
            '投资指数': '市场参考',
            'ROI': '性价比',
            '变异系数': '价格稳定性',
            '流动性': '交易活跃度'
        }
    },
    'upgrader': {
        name: '改善型购房者',
        showSections: ['all'],  // 显示所有内容，但用换房视角解读
        hideKeywords: []
    }
};

/**
 * 应用内容过滤
 */
function applyContentFilter() {
    // 检查角色是否已加载
    if (typeof isRoleLoaded === 'function' && !isRoleLoaded()) {
        console.log('[ContentFilter] 角色尚未加载，跳过过滤');
        return;
    }
    
    const role = getRole();
    const config = CONTENT_CONFIG[role];
    
    if (!config) return;
    
    console.log('[ContentFilter] 应用内容过滤，角色:', role);
    
    // 如果是投资顾问或改善型，显示所有内容
    if (config.showSections.includes('all')) {
        document.querySelectorAll('.analysis-section').forEach(section => {
            section.style.display = '';
        });
        return;
    }
    
    // 对于首次购房者，隐藏专业内容
    if (role === 'first_time_buyer') {
        console.log('Filtering content for first-time buyer...');
        
        // 定义需要隐藏的标题关键词（投资相关、专业分析）
        const hideKeywords = [
            // 投资相关
            '综合投资指数',
            '投资综合评分',
            '投资价值指数',
            '投资指数对比',
            '投资评分',
            '投资建议',
            '专业投资',
            'ROI',
            
            // 专业图表
            '雷达图',
            '箱线图',
            '小提琴图',
            '热力图',
            '瀑布图',
            
            // 专业分析
            '市场波动性',
            '年度同比',
            '增长率对比',
            '季节性特征',
            '季节性',
            '变异系数'
        ];
        
        // 隐藏投资指数卡片
        const investmentCard = document.querySelector('.index-card');
        if (investmentCard) {
            investmentCard.style.display = 'none';
            console.log('Hidden: 投资指数卡片');
        }
        
        // 遍历所有h2标题，隐藏包含关键词的section
        document.querySelectorAll('h2').forEach(h2 => {
            const title = h2.textContent;
            const shouldHide = hideKeywords.some(keyword => title.includes(keyword));
            
            if (shouldHide) {
                // 找到包含这个h2的.analysis-section
                const section = h2.closest('.analysis-section');
                if (section) {
                    section.style.display = 'none';
                    console.log('Hidden section:', title);
                }
            }
        });
        
        // 判断是单城市页面还是全国对比页面
        const isNationalPage = window.location.pathname.includes('national');
        
        if (isNationalPage) {
            // 全国对比页面：添加首次购房者提示
            addNationalBeginnerTips();
        } else {
            // 单城市页面：添加新手购房提示
            addBeginnerTips();
        }
    }
}

/**
 * 为首次购房者添加新手提示
 */
function addBeginnerTips() {
    // 检查是否已添加
    if (document.getElementById('beginner-tips')) return;
    
    const tipsHtml = `
        <div id="beginner-tips" class="analysis-section" style="
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #10b981;
        ">
            <h3 style="margin: 0 0 15px 0; color: #065f46;">
                🏠 新手购房小贴士
            </h3>
            <div style="color: #064e3b; line-height: 1.8;">
                <p><strong>📍 看房重点：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>交通便利度：地铁站、公交站距离</li>
                    <li>生活配套：超市、菜场、医院</li>
                    <li>教育资源：学校质量（如果有孩子）</li>
                    <li>小区环境：绿化、物业、邻里</li>
                </ul>
                
                <p><strong>💰 预算建议：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>首付准备：至少30%，预留装修费用</li>
                    <li>月供压力：不超过家庭月收入的40%</li>
                    <li>应急储备：保留6个月生活费</li>
                </ul>
                
                <p><strong>⚠️ 注意事项：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>多看几套对比，不要被销售催促</li>
                    <li>签合同前找懂行的人帮忙看</li>
                    <li>仔细查看房屋质量和产权</li>
                    <li>了解小区的口碑和评价</li>
                </ul>
            </div>
        </div>
    `;
    
    // 插入到AI智能概览之后
    const aiOverview = document.querySelector('.analysis-section');
    if (aiOverview && aiOverview.nextElementSibling) {
        aiOverview.insertAdjacentHTML('afterend', tipsHtml);
    }
}

/**
 * 为全国对比页面添加首次购房者提示
 */
function addNationalBeginnerTips() {
    // 检查是否已添加
    if (document.getElementById('national-beginner-tips')) return;
    
    const tipsHtml = `
        <div id="national-beginner-tips" class="analysis-section" style="
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #10b981;
        ">
            <h3 style="margin: 0 0 15px 0; color: #065f46;">
                🏠 首次购房者选城市指南
            </h3>
            <div style="color: #064e3b; line-height: 1.8;">
                <p><strong>📍 选择城市要考虑：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>工作机会：是否有稳定的工作和收入来源</li>
                    <li>房价水平：是否在自己的预算范围内</li>
                    <li>生活成本：除了房贷，日常开销是否能承受</li>
                    <li>发展前景：城市是否有发展潜力，房价稳定</li>
                </ul>
                
                <p><strong>💰 价格对比建议：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>一线城市（北上广深）：房价高，压力大，量力而行</li>
                    <li>新一线城市：性价比相对较高，发展潜力好</li>
                    <li>二线城市：价格适中，生活压力小，适合首次购房</li>
                </ul>
                
                <p><strong>⚠️ 注意事项：</strong></p>
                <ul style="margin: 10px 0;">
                    <li>不要只看房价便宜，要综合考虑工作机会</li>
                    <li>选择房价相对稳定的城市，避免大起大落</li>
                    <li>考虑长期发展，不要只图一时便宜</li>
                    <li>首付要在能力范围内，月供不超过收入40%</li>
                </ul>
            </div>
        </div>
    `;
    
    // 插入到AI智能概览之后
    const aiOverview = document.querySelector('.analysis-section');
    if (aiOverview && aiOverview.nextElementSibling) {
        aiOverview.insertAdjacentHTML('afterend', tipsHtml);
    }
}

/**
 * 在页面加载时应用过滤（需要等待角色数据从后端加载）
 */
async function initContentFilter() {
    console.log('[ContentFilter] 初始化内容过滤...');
    
    // 确保角色已从后端加载
    if (typeof ensureRoleLoaded === 'function') {
        const role = await ensureRoleLoaded();
        console.log('[ContentFilter] 角色加载完成:', role);
    }
    
    // 等待DOM准备好
    setTimeout(() => {
        console.log('[ContentFilter] 执行首次过滤...');
        applyContentFilter();
    }, 200);
}

// 页面加载时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initContentFilter);
} else {
    initContentFilter();
}

// 页面完全加载后再次检查（确保动态生成的内容也被过滤）
window.addEventListener('load', function() {
    console.log('[ContentFilter] 页面完全加载，执行二次过滤...');
    setTimeout(() => {
        applyContentFilter();
    }, 800);
});

// 监听analysis.js加载完成后的数据渲染（因为图表是异步加载的）
document.addEventListener('analysisDataLoaded', function() {
    console.log('[ContentFilter] 分析数据加载完成，执行三次过滤...');
    setTimeout(() => {
        applyContentFilter();
    }, 300);
});

