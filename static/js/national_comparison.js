// 全国对比分析页面脚本

let comparisonData = null;

// 完整的颜色方案（支持最多25个省份）
const colorScheme = {
    borderColors: [
        '#667eea', // 紫色 - 北京
        '#10b981', // 绿色 - 上海
        '#f59e0b', // 橙色 - 天津
        '#ef4444', // 红色 - 重庆
        '#8b5cf6', // 紫罗兰 - 安徽
        '#ec4899', // 粉色 - 河北
        '#06b6d4', // 青色 - 黑龙江
        '#84cc16', // 青柠 - 江苏
        '#f97316', // 深橙 - 山东
        '#a855f7', // 亮紫 - 山西
        '#14b8a6', // 青绿 - 河南
        '#f43f5e', // 玫瑰红 - 江西
        '#3b82f6', // 蓝色 - 浙江
        '#eab308', // 黄色 - 福建
        '#6366f1', // 靛蓝 - 辽宁
        '#d946ef', // 品红 - 新疆
        '#22c55e', // 翠绿 - 湖北
        '#fb923c', // 浅橙 - 湖南
        '#a78bfa', // 淡紫 - 广西
        '#fbbf24', // 金黄 - 宁夏
        '#0ea5e9', // 天蓝 - 吉林
        '#f472b6', // 亮粉 - 内蒙古
        '#34d399', // 浅绿 - 上海
        '#facc15', // 柠檬黄
        '#818cf8'  // 灰紫
    ],
    backgroundColors: [
        'rgba(102, 126, 234, 0.15)',
        'rgba(16, 185, 129, 0.15)',
        'rgba(245, 158, 11, 0.15)',
        'rgba(239, 68, 68, 0.15)',
        'rgba(139, 92, 246, 0.15)',
        'rgba(236, 72, 153, 0.15)',
        'rgba(6, 182, 212, 0.15)',
        'rgba(132, 204, 22, 0.15)',
        'rgba(249, 115, 22, 0.15)',
        'rgba(168, 85, 247, 0.15)',
        'rgba(20, 184, 166, 0.15)',
        'rgba(244, 63, 94, 0.15)',
        'rgba(59, 130, 246, 0.15)',
        'rgba(234, 179, 8, 0.15)',
        'rgba(99, 102, 241, 0.15)',
        'rgba(217, 70, 239, 0.15)',
        'rgba(34, 197, 94, 0.15)',
        'rgba(251, 146, 60, 0.15)',
        'rgba(167, 139, 250, 0.15)',
        'rgba(251, 191, 36, 0.15)',
        'rgba(14, 165, 233, 0.15)',
        'rgba(244, 114, 182, 0.15)',
        'rgba(52, 211, 153, 0.15)',
        'rgba(250, 204, 21, 0.15)',
        'rgba(129, 140, 248, 0.15)'
    ]
};

