/**
 * 图表计算方法说明组件
 * 为每个图表提供"查看计算方法"按钮和弹窗说明
 */

// 图表计算方法说明数据
const chartExplanations = {
    // ==================== 城市深度分析页面 ====================
    'trend': {
        title: '📈 月度价格趋势图',
        type: '面积折线图 (ECharts Line with Area)',
        calculation: `
            <div class="calc-section">
                <h4>📊 数据处理</h4>
                <ol>
                    <li>按年月分组：将成交日期转换为月份格式（如 2024-01）</li>
                    <li>计算月均价：<code>月均价 = SUM(成交价) / COUNT(成交)</code></li>
                </ol>
            </div>
            <div class="calc-section">
                <h4>📐 环比增长率</h4>
                <div class="formula">环比 = (当月均价 - 上月均价) / 上月均价 × 100%</div>
                <p class="note">环比增长率反映月度变化趋势，正值表示上涨，负值表示下跌</p>
            </div>
            <div class="calc-section">
                <h4>📍 标记点</h4>
                <ul>
                    <li><strong>最高点</strong>：历史最高月均价</li>
                    <li><strong>最低点</strong>：历史最低月均价</li>
                    <li><strong>平均线</strong>：所有月份的平均值</li>
                </ul>
            </div>
        `
    },
    
    'boxplot': {
        title: '📊 价格分布箱线图',
        type: '箱线图 (ECharts Boxplot)',
        calculation: `
            <div class="calc-section">
                <h4>📐 五数概括</h4>
                <ul>
                    <li><strong>最小值 (Min)</strong>：所有成交价中的最小值</li>
                    <li><strong>Q1 (25分位数)</strong>：排序后第25%位置的值，75%的数据大于此值</li>
                    <li><strong>中位数 (Median)</strong>：排序后第50%位置的值，将数据分成两半</li>
                    <li><strong>Q3 (75分位数)</strong>：排序后第75%位置的值，25%的数据大于此值</li>
                    <li><strong>最大值 (Max)</strong>：所有成交价中的最大值</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📊 附加统计</h4>
                <ul>
                    <li><strong>平均值</strong>：<code>Mean = SUM(成交价) / COUNT(成交)</code></li>
                    <li><strong>标准差</strong>：<code>Std = √[Σ(xi - mean)² / n]</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <ul>
                    <li><strong>四分位数</strong>：将数据分成4等份的3个分界点</li>
                    <li><strong>IQR (四分位距)</strong>：Q3 - Q1，用于识别异常值</li>
                </ul>
            </div>
        `
    },
    
    'radar': {
        title: '🎯 投资综合评分雷达图',
        type: '雷达图 (ECharts Radar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 五个维度计算</h4>
                <table class="calc-table">
                    <tr><th>维度</th><th>权重</th><th>计算公式</th></tr>
                    <tr>
                        <td>价格趋势</td>
                        <td>40%</td>
                        <td><code>(最近6月均价 - 之前6月均价) / 之前6月均价 × 100</code></td>
                    </tr>
                    <tr>
                        <td>成交量趋势</td>
                        <td>20%</td>
                        <td><code>(最近6月成交量 - 之前6月成交量) / 之前6月成交量 × 100</code></td>
                    </tr>
                    <tr>
                        <td>市场稳定性</td>
                        <td>40%</td>
                        <td><code>100 / (1 + CV/10)</code>，CV越小分数越高</td>
                    </tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <p><strong>CV (变异系数, Coefficient of Variation)</strong></p>
                <div class="formula">CV = 标准差 / 均值 × 100%</div>
                <p class="note">CV 衡量数据的离散程度，CV 越小表示价格越稳定</p>
            </div>
            <div class="calc-section">
                <h4>🏆 投资指数评级</h4>
                <ul>
                    <li>80-100分：<span class="level-excellent">优秀</span></li>
                    <li>70-79分：<span class="level-good">良好</span></li>
                    <li>60-69分：<span class="level-normal">一般</span></li>
                    <li>50-59分：<span class="level-poor">较差</span></li>
                    <li>&lt;50分：<span class="level-bad">不建议</span></li>
                </ul>
            </div>
        `
    },
    
    'priceRange': {
        title: '💰 价格区间分布图',
        type: '柱状图 (ECharts Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 价格区间划分</h4>
                <table class="calc-table">
                    <tr><th>区间名称</th><th>价格范围</th></tr>
                    <tr><td>100万以下</td><td>0 ≤ 价格 &lt; 100万</td></tr>
                    <tr><td>100-200万</td><td>100 ≤ 价格 &lt; 200万</td></tr>
                    <tr><td>200-300万</td><td>200 ≤ 价格 &lt; 300万</td></tr>
                    <tr><td>300-500万</td><td>300 ≤ 价格 &lt; 500万</td></tr>
                    <tr><td>500-800万</td><td>500 ≤ 价格 &lt; 800万</td></tr>
                    <tr><td>800-1000万</td><td>800 ≤ 价格 &lt; 1000万</td></tr>
                    <tr><td>1000万以上</td><td>价格 ≥ 1000万</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>📊 统计计算</h4>
                <ul>
                    <li><strong>成交量</strong>：<code>COUNT(该区间内的成交)</code></li>
                    <li><strong>占比</strong>：<code>成交量 / 总成交量 × 100%</code></li>
                </ul>
            </div>
        `
    },
    
    'area': {
        title: '🏠 户型面积分布图',
        type: '平滑曲线面积图 (ECharts Line with Area)',
        calculation: `
            <div class="calc-section">
                <h4>📐 面积区间划分</h4>
                <table class="calc-table">
                    <tr><th>类型</th><th>面积范围</th></tr>
                    <tr><td>小户型</td><td>0 ≤ 面积 &lt; 50㎡</td></tr>
                    <tr><td>中小户型</td><td>50 ≤ 面积 &lt; 90㎡</td></tr>
                    <tr><td>中户型</td><td>90 ≤ 面积 &lt; 120㎡</td></tr>
                    <tr><td>中大户型</td><td>120 ≤ 面积 &lt; 150㎡</td></tr>
                    <tr><td>大户型</td><td>150 ≤ 面积 &lt; 200㎡</td></tr>
                    <tr><td>豪宅</td><td>面积 ≥ 200㎡</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>📊 每区间统计</h4>
                <ul>
                    <li><strong>成交量</strong>：<code>COUNT(该区间内的成交)</code></li>
                    <li><strong>平均价格</strong>：<code>AVG(该区间内的成交价)</code></li>
                    <li><strong>占比</strong>：<code>成交量 / 总成交量 × 100%</code></li>
                </ul>
            </div>
        `
    },
    
    'violin': {
        title: '🎻 价格分布小提琴图',
        type: '箱线图变体 + 密度估计',
        calculation: `
            <div class="calc-section">
                <h4>📐 基础统计量</h4>
                <p>与箱线图相同：最小值、Q1、中位数、Q3、最大值、平均值、标准差</p>
            </div>
            <div class="calc-section">
                <h4>📊 密度估计</h4>
                <ul>
                    <li>使用直方图方法估计密度分布</li>
                    <li>分为30个分箱（bin）</li>
                    <li>密度公式：<code>density[i] = count[i] / (total × bin_width)</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <p><strong>小提琴图</strong>：结合了箱线图和密度图的优点，既能看到统计特征（中位数、四分位数），又能看到数据的分布形状。</p>
            </div>
        `
    },
    
    'heatmap': {
        title: '🗺️ 区域-时间价格热力图',
        type: '热力图 (ECharts Heatmap)',
        calculation: `
            <div class="calc-section">
                <h4>📐 矩阵构建</h4>
                <ul>
                    <li><strong>行 (Y轴)</strong>：各个区域名称</li>
                    <li><strong>列 (X轴)</strong>：各个月份</li>
                    <li><strong>值</strong>：该区域该月的平均单价（元/㎡）</li>
                </ul>
                <div class="formula">单元格值 = AVG(该区域该月所有成交单价)</div>
            </div>
            <div class="calc-section">
                <h4>🎨 颜色映射</h4>
                <ul>
                    <li>使用线性颜色梯度：浅蓝 → 深蓝</li>
                    <li>最低价 → 最浅色</li>
                    <li>最高价 → 最深色</li>
                </ul>
            </div>
        `
    },
    
    'waterfall': {
        title: '📊 价格变化瀑布图',
        type: '瀑布图/桥图 (ECharts Bar Stack)',
        calculation: `
            <div class="calc-section">
                <h4>📐 价格变化因素拆解</h4>
                <p>将总价格变化拆解为多个影响因素：</p>
                <table class="calc-table">
                    <tr><th>因素</th><th>占比</th><th>计算</th></tr>
                    <tr><td>起始价格</td><td>-</td><td>首月均价</td></tr>
                    <tr><td>市场趋势</td><td>40%</td><td>总变化 × 40%</td></tr>
                    <tr><td>区域发展</td><td>30%</td><td>总变化 × 30%</td></tr>
                    <tr><td>政策影响</td><td>20%</td><td>总变化 × 20%</td></tr>
                    <tr><td>其他因素</td><td>10%</td><td>总变化 × 10%</td></tr>
                    <tr><td>当前价格</td><td>-</td><td>末月均价</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <p><strong>瀑布图</strong>：展示一个值如何从初始值经过多个中间步骤变化到最终值，绿色表示增加，红色表示减少。</p>
            </div>
        `
    },
    
    'house-type': {
        title: '🏠 户型分析系列图表',
        type: '饼图 + 柱状图 + 折线图组合',
        calculation: `
            <div class="calc-section">
                <h4>📐 户型分布饼图</h4>
                <ul>
                    <li><strong>成交量</strong>：<code>COUNT(该户型)</code></li>
                    <li><strong>占比</strong>：<code>成交量 / 总成交量 × 100%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📊 按室数统计</h4>
                <ul>
                    <li>从户型字符串提取室数：正则匹配 <code>(\\d+)室</code></li>
                    <li>按室数分组计算：成交量、平均总价、平均单价、平均面积</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📈 户型价格趋势</h4>
                <p>取前5种主流户型，按月统计每种户型的平均价格</p>
            </div>
        `
    },
    
    'volatility': {
        title: '💹 市场波动性分析',
        type: '统计卡片',
        calculation: `
            <div class="calc-section">
                <h4>📐 变异系数 (CV)</h4>
                <div class="formula">CV = (月均价标准差 / 月均价平均值) × 100%</div>
                <p class="note">CV 越小表示价格越稳定</p>
            </div>
            <div class="calc-section">
                <h4>📊 价格波动幅度</h4>
                <ul>
                    <li><strong>波动范围</strong>：<code>range = max(月均价) - min(月均价)</code></li>
                    <li><strong>波动比例</strong>：<code>range / mean(月均价) × 100%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🏷️ 稳定性评级标准</h4>
                <table class="calc-table">
                    <tr><th>CV值</th><th>评级</th></tr>
                    <tr><td>CV &lt; 5%</td><td><span class="level-excellent">非常稳定</span></td></tr>
                    <tr><td>5% ≤ CV &lt; 10%</td><td><span class="level-good">稳定</span></td></tr>
                    <tr><td>10% ≤ CV &lt; 15%</td><td><span class="level-normal">一般</span></td></tr>
                    <tr><td>15% ≤ CV &lt; 20%</td><td><span class="level-poor">波动较大</span></td></tr>
                    <tr><td>CV ≥ 20%</td><td><span class="level-bad">波动剧烈</span></td></tr>
                </table>
            </div>
        `
    },
    
    'yoy': {
        title: '📊 年度同比分析',
        type: '数据表格',
        calculation: `
            <div class="calc-section">
                <h4>📐 年度统计</h4>
                <ul>
                    <li><strong>平均成交价</strong>：<code>AVG(该年所有成交价)</code></li>
                    <li><strong>平均单价</strong>：<code>AVG(该年所有成交单价)</code></li>
                    <li><strong>成交量</strong>：<code>COUNT(该年成交)</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📈 同比计算</h4>
                <ul>
                    <li><strong>价格同比</strong>：<code>(本年均价 - 上年均价) / 上年均价 × 100%</code></li>
                    <li><strong>成交量同比</strong>：<code>(本年成交量 - 上年成交量) / 上年成交量 × 100%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <p><strong>同比 (YoY, Year over Year)</strong>：与去年同期相比的变化率，用于消除季节性因素的影响。</p>
            </div>
        `
    },
    
    'seasonal': {
        title: '🌸 季节性特征分析',
        type: '统计卡片',
        calculation: `
            <div class="calc-section">
                <h4>📐 季度划分</h4>
                <ul>
                    <li><strong>Q1 (第一季度)</strong>：1-3月</li>
                    <li><strong>Q2 (第二季度)</strong>：4-6月</li>
                    <li><strong>Q3 (第三季度)</strong>：7-9月</li>
                    <li><strong>Q4 (第四季度)</strong>：10-12月</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📊 季度统计</h4>
                <ul>
                    <li><strong>季度均价</strong>：<code>AVG(该季度成交价)</code></li>
                    <li><strong>季度成交量</strong>：<code>COUNT(该季度成交) / 年数</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📈 季节性指数</h4>
                <div class="formula">季节性指数 = (季度均价 / 全年均价 - 1) × 100%</div>
                <p class="note">正值表示该季度价格高于平均，负值表示低于平均</p>
            </div>
        `
    },
    
    // ==================== 全国对比分析页面 ====================
    'investment_comparison': {
        title: '🏆 投资价值指数对比',
        type: '多数据系列雷达图 (Chart.js Radar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 各城市投资指数计算</h4>
                <p>每个城市独立计算以下指标：</p>
                <ul>
                    <li><strong>总评分</strong>：投资指数 (0-100分)</li>
                    <li><strong>价格趋势</strong>：50 + price_trend_score（归一化到0-100）</li>
                    <li><strong>成交量趋势</strong>：50 + volume_trend_score（归一化到0-100）</li>
                    <li><strong>市场稳定性</strong>：stability_score (0-100)</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🏅 排名规则</h4>
                <p>所有城市按综合投资指数从高到低排名</p>
            </div>
        `
    },
    
    'price_comparison': {
        title: '💰 价格水平对比',
        type: '双Y轴柱状图 (Chart.js Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 对比指标</h4>
                <ul>
                    <li><strong>左Y轴</strong>：平均成交价（万元）= AVG(成交价)</li>
                    <li><strong>右Y轴</strong>：平均单价（元/㎡）= AVG(成交单价)</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📊 价格差距分析</h4>
                <ul>
                    <li><strong>价格差距</strong>：<code>max(各城市均价) - min(各城市均价)</code></li>
                    <li><strong>价格倍数</strong>：<code>max(各城市均价) / min(各城市均价)</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🏷️ 差距评级</h4>
                <table class="calc-table">
                    <tr><th>倍数</th><th>评级</th></tr>
                    <tr><td>&lt; 1.5倍</td><td>差距较小</td></tr>
                    <tr><td>1.5-2倍</td><td>差距中等</td></tr>
                    <tr><td>2-3倍</td><td>差距较大</td></tr>
                    <tr><td>≥ 3倍</td><td>差距悬殊</td></tr>
                </table>
            </div>
        `
    },
    
    'area_comparison': {
        title: '📏 城市平均面积对比',
        type: '柱状图 (Chart.js Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 计算方法</h4>
                <p>每城市平均面积 = <code>AVG(所有成交的面积)</code></p>
            </div>
            <div class="calc-section">
                <h4>📊 统计指标</h4>
                <ul>
                    <li><strong>最大面积</strong>：面积最大的城市及其值</li>
                    <li><strong>最小面积</strong>：面积最小的城市及其值</li>
                    <li><strong>全国平均</strong>：<code>AVG(各城市平均面积)</code></li>
                    <li><strong>面积差距</strong>：最大面积 - 最小面积</li>
                </ul>
            </div>
        `
    },
    
    'market_scale': {
        title: '📈 市场规模对比',
        type: '柱状图 (Chart.js Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 规模指标计算</h4>
                <ul>
                    <li><strong>总成交量</strong>：<code>COUNT(成交)</code></li>
                    <li><strong>总成交额</strong>：<code>SUM(成交价)</code>（万元）</li>
                    <li><strong>月均成交量</strong>：<code>总成交量 / 月份数</code></li>
                    <li><strong>日均成交量</strong>：<code>总成交量 / 天数</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📊 市场份额</h4>
                <div class="formula">市场份额 = 该城市成交量 / 全国成交量 × 100%</div>
            </div>
        `
    },
    
    'growth_comparison': {
        title: '📊 增长率对比',
        type: '多折线图 (Chart.js Line)',
        calculation: `
            <div class="calc-section">
                <h4>📐 年度价格趋势</h4>
                <p>X轴：年份，Y轴：各城市该年平均价格</p>
            </div>
            <div class="calc-section">
                <h4>📈 整体趋势判断</h4>
                <ul>
                    <li>所有城市均上涨 → "全面上涨"</li>
                    <li>所有城市均下跌 → "全面下跌"</li>
                    <li>混合情况 → 根据平均增长判断 "整体上涨/下跌，局部分化"</li>
                </ul>
            </div>
        `
    },
    
    'affordability': {
        title: '💸 购房可负担性对比',
        type: '双Y轴柱状图 (Chart.js Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 可负担性定义</h4>
                <p><strong>可负担房源</strong>：成交价 ≤ 200万 的房源</p>
            </div>
            <div class="calc-section">
                <h4>📊 计算指标</h4>
                <ul>
                    <li><strong>可负担比例</strong>：<code>COUNT(价格≤200万) / 总成交量 × 100%</code></li>
                    <li><strong>中档比例</strong>：<code>COUNT(200&lt;价格≤500万) / 总成交量 × 100%</code></li>
                    <li><strong>高端比例</strong>：<code>COUNT(价格&gt;500万) / 总成交量 × 100%</code></li>
                    <li><strong>30%首付</strong>：<code>平均成交价 × 30%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🏷️ 可负担性评级</h4>
                <table class="calc-table">
                    <tr><th>可负担比例</th><th>评级</th></tr>
                    <tr><td>&gt; 70%</td><td>高可负担性</td></tr>
                    <tr><td>50-70%</td><td>中等可负担性</td></tr>
                    <tr><td>30-50%</td><td>低可负担性</td></tr>
                    <tr><td>&lt; 30%</td><td>较难负担</td></tr>
                </table>
            </div>
        `
    },
    
    'house_type_comparison': {
        title: '🏠 全国户型分布对比',
        type: '分组柱状图 (Chart.js Bar)',
        calculation: `
            <div class="calc-section">
                <h4>📐 主流户型识别</h4>
                <p>统计各城市出现频率最高的户型（如2室1厅、3室2厅等）</p>
            </div>
            <div class="calc-section">
                <h4>📊 对比维度</h4>
                <ul>
                    <li><strong>主流户型占比</strong>：各城市主流户型的成交占比</li>
                    <li><strong>按室数价格对比</strong>：1室、2室、3室等不同室数的平均价格</li>
                </ul>
            </div>
        `
    },
    
    // ==================== AI预测页面 ====================
    'prediction': {
        title: '📈 预测对比图表',
        type: '多折线图 + 区间填充 (ECharts Line)',
        calculation: `
            <div class="calc-section">
                <h4>📐 统计预测方法</h4>
                <ol>
                    <li>计算最近6个月的价格变化趋势</li>
                    <li>平均变化量：<code>avg_change = mean(相邻月份差值)</code></li>
                    <li>预测价格：<code>预测价格 = 当前价格 + avg_change × (1 + random(-0.3, 0.3))</code></li>
                </ol>
            </div>
            <div class="calc-section">
                <h4>📊 置信度计算</h4>
                <div class="formula">confidence[i] = max(40, 90 - i × 8)</div>
                <p class="note">预测越远，置信度越低</p>
            </div>
            <div class="calc-section">
                <h4>📈 预测区间</h4>
                <ul>
                    <li><strong>下限</strong>：<code>predicted_price × 0.95</code></li>
                    <li><strong>上限</strong>：<code>predicted_price × 1.05</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🤖 AI预测</h4>
                <p>基于 DeepSeek-V3 大语言模型，综合分析历史数据、市场因素、季节性特征生成预测</p>
            </div>
        `
    },
    
    // ==================== 3D地图页面 ====================
    'map3d': {
        title: '🗺️ 3D房价地图',
        type: '3D柱状图 (ECharts GL Bar3D)',
        calculation: `
            <div class="calc-section">
                <h4>📐 3D柱状图数据</h4>
                <ul>
                    <li><strong>位置 (X/Y)</strong>：区域中心坐标（经纬度）</li>
                    <li><strong>高度 (Z)</strong>：根据视图模式映射数据值</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>👁️ 四种视图模式</h4>
                <table class="calc-table">
                    <tr><th>模式</th><th>高度映射</th></tr>
                    <tr><td>💰 价格模式</td><td>平均成交价（万元）</td></tr>
                    <tr><td>📊 成交量模式</td><td>成交数量（套）</td></tr>
                    <tr><td>📈 涨跌幅模式</td><td>价格变化百分比</td></tr>
                    <tr><td>🏢 单价模式</td><td>平均单价（元/㎡）</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>🎨 颜色映射</h4>
                <div class="formula">低价（绿色）→ 中价（黄色）→ 高价（红色）</div>
                <p class="note">颜色随数值线性渐变</p>
            </div>
        `
    },
    
    // ==================== AI购房策略规划页面 ====================
    'strategy_affordability': {
        title: '💰 购买力分析',
        type: '数据统计分析',
        calculation: `
            <div class="calc-section">
                <h4>📐 可购面积计算</h4>
                <div class="formula">可购面积 = 预算 × 10000 / 平均单价</div>
                <p class="note">平均单价 = 城市所有成交记录的平均成交单价（元/㎡）</p>
            </div>
            <div class="calc-section">
                <h4>📊 预算匹配度</h4>
                <ul>
                    <li><strong>匹配房源数</strong>：预算 ±20% 范围内的成交房源数量</li>
                    <li><strong>房源占比</strong>：<code>匹配房源数 / 总成交数 × 100%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>📈 预算分位数</h4>
                <div class="formula">分位数 = COUNT(成交价 ≤ 预算) / 总成交数 × 100%</div>
                <p class="note">表示您的预算超过了多少比例的房源</p>
            </div>
            <div class="calc-section">
                <h4>🏷️ 购买力评级标准</h4>
                <table class="calc-table">
                    <tr><th>分位数</th><th>评级</th></tr>
                    <tr><td>&lt; 25%</td><td><span class="level-poor">经济型（入门级）</span></td></tr>
                    <tr><td>25%-50%</td><td><span class="level-normal">标准型（中低端）</span></td></tr>
                    <tr><td>50%-75%</td><td><span class="level-good">舒适型（中高端）</span></td></tr>
                    <tr><td>&gt; 75%</td><td><span class="level-excellent">高端型（高端市场）</span></td></tr>
                </table>
            </div>
        `
    },
    
    'strategy_district': {
        title: '🗺️ 区域推荐算法',
        type: '多维度评分排序',
        calculation: `
            <div class="calc-section">
                <h4>📐 区域统计指标</h4>
                <ul>
                    <li><strong>平均价格</strong>：<code>AVG(该区域成交价)</code></li>
                    <li><strong>中位价格</strong>：<code>MEDIAN(该区域成交价)</code></li>
                    <li><strong>平均单价</strong>：<code>AVG(该区域成交单价)</code></li>
                    <li><strong>成交量</strong>：<code>COUNT(该区域成交)</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💹 性价比评分</h4>
                <div class="formula">可买面积 = 预算 × 10000 / 区域平均单价</div>
                <p class="note">按可买面积从大到小排序，面积越大性价比越高</p>
            </div>
            <div class="calc-section">
                <h4>📈 价格趋势计算</h4>
                <ul>
                    <li>取最近30%成交数据计算平均价格（recent_price）</li>
                    <li>取最早30%成交数据计算平均价格（earlier_price）</li>
                    <li>趋势：<code>(recent - earlier) / earlier × 100%</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🎯 排序规则</h4>
                <ol>
                    <li>如有指定期望区域 → 优先匹配</li>
                    <li>筛选成交量 ≥ 100 套的区域</li>
                    <li>按可买面积降序排列</li>
                    <li>返回前5个推荐区域</li>
                </ol>
            </div>
        `
    },
    
    'strategy_timing': {
        title: '⏰ 市场时机评估',
        type: '综合评分模型',
        calculation: `
            <div class="calc-section">
                <h4>📐 核心指标计算</h4>
                <table class="calc-table">
                    <tr><th>指标</th><th>计算方法</th></tr>
                    <tr>
                        <td>价格变化</td>
                        <td><code>(最近25%均价 - 最早25%均价) / 最早25%均价 × 100%</code></td>
                    </tr>
                    <tr>
                        <td>成交量变化</td>
                        <td><code>(最近25%成交量 - 最早25%成交量) / 最早25%成交量 × 100%</code></td>
                    </tr>
                    <tr>
                        <td>波动性 (CV)</td>
                        <td><code>标准差 / 均价 × 100%</code></td>
                    </tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>🎯 时机评分算法</h4>
                <p>基准分：<strong>50分</strong></p>
                <table class="calc-table">
                    <tr><th>条件</th><th>分数调整</th></tr>
                    <tr><td>价格下跌 &gt; 5%</td><td>+20（买入好时机）</td></tr>
                    <tr><td>价格上涨 &gt; 5%</td><td>-20（时机一般）</td></tr>
                    <tr><td>价格变化 ≤ 5%</td><td>+10（市场平稳）</td></tr>
                    <tr><td>成交量下降 &gt; 10%</td><td>+10（议价空间大）</td></tr>
                    <tr><td>成交量上升 &gt; 10%</td><td>-10（竞争激烈）</td></tr>
                    <tr><td>波动性 &lt; 10%</td><td>+10（市场稳定）</td></tr>
                    <tr><td>波动性 &gt; 20%</td><td>-10（风险较高）</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>🏷️ 时机评级标准</h4>
                <table class="calc-table">
                    <tr><th>评分</th><th>评级</th><th>建议</th></tr>
                    <tr><td>≥ 70</td><td><span class="level-excellent">极佳时机</span></td><td>积极看房，果断出手</td></tr>
                    <tr><td>60-69</td><td><span class="level-good">较好时机</span></td><td>可以看房，不必着急</td></tr>
                    <tr><td>50-59</td><td><span class="level-normal">适中时机</span></td><td>边看边等，挑选性价比</td></tr>
                    <tr><td>40-49</td><td><span class="level-poor">需谨慎</span></td><td>多观察，谨慎决策</td></tr>
                    <tr><td>&lt; 40</td><td><span class="level-bad">建议观望</span></td><td>暂缓购房，等待时机</td></tr>
                </table>
            </div>
        `
    },
    
    'strategy_loan': {
        title: '🏦 贷款方案计算',
        type: '等额本息计算器',
        calculation: `
            <div class="calc-section">
                <h4>📐 基础参数</h4>
                <ul>
                    <li><strong>首付比例</strong>：默认 30%</li>
                    <li><strong>贷款年限</strong>：默认 30 年</li>
                    <li><strong>年利率</strong>：默认 4.2%</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💰 核心计算公式</h4>
                <p><strong>首付金额：</strong></p>
                <div class="formula">首付 = 总价 × 首付比例</div>
                
                <p><strong>贷款金额：</strong></p>
                <div class="formula">贷款 = 总价 - 首付</div>
                
                <p><strong>月供（等额本息）：</strong></p>
                <div class="formula">
                    月供 = 贷款 × r × (1+r)^n / [(1+r)^n - 1]
                </div>
                <p class="note">其中 r = 年利率/12（月利率），n = 贷款年限×12（总月数）</p>
            </div>
            <div class="calc-section">
                <h4>📊 利息计算</h4>
                <ul>
                    <li><strong>总利息</strong>：<code>月供 × 总月数 - 贷款本金</code></li>
                    <li><strong>总还款</strong>：<code>贷款本金 + 总利息</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💡 名词解释</h4>
                <p><strong>等额本息</strong>：每月还款金额固定，前期利息多、本金少，后期本金多、利息少。</p>
            </div>
        `
    },
    
    'strategy_ai': {
        title: '🤖 AI智能建议',
        type: 'DeepSeek-V3 大语言模型',
        calculation: `
            <div class="calc-section">
                <h4>📐 AI输入数据</h4>
                <p>AI模型接收以下结构化数据作为分析依据：</p>
                <ul>
                    <li><strong>用户画像</strong>：城市、预算、目的、家庭人数、急迫程度</li>
                    <li><strong>购买力分析</strong>：可买面积、匹配房源数、预算分位数</li>
                    <li><strong>区域推荐</strong>：Top3区域的价格、趋势、成交量</li>
                    <li><strong>市场时机</strong>：评分、价格变化、波动性</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🎯 AI分析维度</h4>
                <ol>
                    <li><strong>综合购房策略</strong>：结合预算定位、市场时机、购房目的判断入手时机</li>
                    <li><strong>户型面积建议</strong>：根据家庭人数推荐合理户型</li>
                    <li><strong>区域选择指导</strong>：对比推荐区域，给出最优选择</li>
                    <li><strong>风险提示</strong>：基于市场波动和房源占比提醒风险</li>
                </ol>
            </div>
            <div class="calc-section">
                <h4>⚙️ 模型参数</h4>
                <ul>
                    <li><strong>模型</strong>：DeepSeek-V3</li>
                    <li><strong>Temperature</strong>：0.7（适度创造性）</li>
                    <li><strong>Max Tokens</strong>：500（约300字）</li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>💡 提示词工程</h4>
                <p>使用结构化Prompt，要求AI：</p>
                <ul>
                    <li>必须引用具体数据支撑观点</li>
                    <li>语言专业但易懂</li>
                    <li>给出可执行的具体建议</li>
                    <li>分4段输出，每段有小标题</li>
                </ul>
            </div>
        `
    },
    
    // ==================== 首页地图 ====================
    'china_price_map': {
        title: '🗺️ 全国房价均价地图',
        type: '中国地图 (ECharts Map)',
        calculation: `
            <div class="calc-section">
                <h4>📐 省份均价计算</h4>
                <p>对每个省份独立计算：</p>
                <ul>
                    <li><strong>平均单价</strong>：<code>AVG(该省所有成交单价)</code>（元/㎡）</li>
                    <li><strong>平均总价</strong>：<code>AVG(该省所有成交价)</code>（万元）</li>
                    <li><strong>成交量</strong>：<code>COUNT(该省成交记录)</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🎨 颜色映射</h4>
                <p>使用线性颜色梯度展示价格高低：</p>
                <table class="calc-table">
                    <tr><th>价格水平</th><th>颜色</th></tr>
                    <tr><td>最低</td><td><span style="color: #10b981;">■</span> 绿色</td></tr>
                    <tr><td>中低</td><td><span style="color: #84cc16;">■</span> 青柠</td></tr>
                    <tr><td>中等</td><td><span style="color: #eab308;">■</span> 黄色</td></tr>
                    <tr><td>中高</td><td><span style="color: #f97316;">■</span> 橙色</td></tr>
                    <tr><td>最高</td><td><span style="color: #ef4444;">■</span> 红色</td></tr>
                </table>
            </div>
            <div class="calc-section">
                <h4>📊 统计指标</h4>
                <ul>
                    <li><strong>最低均价省份</strong>：单价最低的省份</li>
                    <li><strong>最高均价省份</strong>：单价最高的省份</li>
                    <li><strong>全国平均单价</strong>：<code>AVG(各省平均单价)</code></li>
                    <li><strong>价格差距倍数</strong>：<code>最高单价 / 最低单价</code></li>
                </ul>
            </div>
            <div class="calc-section">
                <h4>🖱️ 交互说明</h4>
                <ul>
                    <li>鼠标悬停：显示省份详细数据</li>
                    <li>点击省份：跳转查看该省详情</li>
                    <li>滚轮缩放：放大/缩小地图</li>
                    <li>拖拽：平移地图视角</li>
                </ul>
            </div>
        `
    }
};

// 创建并显示计算说明弹窗
function showChartExplanation(chartKey) {
    const explanation = chartExplanations[chartKey];
    if (!explanation) {
        console.warn('未找到图表说明:', chartKey);
        return;
    }
    
    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.className = 'chart-explanation-overlay';
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            closeChartExplanation();
        }
    };
    
    // 创建弹窗
    const modal = document.createElement('div');
    modal.className = 'chart-explanation-modal';
    modal.innerHTML = `
        <div class="explanation-header">
            <h2>${explanation.title}</h2>
            <button class="close-btn" onclick="closeChartExplanation()">✕</button>
        </div>
        <div class="explanation-type">
            <span class="type-badge">图表类型</span>
            <span class="type-value">${explanation.type}</span>
        </div>
        <div class="explanation-content">
            <h3>📐 计算方法详解</h3>
            ${explanation.calculation}
        </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // 添加动画
    requestAnimationFrame(() => {
        overlay.classList.add('show');
    });
}

// 关闭弹窗
function closeChartExplanation() {
    const overlay = document.querySelector('.chart-explanation-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => {
            overlay.remove();
        }, 300);
    }
}

