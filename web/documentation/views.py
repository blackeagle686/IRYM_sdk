import os
import re
import markdown
from django.shortcuts import render
from django.conf import settings

def home(request):
    return render(request, 'home.html')

def docs(request, doc_name='README'):
    filename = 'README.md' if doc_name == 'README' else 'GUIDE.md'
    readme_path = os.path.join(settings.BASE_DIR.parent, filename)

    if not os.path.exists(readme_path):
        readme_path = os.path.join(settings.BASE_DIR.parent, 'README.md')

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        content,
        extensions=['fenced_code', 'codehilite', 'tables', 'toc']
    )

    # Fix Mermaid blocks: <pre><code class="language-mermaid">...</code></pre>
    # must become <pre class="mermaid">...</pre>
    html_content = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<pre class="mermaid">\1</pre>',
        html_content,
        flags=re.DOTALL
    )

    return render(request, 'docs.html', {
        'content': html_content,
        'doc_name': doc_name
    })
