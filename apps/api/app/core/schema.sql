-- dailyNews Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表 (MVP 阶段可选，先支持游客模式)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id TEXT UNIQUE,  -- 游客模式用设备ID
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 领域配置表
CREATE TABLE IF NOT EXISTS user_domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    domain_id TEXT NOT NULL,  -- technology, ai, business, etc.
    is_primary BOOLEAN DEFAULT true,  -- 主选 vs 探索关注
    followed_at TIMESTAMPTZ DEFAULT NOW(),
    trial_expires_at TIMESTAMPTZ,  -- 7天试用期
    UNIQUE(user_id, domain_id)
);

-- 文章表
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,  -- ≤100字结论卡
    content TEXT,  -- 全文内容
    source_url TEXT NOT NULL,
    source_name TEXT,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    fetch_status TEXT DEFAULT 'pending',  -- pending, success, failed
    url_hash TEXT UNIQUE,  -- URL去重用
    title_similarity_hash TEXT  -- 标题近似折叠用
);

-- 用户已读记录
CREATE TABLE IF NOT EXISTS read_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    read_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

-- 用户收藏
CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

-- 探索记录（7天去重用）
CREATE TABLE IF NOT EXISTS explore_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    domain_id TEXT NOT NULL,
    shown_at TIMESTAMPTZ DEFAULT NOW(),
    action TEXT DEFAULT 'shown',  -- shown, followed, dismissed
    UNIQUE(user_id, domain_id, shown_at::date)
);

-- 不感兴趣记录（降权用）
CREATE TABLE IF NOT EXISTS dismissals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    domain_id TEXT NOT NULL,
    dismissed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, domain_id)
);

-- 内容来源配置
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    tier TEXT DEFAULT 'B',  -- A, B, C
    source_type TEXT DEFAULT 'web',  -- rss, web
    rss_url TEXT,
    is_active BOOLEAN DEFAULT true,
    last_fetched_at TIMESTAMPTZ,
    fetch_interval_minutes INTEGER DEFAULT 60
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_articles_domain ON articles(domain_id);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_url_hash ON articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_read_records_user ON read_records(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_explore_records_user ON explore_records(user_id, shown_at);
CREATE INDEX IF NOT EXISTS idx_sources_domain ON sources(domain_id);
