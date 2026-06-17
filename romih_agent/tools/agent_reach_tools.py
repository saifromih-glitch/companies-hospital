"""
Romih Agent — Agent Reach Tools
================================
Web browsing: YouTube, GitHub, RSS, V2EX, Web pages
Local only — requires agent-reach CLI on the machine
"""
import subprocess, os, sys, json
from dataclasses import dataclass

@dataclass
class WebReader:
    """Read any webpage using Jina Reader"""
    name = "web_read"
    description = "Read and extract content from any webpage URL"
    category = "web"
    risk = "low"
    
    def execute(self, url: str = "") -> str:
        try:
            r = subprocess.run(
                ["curl", "-s", f"https://r.jina.ai/{url}"],
                capture_output=True, text=True, timeout=30,
                shell=True
            )
            return r.stdout[:3000] if r.returncode == 0 else f"Error reading page"
        except Exception as e:
            return f"Web read error: {e}"

@dataclass
class YouTubeReader:
    """Read YouTube video subtitles"""
    name = "youtube_read"
    description = "Extract subtitles/transcript from a YouTube video"
    category = "web"
    risk = "low"
    
    def execute(self, url: str = "") -> str:
        try:
            r = subprocess.run(
                f'yt-dlp --write-auto-subs --sub-lang en,ar --skip-download --print-to-stdout "{url}"',
                capture_output=True, text=True, timeout=60,
                shell=True
            )
            return r.stdout[:3000] if r.returncode == 0 else f"Error: {r.stderr[:200]}"
        except Exception as e:
            return f"YouTube error: {e}"

@dataclass
class GitHubReader:
    """Read GitHub repositories"""
    name = "github_read"
    description = "Read a GitHub repository: view info, readmes, issues"
    category = "web"
    risk = "low"
    
    def execute(self, repo: str = "", action: str = "view") -> str:
        """action: view (repo info), readme, issues"""
        try:
            if action == "view":
                r = subprocess.run(["gh", "repo", "view", repo], capture_output=True, text=True, timeout=30, shell=True)
            elif action == "issues":
                r = subprocess.run(["gh", "issue", "list", "--repo", repo, "--limit", "5"], capture_output=True, text=True, timeout=30, shell=True)
            else:
                r = subprocess.run(["gh", "repo", "view", repo, "--web"], capture_output=True, text=True, shell=True)
            return r.stdout[:3000] if r.returncode == 0 else f"Error: {r.stderr[:200]}"
        except Exception as e:
            return f"GitHub error: {e}"

@dataclass
class V2EXReader:
    """Read V2EX forums"""
    name = "v2ex_read"
    description = "Read V2EX tech forum: hot topics, posts, comments"
    category = "web"
    risk = "low"
    
    def execute(self, endpoint: str = "topics/hot.json") -> str:
        try:
            r = subprocess.run(
                f'curl -s "https://www.v2ex.com/api/{endpoint}"',
                capture_output=True, text=True, timeout=15,
                shell=True
            )
            return r.stdout[:3000] if r.returncode == 0 else "Error reading V2EX"
        except Exception as e:
            return f"V2EX error: {e}"


@dataclass
class TwitterReader:
    """Search and read Twitter/X posts"""
    name = "twitter_search"
    description = "Search Twitter/X for posts and read tweets"
    category = "web"
    risk = "low"
    
    def execute(self, query: str = "", action: str = "search") -> str:
        try:
            if action == "search" and query:
                r = subprocess.run(
                    f'python -m agent_reach twitter search "{query}"',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            elif action == "read" and query:
                r = subprocess.run(
                    f'python -m agent_reach twitter read "{query}"',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            else:
                return "Usage: twitter_search(query='keyword')"
            return (r.stdout or r.stderr or "No results")[:3000]
        except Exception as e:
            return f"Twitter search error: {e}"

@dataclass
class RedditReader:
    """Search and read Reddit posts"""
    name = "reddit_search"
    description = "Search Reddit for posts and read threads/comments"
    category = "web"
    risk = "low"
    
    def execute(self, query: str = "", subreddit: str = "", action: str = "search") -> str:
        try:
            if action == "search" and query:
                r = subprocess.run(
                    f'python -m agent_reach reddit search "{query}"',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            elif action == "hot" and subreddit:
                r = subprocess.run(
                    f'python -m agent_reach reddit hot -s {subreddit}',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            elif action == "read" and query:
                r = subprocess.run(
                    f'python -m agent_reach reddit read "{query}"',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            else:
                return "Usage: reddit_search(query) or reddit_search(subreddit, action=hot)"
            return (r.stdout or r.stderr or "No results")[:3000]
        except Exception as e:
            return f"Reddit search error: {e}"

@dataclass
class RSSReader:
    """Read RSS/Atom feeds"""
    name = "rss_read"
    description = "Read RSS/Atom feeds from any URL"
    category = "web"
    risk = "low"
    
    def execute(self, url: str = "", action: str = "read") -> str:
        try:
            if action == "read" and url:
                r = subprocess.run(
                    f'python -m agent_reach rss read "{url}"',
                    capture_output=True, text=True, timeout=30,
                    shell=True
                )
            else:
                return "Usage: rss_read(url='https://example.com/feed.xml')"
            return (r.stdout or r.stderr or "No RSS results")[:3000]
        except Exception as e:
            return f"RSS error: {e}"


# Register all tools
AGENT_REACH_TOOLS = [WebReader, YouTubeReader, GitHubReader, V2EXReader, TwitterReader, RedditReader, RSSReader]

def register(registry):
    """Register Agent Reach tools in the tool registry"""
    for tool_class in AGENT_REACH_TOOLS:
        t = tool_class()
        from tools.registry import Tool, RiskLevel, ToolParam
        tool = Tool(
            name=t.name,
            description=t.description,
            category=t.category,
            risk=RiskLevel.LOW,
            params=[ToolParam("url", "str", "URL or query string")],
            execute=t.execute,
            requires_approval=False
        )
        registry.register(tool)
    print(f"Agent Reach: {len(AGENT_REACH_TOOLS)} tools registered")
