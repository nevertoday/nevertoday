from dataclasses import dataclass

from palette import TRADITIONAL

PROFILE = {
    "name": "小小东",
    "name_en": "Xiaoxiaodong",
    "handle": "@nevertoday",
    "slogan_zh": "把创作经验，做成 AI 能执行的开源工具。",
    "slogan_en": "Turning creative know-how into open-source tools an AI can run.",
    "intro_zh": "独立开发者。把写作、视觉、配色、排版和出门上网这些事里攒下的经验，做成免费开源、AI 照着就能做的工具。",
    "intro_en": "Independent maker. I turn what I have learned about writing, visuals, color, layout and staying online abroad into free, open-source tools an AI can follow.",
    "thanks_zh": "如果这些项目帮到了你，点一颗 star 就是最好的鼓励。",
    "thanks_en": "If any of these help you, a star is the best encouragement. Thanks for stopping by.",
    "github": "https://github.com/nevertoday",
    "site": "https://xiaoxiaodong.ai",
    "site_label": "xiaoxiaodong.ai",
    "x": "https://x.com/xiaoxiaodong01",
    "x_handle": "@xiaoxiaodong01",
    "wechat": "newbe2012",
}


@dataclass(frozen=True)
class Project:
    no: str
    repo: str
    name: str
    kind_en: str
    color_name: str
    color_hex: str
    slogan_zh: str
    slogan_en: str
    stats: tuple
    lead_zh: str
    body_zh: str
    lead_en: str
    body_en: str
    cta_en: str
    cta_zh: str
    cta_url: str
    scene: str

    def __post_init__(self):
        assert TRADITIONAL.get(self.color_name) == self.color_hex, (
            f"{self.color_name} {self.color_hex} is not in data/colors.txt"
        )
        assert len(self.stats) == 3, f"{self.repo} needs three stats"

    @property
    def url(self):
        return f"https://github.com/nevertoday/{self.repo}"


