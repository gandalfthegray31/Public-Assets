#!/usr/bin/env python3
"""
Medium Article Downloader
Downloads Medium articles from URLs in blog index and extracts clean HTML content with images.
"""

import json
import os
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from datetime import datetime

class MediumArticleDownloader:
    def __init__(self, blogs_dir="Blogs", output_dir="medium"):
        self.blogs_dir = Path(blogs_dir)
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.ensure_output_dirs()
    
    def ensure_output_dirs(self):
        """Create necessary output directories"""
        self.output_dir.mkdir(exist_ok=True)
    
    def load_blog_index(self):
        """Load the blog index JSON file"""
        index_path = self.blogs_dir / "index.json"
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def sanitize_filename(self, filename):
        """Sanitize filename for filesystem"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
    
    def download_image(self, img_url, img_path):
        """Download image from URL"""
        try:
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            with open(img_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"    ❌ Failed to download image {img_url}: {e}")
            return False
    
    def extract_article_content(self, soup):
        """Extract clean article content from Medium page"""
        try:
            # Find the main article content - try multiple selectors
            article = None
            
            # Try different selectors for Medium's current structure
            selectors = [
                'article',
                'div[data-testid="postArticle"]',
                'div[data-testid="postContent"]',
                'div.postArticle',
                'div.article',
                'div[role="article"]',
                'main',
                'div[class*="post"]',
                'div[class*="article"]'
            ]
            
            for selector in selectors:
                article = soup.select_one(selector)
                if article:
                    print(f"    ✅ Found content with selector: {selector}")
                    break
            
            if not article:
                print("    ⚠️  Could not find article content, trying to extract from body")
                article = soup.find('body')
            
            if not article:
                print("    ❌ Could not find any content to extract")
                return None
            
            # Debug: Print some info about what we found
            print(f"    🔍 Found article element with tag: {article.name}")
            print(f"    🔍 Article classes: {article.get('class', [])}")
            print(f"    🔍 Article text length: {len(article.get_text())}")
            
            # Extract title
            title_elem = article.find('h1') or article.find('h2')
            title = title_elem.get_text().strip() if title_elem else "Untitled"
            print(f"    📝 Title: {title}")
            
            # Extract author
            author_elem = article.find('a', class_=re.compile(r'author|writer|byline'))
            author = author_elem.get_text().strip() if author_elem else "Unknown Author"
            print(f"    👤 Author: {author}")
            
            # Extract publication date
            date_elem = article.find('time') or article.find('span', class_=re.compile(r'date|time'))
            if date_elem:
                pub_date = date_elem.get('datetime') or date_elem.get_text().strip()
            else:
                pub_date = ""
            print(f"    📅 Date: {pub_date}")
            
            # Extract reading time
            read_time_elem = article.find('span', class_=re.compile(r'readTime|reading'))
            read_time = read_time_elem.get_text().strip() if read_time_elem else "Unknown"
            print(f"    ⏱️  Reading time: {read_time}")
            
            # Extract tags
            tags = []
            tag_elements = article.find_all('a', class_=re.compile(r'tag|category'))
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text().strip()
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
            print(f"    🏷️  Tags found: {len(tags)}")
            
            # Clean up the article content
            # Remove Medium-specific elements
            for elem in article.find_all(['script', 'style', 'nav', 'header', 'footer']):
                elem.decompose()
            
            # Remove Medium-specific classes and IDs
            for elem in article.find_all(True):
                # Remove Medium-specific classes
                if elem.get('class'):
                    elem['class'] = [cls for cls in elem['class'] 
                                   if not any(medium_class in cls.lower() 
                                            for medium_class in ['medium', 'post', 'article', 'story', 'section'])]
                    if not elem['class']:
                        del elem['class']
                
                # Remove Medium-specific IDs
                if elem.get('id') and any(medium_id in elem.get('id', '').lower() 
                                        for medium_id in ['medium', 'post', 'article', 'story']):
                    del elem['id']
            
            # Extract images and prepare for download
            images = []
            img_elements = article.find_all('img')
            print(f"    🖼️  Found {len(img_elements)} image elements")
            
            for i, img in enumerate(img_elements):
                try:
                    img_src = img.get('src') or img.get('data-src')
                    if not img_src:
                        print(f"    ⚠️  Image {i+1} has no src attribute")
                        continue
                    
                    # Convert relative URLs to absolute
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = 'https://medium.com' + img_src
                    
                    # Generate filename
                    img_ext = os.path.splitext(urlparse(img_src).path)[1] or '.jpg'
                    img_filename = f"image_{i+1:03d}{img_ext}"
                    
                    # Update img src to local path
                    img['src'] = f"images/{img_filename}"
                    img['alt'] = img.get('alt', f"Image {i+1}")
                    
                    images.append({
                        'url': img_src,
                        'filename': img_filename,
                        'alt': img.get('alt', f"Image {i+1}")
                    })
                    print(f"    ✅ Processed image {i+1}: {img_filename}")
                except Exception as e:
                    print(f"    ❌ Error processing image {i+1}: {e}")
                    continue
            
            return {
                'title': title,
                'author': author,
                'pub_date': pub_date,
                'read_time': read_time,
                'tags': tags,
                'content': str(article),
                'images': images
            }
        except Exception as e:
            print(f"    ❌ Error in extract_article_content: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_article(self, blog_data):
        """Download a single Medium article"""
        medium_url = blog_data.get('mediumUrl')
        if not medium_url:
            print(f"    ⚠️  No Medium URL found for: {blog_data['title']}")
            return False
        
        print(f"    📄 Downloading: {blog_data['title']}")
        print(f"    🔗 URL: {medium_url}")
        
        try:
            # Create blog folder
            blog_folder = self.output_dir / self.sanitize_filename(blog_data['id'])
            blog_folder.mkdir(exist_ok=True)
            
            # Create images folder
            images_folder = blog_folder / "images"
            images_folder.mkdir(exist_ok=True)
            
            # Download the Medium page
            response = self.session.get(medium_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article content
            article_data = self.extract_article_content(soup)
            if not article_data:
                print(f"    ❌ Failed to extract content from: {medium_url}")
                return False
            
            # Download images
            print(f"    🖼️  Downloading {len(article_data['images'])} images...")
            for img_data in article_data['images']:
                img_path = images_folder / img_data['filename']
                if not img_path.exists():  # Don't re-download existing images
                    self.download_image(img_data['url'], img_path)
            
            # Create clean HTML file
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }}
        p {{
            margin-bottom: 1.5em;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1em 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 1.5em 0;
            padding-left: 1.5em;
            font-style: italic;
            color: #666;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        .article-meta {{
            background: #f8f9fa;
            padding: 1em;
            border-radius: 5px;
            margin-bottom: 2em;
            font-size: 0.9em;
            color: #666;
        }}
        .tags {{
            margin-top: 1em;
        }}
        .tag {{
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 0.25em 0.5em;
            border-radius: 3px;
            margin-right: 0.5em;
            margin-bottom: 0.5em;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="article-meta">
        <h1>{article_data['title']}</h1>
        <p><strong>Author:</strong> {article_data['author']}</p>
        <p><strong>Published:</strong> {article_data['pub_date']}</p>
        <p><strong>Reading Time:</strong> {article_data['read_time']}</p>
        {f'<div class="tags"><strong>Tags:</strong> {" ".join([f"<span class=\"tag\">{tag}</span>" for tag in article_data["tags"]])}</div>' if article_data['tags'] else ''}
    </div>
    
    <div class="article-content">
        {article_data['content']}
    </div>
</body>
</html>"""
            
            # Save HTML file
            html_file = blog_folder / "article.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save metadata
            metadata = {
                'original_url': medium_url,
                'title': article_data['title'],
                'author': article_data['author'],
                'pub_date': article_data['pub_date'],
                'read_time': article_data['read_time'],
                'tags': article_data['tags'],
                'downloaded_at': datetime.now().isoformat(),
                'image_count': len(article_data['images'])
            }
            
            metadata_file = blog_folder / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"    ✅ Successfully downloaded to: {blog_folder}")
            return True
            
        except Exception as e:
            print(f"    ❌ Error downloading {medium_url}: {e}")
            return False
    
    def download_all_articles(self):
        """Download all Medium articles from blog index"""
        print("🚀 Starting Medium article download...")
        print("=" * 50)
        
        # Load blog index
        try:
            blogs_data = self.load_blog_index()
        except Exception as e:
            print(f"❌ Error loading blog index: {e}")
            return
        
        print(f"📚 Found {len(blogs_data)} blogs in index")
        
        # Filter blogs with Medium URLs
        medium_blogs = [blog for blog in blogs_data if blog.get('mediumUrl')]
        print(f"🔗 Found {len(medium_blogs)} blogs with Medium URLs")
        
        if not medium_blogs:
            print("⚠️  No blogs with Medium URLs found!")
            return
        
        # Download each article
        successful = 0
        failed = 0
        
        for i, blog in enumerate(medium_blogs, 1):
            print(f"\n[{i}/{len(medium_blogs)}] Processing: {blog['title']}")
            
            if self.download_article(blog):
                successful += 1
            else:
                failed += 1
            
            # Add delay to be respectful to Medium
            if i < len(medium_blogs):
                print("    ⏳ Waiting 2 seconds before next download...")
                time.sleep(2)
        
        print("\n" + "=" * 50)
        print(f"✅ Download complete!")
        print(f"   📄 Successfully downloaded: {successful}")
        print(f"   ❌ Failed downloads: {failed}")
        print(f"   📁 Articles saved to: {self.output_dir}")
        
        # Create index file
        self.create_download_index(medium_blogs)
    
    def create_download_index(self, blogs_data):
        """Create an index file of downloaded articles"""
        index_data = {
            'downloaded_at': datetime.now().isoformat(),
            'total_articles': len(blogs_data),
            'articles': []
        }
        
        for blog in blogs_data:
            if blog.get('mediumUrl'):
                blog_folder = self.output_dir / self.sanitize_filename(blog['id'])
                if blog_folder.exists():
                    article_info = {
                        'id': blog['id'],
                        'title': blog['title'],
                        'original_medium_url': blog['mediumUrl'],
                        'local_folder': str(blog_folder.relative_to(self.output_dir)),
                        'html_file': 'article.html',
                        'images_folder': 'images/',
                        'metadata_file': 'metadata.json'
                    }
                    index_data['articles'].append(article_info)
        
        index_file = self.output_dir / "download_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Created download index: {index_file}")

def main():
    downloader = MediumArticleDownloader()
    downloader.download_all_articles()

if __name__ == "__main__":
    main()
