/**
 * 3D房价地图 - 核心逻辑
 * 使用ECharts GL实现3D柱状图
 */

let mapChart;
let mapData = null;
let currentMonthIndex = 0;
let isPlaying = false;
let playInterval = null;
let currentViewMode = 'price';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadMapData();
    
    // 显示当前角色
    const role = getRole();
    const roleName = {
        'investment_advisor': '投资顾问视角',
        'first_time_buyer': '首次购房者视角',
        'upgrader': '改善型购房者视角'
    }[role];
    document.getElementById('role-badge').textContent = roleName;
});

/**
 * 加载地图数据
 */
async function loadMapData() {
    try {
        const response = await fetch(`/api/city/${cityNameEn}/map-data`);
        const result = await response.json();
        
        if (result.success) {
            mapData = result;
            initMap();
            setupTimeline();
            hideLoading();
        } else {
            alert('数据加载失败');
        }
    } catch (error) {
        console.error('数据加载错误:', error);
        alert('数据加载失败，请刷新重试');
    }
}

/**
 * 初始化地图
 */
function initMap() {
    mapChart = echarts.init(document.getElementById('map-3d'));
    
    // 初始化显示第一个月的数据
    updateMap(0);
    
    // 窗口大小变化时重新渲染
    window.addEventListener('resize', function() {
        mapChart.resize();
    });
}

/**
 * 更新地图显示
 */
function updateMap(monthIndex) {
    const targetMonth = mapData.months[monthIndex];
    currentMonthIndex = monthIndex;
    
    // 更新当前月份显示
    document.getElementById('current-month').textContent = targetMonth;
    document.getElementById('timeline').value = monthIndex;
    
    // 筛选当前月份的数据
    const monthData = mapData.data.filter(d => d.month === targetMonth);
    
    // 准备3D柱状图数据
    const chartData = prepareChartData(monthData);
    
    // 配置图表
    const option = get3DBarOption(chartData, targetMonth);
    
    // 渲染
    mapChart.setOption(option, true);
}

/**
 * 准备图表数据
 */
function prepareChartData(monthData) {
    // 创建区域索引映射
    const districtIndex = {};
    mapData.districts.forEach((district, index) => {
        districtIndex[district] = index;
    });
    
    const data = [];
    const maxValue = Math.max(...monthData.map(d => {
        if (currentViewMode === 'price') return d.avg_price;
        if (currentViewMode === 'volume') return d.volume;
        if (currentViewMode === 'unit') return d.avg_unit_price;
        return 0;
    }));
    
    monthData.forEach(item => {
        const x = districtIndex[item.district];
        const y = 0; // Y轴固定为0（区域在一行）
        
        let value, heightValue;
        if (currentViewMode === 'price') {
            value = item.avg_price;
            heightValue = (value / maxValue) * 100;
        } else if (currentViewMode === 'volume') {
            value = item.volume;
            heightValue = (value / maxValue) * 100;
        } else if (currentViewMode === 'unit') {
            value = item.avg_unit_price;
            heightValue = (value / maxValue) * 100;
        } else {
            // trend mode - 需要计算
            const summary = mapData.summary.find(s => s.district === item.district);
            value = summary ? summary.trend_percent : 0;
            heightValue = Math.abs(value) * 2; // 放大趋势显示
        }
        
        data.push({
            value: [x, y, heightValue],
            realValue: value,
            district: item.district,
            volume: item.volume,
            avg_price: item.avg_price,
            avg_unit_price: item.avg_unit_price
        });
    });
    
    return data;
}

/**
 * 获取3D柱状图配置
 */
