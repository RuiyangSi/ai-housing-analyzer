/**
 * 购房策略规划器 - 前端逻辑
 */

let currentStep = 1;
let formData = {};

/**
 * 下一步
 */
function nextStep(step) {
    // 验证当前步骤的表单
    if (!validateStep(currentStep)) {
        return;
    }
    
    // 保存当前步骤的数据
    saveStepData(currentStep);
    
    // 切换步骤
    currentStep = step;
    updateStepIndicator();
    showSection(step);
}

/**
 * 上一步
 */
function prevStep(step) {
    currentStep = step;
    updateStepIndicator();
    showSection(step);
}

/**
 * 验证步骤
 */
function validateStep(step) {
    const section = document.querySelector(`.form-section[data-section="${step}"]`);
    const requiredFields = section.querySelectorAll('[required]');
    
    for (let field of requiredFields) {
        if (field.type === 'radio') {
            const radioGroup = section.querySelectorAll(`[name="${field.name}"]`);
            const checked = Array.from(radioGroup).some(radio => radio.checked);
            if (!checked) {
                alert(`请选择 ${field.closest('.form-group').querySelector('label').textContent.split('*')[0].trim()}`);
                return false;
            }
        } else if (!field.value) {
            field.focus();
            alert(`请填写 ${field.closest('.form-group').querySelector('label').textContent.split('*')[0].trim()}`);
            return false;
        }
    }
    
    return true;
}

/**
 * 保存步骤数据
 */
function saveStepData(step) {
    const section = document.querySelector(`.form-section[data-section="${step}"]`);
    const inputs = section.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        } else {
            formData[input.name] = input.value;
        }
    });
}

/**
 * 更新步骤指示器
 */
function updateStepIndicator() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        const stepNum = index + 1;
        if (stepNum < currentStep) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

/**
 * 显示指定步骤
 */
