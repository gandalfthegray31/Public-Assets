#!/usr/bin/env python3
"""
Manual Blog Adder for Public-Assets Repository

This script helps you add a new blog to the Public-Assets repository structure
by prompting for the necessary information.

Usage:
    python add_blog_manual.py

The script will interactively ask for:
- Blog title
- Blog ID (generated from title if not provided)
- Author
- Category
- Medium URL
- Excerpt
- Content (opens in default editor)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime


def slugify(text):
    """Convert text to a URL-friendly slug."""
    # Remove special characters and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def get_user_input(prompt, default=None):
    """Get input from user with optional default value."""
    if default:
        result = input(f"{prompt} [{default}]: ")
        return result if result else default
    else:
        return input(f"{prompt}: ")


def get_multiline_input(prompt):
    """Open editor for multiline input."""
    print(f"{prompt} (Your default editor will open)")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp:
        temp_filename = temp.name
        # Add some instructions
        temp.write(b"# Enter your blog content here\n\nWrite your content in Markdown format.\nSave and close the editor when done.\n\n")
    
    # Open editor
    if sys.platform.startswith('darwin'):  # macOS
        subprocess.call(['open', '-t', temp_filename])
    elif sys.platform.startswith('linux'):
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.call([editor, temp_filename])
    elif sys.platform.startswith('win'):
        os.startfile(temp_filename)
    
    # Wait for user to finish
    input("Press Enter when you've finished editing the content...")
    
    # Read the content
    with open(temp_filename, 'r') as temp:
        content = temp.read()
    
    # Clean up
    os.unlink(temp_filename)
    
    return content


def create_blog_structure(blog_data):
    """Create the blog structure in the Public-Assets repository."""
    blogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Blogs')
    
    # Create blog directory
    blog_dir = os.path.join(blogs_dir, 'allBlogs', blog_data['id'])
    os.makedirs(blog_dir, exist_ok=True)
    
    # Determine image path and placeholder
    image_filename = f"{slugify(blog_data['category'])}.svg"
    image_path = f"allBlogs/{blog_data['id']}/{image_filename}"
    
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
        'id': blog_data['id'],
        'title': blog_data['title'],
        'excerpt': blog_data['excerpt'],
        'content': blog_data['content'],
        'author': blog_data['author'],
        'publishedDate': blog_data['publishedDate'],
        'readTime': f"{max(1, len(blog_data['content']) // 1000)} min read",
        'tags': [blog_data['category'], "AWS"],
        'mediumUrl': blog_data['mediumUrl'],
        'image': image_path,
        'category': blog_data['category']
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
        if entry.get('id') == blog_data['id']:
            # Update existing entry
            index_data[i] = {
                'id': blog_data['id'],
                'title': blog_data['title'],
                'excerpt': blog_data['excerpt'],
                'publishedDate': blog_data['publishedDate'],
                'coverImage': image_path,
                'category': blog_data['category'],
                'mediumUrl': blog_data['mediumUrl']
            }
            break
    else:
        # Add new entry
        index_data.append({
            'id': blog_data['id'],
            'title': blog_data['title'],
            'excerpt': blog_data['excerpt'],
            'publishedDate': blog_data['publishedDate'],
            'coverImage': image_path,
            'category': blog_data['category'],
            'mediumUrl': blog_data['mediumUrl']
        })
    
    # Sort by publishedDate (newest first)
    index_data.sort(key=lambda x: x['publishedDate'], reverse=True)
    
    # Write updated index
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    return blog_data['id']


def main():
    print("=== Add New Blog to Public-Assets Repository ===\n")
    
    # Get blog information
    title = get_user_input("Blog title")
    suggested_id = slugify(title)
    blog_id = get_user_input("Blog ID", suggested_id)
    author = get_user_input("Author", "SolutionsGSI Team")
    category = get_user_input("Category", "AWS")
    medium_url = get_user_input("Medium URL", "")
    
    # Get publish date
    today = datetime.now().strftime('%Y-%m-%d')
    publish_date = get_user_input("Publish date (YYYY-MM-DD)", today)
    
    # Get excerpt
    excerpt = get_user_input("Blog excerpt (short description)")
    
    # Get content
    print("\nNow you'll enter the blog content in Markdown format.")
    content = get_multiline_input("Blog content")
    
    # Create blog data
    blog_data = {
        'id': blog_id,
        'title': title,
        'excerpt': excerpt,
        'content': content,
        'author': author,
        'publishedDate': publish_date,
        'mediumUrl': medium_url,
        'category': category
    }
    
    # Create blog structure
    print("\nCreating blog structure...")
    blog_id = create_blog_structure(blog_data)
    
    print(f"\nBlog successfully added with ID: {blog_id}")
    print(f"Blog directory: /Users/saif/Projects/Public-Assets/Blogs/allBlogs/{blog_id}/")


if __name__ == "__main__":
    main()
