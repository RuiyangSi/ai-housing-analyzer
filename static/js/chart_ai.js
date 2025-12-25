/**
 * 图表AI分析模块
 * 为图表提供智能分析和洞察
 */

// 存储图表数据供AI分析使用
let chartDataStore = {};

/**
 * 保存图表数据
 */
function saveChartData(chartType, data) {
    chartDataStore[chartType] = data;
}

/**
 * 分析图表 - 主函数
 * @param {string} chartType - 图表类型
 * @param {string} chartId - 图表DOM ID（可选）
 * @param {string} chartTitle - 图表标题（可选）
 */
async function analyzeChart(chartType, chartId, chartTitle) {
    // 兼容两种ID格式
    // 单城市页面: {chartType}-ai-insight
    // 全国对比页面: ai-insight-{chartId}
    let insightDiv = document.getElementById(`${chartType}-ai-insight`);
    if (!insightDiv && chartId) {
        insightDiv = document.getElementById(`ai-insight-${chartId}`);
    }
    
    if (!insightDiv) {
        console.error(`找不到AI分析容器: ${chartType}-ai-insight 或 ai-insight-${chartId}`);
        alert('AI分析容器未找到，请刷新页面重试');
        return;
    }
    
    const button = event.target;
    
    // 显示加载状态，重置外层样式
    insightDiv.style.display = 'block';
    insightDiv.style.background = 'transparent';
    insightDiv.style.padding = '0';
    insightDiv.style.borderLeft = 'none';
    
    insightDiv.innerHTML = `
        <div style="padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; border-left: 4px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div>
                <strong style="color: #4f46e5;">🤖 AI正在分析图表...</strong>
            </div>
            <p style="margin: 0; color: #64748b; font-size: 0.9em;">DeepSeek-V3正在深度解读数据，请稍候...</p>
        </div>
    `;
    
    // 禁用按钮
    button.disabled = true;
    button.textContent = '分析中...';
    
    try {
        // 尝试获取图表数据（兼容两种key格式）
        let chartData = chartDataStore[chartType];
        if (!chartData && chartId) {
            chartData = chartDataStore[chartId];
        }
        
        if (!chartData) {
            throw new Error(`图表数据未找到: ${chartType} 或 ${chartId}`);
        }
        
        // 获取当前AI角色
        const role = getRole();
        
        console.log('Analyzing chart with role:', role);  // 调试日志
        
        // 调用AI分析API
        const response = await fetch('/api/ai/analyze-chart-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chart_type: chartTitle || chartType,
                chart_data: chartData,
                city: cityName || '全国对比',
                context: generateChartContext(chartType, chartData, chartTitle),
                role: role  // 传递AI角色
            })
        });
        
        if (!response.ok) {
            throw new Error('AI分析请求失败');
        }
        
        // 流式读取AI分析
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        
        // 重置外层容器样式，避免两层背景
        insightDiv.style.background = 'transparent';
        insightDiv.style.padding = '0';
        insightDiv.style.borderLeft = 'none';
        
        insightDiv.innerHTML = `
            <div style="padding: 20px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border-left: 4px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <span style="font-size: 1.5em;">🤖</span>
                    <strong style="color: #667eea; font-size: 1.1em;">AI 智能洞察</strong>
                </div>
                <div id="${chartType}-ai-text" style="line-height: 1.8; color: #1e293b;"></div>
            </div>
        `;
        
        const textDiv = document.getElementById(`${chartType}-ai-text`);
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            fullText += parsed.content;
                            // 渲染 Markdown 格式
                            textDiv.innerHTML = renderMarkdown(fullText);
                        } else if (parsed.error) {
                            textDiv.innerHTML = `<p style="color: #ef4444;">❌ ${parsed.error}</p>`;
                        }
                    } catch (e) {
                        // 跳过无法解析的行
                    }
                }
            }
        }
        
        if (!fullText) {
            textDiv.innerHTML = '<p style="color: #ef4444;">AI分析暂时不可用，请稍后再试。</p>';
        }
        
    } catch (error) {
        console.error('AI分析错误:', error);
        insightDiv.style.background = 'transparent';
        insightDiv.style.padding = '0';
        insightDiv.style.borderLeft = 'none';
        insightDiv.innerHTML = `
            <div style="padding: 20px; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; border-left: 4px solid #ef4444; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <p style="margin: 0; color: #dc2626;"><strong>❌ 分析失败</strong></p>
                <p style="margin: 10px 0 0 0; color: #64748b; font-size: 0.9em;">${error.message}</p>
            </div>
        `;
    } finally {
        // 恢复按钮
        button.disabled = false;
        button.innerHTML = '🤖 AI分析此图表';
    }
}

/**
 * 生成图表上下文信息
 */
