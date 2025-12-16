#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   GitHub 上传脚本 v1.5.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 错误：Git未安装${NC}"
    echo "请先安装Git: https://git-scm.com/downloads"
    exit 1
fi

# 检查是否是Git仓库
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠️  警告：当前目录不是Git仓库${NC}"
    read -p "是否初始化Git仓库? (y/n): " init_git
    if [ "$init_git" = "y" ]; then
        git init
        echo -e "${GREEN}✅ Git仓库初始化成功${NC}"
    else
        echo -e "${RED}❌ 取消操作${NC}"
        exit 1
    fi
fi

# 显示当前状态
echo -e "${BLUE}📊 当前Git状态:${NC}"
git status --short
echo ""

# 添加所有文件
echo -e "${YELLOW}📦 添加文件到暂存区...${NC}"
git add .
echo -e "${GREEN}✅ 文件添加完成${NC}"
echo ""

# 显示将要提交的文件
echo -e "${BLUE}📝 将要提交的文件:${NC}"
git status --short
echo ""

# 确认提交
read -p "是否继续提交? (y/n): " confirm_commit
if [ "$confirm_commit" != "y" ]; then
    echo -e "${RED}❌ 取消操作${NC}"
    exit 1
fi

# 提交
echo -e "${YELLOW}💾 提交修改...${NC}"
git commit -m "v1.5.0: 视觉优化与信息完善 - 最终版

🎨 视觉优化:
- 首页数据分布全景：扩展颜色方案至26种（支持全部省份）
- 全国对比页面：更新页面描述文案

📊 数据更新:
- 修正省份数量显示：13个 → 26个省级行政区
- 优化数据展示准确性

🐛 Bug修复 (v1.4.1):
- 修复AI策略规划器点击无反应问题
- 修复Markdown渲染吞字问题
- 修复AI智能浏览双击调用2次API问题

✨ 新功能 (v1.4.1):
- 城市实时搜索功能
- 区域筛选功能（7大区域）
- 智能分页功能（每页6个）
- 完整Markdown渲染支持

📝 文档:
- 新增10+份技术文档
- 完善功能说明和使用指南

🎯 最终版说明:
- 所有核心功能已完成
- 用户体验优化到位
- 数据准确性验证完成
- 视觉呈现统一美观"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 提交成功${NC}"
else
    echo -e "${RED}❌ 提交失败${NC}"
    exit 1
fi
echo ""

# 检查远程仓库
if git remote | grep -q 'origin'; then
    echo -e "${BLUE}🌐 检测到远程仓库:${NC}"
    git remote -v
    echo ""
    
    # 推送到远程
    read -p "是否推送到GitHub? (y/n): " confirm_push
    if [ "$confirm_push" = "y" ]; then
        echo -e "${YELLOW}🚀 推送到GitHub...${NC}"
        git push origin main || git push origin master
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 推送成功!${NC}"
            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}   🎉 上传完成!${NC}"
            echo -e "${GREEN}========================================${NC}"
        else
            echo -e "${RED}❌ 推送失败${NC}"
            echo ""
            echo -e "${YELLOW}可能的解决方案:${NC}"
            echo "1. 先拉取远程更新: git pull origin main --rebase"
            echo "2. 检查远程仓库URL: git remote -v"
            echo "3. 检查GitHub认证: git config --list | grep user"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  未检测到远程仓库${NC}"
    echo ""
    echo -e "${BLUE}请按以下步骤操作:${NC}"
    echo "1. 在GitHub上创建新仓库（不要初始化README）"
    echo "2. 运行以下命令:"
    echo -e "${GREEN}   git remote add origin https://github.com/你的用户名/仓库名.git${NC}"
    echo -e "${GREEN}   git push -u origin main${NC}"
fi

echo ""
echo -e "${BLUE}📚 更多帮助请查看: GITHUB_UPLOAD_GUIDE.md${NC}"