// 动态获取颜色（支持无限省份）
function getColor(index, opacity = 1) {
    const colors = [
        [102, 126, 234], [16, 185, 129], [245, 158, 11], [239, 68, 68],
        [139, 92, 246], [236, 72, 153], [6, 182, 212], [132, 204, 22],
        [249, 115, 22], [168, 85, 247], [20, 184, 166], [244, 63, 94],
        [59, 130, 246], [234, 179, 8], [99, 102, 241], [217, 70, 239],
        [34, 197, 94], [251, 146, 60], [167, 139, 250], [251, 191, 36],
        [14, 165, 233], [244, 114, 182], [52, 211, 153], [250, 204, 21],
        [129, 140, 248]
    ];
    const colorIndex = index % colors.length;
    const [r, g, b] = colors[colorIndex];
    return opacity === 1 ? `rgb(${r}, ${g}, ${b})` : `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// 页面加载完成后获取数据
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/api/national-comparison');
        const result = await response.json();
        
        if (result.success) {
            comparisonData = result.comparison;
            renderComparison();
            loadAIOverview();  // 加载AI概览
        } else {
            showError('数据加载失败');
        }
    } catch (error) {
        console.error('Error loading comparison:', error);
        showError('数据加载失败: ' + error.message);
    }
});

// 加载AI概览分析（流式）
async function loadAIOverview() {
    const contentDiv = document.getElementById('ai-overview-content');
    contentDiv.innerHTML = '<p style="opacity: 0.8; text-align: center;">🤖 AI正在思考中...</p>';
    
    // 等待角色加载完成
    const role = await ensureRoleLoaded() || 'investment_advisor';
    console.log('Loading national AI overview with role:', role);
    
    // 使用EventSource接收流式数据（传递role参数）
    const eventSource = new EventSource(`/api/national-comparison/ai-overview-stream?role=${role}`);
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
                // 使用 Markdown 渲染
                contentDiv.innerHTML = renderMarkdown(fullText);
                
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

// 刷新AI概览
function refreshAIOverview() {
    document.getElementById('ai-overview-content').innerHTML = `
        <div class="spinner" style="margin: 50px auto;"></div>
        <p style="text-align: center;">AI正在重新分析数据...</p>
    `;
    loadAIOverview();
}

function renderComparison() {
    document.getElementById('loading-analysis').style.display = 'none';
    document.getElementById('analysis-content').style.display = 'block';
    document.getElementById('analysis-time').textContent = new Date().toLocaleString('zh-CN');
    
    renderOverview();
    renderInvestmentComparison();
    renderPriceComparison();
    renderAreaComparison();  // 新增平均面积对比
    renderMarketScale();
    renderGrowthRates();
    renderVolatility();
    renderAffordability();
    renderRecommendations();
    renderRegionalCharacteristics();
}

function renderOverview() {
    const data = comparisonData.overview;
    const container = document.getElementById('overview-stats');
    
    const stats = [
        { label: '总成交量', value: formatNumber(data.total_transactions_all), unit: '套' },
        { label: '价格最高城市', value: data.highest_price_city, unit: '' },
        { label: '价格最低城市', value: data.lowest_price_city, unit: '' },
        { label: '最活跃城市', value: data.most_active_city, unit: '' }
    ];
    
    container.innerHTML = stats.map(stat => `
        <div class="stat-box">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}<span class="stat-unit">${stat.unit}</span></div>
        </div>
    `).join('');
}

function renderInvestmentComparison() {
    const data = comparisonData.investment_scores.scores;
    const container = document.getElementById('investment-cards');
    
    container.innerHTML = data.map((city, index) => `
        <div class="city-card">
            <div class="city-card-header">
                <div class="city-name">${city.city}</div>
                <div class="rank-badge rank-${index + 1}">
                    ${index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'} 第${index + 1}名
                </div>
            </div>
            <div class="stat-value" style="text-align: center; margin: 20px 0;">
                ${city.total_score}<span class="stat-unit">分</span>
            </div>
            <div style="text-align: center; color: #667eea; font-weight: 600; margin-bottom: 15px;">
                ${city.level}
            </div>
            <div style="font-size: 0.9em; color: #64748b; line-height: 1.6;">
                ${city.recommendation}
            </div>
        </div>
    `).join('');
    
    // 绘制投资指数对比图
    const ctx = document.getElementById('investment-chart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['总评分', '价格趋势', '成交量趋势', '市场稳定性'],
            datasets: data.map((city, index) => ({
                label: city.city,
                data: [
                    city.total_score,
                    50 + city.price_trend,
                    50 + city.volume_trend,
                    city.stability
                ],
                borderColor: getColor(index, 1),
                backgroundColor: getColor(index, 0.2),
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });
    
    // 保存数据供AI分析
    saveChartData('investment-chart', {
        cities: data.map(c => c.city),
        scores: data.map(c => ({
            city: c.city,
            totalScore: c.total_score,
            level: c.level,
            priceTrend: c.price_trend,
            volumeTrend: c.volume_trend,
            stability: c.stability,
            recommendation: c.recommendation
        })),
        topRanked: comparisonData.investment_scores.top_ranked
    });
}

function renderPriceComparison() {
    const priceData = comparisonData.price_comparison.price_comparison;
    const unitPriceData = comparisonData.price_comparison.unit_price_comparison;
    
    // 价格统计卡片
    const container = document.getElementById('price-stats');
    container.innerHTML = `
        <div class="stat-box">
            <div class="stat-label">价格差距</div>
            <div class="stat-value">${formatNumber(comparisonData.price_comparison.price_gap)}<span class="stat-unit">万元</span></div>
        </div>
        <div class="stat-box">
            <div class="stat-label">价格倍数</div>
            <div class="stat-value">${comparisonData.price_comparison.price_ratio}<span class="stat-unit">倍</span></div>
        </div>
        <div class="stat-box">
            <div class="stat-label">差距评级</div>
            <div class="stat-value">${comparisonData.price_comparison.price_disparity_level}</div>
        </div>
    `;
    
    // 绘制价格对比图
    const ctx = document.getElementById('price-comparison-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: priceData.map(c => c.city),
            datasets: [
                {
                    label: '平均成交价（万元）',
                    data: priceData.map(c => c.mean),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    yAxisID: 'y'
                },
                {
                    label: '平均单价（元/m²）',
                    data: unitPriceData.map(c => c.mean),
                    backgroundColor: 'rgba(124, 58, 237, 0.8)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: '平均成交价（万元）' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: '平均单价（元/m²）' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
    
    // 保存数据供AI分析
    saveChartData('price-comparison-chart', {
        cities: priceData.map(c => c.city),
        avgPrice: priceData.map(c => ({ city: c.city, price: c.mean })),
        unitPrice: unitPriceData.map(c => ({ city: c.city, price: c.mean })),
        priceGap: comparisonData.price_comparison.price_gap,
        priceRatio: comparisonData.price_comparison.price_ratio
    });
}

function renderAreaComparison() {
    const areaData = comparisonData.overview.cities;
    
    // 排序：按平均面积降序
    const sortedData = [...areaData].sort((a, b) => b.avg_area - a.avg_area);
    
    // 计算统计信息
    const areas = areaData.map(c => c.avg_area);
    const maxArea = Math.max(...areas);
    const minArea = Math.min(...areas);
    const avgArea = areas.reduce((sum, val) => sum + val, 0) / areas.length;
    
    // 面积统计卡片
    const container = document.getElementById('area-stats');
    container.innerHTML = `
        <div class="stat-box">
            <div class="stat-label">最大面积</div>
            <div class="stat-value">${maxArea.toFixed(1)}<span class="stat-unit">m²</span></div>
            <div class="stat-label" style="font-size: 0.85em; margin-top: 5px;">${sortedData[0].city}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">最小面积</div>
            <div class="stat-value">${minArea.toFixed(1)}<span class="stat-unit">m²</span></div>
            <div class="stat-label" style="font-size: 0.85em; margin-top: 5px;">${sortedData[sortedData.length - 1].city}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">全国平均</div>
            <div class="stat-value">${avgArea.toFixed(1)}<span class="stat-unit">m²</span></div>
        </div>
        <div class="stat-box">
            <div class="stat-label">面积差距</div>
            <div class="stat-value">${(maxArea - minArea).toFixed(1)}<span class="stat-unit">m²</span></div>
        </div>
    `;
    
    // 绘制平均面积对比图
    const ctx = document.getElementById('area-comparison-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(c => c.city),
            datasets: [{
                label: '平均面积（m²）',
                data: sortedData.map(c => c.avg_area),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(6, 182, 212, 0.8)',
                    'rgba(132, 204, 22, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(14, 165, 233, 0.8)',
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(217, 70, 239, 0.8)'
                ].slice(0, sortedData.length),
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(236, 72, 153, 1)',
                    'rgba(6, 182, 212, 1)',
                    'rgba(132, 204, 22, 1)',
                    'rgba(249, 115, 22, 1)',
                    'rgba(168, 85, 247, 1)',
                    'rgba(14, 165, 233, 1)',
                    'rgba(234, 179, 8, 1)',
                    'rgba(217, 70, 239, 1)'
                ].slice(0, sortedData.length),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: '各城市平均成交面积对比（m²）',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} m²`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '平均面积（m²）'
                    }
                }
            }
        }
    });
    
    // 保存数据供AI分析
    saveChartData('area-comparison-chart', {
        cities: sortedData.map(c => c.city),
        areas: sortedData.map(c => ({ city: c.city, area: c.avg_area })),
        maxArea: maxArea,
        minArea: minArea,
        avgArea: avgArea,
        areaGap: maxArea - minArea
    });
}

