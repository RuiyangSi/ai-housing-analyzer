/**
 * ECharts渲染模块
 * 使用ECharts创建专业的数据可视化
 */

/**
 * 渲染价格趋势图（K线风格）
 */
function renderPriceTrendECharts(data, containerId = 'trend-chart') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    const monthly = data.monthly_data;
    
    // 保存数据供AI分析
    saveChartData('trend', {
        months: monthly.map(m => m['年月']),
        prices: monthly.map(m => m['成交价（万元）']),
        changes: monthly.map(m => m['环比'])
    });
    
    const option = {
        title: {
            text: '月度价格趋势',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#667eea',
            borderWidth: 1,
            textStyle: {
                color: '#1e293b'
            },
            formatter: function(params) {
                let result = `<strong>${params[0].name}</strong><br/>`;
                params.forEach(param => {
                    result += `${param.marker} ${param.seriesName}: <strong>${param.value}</strong> 万元<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: ['平均成交价'],
            top: 35
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 80,
            containLabel: true
        },
        toolbox: {
            feature: {
                dataZoom: {
                    yAxisIndex: 'none',
                    title: {
                        zoom: '区域缩放',
                        back: '还原'
                    }
                },
                restore: {title: '还原'},
                saveAsImage: {
                    title: '保存为图片',
                    pixelRatio: 2
                }
            },
            right: 20
        },
        dataZoom: [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                start: 0,
                end: 100,
                height: 30,
                bottom: 20
            }
        ],
        xAxis: {
            type: 'category',
            data: monthly.map(m => m['年月']),
            boundaryGap: false,
            axisLabel: {
                rotate: 45,
                fontSize: 11
            }
        },
        yAxis: {
            type: 'value',
            name: '成交价（万元）',
            axisLabel: {
                formatter: '{value}'
            }
        },
        series: [
            {
                name: '平均成交价',
                type: 'line',
                data: monthly.map(m => m['成交价（万元）']),
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        {offset: 0, color: '#667eea'},
                        {offset: 1, color: '#764ba2'}
                    ])
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {offset: 0, color: 'rgba(102, 126, 234, 0.3)'},
                        {offset: 1, color: 'rgba(102, 126, 234, 0.05)'}
                    ])
                },
                emphasis: {
                    focus: 'series',
                    itemStyle: {
                        borderColor: '#667eea',
                        borderWidth: 2
                    }
                },
                markPoint: {
                    data: [
                        {type: 'max', name: '最高点'},
                        {type: 'min', name: '最低点'}
                    ],
                    label: {
                        formatter: '{c} 万元'
                    }
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ],
                    label: {
                        formatter: '均值: {c} 万元'
                    }
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染价格区间分布（ECharts柱状图）
 */
function renderPriceRangeECharts(data, containerId = 'price-range-chart') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    const distribution = data.distribution;
    
    // 保存数据供AI分析
    saveChartData('priceRange', {
        ranges: distribution.map(d => d.range),
        counts: distribution.map(d => d.count),
        percentages: distribution.map(d => d.percentage)
    });
    
    const option = {
        title: {
            text: '价格区间分布',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#667eea',
            borderWidth: 1,
            formatter: function(params) {
                const item = params[0];
                const percentage = distribution[item.dataIndex].percentage;
                return `<strong>${item.name}</strong><br/>
                        ${item.marker} 成交量: <strong>${item.value}</strong> 套<br/>
                        占比: <strong>${percentage.toFixed(2)}%</strong>`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 60,
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {
                    title: '保存为图片',
                    pixelRatio: 2
                }
            },
            right: 20
        },
        xAxis: {
            type: 'category',
            data: distribution.map(d => d.range),
            axisLabel: {
                rotate: 45,
                fontSize: 11
            }
        },
        yAxis: {
            type: 'value',
            name: '成交量（套）'
        },
        series: [
            {
                name: '成交量',
                type: 'bar',
                data: distribution.map(d => d.count),
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {offset: 0, color: '#667eea'},
                        {offset: 1, color: '#764ba2'}
                    ]),
                    borderRadius: [5, 5, 0, 0]
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            {offset: 0, color: '#764ba2'},
                            {offset: 1, color: '#667eea'}
                        ])
                    }
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}',
                    fontSize: 10
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染面积分布图（ECharts平滑曲线）
 */
function renderAreaDistributionECharts(data, containerId = 'area-chart') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    const distribution = data.distribution;
    
    // 保存数据供AI分析
    saveChartData('area', {
        ranges: distribution.map(d => d.category || d.range),
        counts: distribution.map(d => d.count),
        percentages: distribution.map(d => d.percentage)
    });
    
    const option = {
        title: {
            text: '户型面积分布',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#10b981',
            borderWidth: 1,
            formatter: function(params) {
                const item = params[0];
                const percentage = distribution[item.dataIndex].percentage;
                return `<strong>${item.name}</strong><br/>
                        ${item.marker} 成交量: <strong>${item.value}</strong> 套<br/>
                        占比: <strong>${percentage.toFixed(2)}%</strong>`;
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: 60,
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {
                    title: '保存为图片',
                    pixelRatio: 2
                }
            },
            right: 20
        },
        xAxis: {
            type: 'category',
            data: distribution.map(d => d.category || d.range),
            axisLabel: {
                fontSize: 11,
                rotate: 0
            }
        },
        yAxis: {
            type: 'value',
            name: '成交量（套）'
        },
        series: [
            {
                name: '成交量',
                type: 'line',
                data: distribution.map(d => d.count),
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: '#10b981'
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {offset: 0, color: 'rgba(16, 185, 129, 0.3)'},
                        {offset: 1, color: 'rgba(16, 185, 129, 0.05)'}
                    ])
                },
                emphasis: {
                    focus: 'series'
                },
                markPoint: {
                    data: [
                        {type: 'max', name: '最高峰'},
                    ],
                    label: {
                        formatter: '{c} 套'
                    }
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染价格小提琴图（价格分布密度可视化）
 */
function renderPriceViolin(violinData, containerId = 'price-violin') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!violinData || !violinData.stats) {
        console.warn('小提琴图数据不存在');
        container.innerHTML = '<div style="text-align: center; padding: 50px; color: #94a3b8;">数据不足，无法生成小提琴图</div>';
        return;
    }
    
    const chart = echarts.init(container);
    const stats = violinData.stats;
    const density = violinData.density;
    
    // 保存数据供AI分析
    saveChartData('violin', {
        stats: stats,
        density: density,
        distribution: '价格分布密度'
    });
    
    // 创建箱线图数据
    const boxplotData = [[
        stats.min,
        stats.q1,
        stats.median,
        stats.q3,
        stats.max
    ]];
    
    const option = {
        title: {
            text: '价格分布小提琴图',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#8b5cf6',
            borderWidth: 1
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: 100
        },
        xAxis: {
            type: 'category',
            data: ['价格分布'],
            axisLabel: {
                fontSize: 13,
                fontWeight: 600
            }
        },
        yAxis: {
            type: 'value',
            name: '成交价（万元）',
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        series: [
            // 箱线图层
            {
                name: '价格统计',
                type: 'boxplot',
                data: boxplotData,
                itemStyle: {
                    color: 'rgba(139, 92, 246, 0.3)',
                    borderColor: '#8b5cf6',
                    borderWidth: 2
                },
                tooltip: {
                    formatter: function(param) {
                        return `<strong>价格统计</strong><br/>
                                最大值: <strong>${param.data[4].toFixed(2)}</strong> 万元<br/>
                                Q3: <strong>${param.data[3].toFixed(2)}</strong> 万元<br/>
                                中位数: <strong>${param.data[2].toFixed(2)}</strong> 万元<br/>
                                Q1: <strong>${param.data[1].toFixed(2)}</strong> 万元<br/>
                                最小值: <strong>${param.data[0].toFixed(2)}</strong> 万元`;
                    }
                }
            },
            // 平均值标记
            {
                name: '平均值',
                type: 'scatter',
                data: [[0, stats.mean]],
                symbolSize: 15,
                itemStyle: {
                    color: '#ef4444'
                },
                label: {
                    show: true,
                    formatter: '均值\n{c}',
                    position: 'right',
                    color: '#ef4444',
                    fontSize: 11,
                    fontWeight: 600
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染区域价格热力图（时间-区域价格矩阵）
 */
function renderDistrictHeatmapFull(heatmapData, containerId = 'district-heatmap') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!heatmapData || !heatmapData.data || heatmapData.data.length === 0) {
        console.warn('热力图数据不存在');
        container.innerHTML = '<div style="text-align: center; padding: 50px; color: #94a3b8;">数据不足，无法生成热力图</div>';
        return;
    }
    
    const chart = echarts.init(container);
    
    // 转换数据格式为 [x, y, value]
    const seriesData = [];
    for (let i = 0; i < heatmapData.districts.length; i++) {
        for (let j = 0; j < heatmapData.months.length; j++) {
            if (heatmapData.data[i][j] > 0) {
                seriesData.push([j, i, heatmapData.data[i][j]]);
            }
        }
    }
    
    // 保存数据供AI分析
    saveChartData('heatmap', {
        districts: heatmapData.districts,
        months: heatmapData.months,
        data: heatmapData.data,
        minPrice: heatmapData.min_price,
        maxPrice: heatmapData.max_price
    });
    
    const option = {
        title: {
            text: '区域-时间价格热力图',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            position: 'top',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#06b6d4',
            borderWidth: 1,
            formatter: function(params) {
                return `<strong>${heatmapData.districts[params.data[1]]}</strong><br/>
                        ${heatmapData.months[params.data[0]]}<br/>
                        单价: <strong>${params.data[2].toFixed(0)}</strong> 元/m²`;
            }
        },
        grid: {
            left: '15%',
            right: '10%',
            bottom: '15%',
            top: 80
        },
        xAxis: {
            type: 'category',
            data: heatmapData.months,
            splitArea: {
                show: true
            },
            axisLabel: {
                rotate: 45,
                fontSize: 10
            }
        },
        yAxis: {
            type: 'category',
            data: heatmapData.districts,
            splitArea: {
                show: true
            },
            axisLabel: {
                fontSize: 11
            }
        },
        visualMap: {
            min: heatmapData.min_price,
            max: heatmapData.max_price,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
            inRange: {
                color: ['#e0f2fe', '#0ea5e9', '#0369a1', '#075985']
            },
            text: ['高', '低'],
            textStyle: {
                color: '#1e293b'
            }
        },
        series: [{
            name: '单价',
            type: 'heatmap',
            data: seriesData,
            label: {
                show: false
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染价格变化瀑布图（因素拆解）
 */
function renderPriceWaterfall(waterfallData, containerId = 'price-waterfall') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!waterfallData || !waterfallData.factors || waterfallData.factors.length === 0) {
        console.warn('瀑布图数据不存在');
        container.innerHTML = '<div style="text-align: center; padding: 50px; color: #94a3b8;">数据不足，无法生成瀑布图</div>';
        return;
    }
    
    const chart = echarts.init(container);
    const factors = waterfallData.factors;
    
    // 保存数据供AI分析
    saveChartData('waterfall', {
        factors: factors,
        totalChange: waterfallData.total_change,
        changePercent: waterfallData.total_change_percent
    });
    
    // 构建瀑布图数据
    const seriesData = [];
    let cumulative = 0;
    
    factors.forEach((factor, index) => {
        if (factor.type === 'start' || factor.type === 'end') {
            seriesData.push({
                value: factor.value,
                itemStyle: {
                    color: factor.type === 'start' ? '#94a3b8' : '#10b981'
                }
            });
        } else {
            seriesData.push({
                value: Math.abs(factor.value),
                itemStyle: {
                    color: factor.type === 'increase' ? '#10b981' : '#ef4444'
                }
            });
        }
    });
    
    const option = {
        title: {
            text: '价格变化因素拆解（瀑布图）',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#f59e0b',
            borderWidth: 1,
            formatter: function(params) {
                const factor = factors[params[0].dataIndex];
                return `<strong>${factor.name}</strong><br/>
                        ${factor.type === 'start' || factor.type === 'end' ? 
                            `价格: <strong>${factor.value.toFixed(2)}</strong> 万元` :
                            `变化: <strong>${factor.value > 0 ? '+' : ''}${factor.value.toFixed(2)}</strong> 万元`
                        }`;
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: 80
        },
        xAxis: {
            type: 'category',
            data: factors.map(f => f.name),
            axisLabel: {
                rotate: 30,
                fontSize: 11
            }
        },
        yAxis: {
            type: 'value',
            name: '价格（万元）'
        },
        series: [{
            name: '价格变化',
            type: 'bar',
            stack: 'total',
            data: seriesData,
            label: {
                show: true,
                position: 'inside',
                formatter: function(params) {
                    const factor = factors[params.dataIndex];
                    if (factor.type === 'start' || factor.type === 'end') {
                        return factor.value.toFixed(0);
                    } else {
                        return (factor.value > 0 ? '+' : '') + factor.value.toFixed(0);
                    }
                },
                fontSize: 10,
                fontWeight: 600,
                color: '#fff'
            }
        }]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染价格箱线图（展示价格分布统计）
 */
function renderPriceBoxPlot(basicStats, containerId = 'price-boxplot') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // 检查数据是否存在
    if (!basicStats || !basicStats.price) {
        console.warn('价格统计数据不存在，跳过箱线图渲染');
        container.innerHTML = '<div style="text-align: center; padding: 50px; color: #94a3b8;">数据不足，无法生成箱线图</div>';
        return;
    }
    
    const chart = echarts.init(container);
    const price = basicStats.price;
    
    // 使用后端提供的四分位数
    const q1 = price.q25;
    const q3 = price.q75;
    
    // 保存数据供AI分析
    saveChartData('boxplot', {
        min: price.min,
        q1: q1,
        median: price.median,
        q3: q3,
        max: price.max,
        mean: price.mean,
        std: price.std
    });
    
    const option = {
        title: {
            text: '价格分布统计（箱线图）',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#f59e0b',
            borderWidth: 1
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: 80
        },
        xAxis: {
            type: 'category',
            data: ['成交价分布'],
            axisLabel: {
                fontSize: 13,
                fontWeight: 600
            }
        },
        yAxis: {
            type: 'value',
            name: '成交价（万元）',
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            }
        },
        series: [
            {
                name: '价格统计',
                type: 'boxplot',
                data: [[
                    price.min,          // 最小值
                    q1,                 // Q1（25分位）
                    price.median,       // 中位数
                    q3,                 // Q3（75分位）
                    price.max           // 最大值
                ]],
                itemStyle: {
                    color: 'rgba(102, 126, 234, 0.5)',
                    borderColor: '#667eea',
                    borderWidth: 2
                },
                tooltip: {
                    formatter: function(param) {
                        return `<strong>价格统计</strong><br/>
                                最大值: <strong>${param.data[4].toFixed(2)}</strong> 万元<br/>
                                Q3 (75%): <strong>${param.data[3].toFixed(2)}</strong> 万元<br/>
                                中位数: <strong>${param.data[2].toFixed(2)}</strong> 万元<br/>
                                Q1 (25%): <strong>${param.data[1].toFixed(2)}</strong> 万元<br/>
                                最小值: <strong>${param.data[0].toFixed(2)}</strong> 万元<br/>
                                平均值: <strong>${price.mean.toFixed(2)}</strong> 万元`;
                    }
                }
            },
            {
                name: '平均值',
                type: 'scatter',
                data: [[0, price.mean]],
                symbolSize: 15,
                itemStyle: {
                    color: '#ef4444'
                },
                label: {
                    show: true,
                    formatter: '平均\n{c}',
                    position: 'right',
                    color: '#ef4444',
                    fontSize: 11,
                    fontWeight: 600
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染投资评分雷达图
 */
function renderInvestmentRadar(investmentData, volatilityData, containerId = 'investment-radar') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    
    // 保存数据供AI分析
    const radarData = {
        price_trend: Math.max(0, Math.min(100, 50 + investmentData.price_trend_score)),
        volume_trend: Math.max(0, Math.min(100, 50 + investmentData.volume_trend_score)),
        stability: investmentData.stability_score,
        index: investmentData.index_score,
        activity: volatilityData.market_activity_score || 50
    };
    saveChartData('radar', radarData);
    
    const option = {
        title: {
            text: '投资综合评分雷达图',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#667eea',
            borderWidth: 1
        },
        legend: {
            data: ['当前评分'],
            top: 40
        },
        radar: {
            indicator: [
                { name: '价格趋势', max: 100 },
                { name: '成交量趋势', max: 100 },
                { name: '市场稳定性', max: 100 },
                { name: '投资指数', max: 100 },
                { name: '市场活跃度', max: 100 }
            ],
            shape: 'polygon',
            splitNumber: 5,
            axisLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.2)'
                }
            },
            splitLine: {
                lineStyle: {
                    color: 'rgba(102, 126, 234, 0.2)'
                }
            },
            splitArea: {
                areaStyle: {
                    color: ['rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.1)']
                }
            }
        },
        series: [
            {
                name: '投资评分',
                type: 'radar',
                data: [
                    {
                        value: [
                            Math.max(0, Math.min(100, 50 + investmentData.price_trend_score)),
                            Math.max(0, Math.min(100, 50 + investmentData.volume_trend_score)),
                            investmentData.stability_score,
                            investmentData.index_score,
                            volatilityData.market_activity_score || 50
                        ],
                        name: '当前评分',
                        areaStyle: {
                            color: 'rgba(102, 126, 234, 0.3)'
                        },
                        lineStyle: {
                            color: '#667eea',
                            width: 2
                        },
                        itemStyle: {
                            color: '#667eea'
                        }
                    }
                ]
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染区域价格热力图
 */
function renderDistrictHeatmap(districtData, containerId = 'district-heatmap') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    const topDistricts = districtData.top_districts.slice(0, 15);
    
    const option = {
        title: {
            text: '区域单价热力图（Top 15）',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            position: 'top',
            backgroundColor: 'rgba(255,255,255,0.95)',
            borderColor: '#667eea',
            borderWidth: 1,
            formatter: function(params) {
                return `<strong>${params.name}</strong><br/>
                        平均单价: <strong>${params.value}</strong> 元/m²<br/>
                        排名: <strong>第${params.data[2] + 1}名</strong>`;
            }
        },
        grid: {
            height: '50%',
            top: 80
        },
        xAxis: {
            type: 'category',
            data: topDistricts.map((d, i) => `${i+1}. ${d.district_name}`),
            splitArea: {
                show: true
            },
            axisLabel: {
                rotate: 45,
                fontSize: 10
            }
        },
        yAxis: {
            type: 'value',
            splitArea: {
                show: true
            }
        },
        visualMap: {
            min: Math.min(...topDistricts.map(d => d.avg_unit_price)),
            max: Math.max(...topDistricts.map(d => d.avg_unit_price)),
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
            inRange: {
                color: ['#e0f2fe', '#0ea5e9', '#667eea', '#764ba2']
            }
        },
        series: [
            {
                name: '平均单价',
                type: 'heatmap',
                data: topDistricts.map((d, i) => [i, 0, d.avg_unit_price, i]),
                label: {
                    show: true,
                    formatter: function(params) {
                        return (params.value[2] / 1000).toFixed(1) + 'k';
                    },
                    color: '#fff',
                    fontWeight: 600
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 渲染季节性热力日历图
 */
function renderSeasonalCalendar(monthlyData, containerId = 'seasonal-calendar') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const chart = echarts.init(container);
    
    // 准备日历数据
    const calendarData = monthlyData.map(m => {
        // 将"2023-01"格式转换为"2023-01-01"
        const date = m['年月'] + '-01';
        return [date, m['成交量']];
    });
    
    const years = [...new Set(monthlyData.map(m => m['年月'].split('-')[0]))];
    
    const option = {
        title: {
            text: '成交量时间热力图',
            left: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 600,
                color: '#1e293b'
            }
        },
        tooltip: {
            formatter: function(params) {
                return `<strong>${params.value[0]}</strong><br/>
                        成交量: <strong>${params.value[1]}</strong> 套`;
            }
        },
        visualMap: {
            min: Math.min(...monthlyData.map(m => m['成交量'])),
            max: Math.max(...monthlyData.map(m => m['成交量'])),
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: 20,
            inRange: {
                color: ['#e0f2fe', '#0ea5e9', '#667eea']
            }
        },
        calendar: years.map((year, index) => ({
            top: 80 + index * 180,
            range: year,
            cellSize: ['auto', 20],
            yearLabel: {
                show: true,
                fontSize: 14,
                fontWeight: 600,
                color: '#1e293b'
            },
            monthLabel: {
                fontSize: 11,
                nameMap: 'cn'
            },
            dayLabel: {
                show: false
            }
        })),
        series: years.map((year, index) => ({
            type: 'heatmap',
            coordinateSystem: 'calendar',
            calendarIndex: index,
            data: calendarData.filter(d => d[0].startsWith(year))
        }))
    };
    
    chart.setOption(option);
    
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    return chart;
}

/**
 * 通用ECharts主题配置
 */
const echartsTheme = {
    color: ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444', '#06b6d4'],
    backgroundColor: 'transparent',
    textStyle: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    title: {
        textStyle: {
            color: '#1e293b'
        }
    },
    legend: {
        textStyle: {
            color: '#64748b'
        }
    }
};

