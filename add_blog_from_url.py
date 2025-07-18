#!/usr/bin/env python3
"""
Blog URL Importer for Public-Assets Repository

This script takes a blog URL as input and creates the necessary assets in the
structure required for the SolutionGSI website's blog system.

Usage:
    python add_blog_from_url.py --url <blog_url> [--id <blog_id>] [--category <category>]

Example:
    python add_blog_from_url.py --url https://medium.com/@author/blog-title-123456 --category "AWS Architecture"
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


def slugify(text):
    """Convert text to a URL-friendly slug."""
    # Remove special characters and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def extract_medium_info(url):
    """Extract information from a Medium blog post URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title').text.split('|')[0].strip()
        
        # Extract content
        content_div = soup.find('article')
        if content_div:
            # Convert to markdown (simplified)
            paragraphs = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = []
            
            for p in paragraphs:
                if p.name.startswith('h'):
                    level = int(p.name[1])
                    content.append(f"{'#' * level} {p.text.strip()}")
                else:
                    content.append(p.text.strip())
            
            content = "\n\n".join(content)
        else:
            content = "# " + title + "\n\nContent not available. Please add your content here."
        
        # Extract author
        author_elem = soup.find('meta', {'name': 'author'})
        author = author_elem['content'] if author_elem else "Unknown Author"
        
        # Extract publish date
        date_elem = soup.find('meta', {'property': 'article:published_time'})
        if date_elem:
            publish_date = date_elem['content'].split('T')[0]
        else:
            publish_date = datetime.now().strftime('%Y-%m-%d')
        
        # Generate excerpt
        excerpt = soup.find('meta', {'name': 'description'})
        if excerpt:
            excerpt = excerpt['content']
        else:
            # Take first paragraph as excerpt
            first_para = soup.find('p')
            excerpt = first_para.text[:200] + "..." if first_para else f"Read about {title}"
        
        return {
            'title': title,
            'content': content,
            'author': author,
            'publishedDate': publish_date,
            'excerpt': excerpt,
            'mediumUrl': url
        }
    
    except Exception as e:
        print(f"Error extracting information from {url}: {e}")
        return None


def create_blog_structure(blog_data, blog_id=None, category=None):
    """Create the blog structure in the Public-Assets repository."""
    blogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Blogs')
    
    # Generate blog ID if not provided
    if not blog_id:
        blog_id = slugify(blog_data['title'])
    
    # Set default category if not provided
    if not category:
        category = "AWS"
    
    # Create blog directory
    blog_dir = os.path.join(blogs_dir, 'allBlogs', blog_id)
    os.makedirs(blog_dir, exist_ok=True)
    
    # Determine image path and placeholder
    image_filename = f"{slugify(category)}.svg"
    image_path = f"allBlogs/{blog_id}/{image_filename}"
    
    # Find a suitable image from existing categories
    source_image = None
    for root, _, files in os.walk(os.path.join(blogs_dir, 'allBlogs')):
        for file in files:
            if file.endswith('.svg'):
                source_image = os.path.join(root, file)
                break
        if source_image:
            break
    
    # Copy image if found
    if source_image:
        with open(source_image, 'rb') as src_file:
            with open(os.path.join(blog_dir, image_filename), 'wb') as dest_file:
                dest_file.write(src_file.read())
    
    # Create blog.json
    blog_json = {
        'id': blog_id,
        'title': blog_data['title'],
        'excerpt': blog_data['excerpt'],
        'content': blog_data['content'],
        'author': blog_data['author'],
        'publishedDate': blog_data['publishedDate'],
        'readTime': f"{max(1, len(blog_data['content']) // 1000)} min read",
        'tags': [category, "AWS"],
        'mediumUrl': blog_data['mediumUrl'],
        'image': image_path,
        'category': category
    }
    
    with open(os.path.join(blog_dir, 'blog.json'), 'w') as f:
        json.dump(blog_json, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    # Update index.json
    index_path = os.path.join(blogs_dir, 'index.json')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index_data = json.load(f)
    else:
        index_data = []
    
    # Check if blog already exists in index
    for i, entry in enumerate(index_data):
        if entry.get('id') == blog_id:
            # Update existing entry
            index_data[i] = {
                'id': blog_id,
                'title': blog_data['title'],
                'excerpt': blog_data['excerpt'],
                'publishedDate': blog_data['publishedDate'],
                'coverImage': image_path,
                'category': category,
                'mediumUrl': blog_data['mediumUrl']
            }
            break
    else:
        # Add new entry
        index_data.append({
            'id': blog_id,
            'title': blog_data['title'],
            'excerpt': blog_data['excerpt'],
            'publishedDate': blog_data['publishedDate'],
            'coverImage': image_path,
            'category': category,
            'mediumUrl': blog_data['mediumUrl']
        })
    
    # Sort by publishedDate (newest first)
    index_data.sort(key=lambda x: x['publishedDate'], reverse=True)
    
    # Write updated index
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    return blog_id


def main():
    parser = argparse.ArgumentParser(description='Import blog from URL to Public-Assets repository')
    parser.add_argument('--url', required=True, help='URL of the blog post')
    parser.add_argument('--id', help='Custom ID for the blog (optional)')
    parser.add_argument('--category', help='Blog category (optional)')
    
    args = parser.parse_args()
    
    print(f"Fetching blog data from {args.url}...")
    blog_data = extract_medium_info(args.url)
    
    if not blog_data:
        print("Failed to extract blog data. Exiting.")
        sys.exit(1)
    
    print(f"Creating blog structure for '{blog_data['title']}'...")
    blog_id = create_blog_structure(blog_data, args.id, args.category)
    
    print(f"Blog successfully added with ID: {blog_id}")
    print(f"Blog directory: /Users/saif/Projects/Public-Assets/Blogs/allBlogs/{blog_id}/")


if __name__ == "__main__":
    main()
