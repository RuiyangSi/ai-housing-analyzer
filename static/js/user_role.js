// user_role.js - 用户角色管理（从后端获取）
let currentAIRole = null;
let currentUser = null;
let roleLoadPromise = null;
let roleLoaded = false;

// 获取当前用户信息（包括角色）
async function getCurrentUserRole() {
    // 避免重复请求
    if (roleLoadPromise) {
        return roleLoadPromise;
    }
    
    roleLoadPromise = (async () => {
        try {
            console.log('[UserRole] 正在从后端获取用户角色...');
            const response = await fetch('/api/auth/current-user');
            const result = await response.json();
            
            if (result.success && result.user) {
                currentUser = result.user;
                currentAIRole = result.user.role;
                roleLoaded = true;
                console.log('[UserRole] 用户角色加载成功:', currentAIRole);
                return currentAIRole;
            }
        } catch (error) {
            console.error('[UserRole] 获取用户角色失败:', error);
        }
        return null;
    })();
    
    return roleLoadPromise;
}

// 确保角色已加载（异步等待）
async function ensureRoleLoaded() {
    if (roleLoaded && currentAIRole) {
        return currentAIRole;
    }
    
    // 等待加载完成
    const role = await getCurrentUserRole();
    console.log('[UserRole] ensureRoleLoaded 返回:', role);
    return role;
}

// 同步获取角色（仅在角色已加载后使用）
function getRole() {
    const role = currentAIRole || 'investment_advisor';
    console.log('[UserRole] getRole 返回:', role, '(已加载:', roleLoaded, ')');
    return role;
}

// 检查角色是否已加载
function isRoleLoaded() {
    return roleLoaded;
}

// 页面加载时立即获取用户角色
(async function() {
    await getCurrentUserRole();
})();

