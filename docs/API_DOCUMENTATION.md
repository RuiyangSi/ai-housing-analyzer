# 📚 API 接口文档

**AI 驱动的智能房价分析系统 - RESTful API 文档**

- **版本**：v1.0.0
- **基础URL**：`http://localhost:5001`
- **认证方式**：Session Cookie

---

## 📑 目录

1. [认证接口](#1-认证接口)
2. [城市数据接口](#2-城市数据接口)
3. [AI 智能接口](#3-ai-智能接口)
4. [房价预测接口](#4-房价预测接口)
5. [策略规划接口](#5-策略规划接口)
6. [错误码说明](#6-错误码说明)

---

## 1. 认证接口

### 1.1 用户注册

**POST** `/api/auth/register`

注册新用户账号。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名（3-20字符） |
| password | string | 是 | 密码（6位以上） |
| role | string | 是 | 角色类型 |

**角色类型**

| 值 | 说明 |
|----|------|
| `first_time_buyer` | 首次购房者 |
| `investment_advisor` | 投资顾问 |
| `upgrader` | 改善型购房者 |

**请求示例**

```json
{
  "username": "testuser",
  "password": "password123",
  "role": "first_time_buyer"
}
```

**响应示例**

```json
{
  "success": true,
  "message": "注册成功"
}
```

---

### 1.2 用户登录

**POST** `/api/auth/login`

用户登录获取会话。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应示例**

```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "username": "testuser",
    "role": "first_time_buyer"
  }
}
```

---

### 1.3 用户登出

**POST** `/api/auth/logout`

退出当前登录会话。

**响应示例**

```json
{
  "success": true,
  "message": "已退出登录"
}
```

---

### 1.4 获取当前用户

**GET** `/api/auth/current-user`

获取当前登录用户信息。

**响应示例**

```json
{
  "logged_in": true,
  "username": "testuser",
  "role": "first_time_buyer"
}
```

---

## 2. 城市数据接口

### 2.1 获取城市统计数据

**GET** `/api/city/{city_name_en}/stats`

获取指定城市的统计数据。

**路径参数**

| 参数 | 说明 |
|------|------|
| city_name_en | 城市英文名（beijing/wuhan/xiamen） |

**响应示例**

```json
{
  "city_name": "北京",
  "overall": {
    "total_count": 184945,
    "avg_price": 457.81,
    "avg_unit_price": 54931.62,
    "avg_area": 84.0
  },
  "yearly": [
    {
      "year": 2023,
      "count": 65432,
      "avg_price": 450.23,
      "avg_unit_price": 53890.12
    }
  ],
  "monthly": [...],
  "districts": [...]
}
```

---

### 2.2 获取城市深度分析

**GET** `/api/city/{city_name_en}/deep-analysis`

获取城市深度分析报告数据。

**响应示例**

```json
{
  "city_name": "北京",
  "analysis": {
    "basic_stats": {
      "total_transactions": 184945,
      "price": {
        "mean": 457.81,
        "median": 420.00,
        "std": 196.32
      }
    },
    "price_trend": {...},
    "volatility": {...},
    "investment_index": {
      "score": 46.3,
      "level": "一般",
      "breakdown": {...}
    }
  }
}
```

---

### 2.3 获取全国对比数据

**GET** `/api/national-comparison`

获取多城市横向对比分析数据。

**响应示例**

```json
{
  "overview": {
    "total_transactions_all": 321765,
    "highest_price_city": "北京",
    "lowest_price_city": "武汉"
  },
  "city_comparison": [...],
  "investment_ranking": [...],
  "recommendations": {
    "for_first_time_buyers": [...],
    "for_upgraders": [...],
    "for_investors": [...]
  }
}
```

---

## 3. AI 智能接口

### 3.1 AI 对话（非流式）

**POST** `/api/ai/chat`

与 AI 助手进行对话。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息 |
| city | string | 否 | 城市英文名 |

**请求示例**

```json
{
  "message": "北京房价最近走势如何？",
  "city": "beijing"
}
```

**响应示例**

```json
{
  "success": true,
  "message": "根据2023-2025年的数据分析，北京房价整体呈现..."
}
```

---

### 3.2 AI 对话（流式）

**GET** `/api/ai/chat-stream`

流式接收 AI 响应（Server-Sent Events）。

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息（URL编码） |
| city | string | 否 | 城市英文名 |

**响应格式**

```
data: {"content": "根据"}

data: {"content": "数据"}

data: {"content": "分析"}

data: [DONE]
```

---

### 3.3 AI 城市概览（流式）

**GET** `/api/city/{city_name_en}/ai-overview-stream`

获取 AI 生成的城市概览分析（流式）。

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | 否 | 用户角色（影响分析视角） |

**响应格式**

Server-Sent Events 流式响应

---

### 3.4 AI 图表分析

**POST** `/api/ai/analyze-chart`

AI 分析指定图表数据。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chart_type | string | 是 | 图表类型 |
| chart_data | object | 是 | 图表数据 |
| city | string | 是 | 城市名 |

**图表类型**

| 值 | 说明 |
|----|------|
| `trend` | 价格趋势图 |
| `boxplot` | 箱线图 |
| `radar` | 雷达图 |
| `heatmap` | 热力图 |
| `priceRange` | 价格区间分布 |

---

### 3.5 AI 图像生成

**POST** `/api/ai/generate-image`

生成 AI 创意图像。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scene | string | 是 | 场景类型 |
| keywords | array | 是 | 关键词列表 |
| style | string | 否 | 风格（默认realistic） |
| custom_prompt | string | 否 | 自定义提示 |
| city | string | 否 | 城市名 |

**场景类型**

| 值 | 说明 |
|----|------|
| `dream_home` | 梦想家园 |
| `lifestyle` | 生活场景 |
| `renovation` | 装修效果 |
| `seasonal` | 季节氛围 |

**响应示例**

```json
{
  "success": true,
  "image_url": "https://...",
  "prompt_used": "..."
}
```

---

## 4. 房价预测接口

### 4.1 统计预测

**POST** `/api/prediction/stats`

基于统计模型的房价预测。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市英文名 |
| months | int | 否 | 预测月数（默认6） |
| district | string | 否 | 指定区域 |

**响应示例**

```json
{
  "success": true,
  "city": "北京",
  "historical": [...],
  "predictions": [
    {
      "month": "2025-07",
      "price": 455.2,
      "change": -0.5
    }
  ],
  "factors": {
    "price_trend": 2.3,
    "volume_trend": -5.2,
    "stability": 72.5
  }
}
```

---

### 4.2 AI 预测数据

**POST** `/api/prediction/ai-data`

获取 AI 深度预测分析数据。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市英文名 |
| months | int | 否 | 预测月数 |
| role | string | 否 | 用户角色 |

**响应示例**

```json
{
  "success": true,
  "ai_predictions": [
    {
      "month": "2025-07",
      "price": 452.0,
      "high": 470.0,
      "low": 435.0
    }
  ],
  "trend": "stable",
  "confidence": 75,
  "recommendation": "建议持币观望...",
  "key_factors": [...]
}
```

---

## 5. 策略规划接口

### 5.1 生成购房策略

**POST** `/api/strategy/generate`

AI 生成个性化购房策略。

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市英文名 |
| budget | number | 是 | 预算（万元） |
| purpose | string | 是 | 购房目的 |
| family_size | int | 是 | 家庭人数 |
| urgency | string | 是 | 急迫程度 |
| preferred_district | string | 否 | 期望区域 |
| work_location | string | 否 | 工作地点 |
| has_kid | boolean | 否 | 是否有小孩 |

**购房目的**

| 值 | 说明 |
|----|------|
| `self_living` | 自住 |
| `investment` | 投资 |
| `education` | 学区 |

**急迫程度**

| 值 | 说明 |
|----|------|
| `urgent` | 急迫（3个月内） |
| `moderate` | 适中（半年内） |
| `relaxed` | 不急（1年内） |

**响应示例**

```json
{
  "success": true,
  "strategy": {
    "summary": {
      "budget_range": "280-320万",
      "recommended_area": "70-90㎡",
      "recommended_type": "两居室"
    },
    "top_districts": [
      {
        "name": "昌平",
        "avg_price": 285.5,
        "match_score": 92
      }
    ],
    "action_plan": [...],
    "ai_advice": "..."
  }
}
```

---

## 6. 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 302 | 重定向（通常跳转登录） |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 业务错误码

```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

| 错误码 | 说明 |
|--------|------|
| `CITY_NOT_FOUND` | 城市数据不存在 |
| `INVALID_PARAMS` | 参数无效 |
| `AI_ERROR` | AI 服务异常 |
| `AUTH_REQUIRED` | 需要登录 |
| `USER_EXISTS` | 用户名已存在 |

---

## 📝 使用示例

### cURL 示例

```bash
# 1. 登录
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "123456"}' \
  -c cookies.txt

# 2. 获取城市统计
curl http://localhost:5001/api/city/beijing/stats \
  -b cookies.txt

# 3. AI 对话
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京房价趋势如何？", "city": "beijing"}' \
  -b cookies.txt

# 4. 房价预测
curl -X POST http://localhost:5001/api/prediction/stats \
  -H "Content-Type: application/json" \
  -d '{"city": "beijing", "months": 6}' \
  -b cookies.txt
```

### JavaScript 示例

```javascript
// 获取城市统计数据
async function getCityStats(city) {
  const response = await fetch(`/api/city/${city}/stats`);
  const data = await response.json();
  return data;
}

// AI 流式对话
function streamChat(message, city) {
  const url = `/api/ai/chat-stream?message=${encodeURIComponent(message)}&city=${city}`;
  const eventSource = new EventSource(url);
  
  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      return;
    }
    const data = JSON.parse(event.data);
    console.log(data.content);
  };
}
```

---

## 🔗 相关链接

- [项目 README](../README.md)
- [团队分工](../CONTRIBUTION.md)
- [GitHub 仓库](https://github.com/RuiyangSi/ai-housing-analyzer)

---

**文档更新时间**：2024年12月

