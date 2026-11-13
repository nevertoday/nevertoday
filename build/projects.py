from dataclasses import dataclass

from palette import TRADITIONAL

PROFILE = {
    "name": "小小东",
    "name_en": "Xiaoxiaodong",
    "handle": "@nevertoday",
    "slogan_zh": "踩过的坑，写成 AI 能照着走的路。",
    "slogan_en": "Every pit I fell into, written up as a road your AI can walk.",
    "intro_zh": "独立开发者。写作、配色、排版、出国上网，这些事我都踩过坑。踩完就写下来，做成免费开源的工具，你的 AI 照着就能做好。",
    "intro_en": "Independent maker. Writing, color, layout, getting online abroad: I have tripped over all of it. "
                "Each time I write the fix down as a free, open-source tool your AI can follow.",
    "thanks_zh": "都是免费的。哪个帮到你了，点个 star，或者来 X 上打个招呼。",
    "thanks_en": "All free. If one helped, leave a star or come say hi on X.",
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
        lead_zh='出差到上网不方便的地方，常用的网站和 AI 照样能用。',
        body_zh='买台海外服务器，剩下的交给 Codex 远程配好。服务器你一次都不用登录，手机和电脑导入一个订阅就能上网。',
        lead_en='Travel somewhere the internet is locked down, and keep every site and AI tool you use.',
        body_en='Buy an overseas server and let Codex set it up remotely. You never log into it. Import one subscription on your phone and laptop and you are online.',
        cta_en='OPEN THE GUIDE', cta_zh='打开图文教程',
        cta_url='https://vps.xiaoxiaodong.ai/',
        scene="vps",
    ),
    Project(
        no="02", repo="zhongguo-traditional-colors", name="中华传统色", kind_en="COLOR",
        color_name="胭脂红", color_hex="#F03F24",
        slogan_zh="找到一个颜色，再让它真的用得上。",
        slogan_en="Find a Chinese color, then make it work.",
        stats=(("742", "colors"), ("8,904", "harmony sets"), ("10", "agent skills")),
        lead_zh='742 种中华传统色，不光好看，还拿来就能用。',
        body_zh='每个颜色都有高清色卡、8,904 组配色和真实场景预览，还能直接导出 shadcn 主题和终端配色。',
        lead_en='742 Chinese traditional colors, made to be used, not just admired.',
        body_en='Each one comes with a full-size card, 8,904 pairings and real-scene previews, plus shadcn themes and terminal palettes ready to export.',
        cta_en='PICK A COLOR', cta_zh='去挑颜色',
        cta_url='https://colors.xiaoxiaodong.ai/',
        scene="colors",
    ),
    Project(
        no="03", repo="350-layout-compositions", name="350 种排版", kind_en="LAYOUT",
        color_name="藤黄", color_hex="#FFD111",
        slogan_zh="350 种排版，按 8 类整理好。",
        slogan_en="350 layout references in 8 families.",
        stats=(("350", "layouts"), ("8", "categories"), ("33", "themes")),
        lead_zh='排版没灵感的时候，翻翻这 350 张。',
        body_zh='从三分法到网页 UI，分成 8 类 33 个主题。每张都是高清大图，能搜，能下载。',
        lead_en='Out of layout ideas? Flip through these 350.',
        body_en='From the rule of thirds to web UI, sorted into 8 families and 33 themes. Every one is a full-size image you can search and download.',
        cta_en='BROWSE ALL 350', cta_zh='翻图鉴',
        cta_url='https://github.com/nevertoday/350-layout-compositions/blob/main/docs/350/README.md',
        scene="layouts",
    ),
    Project(
        no="04", repo="xxd-pstack", name="pstack 新手教程", kind_en="GUIDE",
        color_name="铜绿", color_hex="#2BAE85",
        slogan_zh="AI 改完先自己试一遍，再来跟你说。",
        slogan_en="Your AI checks its own work before it says done.",
        stats=(("3", "lessons"), ("34", "skills"), ("10", "languages")),
        lead_zh='AI 说「修好了」，你一打开，还是坏的。',
        body_zh='pstack 让它改完先自己试一遍。这份教程用大白话讲，3 节课、20 分钟上手，只用记一个命令。',
        lead_en='Your AI says “fixed”. You open it. Still broken.',
        body_en='pstack makes it test its own work first. This guide explains it in plain words: three lessons, 20 minutes, one command to remember.',
        cta_en='START LESSON 1', cta_zh='开始学',
        cta_url='https://pstack.xiaoxiaodong.ai',
        scene="pstack",
    ),
    Project(
        no="05", repo="xxd-strip-ai-meta", name="xxd-strip-ai-meta", kind_en="METADATA",
        color_name="月白", color_hex="#EEF7F2",
        slogan_zh="批量清掉图片里的 AI 来源标记和元数据。",
        slogan_en="Strip AI provenance and metadata in bulk.",
        stats=(("7", "formats"), ("0", "pixels re-encoded"), ("0", "python deps")),
        lead_zh='图片里藏着「AI 生成」的标记，一条命令批量清掉。',
        body_zh='C2PA、EXIF、XMP 这些元数据都能清，像素一点不动。画面上看得见的水印它管不了，这点先说清楚。',
        lead_en='Your images carry hidden “made with AI” tags. One command clears them in bulk.',
        body_en='C2PA, EXIF, XMP and the rest go, and the pixels stay untouched. Visible watermarks are out of its reach, to be clear.',
        cta_en='HOW TO USE IT', cta_zh='看用法',
        cta_url='https://github.com/nevertoday/xxd-strip-ai-meta#readme',
        scene="strip",
    ),
    Project(
        no="06", repo="rime-color-scheme", name="Rime 品牌选中色", kind_en="INPUT",
        color_name="丁香紫", color_hex="#C8A2C8",
        slogan_zh="输入法的选中块，用品牌原色。",
        slogan_en="Brand colors for your Rime highlight.",
        stats=(("20", "schemes"), ("2", "modes each"), ("2", "platforms")),
        lead_zh='打字时那个选中块，换成你喜欢的品牌色。',
        body_zh='蒂芙尼蓝、爱马仕橙、克莱因蓝，20 套品牌原色，每套都有浅色和夜色。复制一段话给 AI，它就帮你装好。',
        lead_en='Give the highlight you type into a brand color you love.',
        body_en='Tiffany blue, Hermès orange, Klein blue: 20 schemes in their published colors, each in light and night. Paste one prompt to your AI and it installs them.',
        cta_en='SEE ALL 20', cta_zh='看全部 20 套',
        cta_url='https://github.com/nevertoday/rime-color-scheme#readme',
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
