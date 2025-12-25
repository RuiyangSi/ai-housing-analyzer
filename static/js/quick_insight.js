/**
 * 一键AI洞察功能
 * 为整个报告生成综合分析
 */

let isGeneratingInsight = false;
let currentEventSource = null;  // ✅ 保存当前EventSource引用，确保只有一个连接

/**
 * 生成快速洞察
 */
function generateQuickInsight() {
    // ✅ 防止双击：在函数最开始就检查并设置标志
    if (isGeneratingInsight) {
        console.log('AI正在分析中，请稍候...');
        return;
    }
    
    // ✅ 立即设置标志，防止双击
    isGeneratingInsight = true;
    
    // ✅ 关闭之前的连接（如果存在）
    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }
    
    // 获取当前角色（使用 getRole 函数，返回字符串）
    const currentRole = typeof getRole === 'function' ? getRole() : 'investment_advisor';
    console.log('[QuickInsight] 当前用户角色:', currentRole);
    
    const button = document.getElementById('quick-insight-btn');
    const contentDiv = document.getElementById('quick-insight-content');
    
    // 根据角色显示不同的提示文案
    const roleHints = {
        'investment_advisor': '市场定位、投资价值、趋势研判、投资建议和风险提示',
        'first_time_buyer': '房价分析、购买时机、注意事项和实用建议',
        'upgrader': '换房时机、市场行情、资金规划和换房策略'
    };
    const hintText = roleHints[currentRole] || roleHints['investment_advisor'];
    
    // 立即禁用按钮
    button.disabled = true;
    button.textContent = '⏳ 正在分析...';
    button.style.opacity = '0.6';
    button.style.cursor = 'not-allowed';
    
    // 显示内容区域
    contentDiv.style.display = 'block';
    contentDiv.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #fff5f5 0%, #fef3c7 100%);
            border-left: 4px solid #f59e0b;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 2em; margin-right: 10px;">⚡</span>
                <h3 style="margin: 0; color: #1e293b; font-size: 1.3em;">AI正在生成全面洞察...</h3>
            </div>
            <div id="insight-text" style="
                color: #1e293b;
                line-height: 1.8;
                font-size: 1em;
                white-space: pre-wrap;
            ">正在连接AI分析引擎...</div>
            <div style="
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(0,0,0,0.1);
                font-size: 0.85em;
                color: #64748b;
            ">
                💡 <strong>提示</strong>: AI正在为您分析${hintText}...
            </div>
        </div>
    `;
    
    // 创建EventSource（添加角色参数）
    const roleParam = `?role=${currentRole}`;
    currentEventSource = new EventSource(`/api/ai/quick-insight-stream/${cityNameEn}${roleParam}`);
    console.log('[QuickInsight] 请求URL:', `/api/ai/quick-insight-stream/${cityNameEn}${roleParam}`);
    const insightTextDiv = document.getElementById('insight-text');
    let fullText = '';
    
    currentEventSource.onmessage = function(event) {
        if (event.data === '[DONE]') {
            currentEventSource.close();
            currentEventSource = null;  // ✅ 清除引用
            isGeneratingInsight = false;
            button.disabled = false;
            button.textContent = '⚡ 重新生成洞察';
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
            
            // 添加完成标记
            insightTextDiv.innerHTML = formatInsightText(fullText) + `
                <div style="
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(16, 185, 129, 0.1);
                    border-radius: 8px;
                    text-align: center;
                    color: #059669;
                    font-weight: 600;
                ">
                    ✅ 分析完成！以上内容由AI生成，仅供参考。
                </div>
            `;
            return;
        }
        
        try {
            const data = JSON.parse(event.data);
            if (data.error) {
                insightTextDiv.innerHTML = `
                    <div style="color: #ef4444; padding: 15px; background: #fee; border-radius: 8px;">
                        ❌ 分析失败: ${data.error}
                    </div>
                `;
                currentEventSource.close();
                currentEventSource = null;  // ✅ 清除引用
                isGeneratingInsight = false;
                button.disabled = false;
                button.textContent = '⚡ 重试';
                button.style.opacity = '1';
                button.style.cursor = 'pointer';
            } else if (data.chunk) {
                fullText += data.chunk;
                insightTextDiv.innerHTML = formatInsightText(fullText);
                // 自动滚动到底部
                contentDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } catch (e) {
            console.error('解析AI响应失败:', e);
        }
    };
    
    currentEventSource.onerror = function(error) {
        console.error('EventSource error:', error);
        insightTextDiv.innerHTML = `
            <div style="color: #ef4444; padding: 15px; background: #fee; border-radius: 8px;">
                ❌ 连接失败，请检查网络后重试
            </div>
        `;
        currentEventSource.close();
        currentEventSource = null;  // ✅ 清除引用
        isGeneratingInsight = false;
        button.disabled = false;
        button.textContent = '⚡ 重试';
        button.style.opacity = '1';
        button.style.cursor = 'pointer';
    };
}

/**
 * 格式化洞察文本
 * 将Markdown样式转换为HTML
 */
function formatInsightText(text) {
    if (!text) return '';
    
    let html = text;
    
    // 1. 先处理标题（## 标题 或 ### 标题）
    html = html.replace(/^###\s+(.+)$/gm, '<h4 style="color: #ea580c; margin: 20px 0 12px 0; font-size: 1.05em; font-weight: 700;">$1</h4>');
    html = html.replace(/^##\s+(.+)$/gm, '<h3 style="color: #1e293b; margin: 25px 0 15px 0; font-size: 1.15em; font-weight: 700; border-bottom: 2px solid #f59e0b; padding-bottom: 8px;">$1</h3>');
    
    // 2. 处理加粗 **文字**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong style="color: #1e40af; font-weight: 700;">$1</strong>');
    
    // 3. 处理数字标题（如 "1. **标题**" 格式，常用于首次购房者的报告）
    html = html.replace(/^(\d+)\.\s+\*\*(.+?)\*\*(.*)$/gm, 
        '<div style="margin: 20px 0 12px 0; padding: 12px 16px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 8px; border-left: 4px solid #f59e0b;"><span style="color: #d97706; font-weight: 800; font-size: 1.1em;">$1.</span> <strong style="color: #92400e; font-weight: 700;">$2</strong>$3</div>');
    
    // 4. 处理普通数字列表
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, 
        '<div style="margin: 10px 0; padding-left: 8px;"><span style="color: #f59e0b; font-weight: 700;">$1.</span> $2</div>');
    
    // 5. 处理无序列表
    html = html.replace(/^[-*]\s+(.+)$/gm, '<li style="margin: 8px 0; margin-left: 24px; line-height: 1.8; list-style: disc;">$1</li>');
    
    // 6. 处理段落（跳过已经是HTML标签的行）
    const lines = html.split('\n');
    html = lines.map(line => {
        const trimmed = line.trim();
        if (!trimmed) return '';
        // 已经是 HTML 标签的不再包裹
        if (trimmed.startsWith('<')) return trimmed;
        return `<p style="margin: 12px 0; line-height: 1.85; color: #374151;">${trimmed}</p>`;
    }).filter(line => line).join('');
    
    return html;
}