function showSection(step) {
    const sections = document.querySelectorAll('.form-section');
    sections.forEach(section => {
        if (section.dataset.section == step) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
}

/**
 * 提交表单
 */
async function submitForm() {
    // 验证最后一步
    if (!validateStep(currentStep)) {
        return;
    }
    
    // 保存最后一步数据
    saveStepData(currentStep);
    
    // 显示加载状态
    document.querySelector('.main-card').style.display = 'none';
    // 安全地隐藏header（如果存在）
    const header = document.querySelector('.page-header');
    if (header) header.style.display = 'none';
    document.getElementById('result-section').style.display = 'block';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result-content').style.display = 'none';
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    try {
        // 发送请求
        const response = await fetch('/api/strategy/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示结果
            displayResult(result.strategy);
        } else {
            alert('生成策略失败：' + (result.error || '未知错误'));
            document.querySelector('.main-card').style.display = 'block';
            // 安全地恢复header（如果存在）
            const header = document.querySelector('.page-header');
            if (header) header.style.display = 'block';
            document.getElementById('result-section').style.display = 'none';
        }
    } catch (error) {
        console.error('请求失败:', error);
        alert('网络错误，请稍后重试');
        document.querySelector('.main-card').style.display = 'block';
        // 安全地恢复header（如果存在）
        const header = document.querySelector('.page-header');
        if (header) header.style.display = 'block';
        document.getElementById('result-section').style.display = 'none';
    }
}

/**
 * 增强的Markdown渲染函数（修复"吞字"问题）
 */
function renderMarkdown(text) {
    if (!text) return '';
    
    // 1. 先转义HTML特殊字符（防止XSS）
    text = text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');
    
    // 2. 处理行内格式（必须先处理加粗，再处理斜体，避免冲突）
    // 加粗：**text** 或 __text__（使用非贪婪匹配）
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // 斜体：*text* 或 _text_（但不要匹配已经处理过的strong标签）
    text = text.replace(/\*(?!\*)(.+?)\*(?!\*)/g, '<em>$1</em>');
    text = text.replace(/_(?!_)(.+?)_(?!_)/g, '<em>$1</em>');
    
    // 3. 按行处理，智能识别块级元素
    const lines = text.split('\n');
    let html = '';
    let i = 0;
    
    while (i < lines.length) {
        const line = lines[i].trim();
        
        // 空行：跳过
        if (!line) {
            i++;
            continue;
        }
        
        // 标题：### ## #
        if (line.startsWith('### ')) {
            html += `<h4>${line.substring(4)}</h4>\n`;
            i++;
        } else if (line.startsWith('## ')) {
            html += `<h3>${line.substring(3)}</h3>\n`;
            i++;
        } else if (line.startsWith('# ')) {
            html += `<h2>${line.substring(2)}</h2>\n`;
            i++;
        }
        // 无序列表：- 开头
        else if (line.startsWith('- ')) {
            html += '<ul>\n';
            while (i < lines.length && lines[i].trim().startsWith('- ')) {
                const item = lines[i].trim().substring(2);
                html += `<li>${item}</li>\n`;
                i++;
            }
            html += '</ul>\n';
        }
        // 有序列表：1. 2. 3. 开头
        else if (/^\d+\.\s/.test(line)) {
            html += '<ol>\n';
            while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
                const item = lines[i].trim().replace(/^\d+\.\s*/, '');
                html += `<li>${item}</li>\n`;
                i++;
            }
            html += '</ol>\n';
        }
        // 普通段落：收集连续的非空行
        else {
            let paraLines = [];
            while (i < lines.length) {
                const currentLine = lines[i].trim();
                // 遇到空行、标题、列表，停止收集
                if (!currentLine || 
                    currentLine.startsWith('#') || 
                    currentLine.startsWith('- ') || 
                    /^\d+\.\s/.test(currentLine)) {
                    break;
                }
                paraLines.push(currentLine);
                i++;
            }
            if (paraLines.length > 0) {
                html += `<p>${paraLines.join('<br>\n')}</p>\n`;
            }
        }
    }
    
    return html;
}

/**
 * 显示结果
 */
function displayResult(strategy) {
    document.getElementById('loading').style.display = 'none';
    const resultContent = document.getElementById('result-content');
    resultContent.style.display = 'block';
    
    const purposeMap = {
        'self_living': '自住',
        'investment': '投资',
        'education': '学区'
    };
    
    const urgencyMap = {
        'urgent': '急迫（3个月内）',
        'moderate': '适中（半年内）',
        'relaxed': '不急（1年内）'
    };
    
    resultContent.innerHTML = `
        <a href="/" class="back-btn" style="display: inline-block; color: white; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 25px; margin-bottom: 20px;">← 返回首页</a>
        
        <div class="result-header">
            <h2>🎉 您的个性化购房策略</h2>
            <p>${strategy.city_name} · ${purposeMap[strategy.user_profile.purpose]} · ${strategy.user_profile.budget}万预算</p>
        </div>
        
        <!-- 购买力分析 -->
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h3 style="margin: 0;">💪 购买力分析</h3>
                <button class="explain-btn" onclick="showChartExplanation('strategy_affordability')">❓ 计算方法</button>
            </div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-label">市场定位</div>
                    <div class="stat-value">${strategy.affordability.market_position}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">可购买面积</div>
                    <div class="stat-value">${strategy.affordability.affordable_area}㎡</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">平均单价</div>
                    <div class="stat-value">${strategy.affordability.avg_unit_price.toLocaleString()}元/㎡</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">预算内房源占比</div>
                    <div class="stat-value">${strategy.affordability.availability_rate}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">预算分位数</div>
                    <div class="stat-value">前${strategy.affordability.budget_percentile.toFixed(0)}%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">合适房源数量</div>
                    <div class="stat-value">${strategy.affordability.suitable_properties_count}套</div>
                </div>
            </div>
        </div>
        
        <!-- 市场时机 -->
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0;">⏰ 市场时机评估</h3>
                <button class="explain-btn" onclick="showChartExplanation('strategy_timing')">❓ 计算方法</button>
            </div>
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 15px; margin-bottom: 20px;">
                <div style="font-size: 4em; font-weight: bold; color: #0284c7; margin-bottom: 10px;">
                    ${strategy.timing.timing_score}分
                </div>
                <div style="font-size: 1.5em; color: #0c4a6e;">
                    ${strategy.timing.timing_level}
                </div>
            </div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-label">价格趋势</div>
                    <div class="stat-value" style="color: ${strategy.timing.price_change >= 0 ? '#ef4444' : '#10b981'}">
                        ${strategy.timing.price_change >= 0 ? '↗' : '↘'} ${Math.abs(strategy.timing.price_change)}%
                    </div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">成交量变化</div>
                    <div class="stat-value" style="color: ${strategy.timing.volume_change >= 0 ? '#10b981' : '#ef4444'}">
                        ${strategy.timing.volume_change >= 0 ? '↗' : '↘'} ${Math.abs(strategy.timing.volume_change)}%
                    </div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">市场波动性</div>
                    <div class="stat-value">${strategy.timing.volatility.toFixed(1)}%</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding: 20px; background: #f8fafc; border-radius: 10px; border-left: 4px solid #0284c7;">
                <strong style="color: #0c4a6e;">💡 时机建议：</strong> ${strategy.timing.recommendation}
            </div>
        </div>
        
        <!-- 推荐区域 -->
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0;">🎯 推荐区域（Top ${strategy.recommendations.length}）</h3>
                <button class="explain-btn" onclick="showChartExplanation('strategy_district')">❓ 计算方法</button>
            </div>
            <div class="district-list">
                ${strategy.recommendations.map((district, index) => `
                    <div class="district-item ${district.is_preferred ? 'preferred' : ''}">
                        <div>
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <div class="district-name">${index + 1}. ${district.district}</div>
                                ${district.is_preferred ? '<span class="badge badge-success">您的期望区域</span>' : ''}
                                <span class="badge ${district.trend === '上涨' ? 'badge-warning' : district.trend === '下跌' ? 'badge-info' : 'badge-success'}">
                                    ${district.trend} ${district.trend_percent >= 0 ? '+' : ''}${district.trend_percent}%
                                </span>
                            </div>
                            <div class="district-stats">
                                <div>📊 均价：${district.avg_unit_price.toLocaleString()}元/㎡</div>
                                <div>🏠 可买面积：${district.affordable_area}㎡</div>
                                <div>📈 成交量：${district.transaction_volume}套</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <!-- 贷款方案 -->
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0;">🏦 贷款方案（供参考）</h3>
                <button class="explain-btn" onclick="showChartExplanation('strategy_loan')">❓ 计算方法</button>
            </div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-label">总价</div>
                    <div class="stat-value">${(strategy.loan_plan.total_price / 10000).toFixed(0)}万</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">首付（30%）</div>
                    <div class="stat-value">${(strategy.loan_plan.down_payment / 10000).toFixed(0)}万</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">贷款金额</div>
                    <div class="stat-value">${(strategy.loan_plan.loan_amount / 10000).toFixed(0)}万</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">月供（30年）</div>
                    <div class="stat-value">${(strategy.loan_plan.monthly_payment / 10000).toFixed(2)}万</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">总利息</div>
                    <div class="stat-value">${(strategy.loan_plan.total_interest / 10000).toFixed(0)}万</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">利率</div>
                    <div class="stat-value">${strategy.loan_plan.annual_rate.toFixed(2)}%</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 10px; color: #78350f;">
                <strong>⚠️ 提示：</strong> 以上为等额本息计算，实际利率以银行为准，建议公积金+商贷组合
            </div>
        </div>
        
        <!-- 行动计划 -->
        <div class="result-card">
            <h3>📋 行动计划（6步走）</h3>
            <ul class="action-list">
                ${strategy.action_plan.map(action => `<li>${action}</li>`).join('')}
            </ul>
        </div>
        
        <!-- AI建议 -->
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                <h3 style="margin: 0;">🤖 AI专业建议</h3>
                <button class="explain-btn" onclick="showChartExplanation('strategy_ai')">❓ 计算方法</button>
            </div>
            <div class="ai-advice-box">
                ${renderMarkdown(strategy.ai_advice)}
            </div>
        </div>
        
        <!-- 操作按钮 -->
        <div style="text-align: center; padding: 30px;">
            <button class="btn btn-primary" onclick="downloadPDF()" style="margin-right: 15px;">
                📥 下载PDF报告
            </button>
            <button class="btn btn-secondary" onclick="resetForm()">
                🔄 重新规划
            </button>
        </div>
    `;
}

/**
 * 下载PDF（TODO：需要后端支持）
 */
function downloadPDF() {
    alert('PDF下载功能开发中...\n\n您可以使用浏览器的打印功能（Ctrl/Cmd + P）保存为PDF');
    window.print();
}

/**
 * 重置表单
 */
function resetForm() {
    if (confirm('确定要重新填写吗？')) {
        location.reload();
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('购房策略规划器已加载');
});



