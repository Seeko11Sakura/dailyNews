"""Source configuration for content sources across all user-facing domains.

Each source is defined with metadata needed by the RSS fetcher or web scraper.
Tier A = major, high-volume, reliable sources (prioritised in fetch).
Tier B = solid mid-tier sources.
Tier C = niche, hard-to-scrape, or supplementary sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SourceConfig:
    name: str
    url: str
    domain_id: str  # "technology" | "ai" | "society"
    tier: str  # "A" | "B" | "C"
    source_type: str  # "rss" | "web"
    rss_url: str | None = None
    active: bool = True
    css_selectors: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# A) Science & Technology  (20 sources)
# ---------------------------------------------------------------------------

TECHNOLOGY_SOURCES: list[SourceConfig] = [
    # -- Tier A --
    SourceConfig(
        name="IT之家",
        url="https://www.ithome.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://www.ithome.com/rss/",
    ),
    SourceConfig(
        name="少数派",
        url="https://sspai.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://sspai.com/feed",
    ),
    SourceConfig(
        name="爱范儿",
        url="https://www.ifanr.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://www.ifanr.com/feed",
    ),
    SourceConfig(
        name="36氪",
        url="https://36kr.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://36kr.com/feed",
    ),
    SourceConfig(
        name="虎嗅",
        url="https://www.huxiu.com/",
        domain_id="technology",
        tier="A",
        source_type="rss",
        rss_url="https://www.huxiu.com/rss/0.xml",
    ),
    # -- Tier B --
    SourceConfig(
        name="极客公园",
        url="https://www.geekpark.net/",
        domain_id="technology",
        tier="B",
        source_type="rss",
        rss_url="https://www.geekpark.net/rss",
    ),
    SourceConfig(
        name="雷峰网",
        url="https://www.leiphone.com/",
        domain_id="technology",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": "div.news-list-item a, .article-item a",
            "title": "h3, .title",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="钛媒体",
        url="https://www.tmtpost.com/",
        domain_id="technology",
        tier="B",
        source_type="rss",
        rss_url="https://www.tmtpost.com/rss.xml",
    ),
    SourceConfig(
        name="品玩 PingWest",
        url="https://www.pingwest.com/",
        domain_id="technology",
        tier="B",
        source_type="rss",
        rss_url="https://www.pingwest.com/feed",
    ),
    SourceConfig(
        name="TechWeb",
        url="https://www.techweb.com.cn/",
        domain_id="technology",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    # -- Tier C --
    SourceConfig(
        name="DoNews",
        url="https://www.donews.com/",
        domain_id="technology",
        tier="C",
        source_type="rss",
        rss_url="https://www.donews.com/feed",
    ),
    SourceConfig(
        name="站长之家",
        url="https://www.chinaz.com/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="OSCHINA 开源中国",
        url="https://www.oschina.net/",
        domain_id="technology",
        tier="C",
        source_type="rss",
        rss_url="https://www.oschina.net/news/rss",
    ),
    SourceConfig(
        name="InfoQ 中文",
        url="https://www.infoq.cn/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".article-item a, .news-item a",
            "title": "h4, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="掘金",
        url="https://juejin.cn/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".article-item-link, .content-main a",
            "title": ".title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="SegmentFault 思否",
        url="https://segmentfault.com/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="博客园",
        url="https://www.cnblogs.com/",
        domain_id="technology",
        tier="C",
        source_type="rss",
        rss_url="https://www.cnblogs.com/rss",
        active=False,
    ),
    SourceConfig(
        name="51CTO",
        url="https://www.51cto.com/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".article-item a, .news-list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="199IT",
        url="https://www.199it.com/",
        domain_id="technology",
        tier="C",
        source_type="rss",
        rss_url="https://www.199it.com/feed",
    ),
    SourceConfig(
        name="FreeBuf",
        url="https://www.freebuf.com/",
        domain_id="technology",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

# ---------------------------------------------------------------------------
# B) AI  (20 sources)
# ---------------------------------------------------------------------------

AI_SOURCES: list[SourceConfig] = [
    # -- Tier A --
    SourceConfig(
        name="机器之心",
        url="https://www.jiqizhixin.com/",
        domain_id="ai",
        tier="A",
        source_type="rss",
        rss_url="https://www.jiqizhixin.com/rss",
    ),
    SourceConfig(
        name="量子位",
        url="https://www.qbitai.com/",
        domain_id="ai",
        tier="A",
        source_type="rss",
        rss_url="https://www.qbitai.com/feed",
    ),
    # -- Tier B --
    SourceConfig(
        name="雷峰网·AI科技评论",
        url="https://www.leiphone.com/category/ai",
        domain_id="ai",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": "div.news-list-item a, .article-item a",
            "title": "h3, .title",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="PaperWeekly",
        url="https://www.paperweekly.site/",
        domain_id="ai",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".paper-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="Datawhale",
        url="https://www.datawhale.cn/",
        domain_id="ai",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-item a, .post-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    # -- Tier C --
    SourceConfig(
        name="OpenI 启智社区",
        url="https://www.openi.org.cn/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="魔搭 ModelScope",
        url="https://modelscope.cn/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .blog-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="百度 AI",
        url="https://ai.baidu.com/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="阿里云",
        url="https://www.aliyun.com/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="阿里达摩院",
        url="https://damo.alibaba.com/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="腾讯 AI Lab",
        url="https://ai.tencent.com/ailab/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="华为诺亚方舟实验室",
        url="https://www.noahlab.com.hk/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .publication-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="飞桨 PaddlePaddle",
        url="https://www.paddlepaddle.org.cn/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="商汤",
        url="https://www.sensetime.com/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="科大讯飞开放平台",
        url="https://www.xfyun.cn/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-item a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="36氪（AI补位）",
        url="https://36kr.com/",
        domain_id="ai",
        tier="C",
        source_type="rss",
        rss_url="https://36kr.com/feed",
    ),
    SourceConfig(
        name="GitHub Trending",
        url="https://github.com/trending",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": "article.Box-row",
            "title": "h2 a",
            "link": "h2 a[href]",
        },
    ),
    SourceConfig(
        name="arXiv",
        url="https://arxiv.org/",
        domain_id="ai",
        tier="C",
        source_type="rss",
        rss_url="https://rss.arxiv.org/rss/cs.AI",
    ),
    SourceConfig(
        name="InfoQ（AI补位）",
        url="https://www.infoq.cn/",
        domain_id="ai",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".article-item a, .news-item a",
            "title": "h4, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="OSCHINA（AI补位）",
        url="https://www.oschina.net/",
        domain_id="ai",
        tier="C",
        source_type="rss",
        rss_url="https://www.oschina.net/news/rss",
    ),
]

# ---------------------------------------------------------------------------
# C) Society & Current Affairs  (20 sources)
# ---------------------------------------------------------------------------

SOCIETY_SOURCES: list[SourceConfig] = [
    # -- Tier A --
    SourceConfig(
        name="新华网",
        url="https://www.xinhuanet.com/",
        domain_id="society",
        tier="A",
        source_type="rss",
        rss_url="http://www.xinhuanet.com/politics/xhll.xml",
    ),
    SourceConfig(
        name="人民网",
        url="http://www.people.com.cn/",
        domain_id="society",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": ".news_list a, .ej_list_box a",
            "title": "a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="央视新闻",
        url="https://news.cctv.com/",
        domain_id="society",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="中国新闻网",
        url="https://www.chinanews.com.cn/",
        domain_id="society",
        tier="A",
        source_type="rss",
        rss_url="https://www.chinanews.com.cn/rss/scroll-news.xml",
    ),
    SourceConfig(
        name="澎湃新闻",
        url="https://www.thepaper.cn/",
        domain_id="society",
        tier="A",
        source_type="rss",
        rss_url="https://www.thepaper.cn/rss_newsDetail_wap.jsp",
    ),
    # -- Tier B --
    SourceConfig(
        name="央广网",
        url="https://www.cnr.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news_list a, .list_item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="光明网",
        url="https://www.gmw.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="经济日报",
        url="http://www.ce.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news_list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="中国政府网",
        url="https://www.gov.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="中国互联网联合辟谣平台",
        url="https://www.piyao.org.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="新京报",
        url="https://www.bjnews.com.cn/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="界面新闻",
        url="https://www.jiemian.com/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="南方周末",
        url="https://www.infzm.com/",
        domain_id="society",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .news-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    # -- Tier C --
    SourceConfig(
        name="南方都市报",
        url="https://www.oeeee.com/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="第一财经",
        url="https://www.yicai.com/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="财新",
        url="https://www.caixin.com/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="中国气象局",
        url="https://www.cma.gov.cn/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="应急管理部",
        url="https://www.mem.gov.cn/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="国家卫健委",
        url="http://www.nhc.gov.cn/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="观察者网",
        url="https://www.guancha.cn/",
        domain_id="society",
        tier="C",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

# ---------------------------------------------------------------------------
# D) Extended user-interest domains
# ---------------------------------------------------------------------------

GADGETS_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="中关村在线",
        url="https://news.zol.com.cn/",
        domain_id="gadgets",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": "a[href*='news.zol.com.cn/']",
            "title": "a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="什么值得买",
        url="https://www.smzdm.com/",
        domain_id="gadgets",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".feed-row-wide a, .article-list a, .list a",
            "title": "h5, h3, .title, a",
            "link": "a[href]",
        },
    ),
]

BUSINESS_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="36氪（商业）",
        url="https://36kr.com/",
        domain_id="business",
        tier="A",
        source_type="rss",
        rss_url="https://36kr.com/feed",
    ),
    SourceConfig(
        name="虎嗅（商业）",
        url="https://www.huxiu.com/",
        domain_id="business",
        tier="A",
        source_type="rss",
        rss_url="https://www.huxiu.com/rss/0.xml",
    ),
]

FINANCE_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="第一财经（财经）",
        url="https://www.yicai.com/",
        domain_id="finance",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-item a, .m-list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="财新（财经）",
        url="https://www.caixin.com/",
        domain_id="finance",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

CAREER_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="人人都是产品经理",
        url="https://www.woshipm.com/",
        domain_id="career",
        tier="A",
        source_type="rss",
        rss_url="https://www.woshipm.com/feed",
    ),
    SourceConfig(
        name="PMCAFF",
        url="https://www.pmcaff.com/",
        domain_id="career",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-item a, .post-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

EDUCATION_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="中国教育新闻网",
        url="http://www.jyb.cn/",
        domain_id="education",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .list a, .item a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="芥末堆",
        url="https://www.jiemodui.com/",
        domain_id="education",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .news-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

GAMES_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="机核",
        url="https://www.gcores.com/articles",
        domain_id="games",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": "a[href*='/articles/']",
            "title": "a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="游戏葡萄",
        url="https://youxiputao.com/",
        domain_id="games",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .post-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

MEDIA_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="1905电影网",
        url="https://www.1905.com/news/",
        domain_id="media",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": "a[href*='/news/202']",
            "title": "a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="娱乐资本论",
        url="https://www.yulezibenlun.com/",
        domain_id="media",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .post-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

HEALTH_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="丁香园",
        url="https://www.dxy.cn/",
        domain_id="health",
        tier="A",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .news-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="39健康网",
        url="https://www.39.net/",
        domain_id="health",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".news-list a, .article-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

LIFESTYLE_SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="下厨房",
        url="https://www.xiachufang.com/explore/",
        domain_id="lifestyle",
        tier="A",
        source_type="web",
        active=False,
        css_selectors={
            "article_list": "a[href*='/recipe/']",
            "title": "a",
            "link": "a[href]",
        },
    ),
    SourceConfig(
        name="一条",
        url="https://www.yitiao.tv/",
        domain_id="lifestyle",
        tier="B",
        source_type="web",
        css_selectors={
            "article_list": ".article-list a, .post-list a, .list a",
            "title": "h3, .title, a",
            "link": "a[href]",
        },
    ),
]

# ---------------------------------------------------------------------------
# Combined registry
# ---------------------------------------------------------------------------

FIRST_BATCH_CRAWLER_SELECTORS: dict[str, dict[str, str]] = {
    "IT之家": {
        "article_list": "a[href*='/0/'], a[href*='ithome.com/html/']",
        "title": "a",
        "link": "a[href]",
    },
    "36氪": {
        "article_list": "a[href*='/p/'], a[href*='36kr.com/newsflashes/']",
        "title": "a",
        "link": "a[href]",
    },
    "机器之心": {
        "article_list": "a[href*='/articles/']",
        "title": "a",
        "link": "a[href]",
    },
    "量子位": {
        "article_list": "a[href*='/archives/']",
        "title": "a",
        "link": "a[href]",
    },
    "36氪（商业）": {
        "article_list": "a[href*='/p/'], a[href*='36kr.com/newsflashes/']",
        "title": "a",
        "link": "a[href]",
    },
}


def _crawler_only_source(source: SourceConfig) -> SourceConfig:
    """把第一批 RSS 来源转成网页爬虫来源，其余 RSS 来源暂时停用。"""
    selectors = FIRST_BATCH_CRAWLER_SELECTORS.get(source.name)
    if selectors:
        return SourceConfig(
            name=source.name,
            url=source.url,
            domain_id=source.domain_id,
            tier=source.tier,
            source_type="web",
            active=True,
            css_selectors=selectors,
        )
    if source.source_type == "rss":
        return SourceConfig(
            name=source.name,
            url=source.url,
            domain_id=source.domain_id,
            tier=source.tier,
            source_type=source.source_type,
            rss_url=source.rss_url,
            active=False,
            css_selectors=source.css_selectors,
        )
    return source


ALL_SOURCES: list[SourceConfig] = [
    _crawler_only_source(source)
    for source in (
    TECHNOLOGY_SOURCES
    + AI_SOURCES
    + SOCIETY_SOURCES
    + GADGETS_SOURCES
    + BUSINESS_SOURCES
    + FINANCE_SOURCES
    + CAREER_SOURCES
    + EDUCATION_SOURCES
    + GAMES_SOURCES
    + MEDIA_SOURCES
    + HEALTH_SOURCES
    + LIFESTYLE_SOURCES
)
]

# Lookup helpers
SOURCES_BY_NAME: dict[str, SourceConfig] = {s.name: s for s in ALL_SOURCES}
SOURCES_BY_DOMAIN: dict[str, list[SourceConfig]] = {}
for _src in ALL_SOURCES:
    SOURCES_BY_DOMAIN.setdefault(_src.domain_id, []).append(_src)

RSS_SOURCES: list[SourceConfig] = [s for s in ALL_SOURCES if s.source_type == "rss"]
WEB_SOURCES: list[SourceConfig] = [s for s in ALL_SOURCES if s.source_type == "web"]


def get_sources_by_tier(tier: str) -> list[SourceConfig]:
    """Return all active sources of a given tier, sorted by domain."""
    return [s for s in ALL_SOURCES if s.tier == tier and s.active]


def get_active_sources() -> list[SourceConfig]:
    """Return all active sources, sorted A > B > C tier priority."""
    tier_order = {"A": 0, "B": 1, "C": 2}
    return sorted(
        [s for s in ALL_SOURCES if s.active],
        key=lambda s: (tier_order.get(s.tier, 9), s.domain_id, s.name),
    )