function get3DBarOption(data, month) {
    // 根据角色调整显示
    const role = getRole();
    
    return {
        tooltip: {
            backgroundColor: 'rgba(30, 41, 59, 0.95)',
            borderColor: '#60a5fa',
            textStyle: {
                color: '#fff'
            },
            formatter: function(params) {
                const data = params.data;
                if (!data) return '';
                
                // 安全获取数据属性
                const district = data.district || '未知区域';
                const avgPrice = data.avg_price != null ? data.avg_price.toFixed(1) : '暂无';
                const volume = data.volume != null ? data.volume : '暂无';
                const avgUnitPrice = data.avg_unit_price != null ? data.avg_unit_price.toLocaleString() : '暂无';
                
                let html = `<strong style="font-size: 1.1em;">${district}</strong><br/>`;
                html += `<div style="margin-top: 8px;">`;
                
                if (currentViewMode === 'price') {
                    html += `💰 平均价格：<span style="color:#60a5fa">${avgPrice}万元</span><br/>`;
                } else if (currentViewMode === 'volume') {
                    html += `📊 成交量：<span style="color:#60a5fa">${volume}套</span><br/>`;
                } else if (currentViewMode === 'unit') {
                    html += `🏢 平均单价：<span style="color:#60a5fa">${avgUnitPrice}元/㎡</span><br/>`;
                } else if (currentViewMode === 'trend') {
                    const summary = mapData.summary.find(s => s.district === data.district);
                    const trend = summary ? summary.trend_percent : 0;
                    const trendText = trend > 0 ? '↗️ 上涨' : trend < 0 ? '↘️ 下跌' : '→ 持平';
                    html += `📈 价格趋势：<span style="color:${trend > 0 ? '#ef4444' : trend < 0 ? '#10b981' : '#fbbf24'}">${trendText} ${Math.abs(trend).toFixed(1)}%</span><br/>`;
                }
                
                // 根据角色显示不同信息
                const price = data.avg_price || 0;
                if (role === 'first_time_buyer') {
                    html += `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.9em; opacity: 0.8;">`;
                    html += `💡 首次购房提示：<br/>`;
                    if (price < 200) {
                        html += `该区域价格相对友好，适合预算有限的购房者`;
                    } else if (price < 400) {
                        html += `该区域价格适中，建议结合地段和配套综合考虑`;
                    } else {
                        html += `该区域价格较高，建议谨慎评估自身承受能力`;
                    }
                    html += `</div>`;
                } else if (role === 'investment_advisor') {
                    const summary = mapData.summary.find(s => s.district === district);
                    if (summary) {
                        html += `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.9em; opacity: 0.8;">`;
                        html += `💼 投资价值：${summary.trend_percent > 2 ? '较高' : summary.trend_percent > 0 ? '中等' : '观望'}`;
                        html += `</div>`;
                    }
                }
                
                html += `</div>`;
                return html;
            }
        },
        visualMap: {
            show: false,
            min: 0,
            max: 100,
            inRange: {
                color: ['#10b981', '#fbbf24', '#ef4444']
            }
        },
        xAxis3D: {
            type: 'category',
            data: mapData.districts,
            axisLabel: {
                color: '#fff',
                fontSize: 10,
                interval: 0,
                rotate: 45
            },
            axisLine: {
                lineStyle: {
                    color: '#60a5fa'
                }
            }
        },
        yAxis3D: {
            type: 'value',
            axisLabel: {
                color: '#fff'
            },
            axisLine: {
                lineStyle: {
                    color: '#60a5fa'
                }
            }
        },
        zAxis3D: {
            type: 'value',
            name: getZAxisName(),
            nameTextStyle: {
                color: '#fff',
                fontSize: 14
            },
            axisLabel: {
                color: '#fff',
                formatter: function(value) {
                    return value.toFixed(0);
                }
            },
            axisLine: {
                lineStyle: {
                    color: '#60a5fa'
                }
            }
        },
        grid3D: {
            boxWidth: 200,
            boxDepth: 80,
            boxHeight: 100,
            viewControl: {
                distance: 250,
                alpha: 30,
                beta: 40,
                minDistance: 150,
                maxDistance: 400,
                rotateSensitivity: 1,
                zoomSensitivity: 1
            },
            light: {
                main: {
                    intensity: 1.2,
                    shadow: true
                },
                ambient: {
                    intensity: 0.5
                }
            },
            environment: 'auto'
        },
        series: [{
            type: 'bar3D',
            data: data,  // 传递完整数据对象，包含区域名称等信息
            shading: 'realistic',
            label: {
                show: false
            },
            itemStyle: {
                opacity: 0.85
            },
            emphasis: {
                label: {
                    show: false
                },
                itemStyle: {
                    color: '#60a5fa',
                    opacity: 1
                }
            },
            barSize: [0.8, 0.8]
        }],
        animation: true,
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'quinticInOut'
    };
}

/**
 * 获取Z轴名称
 */
function getZAxisName() {
    if (currentViewMode === 'price') return '平均价格（万元）';
    if (currentViewMode === 'volume') return '成交量（套）';
    if (currentViewMode === 'unit') return '平均单价（元/㎡）';
    if (currentViewMode === 'trend') return '价格涨跌幅（%）';
    return '';
}

/**
 * 设置时间轴
 */
function setupTimeline() {
    const timeline = document.getElementById('timeline');
    timeline.max = mapData.months.length - 1;
    timeline.value = 0;
    
    document.getElementById('timeline-start').textContent = mapData.months[0];
    document.getElementById('timeline-end').textContent = mapData.months[mapData.months.length - 1];
    
    // 时间轴变化事件
    timeline.addEventListener('input', function() {
        const monthIndex = parseInt(this.value);
        updateMap(monthIndex);
    });
    
    // 播放按钮
    document.getElementById('play-btn').addEventListener('click', togglePlay);
}

/**
 * 切换播放/暂停
 */
function togglePlay() {
    const btn = document.getElementById('play-btn');
    
    if (isPlaying) {
        // 暂停
        clearInterval(playInterval);
        isPlaying = false;
        btn.textContent = '▶️ 播放动画';
    } else {
        // 播放
        isPlaying = true;
        btn.textContent = '⏸️ 暂停动画';
        
        playInterval = setInterval(function() {
            currentMonthIndex++;
            
            if (currentMonthIndex >= mapData.months.length) {
                currentMonthIndex = 0; // 循环播放
            }
            
            updateMap(currentMonthIndex);
        }, 1500); // 每1.5秒切换一次
    }
}

/**
 * 切换视图模式
 */
function changeViewMode(mode) {
    currentViewMode = mode;
    
    // 更新按钮状态
    document.querySelectorAll('.view-mode-btn').forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // 重新渲染
    updateMap(currentMonthIndex);
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
    const loading = document.getElementById('loading-3d');
    loading.style.opacity = '0';
    setTimeout(function() {
        loading.style.display = 'none';
    }, 500);
}

// 图表点击事件
document.getElementById('map-3d').addEventListener('click', function() {
    // 可以在这里添加点击某个区域的交互
});



