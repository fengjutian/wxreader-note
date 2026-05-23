"# Feature Specification: Cognitive Reading Graph (认知阅读图谱)

**Feature Branch**: `feature/cognitive-reading-graph`

**Created**: 2025-07-19

**Status**: Draft

**Input**: 用户 PRD - 基于微信读书笔记的 AI 阅读分析与知识图谱系统

---

## 1. Product Vision

### 产品定位
**AI 原生认知操作系统** - 不是"读书笔记工具"，而是人类长期思想结构与认知演化的分析系统。

### 核心价值
将分散的阅读数据转化为：
- 概念网络
- 认知图谱
- AI 驱动的阅读洞察
- "第二大脑"

### 关键概念
- **核心对象**：用户的思想结构与认知演化
- **数据来源**：微信读书笔记（高亮、划线、阅读时间等）
- **目标**：Personal Cognitive OS

---

## 2. User Scenarios & Testing

### 用户角色定义

| 角色 | 特征 | 核心需求 |
|------|------|---------|
| 普通阅读者 | 日常阅读用户 | 管理笔记、快速搜索、AI总结 |
| 深度阅读者 | 长期阅读积累 | 认知分析、思想网络、作者关系 |
| 知识管理者 | 追求系统化 | 第二大脑、知识图谱、思维演化 |

---

### User Story 1 - Markdown 文件导入 (Priority: P1)

**用户旅程**：用户将微信读书导出的 md 文件导入系统，系统自动解析并提取所有数据。

**为什么这个优先级**：
- 这是整个系统的数据入口
- 没有数据导入就没有后续分析
- 是 MVP 的核心功能

**独立测试**：可以通过上传 md 文件并验证解析结果来完全测试

**验收场景**：

1. **Given** 用户有一个微信读书导出的 md 文件
   **When** 用户上传该文件
   **Then** 系统显示文件上传成功，并自动开始解析

2. **Given** md 文件包含高亮、章节、书名等信息
   **When** 解析完成
   **Then** 所有数据正确存储到数据库，包含书名、作者、高亮内容、章节、阅读时间

3. **Given** md 文件格式不符合预期
   **When** 用户上传
   **Then** 系统显示格式错误提示，并给出正确格式示例

4. **Given** 用户批量上传多个 md 文件
   **When** 上传完成
   **Then** 所有文件按书籍分组显示，每本书独立展示

---

### User Story 2 - AI 概念抽取 (Priority: P1)

**用户旅程**：用户导入书籍后，AI 自动分析每条高亮内容，提取核心概念、学科分类、情绪倾向。

**为什么这个优先级**：
- 概念抽取是构建知识图谱的核心能力
- 是区别于普通笔记工具的关键功能
- MVP 必须展示 AI 分析能力

**独立测试**：可以针对单条高亮内容测试 AI 抽取结果

**验收场景**：

1. **Given** 用户有一条领导力相关的高亮内容
   **When** AI 分析完成
   **Then** 返回概念列表 ["领导力", "品格", "人格成长"]、学科 "组织管理"、情绪 "agreement"

2. **Given** 用户有 100 条高亮内容等待分析
   **When** 用户触发批量分析
   **Then** 系统显示分析进度，所有内容分析完成后通知用户

3. **Given** 网络中断导致分析中断
   **When** 网络恢复
   **Then** 系统自动从中断处继续分析，不丢失已分析数据

4. **Given** 高亮内容是图片（暂不支持）
   **When** 用户上传
   **Then** 系统跳过该条高亮，标记"图片内容待支持"，继续处理其他内容

---

### User Story 3 - 知识图谱可视化 (Priority: P1)

**用户旅程**：用户查看个人认知知识图谱，通过可视化界面探索概念之间的关系。

**为什么这个优先级**：
- 图谱可视化是产品的核心卖点
- 用户能直观看到自己的思想网络
- 是"第二大脑"概念的核心体现

**独立测试**：可以独立测试图谱的渲染和交互

**验收场景**：

1. **Given** 用户有 50+ 个概念节点
   **When** 用户打开图谱页面
   **Then** 图谱清晰展示节点和关系，支持缩放、拖拽、点击查看详情

2. **Given** 用户点击某个概念节点
   **When** 点击完成
   **Then** 右侧显示该概念的所有关联内容、高亮、书籍、阅读时间

3. **Given** 用户想筛选特定书籍的概念
   **When** 用户选择书籍过滤器
   **Then** 图谱只显示该书籍相关的概念和关系

4. **Given** 图谱节点过多导致视觉混乱
   **When** 用户打开图谱
   **Then** 系统自动聚类相似概念，并提供筛选器减少节点数量