PROJECTS = [
    Project(
        no="01", repo="xiaoxiaodong-vps", name="小小东 VPS", kind_en="NETWORK",
        color_name="靛青", color_hex="#1661AB",
        slogan_zh="出差在外，常用网站和 AI 照常用。",
        slogan_en="Your own line abroad, set up by Codex.",
        stats=(("4", "steps"), ("2", "nodes"), ("0", "server logins")),
        lead_zh="出差到上网不方便的国家，常用网站和 AI 工具也能照常用。",
        body_zh="在自己电脑上装好 Codex，买一台海外服务器，让 Codex 按这套方案远程配好，手机和电脑导入订阅就能用。"
                "服务器上什么都不用装，也不用登录它。主、备两个节点自动切换，证书、规则和 CLIProxyAPI 自动更新，配置每天备份。",
        lead_en="Travel somewhere the internet is restricted and keep using the sites and AI tools you rely on.",
        body_en="Install Codex on your computer, buy an overseas server, and let Codex set it up remotely from this plan. "
                "Import one subscription on your phone and computer and you are online. Nothing to install or log into on the server. "
                "Two nodes fail over to each other, and certificates, rules and CLIProxyAPI update themselves.",
        cta_en="Open the guide", cta_zh="图文教程", cta_url="https://vps.xiaoxiaodong.ai/",
        scene="vps",
    ),
    Project(
        no="02", repo="zhongguo-traditional-colors", name="中华传统色", kind_en="COLOR",
        color_name="胭脂红", color_hex="#F03F24",
        slogan_zh="找到一个颜色，再让它真的用得上。",
        slogan_en="Find a Chinese color, then make it work.",
        stats=(("742", "colors"), ("8,904", "harmony sets"), ("10", "agent skills")),
        lead_zh="742 种中华传统色，从找到颜色，到搭配、试用、落地。",
        body_zh="每个颜色一张高清色卡，附 8,904 组配色关系、真实场景预览、shadcn 主题和终端配色。"
                "另有 10 个 Agent Skills，把配色流程带进 Claude Code。",
        lead_en="742 Chinese traditional colors, from finding one to pairing, testing and shipping it.",
        body_en="A high-resolution card for every color, 8,904 harmony sets, real-scene previews, shadcn themes and terminal palettes. "
                "Ten Agent Skills bring the same workflow into Claude Code.",
        cta_en="Explore the colors", cta_zh="看色卡", cta_url="https://colors.xiaoxiaodong.ai/",
        scene="colors",
    ),
    Project(
        no="03", repo="350-layout-compositions", name="350 种排版", kind_en="LAYOUT",
        color_name="藤黄", color_hex="#FFD111",
        slogan_zh="350 种排版，按 8 类整理好。",
        slogan_en="350 layout references in 8 families.",
        stats=(("350", "layouts"), ("8", "categories"), ("33", "themes")),
        lead_zh="从经典构图到网页 UI，350 种排版分好类，能浏览、能搜索、能下载。",
        body_zh="覆盖构图逻辑、视觉原则、出版广告、字体网格、网页 UI、影视画面、中国传统构图和演示文稿，"
                "共 8 个一级分类、33 个二级主题。每张都有 1086 × 1448 高清图，附 CSV 和 JSON 目录。",
        lead_en="350 layout compositions, from classic composition rules to web UI, ready to browse, search and download.",
        body_en="Eight categories and 33 themes cover composition logic, visual principles, editorial and advertising, "
                "type and grids, web UI, film frames, Chinese composition and presentations. "
                "Every image comes at 1086 × 1448, with a CSV and JSON catalog.",
        cta_en="Browse the catalog", cta_zh="看分类图鉴", cta_url="https://github.com/nevertoday/350-layout-compositions",
        scene="layouts",
    ),
    Project(
        no="04", repo="xxd-pstack", name="pstack 新手教程", kind_en="GUIDE",
        color_name="铜绿", color_hex="#2BAE85",
        slogan_zh="AI 改完先自己试一遍，再来跟你说。",
        slogan_en="Your AI checks its own work before it says done.",
        stats=(("3", "lessons"), ("34", "skills"), ("10", "languages")),
        lead_zh="AI 说「修好了」，你一打开，还是坏的。pstack 让它改完先自己试一遍。",
        body_zh="这份教程用大白话把 pstack 讲清楚，不会写代码也能学会。新手入门 3 课、20 分钟上手，平时只记一个命令 /poteto-mode。"
                "34 个技能都能读原文，每个还挑了几句拆开讲写法。首页和入门课有 10 种语言。",
        lead_en="Your AI says “fixed” and it is still broken. pstack makes it try its own work first.",
        body_en="A plain-language guide to pstack for Claude Code, Cursor and Codex, no coding background needed. "
                "Three beginner lessons get you going in 20 minutes with one command, /poteto-mode. "
                "All 34 skills can be read in full, each with a few key lines explained, and the start pages come in 10 languages.",
        cta_en="Start the guide", cta_zh="开始学", cta_url="https://pstack.xiaoxiaodong.ai",
        scene="pstack",
    ),
    Project(
        no="05", repo="xxd-strip-ai-meta", name="xxd-strip-ai-meta", kind_en="METADATA",
        color_name="月白", color_hex="#EEF7F2",
        slogan_zh="批量清掉图片里的 AI 来源标记和元数据。",
        slogan_en="Strip AI provenance and metadata in bulk.",
        stats=(("7", "formats"), ("0", "pixels re-encoded"), ("0", "python deps")),
        lead_zh="批量清除图片中的 AI 来源标记和元数据，命令行和 Agent Skill 都能用。",
        body_zh="用 ExifTool 清理 C2PA / Content Credentials、OpenAI gpt-image 来源信息，以及 EXIF、XMP、IPTC、注释等元数据。"
                "默认保留 ICC 色彩配置和修改时间，不重编码像素。它只清元数据，去不掉画面里看得见的水印，也不保证清除像素级隐形水印。",
        lead_en="Batch-remove AI provenance marks and metadata from images, as a CLI or an Agent Skill.",
        body_en="ExifTool clears C2PA / Content Credentials, OpenAI gpt-image provenance, EXIF, XMP, IPTC and comments. "
                "ICC profiles and file times stay, and pixels are never re-encoded. "
                "It cleans metadata only. It cannot remove visible watermarks and does not promise to remove invisible pixel-level ones.",
        cta_en="How to use it", cta_zh="看用法", cta_url="https://github.com/nevertoday/xxd-strip-ai-meta",
        scene="strip",
    ),
    Project(
        no="06", repo="rime-color-scheme", name="Rime 品牌选中色", kind_en="INPUT",
        color_name="丁香紫", color_hex="#C8A2C8",
        slogan_zh="输入法的选中块，用品牌原色。",
        slogan_en="Brand colors for your Rime highlight.",
        stats=(("20", "schemes"), ("2", "modes each"), ("2", "platforms")),
        lead_zh="给鼠须管和小狼毫用的 20 套选中色，每套浅色加夜色。",
        body_zh="选中块不调色，用公开记载的品牌 HEX，比如蒂芙尼蓝 #81D8D0、爱马仕橙 #F37021、克莱因蓝 #002FA7。"
                "浅色是纸，夜色是接近黑的底。复制一段 AI 指令就能装，也可以按步骤手动配置。",
        lead_en="20 highlight color schemes for Squirrel and Weasel, each with a light and a night version.",
        body_en="The highlight uses the published brand HEX as is, such as Tiffany #81D8D0, Hermès orange #F37021 and Klein blue #002FA7. "
                "Light themes sit on paper, night themes on near-black. Paste one AI prompt to install, or follow the manual steps.",
        cta_en="See all 20", cta_zh="看全部配色", cta_url="https://github.com/nevertoday/rime-color-scheme",
        scene="rime",
    ),
]

MORE = [
    ("XXD Panel 视觉系列", "https://github.com/nevertoday?tab=repositories&q=xxd-panel",
     "从照片出发的 AI 视觉 Skills", "photo-led visual Skills"),
    ("ghostty-tint", "https://github.com/nevertoday/ghostty-tint",
     "每个 Ghostty 面板一种安静的颜色", "a quiet color for every Ghostty pane"),
    ("mihomo-forge", "https://github.com/nevertoday/mihomo-forge",
     "在浏览器里合并多份 Mihomo 配置", "merge Mihomo configs in the browser"),
    ("xxd-chrome-publish", "https://github.com/nevertoday/xxd-chrome-publish",
     "一条命令发布 Chrome 插件更新", "ship Chrome extension updates in one command"),
    ("dsh-theme-plugin", "https://github.com/nevertoday/dsh-theme-plugin",
     "DeepSeek Harness 中华传统色主题", "Chinese traditional colors for DeepSeek Harness"),
    ("xxd-notify", "https://github.com/nevertoday/xxd-notify",
     "用 Bark 把任务提醒推到手机", "task alerts to your phone through Bark"),
    ("xiaoxiaodong", "https://github.com/nevertoday/xiaoxiaodong",
     "小小东项目入口", "where all of it starts"),
]
