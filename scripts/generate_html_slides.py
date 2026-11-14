import json

md_path = "/Users/roshansahni/Desktop/smartattend/docs/PRESENTATION_SLIDES_34.md"
html_path = "/Users/roshansahni/Desktop/smartattend/docs/presentation_slides.html"

# Import slides_data from generate_pptx
import sys
sys.path.append("/Users/roshansahni/.gemini/antigravity/scratch/smartattend/scripts")
from generate_pptx import slides_data

# 1. Generate Markdown documentation
md_content = """# 🎓 SmartAttend: 34-Slide Industrial Training & Viva Voce Defense Presentation
### Python Programming Internship at CodeAlpha
**Submitted in Partial Fulfillment for the Degree of Bachelor of Technology in Computer Science & Engineering (AI & DS)**
* Global Institute of Technology and Management (GITM), Gurugram, Haryana
* Student: **Roshan** | Roll No.: **248503** | 7th Semester | Academic Session: **2026-2027**

---
"""

for idx, s in enumerate(slides_data):
    title = s.get("title", "").replace("\n", " ")
    category = s.get("category", "TITLE")
    md_content += f"\n## Slide {idx + 1}: {title}\n"
    md_content += f"**Category**: `{category}`\n\n"
    
    if s.get("type") == "title":
        md_content += f"> **Project**: Smart Attendance System (SmartAttend)\n"
        md_content += f"> **Internship**: CodeAlpha Python Programming Training\n"
        md_content += f"> **Student**: Roshan (Roll No: 248503), B.Tech CSE (AI & DS), 7th Sem\n"
        md_content += f"> **Institution**: Global Institute of Technology & Management, Gurugram\n\n"
    else:
        for card_title, items in s.get("cards", []):
            md_content += f"### {card_title}\n"
            for item in items:
                md_content += f"- {item}\n"
            md_content += "\n"
            
    md_content += "---\n"

with open(md_path, "w") as f:
    f.write(md_content)

