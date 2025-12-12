/**
 * 一键AI洞察功能
 * 为整个报告生成综合分析
 */

let isGeneratingInsight = false;

/**
 * 生成快速洞察
 */
function generateQuickInsight() {
    if (isGeneratingInsight) {
        alert('AI正在分析中，请稍候...');
        return;
    }
    
    // 获取当前角色
    const roleInfo = typeof getCurrentRole === 'function' ? getCurrentRole() : null;
    
    const button = document.getElementById('quick-insight-btn');
    const contentDiv = document.getElementById('quick-insight-content');
    
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
                💡 <strong>提示</strong>: AI正在分析市场定位、投资价值、趋势研判、投资建议和风险提示...
            </div>
        </div>
    `;
    
    // 修改按钮状态
    button.disabled = true;
    button.textContent = '⏳ 正在分析...';
    button.style.opacity = '0.6';
    button.style.cursor = 'not-allowed';
    
    isGeneratingInsight = true;
    
    // 创建EventSource（添加角色参数）
    const roleParam = roleInfo ? `?role=${roleInfo.id}` : '';
    const eventSource = new EventSource(`/api/ai/quick-insight-stream/${cityNameEn}${roleParam}`);
    const insightTextDiv = document.getElementById('insight-text');
    let fullText = '';
    
    eventSource.onmessage = function(event) {
        if (event.data === '[DONE]') {
            eventSource.close();
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
                eventSource.close();
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
    
    eventSource.onerror = function(error) {
        console.error('EventSource error:', error);
        insightTextDiv.innerHTML = `
            <div style="color: #ef4444; padding: 15px; background: #fee; border-radius: 8px;">
                ❌ 连接失败，请检查网络后重试
            </div>
        `;
        eventSource.close();
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
    
    // 替换标题（## 标题 -> <h3>）
    text = text.replace(/##\s+(.+)/g, '<h3 style="color: #1e293b; margin-top: 25px; margin-bottom: 15px; font-size: 1.2em; border-bottom: 2px solid #f59e0b; padding-bottom: 8px;">$1</h3>');
    
    // 替换加粗（**文字** -> <strong>）
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong style="color: #1e293b;">$1</strong>');
    
    // 替换数字列表（1. -> <ol><li>）
    const lines = text.split('\n');
    let inList = false;
    let formattedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const listMatch = line.match(/^(\d+)\.\s+(.+)/);
        
        if (listMatch) {
            if (!inList) {
                formattedLines.push('<ol style="margin: 15px 0; padding-left: 25px;">');
                inList = true;
            }
            formattedLines.push(`<li style="margin: 10px 0; line-height: 1.8;">${listMatch[2]}</li>`);
        } else {
            if (inList && line.trim() === '') {
                formattedLines.push('</ol>');
                inList = false;
            }
            if (line.trim() !== '') {
                formattedLines.push(`<p style="margin: 12px 0;">${line}</p>`);
            }
        }
    }
    
    if (inList) {
        formattedLines.push('</ol>');
    }
    
    text = formattedLines.join('\n');
    
    // 替换项目符号（- -> <li>）
    text = text.replace(/^-\s+(.+)/gm, '<li style="margin: 8px 0; line-height: 1.8;">$1</li>');
    
    return text;
}

