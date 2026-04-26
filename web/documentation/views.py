import os
import re
import markdown
from django.shortcuts import render
from django.conf import settings

from django.utils import translation
from django.views.decorators.cache import cache_page

@cache_page(60 * 15) # Cache home for 15 mins
def home(request):
    return render(request, 'home.html')

@cache_page(60 * 60) # Cache docs for 1 hour
def docs(request, doc_name='README'):
    lang = translation.get_language()
    
    # Map doc_name to valid files or default to README
    valid_docs = ['README', 'GUIDE', 'PIPELINES', 'TRAINING', 'PUBLISH']
    base_filename = doc_name.upper() if doc_name.upper() in valid_docs else 'README'
    
    # Try language-specific file first (e.g., README.ar.md)
    if lang == 'ar':
        filename = f"{base_filename}.ar.md"
    else:
        filename = f"{base_filename}.md"
        
    readme_path = os.path.join(settings.BASE_DIR.parent, filename)

    # Fallback to English if Arabic file doesn't exist
    if not os.path.exists(readme_path):
        filename = f"{base_filename}.md"
        readme_path = os.path.join(settings.BASE_DIR.parent, filename)

    if not os.path.exists(readme_path):
        readme_path = os.path.join(settings.BASE_DIR.parent, 'README.md')

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Protect Mermaid blocks from codehilite
    mermaid_blocks = []
    def protect_mermaid(match):
        mermaid_blocks.append(match.group(1))
        return f"[[MERMAID_BLOCK_{len(mermaid_blocks)-1}]]"

    # Match ```mermaid ... ```
    content = re.sub(r'```mermaid\s*\n(.*?)\n```', protect_mermaid, content, flags=re.DOTALL)

    # 2. Convert markdown to HTML with TOC
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
    html_content = md.convert(content)
    toc_content = md.toc

    # 3. Restore Mermaid blocks and ensure they are NOT wrapped in <p> tags
    def restore_mermaid(match):
        index = int(match.group(1))
        # Strip trailing newlines from content to avoid extra spacing in the diagram
        code = mermaid_blocks[index].strip()
        return f'<pre class="mermaid">{code}</pre>'

    # Also match placeholders inside <p> tags and remove the <p>
    html_content = re.sub(r'<p>\[\[MERMAID_BLOCK_(\d+)\]\]</p>', restore_mermaid, html_content)
    # Generic replacement for any remaining ones
    html_content = re.sub(r'\[\[MERMAID_BLOCK_(\d+)\]\]', restore_mermaid, html_content)

    return render(request, 'docs.html', {
        'content': html_content,
        'toc': toc_content,
        'doc_name': doc_name
    })