function generateChartContext(chartType, data, chartTitle) {
    const city = cityName || '全国';
    
    // 全国对比页面的图表
    if (chartTitle) {
        // 特殊处理户型对比
        if (chartTitle.includes('户型') && data.summary) {
            const citiesCount = data.summary.cities_with_data;
            const totalTypes = data.summary.total_house_types;
            const commonTypes = data.summary.common_types || [];
            const commonTypesText = commonTypes.slice(0, 3).map((item, i) => 
                `${i+1}. ${item.type}（${item.cities_count}个城市主流）`
            ).join('；');
            return `这是全国户型分布对比，共${citiesCount}个城市有户型数据，包含${totalTypes}种户型。最常见户型：${commonTypesText}。`;
        }
        return `这是${chartTitle}，展示了多个城市的对比数据。`;
    }
    
    // 单城市页面的图表
    switch (chartType) {
        case 'trend':
            if (data.prices && data.months) {
                const minPrice = Math.min(...data.prices);
                const maxPrice = Math.max(...data.prices);
                const avgPrice = (data.prices.reduce((sum, p) => sum + p, 0) / data.prices.length).toFixed(2);
                return `这是${city}的月度价格趋势图，共${data.months.length}个月数据，价格从${minPrice.toFixed(2)}万元到${maxPrice.toFixed(2)}万元，平均${avgPrice}万元。`;
            }
            break;
        
        case 'priceRange':
            if (data.counts && data.ranges) {
                const totalCount = data.counts.reduce((sum, c) => sum + c, 0);
                const mostPopularIdx = data.counts.indexOf(Math.max(...data.counts));
                return `这是${city}的价格区间分布图，共${totalCount}套房源，分布在${data.ranges.length}个价格区间，最集中的区间是${data.ranges[mostPopularIdx]}。`;
            }
            break;
        
        case 'area':
            if (data.counts && data.ranges) {
                const totalArea = data.counts.reduce((sum, c) => sum + c, 0);
                const popularAreaIdx = data.counts.indexOf(Math.max(...data.counts));
                return `这是${city}的户型面积分布图，共${totalArea}套房源，最受欢迎的是${data.ranges[popularAreaIdx]}。`;
            }
            break;
        
        case 'boxplot':
            return `这是${city}的价格分布箱线图，展示了价格的统计分布特征，包括最小值、四分位数、中位数、最大值和平均值。`;
        
        case 'radar':
            return `这是${city}的投资综合评分雷达图，从价格趋势、成交量、稳定性、投资指数、市场活跃度五个维度进行评分。`;
        
        case 'violin':
            return `这是${city}的价格分布小提琴图，"胖"的部分表示该价格段房源多，"瘦"的部分表示房源少，能更直观地看出价格集中区间。`;
        
        case 'heatmap':
            return `这是${city}的区域-时间价格热力图，颜色越深表示该区域在该时间段的价格越高。横向看区域随时间的变化，纵向看不同区域在同一时间的差异。`;
        
        case 'waterfall':
            return `这是${city}的价格变化瀑布图，将总价格变化拆解为市场趋势、区域发展、政策影响等因素，清晰展示各因素的贡献度。`;
        
        case 'house-type':
            if (data.summary && data.distribution) {
                const mainType = data.summary.main_type;
                const mainPercentage = data.summary.main_percentage;
                const totalTypes = data.summary.total_types;
                const top5 = data.distribution.slice(0, 5);
                const top5Text = top5.map((item, i) => 
                    `${i+1}. ${item.house_type}：${item.count}套（${item.percentage}%），均价${item.avg_price}万元`
                ).join('；');
                return `这是${city}的户型分析图表。主流户型是${mainType}（占比${mainPercentage}%），共有${totalTypes}种户型。Top 5户型分布：${top5Text}。`;
            }
            return `这是${city}的户型分析图表，展示了各种户型（几室几厅）的分布和价格对比。`;
        
        default:
            break;
    }
    
    return `这是${city}的${chartType}图表，包含相关数据和分析。`;
}

/**
 * HTML转义
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 简单的 Markdown 渲染
 */
function renderMarkdown(text) {
    if (!text) return '';
    
    // 转义 HTML（防止 XSS）
    let html = escapeHtml(text);
    
    // 处理 Markdown 格式
    // 加粗 **text** 或 __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong style="color: #1e40af;">$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong style="color: #1e40af;">$1</strong>');
    
    // 斜体 *text* 或 _text_
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // 标题 ## 或 ###
    html = html.replace(/^### (.+)$/gm, '<h4 style="color: #667eea; margin: 15px 0 10px 0; font-size: 1em;">$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3 style="color: #667eea; margin: 20px 0 10px 0; font-size: 1.1em;">$1</h3>');
    
    // 列表项 - 或 *
    html = html.replace(/^[-*] (.+)$/gm, '<li style="margin: 5px 0; margin-left: 20px;">$1</li>');
    
    // 数字列表
    html = html.replace(/^(\d+)\. (.+)$/gm, '<div style="margin: 8px 0; padding-left: 20px;"><span style="color: #667eea; font-weight: 600;">$1.</span> $2</div>');
    
    // 段落（连续换行变段落）
    const paragraphs = html.split('\n').filter(p => p.trim());
    html = paragraphs.map(p => {
        // 已经是 HTML 标签的不再包裹
        if (p.startsWith('<h') || p.startsWith('<li') || p.startsWith('<div')) {
            return p;
        }
        return `<p style="margin: 10px 0; line-height: 1.8;">${p}</p>`;
    }).join('');
    
    return html;
}

/**
 * 一键AI洞察 - 分析整个报告
 */
async function quickAIInsight() {
    // 收集所有关键数据
    const insights = {
        city: cityName,
        investment_index: analysisData.investment_index,
        price_trend: analysisData.price_trend.overall_trend,
        volatility: analysisData.volatility_analysis,
        market_activity: analysisData.market_activity
    };
    
    // TODO: 实现完整的报告分析
    alert('一键AI洞察功能开发中...');
}
