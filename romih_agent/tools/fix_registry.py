"""Write _register_skills method to registry.py cleanly"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

SKILLS_CODE = '''
    def _register_skills(self):
        """Register AutoClaw/OpenClaw skills as tools"""
        from tools.skills_adapter import ALL_SKILLS

        skills = [
            # (skill_name, tool_name, description, category, risk, params_list, needs_approval)
            ("web_search", "web_search", "Web search (16 engines)", "search", "LOW",
                [("query", "str", "Search query")], False),
            ("deep_research", "deep_research", "Academic deep research + APA", "search", "LOW",
                [("query", "str", "Research topic")], False),
            ("fetch_page", "fetch_page", "Read full webpage content", "search", "LOW",
                [("url", "str", "Page URL")], False),
            ("create_pdf", "create_pdf", "Create professional PDF", "document", "MEDIUM",
                [("title", "str", "Document title"), ("content", "str", "Content", False, "")], False),
            ("create_docx", "create_docx", "Create and edit Word docs", "document", "MEDIUM",
                [("title", "str", "Document title"), ("content", "str", "Content", False, "")], False),
            ("create_xlsx", "create_xlsx", "Create Excel with charts", "document", "MEDIUM",
                [("title", "str", "File title"), ("data", "str", "Data", False, "")], False),
            ("create_ppt", "create_ppt", "Create PowerPoint slides", "document", "MEDIUM",
                [("title", "str", "Presentation title"), ("content", "str", "Content", False, "")], False),
            ("convert_to_markdown", "convert_to_markdown", "Convert any file to Markdown", "document", "LOW",
                [("file", "str", "File path")], False),
            ("stock_analysis", "stock_analysis", "Stock analysis - fundamental + technical", "analysis", "LOW",
                [("ticker", "str", "Stock ticker (AAPL, TSLA...)")], False),
            ("market_research", "market_research", "Market research - TAM/SAM/SOM", "analysis", "LOW",
                [("topic", "str", "Research topic")], False),
            ("backtest_strategy", "backtest_strategy", "Backtest trading strategies", "analysis", "LOW",
                [("strategy", "str", "Strategy description")], False),
            ("generate_image", "generate_image", "AI image generation", "creative", "LOW",
                [("prompt", "str", "Image description")], False),
            ("recognize_image", "recognize_image", "Image analysis + Arabic OCR", "creative", "LOW",
                [("image", "str", "Image path or URL")], False),
            ("create_chart", "create_chart", "Professional charts and diagrams", "creative", "LOW",
                [("type", "str", "Chart type (bar, line, pie...)"), ("data", "str", "Chart data")], False),
            ("edit_video", "edit_video", "Video editing - FFmpeg", "creative", "MEDIUM",
                [("operation", "str", "FFmpeg operation")], False),
            ("transcribe_audio", "transcribe_audio", "Audio transcription - Whisper", "creative", "MEDIUM",
                [("file", "str", "Audio file path")], False),
            ("github_ops", "github_ops", "GitHub CLI operations", "dev", "MEDIUM",
                [("operation", "str", "GitHub operation")], False),
            ("deploy_vercel", "deploy_vercel", "Deploy to Vercel", "dev", "HIGH",
                [("project", "str", "Project name")], True),
            ("code_with_agent", "code_with_agent", "Professional TDD coding", "dev", "MEDIUM",
                [("task", "str", "Coding task")], False),
            ("send_email", "send_email", "Email - Gmail/IMAP", "comm", "MEDIUM",
                [("subject", "str", "Email subject")], False),
            ("get_news", "get_news", "AI and world news", "comm", "LOW",
                [("topic", "str", "News topic", False, "AI")], False),
            ("get_weather", "get_weather", "Weather - current + forecast", "productivity", "LOW",
                [("city", "str", "City name", False, "Makkah")], False),
            ("get_secret", "get_secret", "1Password CLI", "productivity", "HIGH",
                [("key", "str", "Secret key name")], True),
            ("manage_notion", "manage_notion", "Notion management", "productivity", "MEDIUM",
                [("action", "str", "Notion action")], False),
            ("manage_obsidian", "manage_obsidian", "Obsidian management", "productivity", "MEDIUM",
                [("action", "str", "Obsidian action")], False),
            ("browse_web", "browse_web", "Automated web browsing", "browser", "HIGH",
                [("url", "str", "Page URL"), ("action", "str", "Browser action")], True),
            ("download_video", "download_video", "Download video - yt-dlp", "browser", "MEDIUM",
                [("url", "str", "Video URL")], False),
            ("create_slides", "create_slides", "Interactive HTML slides", "education", "MEDIUM",
                [("topic", "str", "Presentation topic")], False),
            ("design_ui", "design_ui", "UI/UX design + RTL Arabic", "education", "MEDIUM",
                [("component", "str", "UI component")], False),
            ("brainstorm", "brainstorm", "Structured brainstorming", "education", "LOW",
                [("topic", "str", "Brainstorm topic")], False),
        ]

        for (skill_name, name, desc, cat, risk_str, params_raw, needs_approval) in skills:
            if skill_name in ALL_SKILLS:
                skill = ALL_SKILLS[skill_name]
                risk = getattr(RiskLevel, risk_str)
                params = []
                for p in params_raw:
                    required = True if len(p) == 3 else p[3]
                    default = p[4] if len(p) == 5 else None
                    params.append(ToolParam(p[0], p[1], p[2], required, default))
                def make_exec(s=skill):
                    return lambda **kw: s.execute(**kw)
                tool = Tool(name, desc, cat, risk, params, make_exec())
                tool.requires_approval = needs_approval
                self.register(tool)
'''

with open('tools/registry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert before the last line (which should be empty or end of file)
insert_at = content.rfind('\n    def get_tools_prompt')
if insert_at == -1:
    print("Could not find insertion point")
    sys.exit(1)

new_content = content[:insert_at] + SKILLS_CODE + '\n' + content[insert_at:]

with open('tools/registry.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Method written successfully")
