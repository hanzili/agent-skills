有没有人无聊，把类似 V0 或 Linear 等很有风格的产品，的Landing page 逆向出来，就是那种直接把源码放出来的，看一下，帮我找一下。

有的，确实有人专门把 Linear 这类高风格落地页给逆向/复刻出来，并直接把源码放 GitHub 上。v0 的落地页专门完整逆向的相对少一点（更多是复刻 v0 这个工具本身），但 Linear 相关的资源比较丰富。

### Linear 落地页复刻（源码直接放出来的）

比较推荐、明确写了是 rebuild / reverse-engineered 的：

1. **yashxcode/linear-rebuilt**  
   https://github.com/yashxcode/linear-rebuilt  
   - 明确写的是 *reverse-engineered rebuild of the Linear.app landing page*  
   - Next.js + TypeScript + TailwindCSS  
   - 强调复杂动画和交互组件  
   - 有 live demo

2. **frontendfyi/rebuilding-linear.app**  
   https://github.com/frontendfyi/rebuilding-linear.app  
   - 用 Next.js + Tailwind + Framer Motion 重建 Linear 首页  
   - 有配套视频教程（一步步拆解 header、hero 动画、footer 等）  
   - stars 比较多，质量较高

3. **rogue-kitten/linear-homepage**  
   https://github.com/rogue-kitten/linear-homepage  
   - Next.js 13 App Router + React Server Components 复刻  
   - 也有 live demo

4. **anoopraju31/linear-landing-page**  
   https://github.com/anoopraju31/linear-landing-page  
   - 另一个 Next.js + Tailwind 版本

另外还有纯 HTML/CSS 的简化版（比如 adithyakirn/linear-web-clone），以及 Figma 里有人做的桌面端还原，但源码层面还是上面几个 GitHub 仓库更直接。

### 其他相关

- 有人做了「网站逐行复刻」的 Agent Skill（boyang-hu/website-rebuild-skill），里面明确把 Linear 列为可做的目标之一（属于 RSC 类站点，用 flight 流做重构式逆向）。  
  https://github.com/boyang-hu/website-rebuild-skill

- v0 这边更多是有人逆向 v0 本身的运行时/浏览器端架构（比如 ManuelAngel99/reverse_engineering_v0），或者官方/社区做的 v0 风格 clone 工具，专门完整还原 v0 落地页源码的公开仓库相对少。

如果你主要想看 **Linear 那种暗色、极简、动画很讲究的落地页实现细节**，优先看前两个仓库就够了，直接 clone 下来对照原站看代码和动画实现会很有收获。需要我帮你再挖某个具体仓库的细节，或者找类似 Raycast / 其他高风格产品的复刻，也可以说。


*****


还有其他类似的吗？我指的是类似那些可以逆向工程 / 完整复刻出来，产品 Landing Page，

非常有风格，可作为行业最佳实践，基本上到了被人当最佳学习案例去模仿借鉴的程度。时间线越往后越好，越能沉淀出那种符合 AI 时代的、 Agent friendly 的资源越好，例如 Skill 啥的。

不仅仅是 linear，当然，我只是只想到这个例子而已，像 Cursor、 Stripe、 Notion、 Shopify、Vercel、Figma、Slack、Airtable、Clerk… 基本都算。


---

有的，而且比单纯“看起来像”的 clone 更有价值的资源正在往 **AI Agent 友好 / Skill 化** 方向沉淀。下面按两类整理：  

1. **高风格产品落地页的人工完整复刻**（可直接当学习案例）  
2. **真正适合 AI 时代的 Agent Skill / 自动化逆向工具**（时间越往后越好）

### 一、高风格产品落地页人工复刻（可学习的最佳实践）