// 创建"查看计算方法"按钮
function createExplainButton(chartKey, style = 'default') {
    const btn = document.createElement('button');
    btn.className = `explain-btn explain-btn-${style}`;
    btn.innerHTML = '❓ 计算方法';
    btn.onclick = () => showChartExplanation(chartKey);
    return btn;
}

// 为指定容器添加说明按钮
function addExplainButtonTo(containerId, chartKey, position = 'header') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // 查找标题行或创建按钮容器
    let targetElement;
    if (position === 'header') {
        // 尝试找到标题行的按钮区域
        targetElement = container.querySelector('.chart-header-buttons') || 
                       container.parentElement.querySelector('[style*="display: flex"]') ||
                       container.parentElement;
    } else {
        targetElement = container;
    }
    
    const btn = createExplainButton(chartKey, 'inline');
    if (targetElement) {
        // 如果是flex容器，直接追加；否则创建wrapper
        if (targetElement.style.display === 'flex' || 
            window.getComputedStyle(targetElement).display === 'flex') {
            targetElement.appendChild(btn);
        } else {
            const wrapper = document.createElement('div');
            wrapper.style.cssText = 'display: inline-block; margin-left: 10px;';
            wrapper.appendChild(btn);
            targetElement.appendChild(wrapper);
        }
    }
}

// ESC 键关闭弹窗
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeChartExplanation();
    }
});

