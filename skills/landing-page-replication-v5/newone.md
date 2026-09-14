# Stylish Landing Pages, Rebuilt

> 一份面向 AI coding agent 的高质量网页源码馆与逆向工程资源地图。先读成品源码，再谈 skill；不是 clone 仓库黄页，也不是“输入 URL，一键 100% 复刻”的愿望清单。
>
> **OSINT 核验日期：2026-09-11。** 本文优先采用项目仓库、官方文档、live demo 和官方产品页。仓库 README 中未经第三方复现的准确率、耗时和兼容性均视为**项目自述**，不当作独立结论。

## 先说结论：源码优先，instruction 靠后

对于 agent，优秀成品源码不是普通参考链接，而是高密度 few-shot context。它同时暴露：

- section 与 component 怎样切；
- typography、spacing、layer、breakpoint 怎样落到代码；
- GSAP timeline、scroll pin、pointer response 和 WebGL render loop 的真实参数；
- assets、fonts、video、shader、fallback 与 responsive variant 怎样组织；
- 一个机制在生产工程里怎样与 routing、SEO、performance 和 accessibility 共存。

所以优先级应当是：

```text
原作者 / 官方生产源码
  → 高质量第三方重建
  → 单机制教学源码
  → 对未开源 live site 做 forensic capture
  → skill / instruction 帮助取证、实现和验收
```

Skill 能告诉 agent “应当检查 motion”；源码能直接给出 timeline、trigger、easing、cleanup 和 mobile branch。前者不能替代后者。只有在源码不存在、版本不对、行为未覆盖，或需要证明 fidelity 时，DOM / CSSOM / runtime capture 与视觉行为 gate 才接手。

本文因此只保留 **8 个高信号源码样本**。筛选不按 stars，也不按品牌凑数；要求尽量具备：

1. 可取得的非空源码；
2. 核验时可访问的 live demo / production site；
3. 至少一个值得单独学习的实现机制；
4. 来源、license 和资产风险能够说清；
5. 不是只有 hero、navbar 或教程壳子的低完成度作业。

较老不等于低质。一个 2021–2024 项目只要 demo 和源码仍有独特信息，就比 2026 年堆满 `pixel-perfect`、`Awwwards-level` 形容词的空壳更值得保留。

---

## 1. Curated source gallery：只留 8 个

这不是客观总排名，而是一套刻意拉开机制差异的 specimen set。`Study` 表示适合读源码；`Reuse` 只评价代码许可，不代表品牌、文案、字体、图片、视频和商标也可复用。

### A. 原作者 / 官方生产源码

#### 1. `Giats2498/giats-portfolio` — 原作者的获奖 WebGL portfolio