function renderMarketScale() {
    const data = comparisonData.market_scale.scale_data;
    
    const ctx = document.getElementById('market-scale-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(c => c.city),
            datasets: [
                {
                    label: '总成交量（套）',
                    data: data.map(c => c.total_transactions),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)'
                },
                {
                    label: '总成交额（万元）',
                    data: data.map(c => c.total_value),
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    hidden: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // 保存数据供AI分析
    saveChartData('market-scale-chart', {
        cities: data.map(c => c.city),
        transactions: data.map(c => ({ city: c.city, count: c.total_transactions })),
        totalValue: data.map(c => ({ city: c.city, value: c.total_value })),
        totalScale: comparisonData.market_scale.total_market_size
    });
}

function renderGrowthRates() {
    const data = comparisonData.growth_rates.growth_data;
    const summary = document.getElementById('growth-summary');
    
    summary.innerHTML = `
        <div class="info-cards">
            ${data.map(city => {
                const trendClass = city.avg_annual_growth >= 0 ? 'trend-up' : 'trend-down';
                return `
                    <div class="info-card">
                        <div class="info-card-title">${city.city}</div>
                        <div class="info-card-content">
                            <div style="font-size: 2em; font-weight: 700; margin: 15px 0;" class="${trendClass}">
                                ${city.avg_annual_growth > 0 ? '+' : ''}${city.avg_annual_growth}%
                            </div>
                            <div>趋势：${city.trend_direction}</div>
                            <div>稳定性：${city.growth_stability}</div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        <div style="margin-top: 20px; padding: 20px; background: #f8fafc; border-radius: 8px;">
            <strong>整体趋势：</strong>${comparisonData.growth_rates.overall_trend}
            <br>
            <strong>最佳表现：</strong>${comparisonData.growth_rates.best_performer} 
            (${comparisonData.growth_rates.best_growth_rate > 0 ? '+' : ''}${comparisonData.growth_rates.best_growth_rate}%)
        </div>
    `;
    
    // 绘制增长率对比图
    const ctx = document.getElementById('growth-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data[0].yearly_details.map(y => y.year + '年'),
            datasets: data.map((city, index) => ({
                label: city.city,
                data: city.yearly_details.map(y => y.avg_price),
                borderColor: getColor(index, 1),
                backgroundColor: getColor(index, 0.1),
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: getColor(index, 1),
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '年度价格走势对比',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' 万元';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '平均成交价（万元）',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '年份',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
    
    // 保存数据供AI分析
    saveChartData('growth-chart', {
        cities: data.map(c => c.city),
        annualGrowth: data.map(c => ({ city: c.city, growth: c.avg_annual_growth, trend: c.trend_direction })),
        yearlyDetails: data.map(c => ({ city: c.city, details: c.yearly_details })),
        bestPerformer: comparisonData.growth_rates.best_performer,
        overallTrend: comparisonData.growth_rates.overall_trend
    });
}

function renderVolatility() {
    const data = comparisonData.volatility.volatility_data;
    const container = document.getElementById('volatility-cards');
    
    container.innerHTML = data.map(city => `
        <div class="city-card">
            <div class="city-card-header">
                <div class="city-name">${city.city}</div>
            </div>
            <div class="stat-value" style="text-align: center; margin: 20px 0;">
                ${city.cv}%<span class="stat-unit">CV</span>
            </div>
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="background: ${city.cv < 10 ? '#10b981' : city.cv < 15 ? '#f59e0b' : '#ef4444'}; 
                      color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                    ${city.stability}
                </span>
            </div>
            <div style="text-align: center; color: #64748b;">
                风险等级：${city.risk_level}
            </div>
        </div>
    `).join('');
}

function renderAffordability() {
    const data = comparisonData.affordability.affordability_data;
    
    const ctx = document.getElementById('affordability-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(c => c.city),
            datasets: [
                {
                    label: '可负担房源占比（%）',
                    data: data.map(c => c.affordable_percent),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)'
                },
                {
                    label: '30%首付金额（万元）',
                    data: data.map(c => c.avg_down_payment),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    position: 'left',
                    title: { display: true, text: '可负担房源占比（%）' }
                },
                y1: {
                    position: 'right',
                    title: { display: true, text: '首付金额（万元）' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
    
    // 保存数据供AI分析
    saveChartData('affordability-chart', {
        cities: data.map(c => c.city),
        affordablePercent: data.map(c => ({ city: c.city, percent: c.affordable_percent })),
        downPayment: data.map(c => ({ city: c.city, payment: c.avg_down_payment })),
        mostAffordable: comparisonData.affordability.most_affordable
    });
}

function renderRecommendations() {
    const recs = comparisonData.recommendations;
    const role = getRole(); // 获取当前用户角色
    
    // 角色配置
    const roleConfig = {
        'first_time_buyer': {
            title: '🏠 首次购房者专属建议',
            subtitle: '为您筛选性价比高、适合刚需的优质房源城市',
            roleName: '首次购房者',
            data: recs.for_first_time_buyers,
            icon: '🏠',
            gradient: 'linear-gradient(135deg, #10b981, #34d399)'
        },
        'upgrader': {
            title: '🏡 改善型购房者专属建议',
            subtitle: '为您推荐品质生活升级的理想置业城市',
            roleName: '改善型购房者',
            data: recs.for_upgraders,
            icon: '🏡',
            gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)'
        },
        'investment_advisor': {
            title: '💼 投资顾问专属建议',
            subtitle: '基于投资回报率和市场潜力的专业分析',
            roleName: '投资顾问',
            data: recs.for_investors,
            icon: '💼',
            gradient: 'linear-gradient(135deg, #6366f1, #8b5cf6)'
        }
    };
    
    const config = roleConfig[role] || roleConfig['first_time_buyer'];
    
    // 更新标题
    const titleEl = document.getElementById('advice-title');
    const subtitleEl = document.getElementById('advice-subtitle');
    const roleTitleEl = document.getElementById('recommendation-role-title');
    const roleDisplayEl = document.getElementById('user-role-display');
    
    if (titleEl) titleEl.textContent = config.title;
    if (subtitleEl) subtitleEl.textContent = config.subtitle;
    if (roleTitleEl) {
        roleTitleEl.innerHTML = `${config.icon} 为您推荐的购房城市`;
    }
    if (roleDisplayEl) roleDisplayEl.textContent = config.roleName;
    
    // 渲染个性化推荐
    const container = document.getElementById('personalized-recommendations');
    if (container && config.data) {
        container.innerHTML = config.data.map((rec, index) => `
            <div class="recommendation-item" style="animation: slideIn 0.4s ease-out ${index * 0.1}s backwards;">
                <div class="recommendation-number" style="background: ${config.gradient};">${rec.priority}</div>
                <div style="flex: 1;">
                    <strong style="font-size: 1.1em; color: #1e293b;">${rec.city}</strong>
                    <p style="color: #64748b; font-size: 0.92em; margin: 6px 0 0 0; line-height: 1.5;">${rec.reason}</p>
                </div>
                <div style="text-align: right;">
                    <span style="
                        display: inline-block;
                        background: linear-gradient(135deg, #f0f4ff, #e8f0fe);
                        color: #4338ca;
                        padding: 4px 12px;
                        border-radius: 20px;
                        font-size: 0.8em;
                        font-weight: 600;
                    ">推荐指数 ${rec.priority}</span>
                </div>
            </div>
        `).join('');
    }
}

function renderRegionalCharacteristics() {
    const data = comparisonData.regional_characteristics.characteristics;
    const container = document.getElementById('regional-characteristics');
    
    container.innerHTML = data.map(city => `
        <div class="city-card">
            <div class="city-card-header">
                <div class="city-name">${city.city}</div>
            </div>
            <div style="margin: 15px 0;">
                <strong>高价区域 Top 3：</strong>
                ${city.high_price_areas.map(d => `
                    <div style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                        ${d.district}: <span style="color: #667eea; font-weight: 600;">
                        ${formatNumber(d.unit_price)} 元/m²</span>
                    </div>
                `).join('')}
            </div>
            <div style="margin: 15px 0;">
                <strong>性价比区域 Top 3：</strong>
                ${city.low_price_areas.map(d => `
                    <div style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                        ${d.district}: <span style="color: #10b981; font-weight: 600;">
                        ${formatNumber(d.unit_price)} 元/m²</span>
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: 15px; padding: 12px; background: #f8fafc; border-radius: 6px;">
                <strong>成交最活跃区域：</strong> ${city.most_active_areas[0].district}
                (${formatNumber(city.most_active_areas[0].volume)} 套)
            </div>
        </div>
    `).join('');
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('zh-CN');
}

function showError(message) {
    document.getElementById('loading-analysis').innerHTML = `
        <div style="color: #ef4444; font-size: 1.2em;">
            ❌ ${message}
        </div>
    `;
}

/**
 * 简单的 Markdown 渲染
 */
function renderMarkdown(text) {
    if (!text) return '';
    
    // 转义 HTML（防止 XSS）
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 处理 Markdown 格式
    // 加粗 **text** 或 __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong style="color: #1e3a5f; font-weight: 700;">$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong style="color: #1e3a5f; font-weight: 700;">$1</strong>');
    
    // 斜体 *text* 或 _text_（排除已处理的加粗）
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    
    // 标题 ### 或 ##
    html = html.replace(/^### (.+)$/gm, '<h4 style="color: #1e3a5f; margin: 20px 0 12px 0; font-size: 1.05em; font-weight: 600;">$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3 style="color: #1e3a5f; margin: 25px 0 15px 0; font-size: 1.15em; font-weight: 700;">$1</h3>');
    
    // 数字列表 1. 2. 3.
    html = html.replace(/^(\d+)\.\s+\*\*(.+?)\*\*(.*)$/gm, 
        '<div style="margin: 18px 0;"><span style="color: #667eea; font-weight: 700; font-size: 1.1em;">$1.</span> <strong style="color: #1e3a5f;">$2</strong>$3</div>');
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, 
        '<div style="margin: 12px 0; padding-left: 5px;"><span style="color: #667eea; font-weight: 600;">$1.</span> $2</div>');
    
    // 列表项 - 或 *
    html = html.replace(/^[-*]\s+(.+)$/gm, '<li style="margin: 8px 0; margin-left: 20px; list-style: disc;">$1</li>');
    
    // 段落（连续换行变段落）
    const lines = html.split('\n');
    html = lines.map(line => {
        const trimmed = line.trim();
        if (!trimmed) return '';
        // 已经是 HTML 标签的不再包裹
        if (trimmed.startsWith('<h') || trimmed.startsWith('<li') || trimmed.startsWith('<div')) {
            return trimmed;
        }
        return `<p style="margin: 15px 0; line-height: 1.9; text-shadow: 1px 1px 2px rgba(0,0,0,0.05);">${trimmed}</p>`;
    }).filter(line => line).join('');
    
    return html;
}
