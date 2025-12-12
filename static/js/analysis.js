// 分析报告页面脚本

let analysisData = null;

// cityNameEn 和 cityName 已在 HTML 中通过模板注入
// 不需要在这里重新声明

// 页面加载完成后获取分析数据
document.addEventListener('DOMContentLoaded', async function() {
    console.log('[Analysis] 开始加载分析数据，城市:', cityNameEn);
    
    // 检查cityNameEn是否存在
    if (typeof cityNameEn === 'undefined' || !cityNameEn) {
        console.error('[Analysis] cityNameEn未定义');
        showError('页面配置错误：城市参数缺失');
        return;
    }
    
    // 设置AI概览中的城市名称
    const aiCityNameEl = document.getElementById('analysis-city-name-ai');
    if (aiCityNameEl) {
        aiCityNameEl.textContent = cityName;
    }
    
    try {
        const url = `/api/city/${cityNameEn}/deep-analysis`;
        console.log('[Analysis] 请求URL:', url);
        
        // 添加超时处理
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
        
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        
        console.log('[Analysis] 响应状态:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Analysis] 响应错误:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[Analysis] 获取到数据，keys:', Object.keys(result));
        
        if (result.success && result.analysis) {
            analysisData = result.analysis;
            console.log('[Analysis] 开始渲染分析数据，analysis keys:', Object.keys(analysisData));
            renderAnalysis();
            loadCityAIOverview();  // 加载AI概览
            
            // 触发自定义事件，通知内容过滤器数据已加载
            console.log('[Analysis] 触发 analysisDataLoaded 事件');
            document.dispatchEvent(new CustomEvent('analysisDataLoaded'));
        } else {
            console.error('[Analysis] 数据格式错误:', result);
            showError('数据格式错误: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('[Analysis] 请求超时');
            showError('数据加载超时，请刷新页面重试');
        } else {
            console.error('[Analysis] 加载分析数据失败:', error);
            showError('数据加载失败: ' + error.message + '，请刷新页面重试');
        }
    }
});

function renderAnalysis() {
    // 隐藏加载动画
    document.getElementById('loading-analysis').style.display = 'none';
    document.getElementById('analysis-content').style.display = 'block';
    
    // 设置分析时间
    document.getElementById('analysis-time').textContent = new Date().toLocaleString('zh-CN');
    
    // 渲染各个部分
    renderInvestmentIndex();
    renderBasicStats();
    
    // 使用ECharts渲染新图表
    renderPriceTrendECharts(analysisData.price_trend, 'trend-chart');
    renderPriceBoxPlot(analysisData.basic_stats, 'price-boxplot');
    renderInvestmentRadar(analysisData.investment_index, analysisData.volatility, 'investment-radar');
    
    // 渲染新增专业图表
    if (analysisData.violin_data) {
        renderPriceViolin(analysisData.violin_data, 'price-violin');
    }
    if (analysisData.heatmap_data) {
        renderDistrictHeatmapFull(analysisData.heatmap_data, 'district-heatmap');
    }
    if (analysisData.waterfall_data) {
        renderPriceWaterfall(analysisData.waterfall_data, 'price-waterfall');
    }
    
    renderVolatility();
    renderMarketActivity();
    renderYoY();
    
    // 使用ECharts渲染
    renderPriceRangeECharts(analysisData.price_range, 'price-range-chart');
    renderAreaDistributionECharts(analysisData.area_analysis, 'area-chart');
    
    renderDistrictAnalysis();
    renderSeasonality();
}

function renderInvestmentIndex() {
    const data = analysisData.investment_index;
    
    // 投资指数分数
    document.getElementById('investment-score').textContent = data.index_score;
    document.getElementById('investment-level').textContent = data.investment_level;
    
    // 子指标进度条
    const priceBar = document.getElementById('price-trend-bar');
    const volumeBar = document.getElementById('volume-trend-bar');
    const stabilityBar = document.getElementById('stability-bar');
    
    // 归一化分数到0-100
    const normalizeTrend = (score) => Math.max(0, Math.min(100, 50 + score));
    
    setTimeout(() => {
        priceBar.style.width = `${normalizeTrend(data.price_trend_score)}%`;
        volumeBar.style.width = `${normalizeTrend(data.volume_trend_score)}%`;
        stabilityBar.style.width = `${data.stability_score}%`;
    }, 300);
    
    document.getElementById('price-trend-score').textContent = data.price_trend_score.toFixed(1);
    document.getElementById('volume-trend-score').textContent = data.volume_trend_score.toFixed(1);
    document.getElementById('stability-score').textContent = data.stability_score.toFixed(1);
    
    // 投资建议
    document.getElementById('recommendation').textContent = data.recommendation;
    
    // 显示计算详情（如果有）
    if (data.calculation_details) {
        const details = data.calculation_details;
        const detailsHtml = `
            <div style="font-weight: 600; margin-bottom: 10px; color: #1e293b;">📋 计算详情</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <strong>价格趋势：</strong><br>
                    最近6月均价: ${details.recent_avg_price}万元<br>
                    之前6月均价: ${details.prev_avg_price}万元
                </div>
                <div>
                    <strong>成交量趋势：</strong><br>
                    最近6月: ${details.recent_volume}套<br>
                    之前6月: ${details.prev_volume}套
                </div>
                <div style="grid-column: 1 / -1;">
                    <strong>市场稳定性：</strong><br>
                    变异系数CV: ${details.cv_percentage}% 
                    <span style="
                        background: ${details.stability_level === '稳定' ? '#10b981' : details.stability_level === '一般' ? '#f59e0b' : '#ef4444'};
                        color: white;
                        padding: 2px 8px;
                        border-radius: 10px;
                        font-size: 0.85em;
                        margin-left: 5px;
                    ">${details.stability_level}</span>
                </div>
            </div>
        `;
        const detailsDiv = document.getElementById('calculation-details');
        if (detailsDiv) {
            detailsDiv.innerHTML = detailsHtml;
            detailsDiv.style.display = 'block';
        }
    }
}

function renderBasicStats() {
    const data = analysisData.basic_stats;
    const container = document.getElementById('basic-stats');
    
    const stats = [
        { label: '总成交量', value: formatNumber(data.total_transactions), unit: '套' },
        { label: '平均成交价', value: formatNumber(data.price.mean), unit: '万元' },
        { label: '中位数成交价', value: formatNumber(data.price.median), unit: '万元' },
        { label: '价格标准差', value: formatNumber(data.price.std), unit: '万元' },
        { label: '平均单价', value: formatNumber(data.unit_price.mean), unit: '元/m²' },
        { label: '中位数单价', value: formatNumber(data.unit_price.median), unit: '元/m²' },
        { label: '平均面积', value: formatNumber(data.area.mean), unit: 'm²' },
        { label: '价格区间', value: `${data.price.min}-${data.price.max}`, unit: '万元' }
    ];
    
    container.innerHTML = stats.map(stat => `
        <div class="stat-box">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}<span class="stat-unit">${stat.unit}</span></div>
        </div>
    `).join('');
}

function renderPriceTrend() {
    // 已迁移到ECharts，保留趋势摘要部分
    const data = analysisData.price_trend;
    const summary = data.overall_trend;
    
    // 趋势摘要
    const trendClass = summary.total_change_percent >= 0 ? 'trend-up' : 'trend-down';
    document.getElementById('trend-summary').innerHTML = `
        <div class="trend-item">
            <div class="trend-item-label">起始价格</div>
            <div class="trend-item-value">${summary.first_price} 万元</div>
            <div class="trend-item-label">${summary.first_month}</div>
        </div>
        <div class="trend-item">
            <div class="trend-item-label">当前价格</div>
            <div class="trend-item-value">${summary.last_price} 万元</div>
            <div class="trend-item-label">${summary.last_month}</div>
        </div>
        <div class="trend-item">
            <div class="trend-item-label">整体变化</div>
            <div class="trend-item-value ${trendClass}">
                ${summary.total_change_percent > 0 ? '+' : ''}${summary.total_change_percent}%
            </div>
            <div class="trend-item-label">${summary.trend_direction}</div>
        </div>
        <div class="trend-item">
            <div class="trend-item-label">最高点</div>
            <div class="trend-item-value">${data.peak_price} 万元</div>
            <div class="trend-item-label">${data.peak_month}</div>
        </div>
        <div class="trend-item">
            <div class="trend-item-label">最低点</div>
            <div class="trend-item-value">${data.lowest_price} 万元</div>
            <div class="trend-item-label">${data.lowest_month}</div>
        </div>
    `;
    
    // 图表渲染已迁移到ECharts（echarts_renderer.js）
}

function renderVolatility() {
    const data = analysisData.volatility;
    
    document.getElementById('volatility-analysis').innerHTML = `
        <div class="info-cards">
            <div class="info-card">
                <div class="info-card-title">变异系数</div>
                <div class="info-card-content">
                    <div style="font-size: 2em; font-weight: 700; color: #1e293b; margin: 15px 0;">
                        ${data.coefficient_of_variation}%
                    </div>
                    <div>稳定性评级：<strong>${data.stability_level}</strong></div>
                </div>
            </div>
            <div class="info-card">
                <div class="info-card-title">价格波动幅度</div>
                <div class="info-card-content">
                    <div style="font-size: 2em; font-weight: 700; color: #1e293b; margin: 15px 0;">
                        ${data.price_range} 万元
                    </div>
                    <div>波动比例：${data.price_range_percent}%</div>
                </div>
            </div>
            <div class="info-card">
                <div class="info-card-title">波动性分析</div>
                <div class="info-card-content">
                    <p>${data.volatility_description}</p>
                </div>
            </div>
        </div>
    `;
}

function renderMarketActivity() {
    const data = analysisData.market_activity;
    
    const html = `
        <div class="info-cards">
            <div class="info-card">
                <div class="info-card-title">月均成交量</div>
                <div class="info-card-content">
                    <div style="font-size: 2em; font-weight: 700; color: #1e293b; margin: 15px 0;">
                        ${formatNumber(data.monthly_average)} 套
                    </div>
                    <div>活跃度：<strong>${data.activity_level}</strong></div>
                </div>
            </div>
            <div class="info-card">
                <div class="info-card-title">成交量区间</div>
                <div class="info-card-content">
                    <p>最高：${formatNumber(data.monthly_max)} 套（${data.most_active_month}）</p>
                    <p>最低：${formatNumber(data.monthly_min)} 套（${data.least_active_month}）</p>
                </div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <h3 style="margin-bottom: 15px;">年度成交量分布</h3>
            <div class="stats-grid">
                ${data.yearly_data.map(year => `
                    <div class="stat-box">
                        <div class="stat-label">${year.year}年</div>
                        <div class="stat-value">${formatNumber(year.volume)}<span class="stat-unit">套</span></div>
                        <div class="stat-label">占比 ${year.market_share}%</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    document.getElementById('market-activity').innerHTML = html;
}

function renderYoY() {
    const data = analysisData.yoy_comparison.yearly_comparison;
    
    const table = document.getElementById('yoy-table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>年份</th>
                <th>平均成交价</th>
                <th>同比涨跌</th>
                <th>平均单价</th>
                <th>成交量</th>
                <th>成交量同比</th>
            </tr>
        </thead>
        <tbody>
            ${data.map(year => `
                <tr>
                    <td><strong>${year.year}</strong></td>
                    <td>${year.avg_price} 万元</td>
                    <td class="${year.yoy_price_change >= 0 ? 'trend-up' : 'trend-down'}">
                        ${year.yoy_price_change !== undefined ? 
                            (year.yoy_price_change > 0 ? '+' : '') + year.yoy_price_change + '%' : '-'}
                    </td>
                    <td>${formatNumber(year.avg_unit_price)} 元/m²</td>
                    <td>${formatNumber(year.volume)} 套</td>
                    <td class="${year.yoy_volume_change >= 0 ? 'trend-up' : 'trend-down'}">
                        ${year.yoy_volume_change !== undefined ? 
                            (year.yoy_volume_change > 0 ? '+' : '') + year.yoy_volume_change + '%' : '-'}
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
}

function renderPriceRange() {
    // 已迁移到ECharts（echarts_renderer.js中的renderPriceRangeECharts）
}

function renderAreaDistribution() {
    // 已迁移到ECharts（echarts_renderer.js中的renderAreaDistributionECharts）
}

function renderDistrictAnalysis() {
    const data = analysisData.district_deep.top_districts;
    
    const table = document.getElementById('district-table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>区域</th>
                <th>平均价格</th>
                <th>中位价格</th>
                <th>平均单价</th>
                <th>成交量</th>
                <th>价格稳定性</th>
            </tr>
        </thead>
        <tbody>
            ${data.map((district, index) => `
                <tr>
                    <td><strong>${index + 1}. ${district.district}</strong></td>
                    <td>${district.avg_price} 万元</td>
                    <td>${district.median_price} 万元</td>
                    <td>${formatNumber(district.avg_unit_price)} 元/m²</td>
                    <td>${formatNumber(district.volume)} 套</td>
                    <td>${district.price_stability}</td>
                </tr>
            `).join('')}
        </tbody>
    `;
}

function renderSeasonality() {
    const data = analysisData.seasonal.quarter_averages;
    
    document.getElementById('seasonal-analysis').innerHTML = `
        <div class="stats-grid">
            ${data.map(q => `
                <div class="stat-box">
                    <div class="stat-label">${q.quarter} 季度</div>
                    <div class="stat-value">${q.avg_price}<span class="stat-unit">万元</span></div>
                    <div class="stat-label">平均成交量: ${formatNumber(q.avg_volume)} 套</div>
                </div>
            `).join('')}
        </div>
    `;
}

function formatNumber(num) {
    return num.toLocaleString('zh-CN');
}

function showError(message) {
    document.getElementById('loading-analysis').innerHTML = `
        <div style="color: #ef4444; font-size: 1.2em;">
            ❌ ${message}
        </div>
    `;
}

// 加载城市AI概览分析（流式）
function loadCityAIOverview() {
    const contentDiv = document.getElementById('city-ai-overview-content');
    contentDiv.innerHTML = '<p style="opacity: 0.8; text-align: center;">🤖 AI正在分析数据...</p>';
    
    // 获取当前AI角色
    const role = getRole();
    
    console.log('Loading AI overview with role:', role);  // 调试日志
    
    // 使用EventSource接收流式数据
    const eventSource = new EventSource(`/api/city/${cityNameEn}/ai-overview-stream?role=${role}`);
    let fullText = '';
    
    eventSource.onmessage = function(event) {
        if (event.data === '[DONE]') {
            eventSource.close();
            return;
        }
        
        try {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                contentDiv.innerHTML = `<p style="opacity: 0.8;">❌ ${data.error}</p>`;
                eventSource.close();
                return;
            }
            
            if (data.content) {
                fullText += data.content;
                // 实时显示累积的文本
                // 按段落分隔
                const paragraphs = fullText.split('\n').filter(p => p.trim());
                contentDiv.innerHTML = paragraphs.map(p => 
                    `<p style="margin: 15px 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">${p}</p>`
                ).join('');
                
                // 自动滚动到底部
                contentDiv.scrollTop = contentDiv.scrollHeight;
            }
        } catch (e) {
            console.error('Error parsing SSE data:', e);
        }
    };
    
    eventSource.onerror = function(error) {
        console.error('SSE Error:', error);
        if (!fullText) {
            contentDiv.innerHTML = '<p style="opacity: 0.8;">AI分析加载失败，请刷新重试</p>';
        }
        eventSource.close();
    };
}

// 刷新城市AI概览
function refreshCityAIOverview() {
    document.getElementById('city-ai-overview-content').innerHTML = `
        <div class="spinner" style="margin: 40px auto;"></div>
        <p style="text-align: center;">AI正在重新分析数据...</p>
    `;
    loadCityAIOverview();
}