---

### User Story 4 - AI 阅读画像 (Priority: P2)

**用户旅程**：用户查看 AI 自动生成的阅读人格与认知画像，包括阅读偏好、思维倾向、阅读盲区。

**为什么这个优先级**：
- 提供有价值的自我认知洞察
- 是产品差异化功能
- 驱动用户持续使用

**独立测试**：可以针对特定数据集合测试画像生成逻辑

**验收场景**：

1. **Given** 用户有 10+ 本已导入的书籍
   **When** 用户请求生成阅读画像
   **Then** 系统分析后显示：阅读偏好列表、思维倾向分析、阅读盲区建议

2. **Given** 用户是新用户（少于 3 本书）
   **When** 用户请求生成画像
   **Then** 系统显示"数据不足"，并建议用户先导入更多书籍

3. **Given** 用户的阅读偏好发生变化
   **When** 用户新增不同领域的书籍
   **Then** 系统更新画像，反映新的阅读兴趣

---

### User Story 5 - 语义搜索与 RAG (Priority: P2)

**用户旅程**：用户使用自然语言搜索自己的所有阅读笔记，系统返回语义相关的结果。

**为什么这个优先级**：
- 提供深度检索能力
- 实现"我关于 X 的所有思考"功能
- 支持知识聚合

**独立测试**：可以针对搜索功能独立测试

**验收场景**：

1. **Given** 用户搜索"信任"
   **When** 搜索完成
   **Then** 返回所有包含"信任"相关概念的高亮内容，按相关性排序

2. **Given** 用户搜索"关于领导力的思考"
   **When** 语义搜索完成
   **Then** 返回包含领导力、影响力、指导等相关概念的内容，不仅仅是"领导力"字面匹配

3. **Given** 用户想总结对某主题的认知
   **When** 用户点击"思想聚合"按钮
   **Then** 系统汇总所有相关内容，生成主题总结

---

### User Story 6 - AI 阅读建议 (Priority: P3)

**用户旅程**：用户获得基于认知图谱的下一本书推荐和阅读路线建议。

**为什么这个优先级**：
- 提供主动价值输出
- 是"AI 阅读教练"愿景的第一步
- 增加用户粘性

**独立测试**：可以针对特定认知图谱测试建议生成

**验收场景**：

1. **Given** 用户的认知图谱显示近期关注领导力、愿景、信任
   **When** 用户请求阅读建议
   **Then** 系统推荐《从优秀到卓越》《第五项修炼》《原则》等书籍，并说明理由

2. **Given** 用户的阅读图谱显示缺少文学、心理学内容
   **When** 系统生成画像
   **Then** 画像中包含"阅读盲区"建议，推荐相关领域书籍

3. **Given** 用户想制定长期阅读计划
   **When** 用户请求阅读路线
   **Then** 系统根据用户现有知识结构，设计循序渐进的学习路径

---

### User Story 7 - 认知成长轨迹 (Priority: P3)

**用户旅程**：用户查看长期思想变化的时间线，分析认知成长路径。

**为什么这个优先级**：
- 展示时间维度上的认知演化
- 提供独特的自我洞察
- 是"第二大脑"愿景的重要组成部分

**独立测试**：可以针对时间序列数据测试轨迹展示

**验收场景**：

1. **Given** 用户有 3 年以上的阅读数据
   **When** 用户查看成长轨迹
   **Then** 显示按年度组织的思想变化时间线（如 2024: AI → 2025: 管理 → 2026: 哲学）

2. **Given** 用户想了解某个时期的阅读主题
   **When** 用户点击时间线节点
   **Then** 显示该时期阅读的书籍列表、高亮内容、概念分布

3. **Given** 用户的阅读主题发生重大转变
   **When** 系统检测到转变
   **Then** 在时间线上标注"思想转型点"，并显示转变原因

---

### Edge Cases

- **空数据**：用户首次使用，没有任何导入数据 → 显示引导教程
- **格式不支持**：用户上传非 md 格式文件 → 明确提示支持的格式
- **重复导入**：用户重复导入同一本书 → 询问是合并还是覆盖
- **API 限流**：AI 分析请求被限流 → 排队处理，显示预计等待时间
- **图数据库故障**：Neo4j 不可用 → 显示降级提示，数据仍可存储
- **向量检索失败**：Qdrant 不可用 → 降级为全文搜索
- **单本书过大**：一本书有 1000+ 高亮 → 分批处理，避免超时
- **用户隐私**：用户删除账号 → 所有个人数据完全清除

---

## 3. Requirements

