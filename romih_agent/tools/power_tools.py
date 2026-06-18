"""
Romih Power Tools - PDF, Excel, Charts, Web Search, YouTube
===========================================================
"""
import os, json, sys, io, tempfile

def register(tools_registry):
    """Register all power tools"""
    
    # === 1. PDF GENERATION ===
    def generate_pdf(params):
        """Generate a professional PDF report. 
        params: title, content (markdown), filename (optional)"""
        title = params.get('title', 'Report')
        content = params.get('content', 'No content')
        filename = params.get('filename', 'report.pdf')
        
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('NotoSansArabic', '', r'C:\Users\saifr\.openclaw-autoclaw\workspace\NotoSansArabic-Regular.ttf', uni=True)
            pdf.set_font('NotoSansArabic', '', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(10)
            pdf.set_font('NotoSansArabic', '', 12)
            pdf.multi_cell(0, 8, content)
            path = os.path.join(tempfile.gettempdir(), filename)
            pdf.output(path)
            return json.dumps({"status": "ok", "file": path, "message": f"PDF generated: {filename}"}, ensure_ascii=False)
        except ImportError:
            return "PDF tool: fpdf not installed. pip install fpdf2"
        except Exception as e:
            return f"PDF error: {e}"

    tools_registry.register(
        tools_registry.Tool(
            name="generate_pdf",
            description="Generate a professional PDF report with Arabic support",
            parameters={"title": "Report title", "content": "Report content (Arabic markdown)", "filename": "Output filename (optional)"},
            func=generate_pdf,
            category="power"
        )
    )

    # === 2. EXCEL GENERATION ===
    def generate_excel(params):
        """Generate an Excel spreadsheet with data.
        params: headers (list), rows (list of lists), filename (optional)"""
        headers = params.get('headers', ['Column1', 'Column2'])
        rows = params.get('rows', [])
        filename = params.get('filename', 'data.xlsx')
        
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            for row in rows:
                ws.append(row)
            path = os.path.join(tempfile.gettempdir(), filename)
            wb.save(path)
            return json.dumps({"status": "ok", "file": path, "rows": len(rows), "message": f"Excel generated: {filename}"}, ensure_ascii=False)
        except ImportError:
            return "Excel tool: openpyxl not installed. pip install openpyxl"
        except Exception as e:
            return f"Excel error: {e}"

    tools_registry.register(
        tools_registry.Tool(
            name="generate_excel",
            description="Generate an Excel spreadsheet from data",
            parameters={"headers": "Column headers (list)", "rows": "Data rows (list of lists)", "filename": "Output filename (optional)"},
            func=generate_excel,
            category="power"
        )
    )

    # === 3. CHART GENERATION ===
    def generate_chart(params):
        """Generate a chart as an image.
        params: type (bar/line/pie), title, labels (list), values (list)"""
        chart_type = params.get('type', 'bar')
        title = params.get('title', 'Chart')
        labels = params.get('labels', ['A', 'B', 'C'])
        values = params.get('values', [10, 20, 30])
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(10, 6))
            if chart_type == 'bar':
                plt.bar(labels, values, color='#2563eb')
            elif chart_type == 'line':
                plt.plot(labels, values, marker='o', color='#2563eb', linewidth=2)
            elif chart_type == 'pie':
                plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#2563eb','#7c3aed','#db2777','#ea580c','#16a34a'])
            
            plt.title(title, fontsize=16, fontweight='bold')
            path = os.path.join(tempfile.gettempdir(), 'chart.png')
            plt.tight_layout()
            plt.savefig(path, dpi=100, bbox_inches='tight')
            plt.close()
            return json.dumps({"status": "ok", "file": path, "type": chart_type, "message": f"Chart generated: {chart_type}"}, ensure_ascii=False)
        except ImportError:
            return "Chart tool: matplotlib not installed. pip install matplotlib"
        except Exception as e:
            return f"Chart error: {e}"

    tools_registry.register(
        tools_registry.Tool(
            name="generate_chart",
            description="Generate a chart (bar, line, pie) as an image",
            parameters={"type": "Chart type: bar/line/pie", "title": "Chart title", "labels": "Data labels", "values": "Data values"},
            func=generate_chart,
            category="power"
        )
    )

    # === 4. WEB SEARCH ===
    def web_search(params):
        """Search the web and return results.
        params: query, num_results (optional, default 5)"""
        query = params.get('query', '')
        num = int(params.get('num_results', 5))
        
        try:
            import urllib.request, urllib.parse
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
            
            # Simple extraction of titles
            import re
            results = []
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', data)
            snippets = re.findall(r'<div class="BNeawe s3v9rd[^"]*">(.*?)</div>', data)
            
            for i in range(min(num, len(titles))):
                title = re.sub(r'<[^>]+>', '', titles[i])
                snippet = re.sub(r'<[^>]+>', '', snippets[i]) if i < len(snippets) else ''
                results.append({"title": title, "snippet": snippet[:200]})
            
            return json.dumps({"query": query, "results": results, "count": len(results)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e), "query": query, "message": "Search failed. Try a different query."}, ensure_ascii=False)

    tools_registry.register(
        tools_registry.Tool(
            name="web_search",
            description="Search the web and return results with titles and snippets",
            parameters={"query": "Search query", "num_results": "Number of results (default 5)"},
            func=web_search,
            category="power"
        )
    )

    # === 5. YOUTUBE TRANSCRIPT ===
    def youtube_transcript(params):
        """Get transcript/subtitles from a YouTube video.
        params: url"""
        url = params.get('url', '')
        
        try:
            import subprocess, tempfile, os
            fd, tmp = tempfile.mkstemp(suffix='.txt')
            os.close(fd)
            
            result = subprocess.run([
                'yt-dlp', '--skip-download', '--write-auto-subs',
                '--sub-lang', 'ar,en', '--convert-subs', 'srt',
                '--output', tmp.replace('.txt', ''), url
            ], capture_output=True, text=True, timeout=60)
            
            # Read the generated subtitle file
            import glob
            base = tmp.replace('.txt', '')
            subs = glob.glob(base + '*.srt') or glob.glob(base + '*.vtt')
            
            if subs:
                with open(subs[0], 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                os.unlink(subs[0])
                # Clean up SRT/VTT formatting
                import re
                text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2}[.,]\d{3} -->.*\n', '', text)
                text = re.sub(r'<[^>]+>', '', text)
                text = re.sub(r'\n{3,}', '\n\n', text).strip()
                return json.dumps({"status": "ok", "transcript": text[:5000], "length": len(text)}, ensure_ascii=False)
            else:
                return json.dumps({"status": "no_subtitles", "url": url, "message": "No subtitles available for this video"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e), "url": url, "message": "Transcript extraction failed"}, ensure_ascii=False)

    tools_registry.register(
        tools_registry.Tool(
            name="youtube_transcript",
            description="Get transcript/subtitles from a YouTube video",
            parameters={"url": "YouTube video URL"},
            func=youtube_transcript,
            category="power"
        )
    )
    
    return 5  # Number of tools registered