- 源码：[github.com/Giats2498/giats-portfolio](https://github.com/Giats2498/giats-portfolio)
- Live：[giats.me](https://giats.me/)
- 身份：Evangelos Giatsidis 公开的原始源码；Awwwards Honorable Mention、CSS Design Awards WOTD、GSAP Site of the Day 均有外部页面可核。
- 栈：Next.js、React Three Fiber、GSAP / ScrollTrigger、SCSS / CSS Modules、GLSL。
- 最值得学：三层合成——动态 3D background、DOM content、实时 fluid pointer overlay；内容区用“window”露出底层 WebGL；自定义页面转场与 smooth-scroll 协调。
- 状态：仓库创建并公开于 2025；核验时 production site 可访问，运行时有 4 个 canvas。
- 许可：MIT，保留 copyright / permission notice。品牌、作品图和第三方素材仍需逐项审查。

**裁决：Study first / Reuse code with notice。** 这是 8 个项目中 provenance 最干净、creative coding 信息密度最高的一个。

#### 2. `supabase/supabase` 的 `apps/www` — 真正上线的大型产品官网

- 源码：[github.com/supabase/supabase/tree/master/apps/www](https://github.com/supabase/supabase/tree/master/apps/www)
- Live：[supabase.com](https://supabase.com/)
- 身份：Supabase 官方 monorepo 内的 production website，不是仿站。
- 栈：Next.js、TypeScript、Tailwind，以及同仓库的 design-system / UI packages。
- 最值得学：大型 developer product 如何组织 homepage、pricing、customers、blog、events、SEO、OG generation、内容数据和共享组件；尤其适合研究长页面的信息密度、code/product theater 与 production constraints。
- 状态：2019 年建立、核验日仍高频更新；`apps/www` 有独立 development guide、assets 规则和完整页面目录。
- 许可：仓库根目录 Apache-2.0；第三方内容和 Supabase trademarks 不因代码许可证自动开放。

**裁决：Study / Reuse under Apache-2.0。** 想学“真实公司官网怎样长期长大”，优先读它，而不是读又一个 SaaS template。

#### 3. `dubinc/dub` — marketing、product UI 与真实业务共仓

- 源码：[github.com/dubinc/dub](https://github.com/dubinc/dub)
- Live：[dub.co](https://dub.co/)
- 身份：Dub 官方 production monorepo；核验时官网和源码均活跃。
- 栈：Next.js、TypeScript、Tailwind、Turborepo；`apps/web` 同时包含 public surfaces、dashboard、shared UI 和测试。
- 最值得学：marketing promise 怎样直接落到可交互产品 mock、analytics / link / partner UI；同一设计语言如何跨官网、auth 和 dashboard；复杂产品如何把 UI、routes、data 与 tests 放在一个可维护系统里。
- 状态：2022 年建立，核验日仍有提交；live homepage 返回完整生产页面。
- 许可：大部分代码为 AGPL-3.0；`apps/web/app/(ee)` 等目录另有 enterprise license。必须按文件路径判断，不能把整个仓库简称为 MIT。

**裁决：Study deeply / Reuse only after license review。** 它是 production reference，不是拿来直接抄一套闭源 SaaS 的模板。

#### 4. `midday-ai/midday` 的 `apps/website` — 视觉完整的开源产品站

- 源码：[github.com/midday-ai/midday/tree/main/apps/website](https://github.com/midday-ai/midday/tree/main/apps/website)
- Live：[midday.ai](https://midday.ai/)
- 身份：Midday 官方网站源码，与 dashboard、API、desktop app 同一 monorepo。
- 栈：Next.js、TypeScript、Tailwind；网站内有独立 `components/motion-primitives`、public assets 和 source tree。
- 最值得学：克制的 editorial typography、finance product screenshots、深浅层次、motion primitives，以及官网如何从品牌叙事自然过渡到真实产品界面。
- 状态：2023 年建立；核验时 production site 可访问，网站目录完整，不是 README showcase。
- 许可：AGPL-3.0；图片、品牌和产品内容另审。

**裁决：Study / Copyleft-aware reuse。** 比通用“暗色渐变 + bento”模板更接近一个有明确产品主语的现代 SaaS 官网。

### B. 高质量第三方重建

#### 5. `yashxcode/linear-rebuilt` — 旧版 Linear 的完整视觉教材

- 源码：[github.com/yashxcode/linear-rebuilt](https://github.com/yashxcode/linear-rebuilt)
- Live：[linear-rebuilt.vercel.app](https://linear-rebuilt.vercel.app/)
- 栈：Next.js、TypeScript、Tailwind CSS；完整组件和本地图片资产。
- 最值得学：hero、command menu、keyboard shortcuts、feature cards、gradients 和长页节奏怎样组成一套高密度 product theater。核验时 demo 可访问，页面约 9.6k CSS px 长，而不是一张 hero 截图。
- 状态：创建于 2024-07-02，公开 HEAD 日期为 2024-07-08；老版本本身不是缺点，它仍是一个完成度高、可直接读的 frozen specimen。
- Provenance caveat：与更早的 [`frontendfyi/rebuilding-linear.app`](https://github.com/frontendfyi/rebuilding-linear.app) 在组件结构和多项 assets 上高度重合；独立来源关系无法仅凭公开材料确认。这里不做抄袭指控，也不把它写成来源已确认的独立原创。
- 许可：仓库没有 LICENSE。公开可读不等于获准复制、修改或商用；Linear 品牌、文案和素材也不属于仓库作者。

**裁决：Study first / Do not redistribute。** 用户已实际指出其 demo 质量优秀；它应当是一级 specimen，而不是被 stars 或年代埋掉。

#### 6. `Thakuma07/Truus.co-Awwward-Website` — playful agency motion 拆解

- 源码：[github.com/Thakuma07/Truus.co-Awwward-Website](https://github.com/Thakuma07/Truus.co-Awwward-Website)
- Live：[truus-awwward-website.vercel.app](https://truus-awwward-website.vercel.app/)
- 栈：Next.js 15、React 19、Vanilla CSS、GSAP / ScrollTrigger / InertiaPlugin、Lenis。
- 最值得学：velocity-based card fling、scribble page transition、elastic card spread、SVG path draw、cursor-speed sticker push、double marquee，以及 desktop interaction 到 mobile scroll reveal 的分支。
- 状态：2026 年项目；核验时 demo 是约 9.8k CSS px 的完整长页，源码按 11 个 CSS partials 和独立 components 组织。
- 缺口：原站 Vimeo hero 受 domain privacy 限制，repo 明确说明视频未随项目提供；showreel 也有 placeholder。
- 许可：没有 LICENSE；Truus 品牌与提取的 logos / stickers / fonts 不应复用。

**裁决：Study motion / Watch gaps / No commercial reuse assumption。** 价值在交互词典，不在“1:1”自述。

#### 7. `ahmedragab15/spylt-gsap-website` — scroll theater 与视频编排

- 源码：[github.com/ahmedragab15/spylt-gsap-website](https://github.com/ahmedragab15/spylt-gsap-website)
- Live：[spylt-gsap-website.vercel.app](https://spylt-gsap-website.vercel.app/)
- 栈：Next.js、TypeScript、Tailwind CSS、GSAP / ScrollTrigger / ScrollSmoother。
- 最值得学：长距离 pinning、parallax、clip-path reveal、text timelines 和多个产品视频之间的 scroll orchestration。
- 状态：2025 年建立、2026 年仍更新；核验时 demo 可访问，约 18.1k CSS px，DOM 中有 10 个 video，明显不是单屏练习。
- 边界：README 只能证明作者声明；本文没有独立 pixel / behavior benchmark。对 mobile、reduced-motion 和 load cost 应自行跑 gate。
- 许可：没有 LICENSE；SPYLT 品牌和 media assets 不可因 GitHub 公开而默认商用。

**裁决：Study scroll choreography / No reuse assumption。** 适合抽取 timeline 结构，不适合整页搬走。

#### 8. `HugoRCD/raycast-nuxt-ui-clone` — 用组件系统重建高密度 product UI

- 源码：[github.com/HugoRCD/raycast-nuxt-ui-clone](https://github.com/HugoRCD/raycast-nuxt-ui-clone)
- Live：[raycast-nuxt-ui.hrcd.fr](https://raycast-nuxt-ui.hrcd.fr/)
- 形态：这不是长 landing page，而是 full-viewport Raycast command palette specimen；保留它是为了给 landing page 的 product theater 提供真实 UI 语法。
- 栈：Nuxt 3、TypeScript、Nuxt UI v3、Tailwind CSS v4、composables。
- 最值得学：command palette、modal、dropdown、context actions、keyboard shortcuts，以及 extensions 如何通过 data/composable/component 边界组合。它证明高辨识度 UI 不一定要绕开组件系统手写一切。
- 状态：2025 年建立、2026 年仍更新；核验时 demo 可访问，有 40 张图片、42 个 button 和多个 UI state。
- 许可：Apache-2.0；Raycast 名称、icons 和 visual identity 仍属各自权利人。

**裁决：Study / Reuse code under Apache-2.0, rebrand assets。** 用它学习 product mock，不要把它误写成 Raycast 官网 clone。

### 为什么其他候选没进前八

- 只做 navbar、hero 或单一 hover 的项目：机制太窄，去看对应组件源码即可。
- README 自称 `pixel-perfect` / `Awwwards-level`，但 demo、源码或 assets 对不上：淘汰。
- `Capsule` 一类桌面 demo 有亮点，但仓库自述仍未完成响应式，且提交了 `node_modules`：不占主馆名额。
- 大量 Rejouice、Sundown、Ochi、Zentry、SPYLT 重复 clone：同源教程和重复机制很多，只保留实质信息增益最高的代表。
- 普通 SaaS starter：能跑不等于值得作为 art-direction specimen；真实产品站优先。

这 8 个不是“可放心复制的 8 套模板”。它们是 8 本不同的实现词典：production information architecture、product theater、editorial SaaS、WebGL layers、Linear density、playful pointer physics、scroll-video theater、command UI。

---

## 2. 找不到足够源码时：Agent-friendly 逆向资源

### A. `boyang-hu/website-rebuild-skill` — 最强在“取证与可追溯”

- 源码：[github.com/boyang-hu/website-rebuild-skill](https://github.com/boyang-hu/website-rebuild-skill)
- 核验时：MIT，Agent Skills-compatible，Node.js ≥22；项目列出 Codex 与 Claude Code 的运行案例。
- 关键机制：
  - 开工前判级，不强行处理不适合的目标；
  - 整站只读镜像、SHA-256 账本、引用闭包与离线运行；
  - bundle 行号溯源；
  - console / network / DOM / geometry / pixel 五层比对；
  - Wayback 死站恢复；
  - 针对 RSC / Next.js App Router 的 flight 数据重构。

它解决的是“**源站究竟做了什么，以及我的重建能否追溯回证据**”。这是 OSINT / software archaeology 路线，不只是看截图写 CSS。

**限制：**

- 逐行还原与 landing-page replication 并不总是同一个目标；商业新产品通常应该复用设计语言，而不是继承源站 bundle 的怪写法和全部行为。
- “逐文件、逐行、整站”会显著增加成本；只复刻一个营销页时可能过重。
- 项目列出的验证成绩主要来自项目自身，本文未找到统一、第三方维护的跨工具 benchmark。

**裁决：Adopt ideas，按需调用；不要取代 v5 主流程。** 最值得吸收的是判级、哈希 provenance、离线证据包和 Wayback 路由。

### B. `voidmatcha/ui-clone-skills` — 最值得跟踪的 motion forensic 专项

- 源码：[github.com/dididy/ui-skills](https://github.com/dididy/ui-skills)（仓库展示名为 `voidmatcha/ui-clone-skills`）
- 核验时：Apache-2.0；Claude Code / Codex plugin；仓库较新、关注量仍低。
- 它把任务拆成四个动作：`decode`、`clone`、`verify`、`extract`。
- 关键机制：下载真实 CSS，以 `getComputedStyle` 兜底；从 bundle 中抽取 GSAP、Framer Motion、anime.js、Lenis、Webflow IX2 参数；用 AE / SSIM 做视觉差异，并单列 motion parity。

它抓住了大多数 screenshot-to-code 工具的盲点：**默认帧相似，不代表 transition、scroll engine、sticky state 或 pointer response 相同。**

**限制：**

- 创建于 2026 年，公开采用与独立复现证据尚薄；不能因技术叙述详细就推断其所有路径稳定。
- “直接保留原 CSS 与 class”有利于 fidelity，但未必有利于长期维护、品牌去耦和商用 rebrand。
- bundle 分析会受混淆、动态加载、bot protection 与框架更新影响。

**裁决：Watch / borrow。** 对 GSAP / Lenis / Webflow / 重 motion 页面很有价值；最值得与 v5 的 runtime gates 做 bake-off。

### C. `aatmik-panse/clone-site-skill` — 方法完整，成熟度未证明

- 源码：[github.com/aatmik-panse/clone-site-skill](https://github.com/aatmik-panse/clone-site-skill)
- 核验时：MIT；Chrome CDP + Node；仓库创建于 2026-08，公开采用极少。
- 方法：`measure → mirror assets → emit tokens → cut into sections → fan out agents → verify → repair`。
- 值得借鉴：
  - palette 按 painted area 聚类；
  - 资产 SHA-256 provenance；
  - 每 section、每 width 的 pixel / perceptual hash / worst tile / geometry / text / token / overflow 检查；
  - bounded repair loop；未解决项写入 `UNRESOLVED.md`，而不是宣布完成；
  - motion 同时从 runtime 与 source 获取。

**限制：**项目太新；能力覆盖面很大，但 README 中的覆盖面不等于所有框架、站点和边缘状态均被验证。

**裁决：Watch。** 它的 `UNRESOLVED.md` 和“每个数字必须实测”原则可信且可移植；整套采用要先拿同一目标与 v5 做盲测。

### D. `iamphduc/claude-skill-web-clone` — 正确的路由思想

- 源码：[github.com/iamphduc/claude-skill-web-clone](https://github.com/iamphduc/claude-skill-web-clone)
- 核验时：MIT；当前仓库是 fork，公开采用很少。
- 最有价值的不是“万能复刻”，而是先分型：
  - 静态站优先 mirror；
  - React / Vue / Next 内容站做工程重建；
  - 多页站先 crawl routes；
  - 交互站记录 hover / click / scroll / canvas drag；
  - WebGL / Canvas 采用 source-first，并以 `SOURCE / PARTIAL / GUESS` 标记证据等级。

**裁决：Borrow the router。** 尤其值得保留的是“能 mirror 就不要先生成”“任何 AI 生成的可执行机制，未经源码或 runtime 证据验证，都只是猜测”。这与 v5 的 capture router 和 behavior gates 同向。

### E. `JCodesMore/ai-website-cloner-template` — 好用的产品化模板，不是客观标杆

- 源码：[github.com/JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)
- 核验时：MIT；2026 年创建，GitHub 可见关注量很高；支持多种 agent 配置。
- 默认输出强绑定 Next.js 16、React 19、Tailwind v4、shadcn/ui。
- 工作流包含 reconnaissance、token/assets、component specs、worktree 并行构建、assembly 与 visual diff。

它适合“我接受这套栈，希望 agent 立即有一个组织良好的工作区”。它不适合被描述为任何现有项目都应迁入的底层能力。

**限制：**

- 多 agent / worktree 增加 merge、上下文和一致性成本；section 彼此耦合时并行并不会自动更快。
- 默认技术栈可能迫使原项目迁移，而不是最小改动。
- 一条命令只是入口，不是 fidelity 证据。

**裁决：Use as a template when greenfield stack matches；既有项目默认不采用。**

---

## 3. Screenshot-to-code：重要兜底，不是逆向工程

### `abi/screenshot-to-code`

- 源码：[github.com/abi/screenshot-to-code](https://github.com/abi/screenshot-to-code)
- 核验时：MIT，2023 年创建，持续维护，支持 HTML/Tailwind、React、Vue、Bootstrap、Ionic；也支持 screen recording。
- 本地运行需要至少一个模型 provider key；部分资产处理与视频能力依赖额外服务。

它适合：

- 原站已经消失；
- 只有设计稿、历史截图或录屏；
- 先生成可编辑初稿，再进入人工/agent 的视觉迭代。

它不拥有 DOM、CSSOM、network、font files、breakpoint rules 或完整状态机。单张 screenshot 本质上是一个采样帧；不可见的 responsive、scroll、hover、focus、reduced-motion 都需要另找证据。

**裁决：Fallback only。** 有 live URL 时，先 capture runtime；没有 live source 时，才把 screenshot-to-code 当起点，并明确所有 off-frame behavior 都是待证假设。

---

## 4. 设计研究正在变得真正 agent-friendly

复刻一个品牌可以学 craft；直接把一个品牌的视觉身份搬到新产品里，则容易过拟合和进入 trade-dress 灰区。对于要公开上线的产品，v5 的正确姿势仍是：**组合 3–5 个 leader，保留机制，替换品牌表达。**

### Mobbin MCP — 最大规模的真实 screen / flow 入口之一

- 官方页：[mobbin.com/mcp](https://mobbin.com/mcp)
- 官方文档列出的工具：`search_screens`、`search_flows`、`search_sections`。
- 官方自述：超过 621,500 个 shipped screens；MCP 包含于付费计划。
- 优点：agent 可以直接查 landing sections、pricing、footer 和产品流程，不必人工截图搬运。
- 限制：库规模不等于样本有效性；“某大厂这样做”也不证明对你的用户或转化目标有效。

### Refero MCP + Refero Skill — 结构化研究更明确

- 官方页：[refero.design/mcp](https://refero.design/mcp)
- 官方自述：142,000+ screens、12,000+ flows；需要 Pro。
- 将资料分成 styles、screens、flows，提供结构化 metadata，并有配套 research-first skill。
- 适合：先比较同类产品的 page argument、flow 与 component anatomy，再选视觉机制。

### 怎么选

- 要大量真实产品屏幕、网页 section 搜索：先试 **Mobbin**。
- 要把 style / screen / flow 三层研究写进 agent 工作流：先试 **Refero**。
- 两者都是**参考数据库**，不是质量裁判。最终仍需针对自己的用户、内容和任务做取舍。

如果没有付费 MCP，不必假装工具缺失等于无法研究。可以用公开官网、官方 changelog、Awwwards/landing gallery、产品发布帖和浏览器 capture 建一个小而明确的 reference set。关键不是图片数量，而是每个 reference 回答了哪个决策。

---

## 5. Component registry：提供零件，不提供品味

### shadcn MCP

- 官方文档：[ui.shadcn.com/docs/mcp](https://ui.shadcn.com/docs/mcp)
- 能力：搜索、查看并安装 shadcn-compatible registries 中的 components、blocks、templates；支持 public、private 和 namespaced registry。
- 价值：agent 获取真实源码、依赖和安装命令，减少 hallucinated props 与重复造轮子。

### 21st.dev

- 官方页：[21st.dev](https://21st.dev/)
- 官方自述：12,000+ React components/templates/themes，其中 2,000+ marketing blocks；组件以 React + Tailwind / shadcn conventions 进入项目，可编辑。
- 价值：animated hero、shader、background、navigation、pricing 等复杂零件的供应比自己从零写更快。

两者都不解决：

- 为什么这一页要有这个 section；
- 哪个产品对象应该成为 hero；
- 页面叙事如何从 hook 走到 proof 再到 conversion；
- 组件拼起来是否像同一个品牌。

**先定 SIGNAL / DESIGN contract，再取组件。** 反过来从 registry 拼页面，通常会得到一张漂亮但没有产品主语的组件目录。

---

## 6. Visual QA：先用已有原语，再升级平台

### 默认：Playwright 原生 screenshot assertions

官方文档：[playwright.dev/docs/test-snapshots](https://playwright.dev/docs/test-snapshots)

```ts
await expect(page).toHaveScreenshot('landing.png')
```

Playwright 会生成 baseline，后续运行做视觉比较。官方也明确警告：OS、浏览器版本、字体、硬件和 headless mode 都会影响渲染；baseline 与比较应在一致环境中生成。

这对 agent 友好，因为：

- 命令可脚本化；
- diff 有明确 pass/fail；
- 不需要先引入 SaaS；
- 可以与 interaction test 放在同一个浏览器会话里。

### 什么时候再加专用平台

- 大量页面/组件需要 PR review、审批和协作：考虑 Argos、Chromatic、Percy 等托管服务。
- 必须本地/self-hosted：评估 BackstopJS 或项目现有测试栈。
- 不要新采用 Lost Pixel：其 GitHub 仓库已于 **2026-04-22** archive，项目公告称产品 sunset、团队加入 Figma。

Pixel diff 也会撒谎：动画相位、时间、随机数据、字体加载、滚动位置不固定，都会制造噪声。必须先冻结或归一化动态因素。更重要的是，**静态像素 pass 不代表行为 pass**；v5 的 scroll-length、pointer-theater、scroll-states、reduced-motion 和 replica-only-motion gates 仍不可省略。

---

## 7. 对 `landing-page-replication-v5` 的实际建议

### 保留现有主干

v5 已经有一条比大多数 cloner README 更清楚的主线：

```text
Capture → Signal Sheet → Skeleton → Density → Micro-parity → Behavior → Polish
```

并且已有可执行 gate：

- IMR / density / type scale；
- scroll-length ratio；
- offline behavior comparison；
- pointer theater 与 scroll-state sampling；
- reduced motion；
- replica-only motion blocker；
- GAPS waiver。

这套主干不应被一个新出现的“one-command clone”替换。

### 最值得吸收的四项外部能力

| 优先级 | 外部启发 | 加到 v5 的位置 | 验收方式 |
|---|---|---|---|
| P1 | SHA-256 asset provenance + readonly evidence pack | Loop 0 Capture | manifest 可重算；offline 无远端主资产请求 |
| P1 | source/runtime motion parameter extraction | Loop 0–1 runtime capture | SIGNAL 中每个 P0 motion 标记 `SOURCE / RUNTIME / GUESS` |
| P2 | Wayback / dead-site recovery router | `capture-router.md` | 同一时间窗、缺口显式登记 |
| P2 | bounded repair + `UNRESOLVED` discipline | Loop 5–6 | 达到迭代上限后写 GAPS，不继续盲 patch |

### 暂时不要吸收

- 为了“multi-agent”而默认开 worktrees；
- 把输出栈锁死到 Next.js 16 + shadcn + Tailwind v4；
- 把原站 CSS/class 永久保留为产品代码；
- 仅凭 star 数或 README demo 宣布工具优胜；
- 再做一套与 v5 重复的 screenshot diff wrapper。

### 最快的真实 bake-off

选择三个机制不同、但范围受控的 section：

1. Linear-class：高密度 product theater；
2. Stripe-class：复杂 gradient / responsive nav；
3. WebGL/Lenis-class：scroll + pointer 驱动。

对同一份 frozen capture，分别运行 v5 与一个候选 skill。记录：

- 首次可运行产物耗时；
- 人工介入次数；
- target live requests 次数；
- desktop/mobile IMR 与 pixel diff；
- SLR；
- behavior blockers；
- 远端资产残留；
- 未声明猜测数；
- 产物能否在原项目栈内维护。

**Kill criterion：**如果候选没有减少人工介入或行为 blocker，只是生成更多文档、agent、worktree 和代码，就不集成。

---

## 8. 一条可以直接交给 agent 的工作流

```text
研究并重建这个 landing page，但不要从截图猜实现。

1. 先确认用途：internal study，还是会公开上线。
2. 先找源码：检查品牌官方仓库、作者仓库、可信重建和教程仓库；
   记录 repo、commit、license、live URL、可借机制与缺失项。
3. 从最接近任务机制的 2–4 个源码 specimen 读取相关 section、styles、
   motion config 和 assets；不要为了“参考”把整个 monorepo塞进 context。
4. 若公开上线，组合多个 reference，替换 logo、文案、客户列表、品牌图片、
   专有字体和 trade dress；代码许可与素材许可分别判断。
5. 只有源码缺失或需要核对当前版本时，才对 positive target 做证据化 capture：
   HTML、DOM、CSS/CSSOM、fonts、assets、network、runtime、
   0/25/50/75/100% scroll screenshots 与 interaction states。
6. 每个关键判断标注证据：SOURCE / RUNTIME / VISUAL / GUESS。
7. 写 SIGNAL / DESIGN contract；先声明 page argument、product theater、
   3 个 sharp edges、responsive behavior 与 P0 interaction contract。
8. 缺少现成实现时，再从 shadcn MCP / 21st.dev 查可编辑组件；
   组件必须适配现有 stack 和 tokens，不反向绑架设计。
9. 按现有项目栈实现，不为 clone 改框架。
10. 在固定浏览器环境做 screenshot diff，并运行 scroll-length、
    pointer/scroll states、reduced-motion 与 offline behavior gates。
11. 达不到的项目写入 GAPS，包含证据、影响、owner 和 pass criterion；
    不用“looks close”或“pixel-perfect”代替结果。
```

---

## 9. 最终使用顺序

1. **先选源码 specimen**：从第 1 节的 8 个项目中按机制取 2–4 个，不要全塞给 agent。
2. **再补当前事实**：目标未开源、源码过时或状态缺失时，用 v5 capture 和 forensic 工具补证据。
3. **然后实现**：保持现有 stack；组件 registry 只补缺失零件。
4. **最后证明**：Playwright screenshot assertions + v5 behavior gates；未解决项进 GAPS。

工具层的最小 shortlist：

- 重取证 / 整站恢复：[`boyang-hu/website-rebuild-skill`](https://github.com/boyang-hu/website-rebuild-skill)
- 重 motion forensic：[`voidmatcha/ui-clone-skills`](https://github.com/dididy/ui-skills)
- 只有截图时：[`abi/screenshot-to-code`](https://github.com/abi/screenshot-to-code)
- 找额外设计参考：[Mobbin MCP](https://mobbin.com/mcp) 或 [Refero MCP](https://refero.design/mcp)
- 找可编辑零件：[shadcn MCP](https://ui.shadcn.com/docs/mcp) + [21st.dev](https://21st.dev/)

执行和验收仍以本仓库的 **Landing Page Replication v5** 为主。

一句话版本：

> 先读好源码；没有源码再逆向；无论哪条路，最后都用视觉与行为证据收口。

---

## Sources and evidence notes

### Curated source gallery

- [Giats2498/giats-portfolio](https://github.com/Giats2498/giats-portfolio)、[live](https://giats.me/)、[Awwwards entry](https://www.awwwards.com/sites/https-giats-me) — 原作者声明、源码、外部奖项与生产站
- [supabase/supabase `apps/www`](https://github.com/supabase/supabase/tree/master/apps/www)、[live](https://supabase.com/) — 官方 website tree、开发说明与 Apache-2.0 根许可
- [dubinc/dub](https://github.com/dubinc/dub)、[live](https://dub.co/)、[license](https://github.com/dubinc/dub/blob/main/LICENSE.md) — 官方 monorepo、AGPL 与 enterprise-directory 例外
- [midday-ai/midday `apps/website`](https://github.com/midday-ai/midday/tree/main/apps/website)、[live](https://midday.ai/) — 官方 website tree 与 AGPL-3.0 根许可
- [yashxcode/linear-rebuilt](https://github.com/yashxcode/linear-rebuilt)、[live](https://linear-rebuilt.vercel.app/) — 完整 demo、源码树、历史 metadata；与 [frontendfyi/rebuilding-linear.app](https://github.com/frontendfyi/rebuilding-linear.app) 的结构与 assets 横向比对
- [Thakuma07/Truus.co-Awwward-Website](https://github.com/Thakuma07/Truus.co-Awwward-Website)、[live](https://truus-awwward-website.vercel.app/) — animation catalog、源码树与已声明的 video/showreel 缺口
- [ahmedragab15/spylt-gsap-website](https://github.com/ahmedragab15/spylt-gsap-website)、[live](https://spylt-gsap-website.vercel.app/) — Next.js / GSAP 源码与 scroll/video demo
- [HugoRCD/raycast-nuxt-ui-clone](https://github.com/HugoRCD/raycast-nuxt-ui-clone)、[live](https://raycast-nuxt-ui.hrcd.fr/) — Nuxt UI source、交互状态与 Apache-2.0 license

### Tooling and method sources

- [boyang-hu/website-rebuild-skill](https://github.com/boyang-hu/website-rebuild-skill) — README、Agent Skills 与验证自述
- [voidmatcha/ui-clone-skills](https://github.com/dididy/ui-skills) — README、license、pipeline 自述
- [aatmik-panse/clone-site-skill](https://github.com/aatmik-panse/clone-site-skill) — README、measurement/repair workflow 自述
- [iamphduc/claude-skill-web-clone](https://github.com/iamphduc/claude-skill-web-clone) — README、source-first router
- [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) — README、stack 与 multi-agent workflow
- [abi/screenshot-to-code](https://github.com/abi/screenshot-to-code) — README、支持输入/输出与本地依赖
- [Mobbin MCP](https://mobbin.com/mcp) 与 [Mobbin MCP docs](https://docs.mobbin.com/mcp/features) — 库规模、计划、工具列表
- [Refero MCP](https://refero.design/mcp) 与 [getting started](https://doc.refero.design/mcp/getting-started) — 库规模、订阅要求、tools/research layers
- [shadcn MCP](https://ui.shadcn.com/docs/mcp) — registry 能力与官方配置
- [21st.dev](https://21st.dev/) — catalog、源码交付形态与官方规模自述
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) — screenshot baseline/diff 与环境一致性警告
- [lost-pixel/lost-pixel](https://github.com/lost-pixel/lost-pixel) — archive 日期与 sunset 公告

### Evidence caveats

- 2026-09-11 对 8 个 gallery live URLs 做了可达性检查；对第三方 demo 还检查了 runtime page length、images、buttons、canvas / video presence。可达和非空不等于 fidelity 已证明。
- GitHub stars、screens 数量和“支持 N 个 agent”只能说明关注度或项目声明，不证明质量。
- 本文没有发现一个独立维护、覆盖 URL→capture→code→behavior 的统一 benchmark；因此没有给候选做伪精确总分。
- landing pages 会持续更新。任何 clone、token dump 或 DESIGN.md 都应记录 capture 日期；没有日期的“最佳实践”会悄悄变成考古。
- GitHub 可读、能 clone、代码有许可证，是三件不同的事；代码许可也不自动覆盖第三方 assets、fonts、brands 或 trade dress。参见本 skill 的 [`references/ip-and-fonts.md`](references/ip-and-fonts.md)。