**Linear 系列**（依然是最经典的教材）：
- [frontendfyi/rebuilding-linear.app](https://github.com/frontendfyi/rebuilding-linear.app)（313 stars）——Next.js + Tailwind + Framer Motion，配套视频拆解，质量最高
- [yashxcode/linear-rebuilt](https://github.com/yashxcode/linear-rebuilt)——明确写 “reverse-engineered rebuild”
- [thenameiswiiwin/linear-clone](https://github.com/thenameiswiiwin/linear-clone)（61 stars）
- [rogue-kitten/linear-homepage](https://github.com/rogue-kitten/linear-homepage)

**Cursor**：
- 目前公开的多为 **HTML + CSS 高保真静态复刻**（学习布局、暗色系、间距的好材料），例如：
  - [NausheenFaiyaz/Cursor](https://github.com/NausheenFaiyaz/Cursor)
  - [electrocoderaman/cursor-clone](https://github.com/electrocoderaman/cursor-clone)
  - [vinnymadaan/cursor-landing-page-clone](https://github.com/vinnymadaan/cursor-landing-page-clone)  
  完整带复杂动画/交互的 Next.js 版本相对少，更多人直接用 AI 现场生成。

**Stripe**：
- 完整落地页公开高质量复刻较少，更多是 **Navbar / 交互组件** 的精细复刻（例如 Stripe 导航栏的 Framer Motion 版本）。
- 全站级的 Stripe 风格学习更多来自官方设计系统和社区组件库，而不是完整源码 dump。

**Vercel**：
- 有人工 UI Clone（例如 rocketseat 的旧版首页 clone），但真正高质量的多是用 Claude Code / 截图驱动生成的。
- 官方也有一些示例落地页（如 spr-landing），可参考。

**Notion**：
- 完整产品 clone 很多（带编辑器、实时协作的），落地页单独复刻相对少，有一些 Next.js + Tailwind 版本。

**其他**：
- Raycast、Figma、Clerk、Shopify 等公开的“完整落地页源码 dump”普遍不如 Linear 多。很多人现在直接用 AI 工具对着原站截图/URL 生成，然后自己 refine。

整体趋势：**Linear 仍然是被模仿最多、公开源码最丰富的“行业最佳实践”**。Cursor / Vercel / Stripe 的视觉语言现在更多通过 AI 现场逆向，而不是等人工仓库。

### 二、真正 AI 时代 / Agent-friendly 的资源（重点推荐）

这些才是你说的“越往后越好、能沉淀成 Skill”的方向：

1. **boyang-hu/website-rebuild-skill**（目前最接近“完整逆向工程”的 Agent Skill）  
   https://github.com/boyang-hu/website-rebuild-skill  
   - 给 URL → 抓只读镜像 → 从压缩代码逐行还原 → 自动化验收（含逐像素比对）  
   - 支持 RSC / Next.js App Router（Linear 被明确列为可做目标）  
   - 已实测 Raycast、Lusion、EIGHT DESIGN、Linear 等  
   - 遵循 Agent Skills 开放规范，Claude Code / Codex 都能跑  
   - **这是目前最符合“AI 时代最佳实践”的资源**

2. **JCodesMore/ai-website-cloner-template**  
   https://github.com/JCodesMore/ai-website-cloner-template  
   - `/clone-website` 一条命令，把任意 URL 重建成 Next.js 16 + shadcn + Tailwind v4  
   - 支持 Claude Code、Cursor、Codex、Windsurf 等 10+ 种 Agent  
   - 设计 token 提取、并行 worktree、视觉 QA  
   - 更偏“快速可用的生产级 clone”，而不是逐行证据链

3. **其他相关 Skill / 工具方向**：
   - `agent-website-design-skills`（偏落地页设计系统 + 转化 + 响应式 QA）
   - 各种 “clone-website” skill 变体正在快速出现

### 总结建议

- **想深度学习实现细节、动画、布局哲学** → 优先看 Linear 的几个人工重建仓库（尤其是 frontendfyi 那个 + 配套视频）。
- **想符合 AI 时代、可复用、Agent 可调用** → 直接装 `website-rebuild-skill` 或 `ai-website-cloner-template`，对着 Linear / Cursor / Raycast / Vercel 等跑一遍，产出既可学习又能当自己的 Skill 基础。
- Cursor、Stripe、Notion、Figma 等目前公开的完整高保真落地页源码仓库质量参差，不如直接用上面两个 Skill 自己生成 + 对比原站更高效。

如果你想，我可以再帮你：
- 具体挑某个产品（比如 Cursor 或 Raycast）推荐最接近的仓库 + 使用 Skill 的实际命令流程
- 或者整理一份“目前最适合被 Agent 学习的落地页案例清单”