### Functional Requirements

#### 3.1 Markdown 导入系统 (模块1)

- **FR-001**: 系统 MUST 支持导入微信读书导出的 md 文件
- **FR-002**: 系统 MUST 解析 md 文件并提取：书名、作者、分类、ISBN、阅读时间、阅读进度、阅读日期
- **FR-003**: 系统 MUST 解析 md 文件并提取高亮数据：章节、划线内容、阅读时间、原始链接
- **FR-004**: 系统 MUST 输出统一的 JSON 数据结构
- **FR-005**: 系统 MUST 支持批量上传多个 md 文件
- **FR-006**: 系统 MUST 验证 md 文件格式，不符合格式时给出明确错误提示

#### 3.2 阅读数据结构化 (模块2)

- **FR-007**: 系统 MUST 定义数据模型：Book, Author, Highlight, Concept, Reader, Chapter
- **FR-008**: 系统 MUST 存储书籍的完整元数据
- **FR-009**: 系统 MUST 关联高亮内容与书籍、章节
- **FR-010**: 系统 MUST 维护概念库，支持概念的增删改查

#### 3.3 AI 概念抽取 (模块3)

- **FR-011**: 系统 MUST 使用 LLM 自动提取核心概念
- **FR-012**: 系统 MUST 对每个高亮内容进行学科分类（管理学、哲学、心理学、AI 等）
- **FR-013**: 系统 MUST 分析高亮内容的情绪倾向（共鸣、质疑、反对、兴奋）
- **FR-014**: 系统 MUST 提取用户关注点和作者观点
- **FR-015**: 系统 MUST 支持批量处理高亮内容
- **FR-016**: 系统 MUST 处理 API 限流和错误重试

#### 3.4 知识图谱系统 (模块4)

- **FR-017**: 系统 MUST 使用 Neo4j 构建个人认知知识图谱
- **FR-018**: 系统 MUST 定义节点类型：Book, Concept, Author, Highlight
- **FR-019**: 系统 MUST 定义关系类型：(Book)-[:HAS_CONCEPT]->(Concept), (Reader)-[:LIKES]->(Concept), (Book)-[:WRITTEN_BY]->(Author), (Highlight)-[:RELATED_TO]->(Concept)
- **FR-020**: 系统 MUST 提供图谱可视化界面
- **FR-021**: 系统 MUST 支持点击节点查看详情
- **FR-022**: 系统 MUST 支持按书籍筛选图谱节点

#### 3.5 Embedding 向量检索 (模块5)

- **FR-023**: 系统 MUST 使用 Qdrant 实现向量检索
- **FR-024**: 系统 MUST 支持语义搜索（搜索"信任"返回所有相关概念内容）
- **FR-025**: 系统 MUST 支持思想聚合（总结用户对某主题的认知）
- **FR-026**: 系统 MUST 在向量检索失败时降级为全文搜索

#### 3.6 AI 阅读画像 (模块6)

- **FR-027**: 系统 MUST 生成阅读偏好分析（学科倾向、作者偏好）
- **FR-028**: 系统 MUST 生成思维倾向分析（理性主义、长期主义、愿景驱动等）
- **FR-029**: 系统 MUST 识别阅读盲区（缺少的学科或领域）
- **FR-030**: 系统 MUST 在数据不足时（少于 3 本书）提示用户

#### 3.7 AI 阅读建议系统 (模块7)

- **FR-031**: 系统 MUST 基于认知图谱推荐下一本书
- **FR-032**: 系统 MUST 推荐阅读路线和学习路径
- **FR-033**: 系统 MUST 推荐思维补全书籍
- **FR-034**: 系统 MUST 解释推荐理由

#### 3.8 认知成长轨迹 (模块8)

- **FR-035**: 系统 MUST 展示用户长期思想变化的时间线
- **FR-036**: 系统 MUST 按年度组织思想主题
- **FR-037**: 系统 MUST 标注"思想转型点"
- **FR-038**: 系统 MUST 支持点击时间节点查看详情

---

### Key Entities

| 实体 | 描述 | 关键属性 |
|------|------|---------|
| **Book** | 书籍 | id, title, author, category, isbn, reading_time, progress, reading_date |
| **Author** | 作者 | id, name, bio, domains |
| **Highlight** | 高亮 | id, book_id, content, chapter, create_time, url, concepts, emotion |
| **Concept** | 概念 | id, name, domain, frequency, last_mentioned |
| **Reader** | 用户 | id, name, reading_profile, interests |
| **Chapter** | 章节 | id, book_id, title, order, highlight_count |

---

## 4. Success Criteria

