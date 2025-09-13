#!/usr/bin/env python3
"""
Blog to HTML Converter
Converts blog markdown content to HTML files with Medium-style formatting.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class BlogToHTMLConverter:
    def __init__(self, blogs_dir="Blogs", output_dir="Blogs-html"):
        self.blogs_dir = Path(blogs_dir)
        self.output_dir = Path(output_dir)
        self.ensure_output_dirs()
    
    def ensure_output_dirs(self):
        """Create necessary output directories"""
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "posts").mkdir(exist_ok=True)
        (self.output_dir / "styles").mkdir(exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
    
    def load_blog_index(self):
        """Load the blog index JSON file"""
        index_path = self.blogs_dir / "index.json"
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_blog_content(self, blog_id):
        """Load individual blog content from JSON"""
        # Handle specific case where ID doesn't match folder name
        if "Ship-Happens-How-to-Build-a-Real-Time-Sensitive-Cargo-Tracking-System-with-AWS-Starlink-and-Off-the-Shelf-IoT" in blog_id:
            blog_path = self.blogs_dir / "allBlogs" / "Ship-Happens-Build-a-Real-Time-Sensitive-Cargo-Shelf-IoT" / "blog.json"
        else:
            # Try the exact blog_id first
            blog_path = self.blogs_dir / "allBlogs" / blog_id / "blog.json"
            
            if not blog_path.exists():
                # If not found, try to find a folder that matches the pattern
                all_blog_dirs = list((self.blogs_dir / "allBlogs").glob("*"))
                for dir_path in all_blog_dirs:
                    if blog_id.lower().replace("-", "").replace(" ", "") in dir_path.name.lower().replace("-", "").replace(" ", ""):
                        blog_path = dir_path / "blog.json"
                        break
        
        if not blog_path.exists():
            raise FileNotFoundError(f"Blog directory not found for ID: {blog_id}")
            
        with open(blog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def convert_markdown_to_html(self, markdown_content):
        """Convert markdown content to HTML"""
        if not markdown_content:
            return ""
        
        # Convert markdown to HTML
        html = markdown_content
        
        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```([\s\S]*?)```', r'<pre><code>\1</code></pre>', html)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # Line breaks and paragraphs
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = re.sub(r'\n', '<br>', html)
        
        # Wrap in paragraphs
        html = f'<p>{html}</p>'
        
        # Clean up empty paragraphs and breaks
        html = re.sub(r'<p></p>', '', html)
        html = re.sub(r'<p><br></p>', '', html)
        html = re.sub(r'<p>\s*</p>', '', html)
        
        return html
    
    def create_blog_post_html(self, blog_data):
        """Create HTML for individual blog post"""
        published_date = datetime.strptime(blog_data['publishedDate'], '%Y-%m-%d').strftime('%B %d, %Y')
        
        # Convert markdown content to HTML
        content_html = self.convert_markdown_to_html(blog_data.get('content', ''))
        
        # Create tags HTML
        tags_html = ""
        if blog_data.get('tags'):
            tags_html = f"""
                <div class="blog-tags">
                    {''.join([f'<span class="blog-tag">{tag}</span>' for tag in blog_data['tags']])}
                </div>
            """
        
        # Medium link
        medium_link = ""
        if blog_data.get('mediumUrl'):
            medium_link = f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="{blog_data['mediumUrl']}" target="_blank" class="blog-tag" style="background: var(--primary-color); color: white; padding: 0.75rem 1.5rem; text-decoration: none;">
                        Read on Medium →
                    </a>
                </div>
            """
        
        # Image HTML
        image_html = ""
        if blog_data.get('image'):
            image_html = f'<img src="../{blog_data["image"]}" alt="{blog_data["title"]}" class="blog-post-image">'
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{blog_data['title']} - Solutions GSI</title>
    <link rel="stylesheet" href="styles/medium-style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Charter:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1 class="site-title">Solutions GSI Blog</h1>
            <p class="site-subtitle">AWS Solutions, AI, and Cloud Architecture Insights</p>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <article class="blog-post">
                <header class="blog-post-header">
                    <h1 class="blog-post-title">{blog_data['title']}</h1>
                    <div class="blog-post-meta">
                        <span class="author">By {blog_data.get('author', 'Solutions GSI')}</span>
                        <span class="date">{published_date}</span>
                        <span class="read-time">{blog_data.get('readTime', '2 min read')}</span>
                    </div>
                    {image_html}
                </header>
                
                <div class="blog-content">
                    {content_html}
                </div>
                
                {tags_html}
                {medium_link}
            </article>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 Solutions GSI. All rights reserved.</p>
            <p><a href="index.html">← Back to all blogs</a></p>
        </div>
    </footer>
</body>
</html>"""
        
        return html_template
    
    def create_blog_index_html(self, blogs_data):
        """Create the main blog index HTML"""
        blog_cards = []
        
        for blog in blogs_data:
            published_date = datetime.strptime(blog['publishedDate'], '%Y-%m-%d').strftime('%B %d, %Y')
            
            card_html = f"""
            <div class="blog-card" onclick="window.open('posts/{blog['id']}.html', '_blank')">
                <img src="../{blog['coverImage']}" alt="{blog['title']}" class="blog-image" onerror="this.style.display='none'">
                <div class="blog-content">
                    <div class="blog-meta">
                        <span class="blog-category">{blog['category']}</span>
                        <span class="blog-date">{published_date}</span>
                    </div>
                    <h2 class="blog-title">{blog['title']}</h2>
                    <p class="blog-excerpt">{blog['excerpt']}</p>
                    <div class="blog-footer">
                        <span class="read-time">2 min read</span>
                        <span class="read-more">Read more →</span>
                    </div>
                </div>
            </div>
            """
            blog_cards.append(card_html)
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blogs - Solutions GSI</title>
    <link rel="stylesheet" href="styles/medium-style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Charter:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1 class="site-title">Solutions GSI Blog</h1>
            <p class="site-subtitle">AWS Solutions, AI, and Cloud Architecture Insights</p>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="blog-grid">
                {''.join(blog_cards)}
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 Solutions GSI. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
        
        return index_html
    
    def convert_all_blogs(self):
        """Convert all blogs to HTML"""
        print("Loading blog index...")
        blogs_data = self.load_blog_index()
        
        print(f"Found {len(blogs_data)} blogs to convert")
        
        # Create individual blog post HTML files
        for blog in blogs_data:
            try:
                print(f"Converting: {blog['title']}")
                blog_content = self.load_blog_content(blog['id'])
                html_content = self.create_blog_post_html(blog_content)
                
                # Save individual blog post
                post_file = self.output_dir / "posts" / f"{blog['id']}.html"
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
            except Exception as e:
                print(f"Error converting {blog['title']}: {e}")
                continue
        
        # Create main index page
        print("Creating blog index page...")
        index_html = self.create_blog_index_html(blogs_data)
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"Conversion complete! HTML files saved to: {self.output_dir}")
        print(f"Open {self.output_dir}/index.html in your browser to view the blogs.")

def main():
    converter = BlogToHTMLConverter()
    converter.convert_all_blogs()

if __name__ == "__main__":
    main()