# 2. Generate Interactive Standalone HTML Presentation
html_slides = []
for idx, s in enumerate(slides_data):
    if s.get("type") == "title":
        slide_html = f"""
        <div class="slide title-slide active" data-slide="{idx+1}">
            <div class="badge-tag">GLOBAL INSTITUTE OF TECHNOLOGY AND MANAGEMENT, GURUGRAM</div>
            <h1 class="main-title">INDUSTRIAL TRAINING REPORT ON<br><span class="highlight">SMART ATTENDANCE SYSTEM</span></h1>
            <p class="subtitle">Python Programming Internship at CodeAlpha<br>Submitted for Bachelor of Technology in CSE (AI & DS), 7th Semester</p>
            <div class="title-grid">
                <div class="title-card">
                    <h4>Submitted By:</h4>
                    <p><strong>Roshan</strong></p>
                    <p>Roll No.: <strong>248503</strong></p>
                    <p>B.Tech CSE (AI & DS), 7th Sem</p>
                </div>
                <div class="title-card">
                    <h4>Submitted To:</h4>
                    <p>Department of CSE</p>
                    <p>Global Institute of Technology & Management</p>
                    <p>Gurugram, Haryana | Session 2026-2027</p>
                </div>
            </div>
            <div class="footer-note">Slide 1 of {len(slides_data)}</div>
        </div>
        """
    else:
        cards_html = ""
        for c_title, items in s.get("cards", []):
            list_items = "".join([f"<li>{item}</li>" for item in items])
            cards_html += f"""
            <div class="content-card">
                <h3>{c_title}</h3>
                <ul>{list_items}</ul>
            </div>
            """
        
        slide_html = f"""
        <div class="slide" data-slide="{idx+1}">
            <div class="slide-header">
                <span class="category-pill">{s.get("category", "SMARTATTEND")}</span>
                <h2>{s.get("title", "")}</h2>
            </div>
            <div class="cards-grid">
                {cards_html}
            </div>
            <div class="slide-footer">
                <span>Slide {idx+1} of {len(slides_data)}</span>
                <span>Roshan (Roll: 248503) • GITM Gurugram • CodeAlpha Internship</span>
            </div>
        </div>
        """
    html_slides.append(slide_html)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartAttend: 34-Slide Final B.Tech Presentation — Roshan (248503)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #0f172a;
            color: #1e293b;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: column;
        }}
        .deck-container {{
            flex: 1;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}
        .slide {{
            display: none;
            width: 100%;
            max-width: 1280px;
            height: 720px;
            background: #f8fafc;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            padding: 40px 48px;
            position: relative;
            flex-direction: column;
            justify-content: space-between;
        }}
        .slide.active {{
            display: flex;
            animation: fadeIn 0.25s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .title-slide {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            text-align: center;
            justify-content: center;
            align-items: center;
            padding: 48px;
        }}
        .badge-tag {{
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.05em;
            margin-bottom: 24px;
        }}
        .main-title {{
            font-size: 32px;
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 12px;
        }}
        .highlight {{
            color: #38bdf8;
        }}
        .subtitle {{
            color: #94a3b8;
            font-size: 15px;
            max-width: 800px;
            line-height: 1.5;
            margin-bottom: 36px;
        }}
        .title-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            width: 100%;
            max-width: 850px;
            text-align: left;
        }}
        .title-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.6;
        }}
        .title-card h4 {{
            color: #38bdf8;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .slide-header {{
            margin-bottom: 20px;
        }}
        .category-pill {{
            font-size: 11px;
            font-weight: 800;
            color: #2563eb;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
            display: block;
        }}
        .slide-header h2 {{
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            flex: 1;
        }}
        .content-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 24px 28px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        }}
        .content-card h3 {{
            color: #2563eb;
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 14px;
            border-bottom: 2px solid #eff6ff;
            padding-bottom: 8px;
        }}
        .content-card ul {{
            list-style: none;
            padding: 0;
        }}
        .content-card li {{
            font-size: 13.5px;
            color: #334155;
            line-height: 1.55;
            margin-bottom: 10px;
            position: relative;
            padding-left: 20px;
        }}
        .content-card li::before {{
            content: "•";
            color: #2563eb;
            font-weight: bold;
            font-size: 18px;
            position: absolute;
            left: 0;
            top: -2px;
        }}
        .slide-footer {{
            display: flex;
            justify-content: space-between;
            font-size: 11.5px;
            color: #64748b;
            font-weight: 500;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
        }}
        .footer-note {{
            font-size: 11.5px;
            color: #64748b;
            margin-top: 24px;
        }}
        .controls-bar {{
            background: #1e293b;
            padding: 12px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid #334155;
            color: #e2e8f0;
            font-size: 13px;
        }}
        .btn {{
            background: #2563eb;
            color: #fff;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #1d4ed8;
        }}
        .btn-outline {{
            background: transparent;
            border: 1px solid #475569;
            color: #cbd5e1;
            margin-right: 8px;
        }}
        .btn-outline:hover {{
            background: #334155;
            color: #fff;
        }}
    </style>
</head>
<body>
    <div class="deck-container">
        {"".join(html_slides)}
    </div>

    <div class="controls-bar">
        <div>
            <strong>SmartAttend ERP</strong> — 34 Slide Master Defense Presentation
        </div>
        <div>
            <button class="btn btn-outline" id="prevBtn">← Previous (Left Arrow)</button>
            <span id="counter" style="margin: 0 16px; font-weight: bold; font-family: monospace;">1 / {len(slides_data)}</span>
            <button class="btn" id="nextBtn">Next (Right Arrow) →</button>
        </div>
        <div>
            <button class="btn btn-outline" onclick="window.print()">🖨️ Print to PDF</button>
        </div>
    </div>

    <script>
        const slides = document.querySelectorAll('.slide');
        const counter = document.getElementById('counter');
        let current = 0;
        const total = slides.length;

        function showSlide(index) {{
            if (index < 0) index = 0;
            if (index >= total) index = total - 1;
            slides.forEach((s, idx) => {{
                s.classList.toggle('active', idx === index);
            }});
            current = index;
            counter.innerText = `${{current + 1}} / ${{total}}`;
        }}

        document.getElementById('prevBtn').addEventListener('click', () => showSlide(current - 1));
        document.getElementById('nextBtn').addEventListener('click', () => showSlide(current + 1));

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') {{
                showSlide(current + 1);
            }} else if (e.key === 'ArrowLeft') {{
                showSlide(current - 1);
            }}
        }});
    </script>
</body>
</html>
"""

with open(html_path, "w") as f:
    f.write(full_html)

print("Generated HTML Presentation & Markdown defense docs successfully!")