### Measurable Outcomes

- **SC-001**: 用户能在 30 秒内完成单个 md 文件的上传和解析
- **SC-002**: AI 概念抽取准确率达到 85%+（概念相关性）
- **SC-003**: 图谱可视化加载时间 < 3 秒（100 个节点）
- **SC-004**: 向量搜索响应时间 < 1 秒
- **SC-005**: AI 阅读画像生成时间 < 10 秒
- **SC-006**: 系统支持 100 万+ 图谱节点
- **SC-007**: MVP 功能完成率 100%（md 导入、解析、AI 概念抽取、Neo4j 图谱、AI 阅读画像）
- **SC-008**: 用户满意度评分 4.5+/5.0（内测反馈）

---

## 5. Non-Functional Requirements

### Performance

| 指标 | 要求 |
|------|------|
| 系统响应时间 | < 3s |
| 向量搜索 | < 1s |
| AI 分析 | < 10s |
| 图谱节点容量 | 100 万+ |

### Scalability

- 支持单用户（MVP 阶段）
- 数据存储设计考虑多用户扩展

### Security

- 用户数据隔离（即使是单用户也要考虑数据安全）
- 无硬编码凭证
- API 密钥使用环境变量

### Technology Stack

| 模块 | 技术 |
|------|------|
| 后端 | FastAPI + AI |
| 图数据库 | Neo4j |
| 向量库 | Qdrant |
| 数据库 | PostgreSQL |
| 前端 | React |
| 图谱可视化 | Cytoscape.js |
| 工作流 | LangChain / LlamaIndex |

---

## 6. MVP Scope (Phase 1)

### Must Have (MVP)

✅ 1. md 导入
✅ 2. 数据解析
✅ 3. AI 概念抽取
✅ 4. Neo4j 图谱
✅ 5. AI 阅读画像

### Out of Scope (Phase 1)

❌ 多用户系统
❌ 社交功能
❌ Agent
❌ 自动写作
❌ 多模态支持

---

## 7. Assumptions

- **假设 1**：用户有微信读书账号并能导出 md 文件
- **假设 2**：用户使用 OpenAI / Qwen / DeepSeek API
- **假设 3**：用户有一定技术背景（能部署和配置系统）
- **假设 4**：用户有 Neo4j 和 Qdrant 的使用经验或愿意学习
- **假设 5**：MVP 阶段为单用户，后续需要多用户支持
- **假设 6**：用户设备有稳定网络连接（依赖云端 API）
- **假设 7**：md 格式为微信读书标准导出格式

---

## 8. Technical Notes

### Data Model (PostgreSQL)

#### books 表
```sql
CREATE TABLE books (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    category VARCHAR(100),
    isbn VARCHAR(20),
    reading_time INTERVAL,
    progress DECIMAL(5,2),
    reading_date DATE
);
```

#### highlights 表
```sql
CREATE TABLE highlights (
    id UUID PRIMARY KEY,
    book_id UUID REFERENCES books(id),
    content TEXT,
    chapter VARCHAR(255),
    create_time TIMESTAMP,
    url TEXT,
    concepts JSONB,
    emotion VARCHAR(50)
);
```

#### concepts 表
```sql
CREATE TABLE concepts (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    domain VARCHAR(100),
    frequency INTEGER DEFAULT 0
);
```

### Neo4j Graph Structure

```
(Book)-[:HAS_CONCEPT]->(Concept)
(Reader)-[:LIKES]->(Concept)
(Book)-[:WRITTEN_BY]->(Author)
(Highlight)-[:RELATED_TO]->(Concept)
```

### API Endpoints (MVP)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | /api/v1/import | 上传 md 文件 |
| GET | /api/v1/books | 获取书籍列表 |
| GET | /api/v1/books/{id} | 获取书籍详情 |
| POST | /api/v1/analyze | 触发 AI 分析 |
| GET | /api/v1/graph | 获取图谱数据 |
| GET | /api/v1/profile | 获取阅读画像 |
| GET | /api/v1/search | 语义搜索 |
| GET | /api/v1/timeline | 获取成长轨迹 |

---

## 9. Future Extensions

1. **AI 读书教练**：每日建议（如"你最近阅读过于偏技术，建议增加文学阅读"）
2. **作者思想网络**：展示思想传承关系（尼采 → 福柯 → 德勒兹）
3. **AI 自动生成读书报告**
4. **多用户认知社交**：发现思想最接近的人
5. **实时同步**：与微信读书 API 同步（如果有）
6. **移动端**：iOS/Android 应用
7. **浏览器插件**：快速添加网页摘录到图谱