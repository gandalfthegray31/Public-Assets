#!/usr/bin/env python3
"""
Blog Manager - Master Script for Public-Assets Repository

This script provides a unified interface for managing blogs in the Public-Assets repository.
It combines functionality from all blog-related scripts for efficient blog management.

Usage:
    python blog_manager.py <command> [options]

Commands:
    add-url      Add blog from Medium URL
    add-manual   Add blog manually (interactive)
    add-image    Add/update image for existing blog
    download     Download Medium HTML content for all blogs
    convert      Convert blogs to HTML with Medium styling
    list         List all blogs
    help         Show this help message

Examples:
    # Add blog from URL
    python blog_manager.py add-url --url "https://medium.com/@author/blog-title" --category "AWS"
    
    # Add blog manually
    python blog_manager.py add-manual
    
    # Download Medium content for all blogs
    python blog_manager.py download
    
    # Convert blogs to HTML
    python blog_manager.py convert
    
    # List all blogs
    python blog_manager.py list
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

class BlogManager:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.blogs_dir = self.scripts_dir / "Blogs"
        
    def run_script(self, script_name, args=None):
        """Run a Python script with optional arguments"""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            return False
            
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
            
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {script_name}: {e}")
            return False
    
    def add_blog_from_url(self, url, blog_id=None, category=None, image_path=None):
        """Add blog from Medium URL"""
        print("🚀 Adding blog from URL...")
        
        args = ["--url", url]
        if blog_id:
            args.extend(["--id", blog_id])
        if category:
            args.extend(["--category", category])
            
        success = self.run_script("add_blog_from_url.py", args)
        
        if success and image_path:
            print("📷 Adding custom image...")
            # Get the blog ID (either provided or generated from title)
            if not blog_id:
                # We need to extract the blog ID from the created blog
                # This is a limitation - we'd need to modify add_blog_from_url.py to return the ID
                print("⚠️  Note: To add a custom image, please run:")
                print(f"   python add_blog_image.py --id <blog_id> --image {image_path}")
            else:
                self.run_script("add_blog_image.py", ["--id", blog_id, "--image", image_path])
        
        return success
    
    def add_blog_manual(self):
        """Add blog manually (interactive)"""
        print("🚀 Adding blog manually...")
        return self.run_script("add_blog_manual.py")
    
    def add_blog_image(self, blog_id, image_path):
        """Add/update image for existing blog"""
        print(f"📷 Adding image to blog: {blog_id}")
        return self.run_script("add_blog_image.py", ["--id", blog_id, "--image", image_path])
    
    def download_medium_content(self):
        """Download Medium HTML content for all blogs"""
        print("📥 Downloading Medium content for all blogs...")
        return self.run_script("download_medium_articles.py")
    
    def convert_blogs_to_html(self):
        """Convert blogs to HTML with Medium styling"""
        print("🎨 Converting blogs to HTML...")
        return self.run_script("convert_blogs_to_html.py")
    
    def list_blogs(self):
        """List all blogs in the repository"""
        print("📋 Listing all blogs...")
        
        index_path = self.blogs_dir / "index.json"
        if not index_path.exists():
            print("❌ No blogs found. Index file not found.")
            return False
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                blogs = json.load(f)
            
            if not blogs:
                print("📝 No blogs found in the repository.")
                return True
            
            print(f"\n📚 Found {len(blogs)} blogs:\n")
            print("-" * 80)
            
            for i, blog in enumerate(blogs, 1):
                print(f"{i:2d}. {blog['title']}")
                print(f"    ID: {blog['id']}")
                print(f"    Category: {blog['category']}")
                print(f"    Published: {blog['publishedDate']}")
                print(f"    Medium URL: {blog.get('mediumUrl', 'N/A')}")
                
                # Check if medium content exists
                medium_folder = self.blogs_dir / "allBlogs" / blog['id'] / "medium"
                if medium_folder.exists():
                    print(f"    Medium HTML: ✅ Available")
                else:
                    print(f"    Medium HTML: ❌ Not downloaded")
                
                print("-" * 80)
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading blogs: {e}")
            return False
    
    def full_workflow(self, url, blog_id=None, category=None, image_path=None):
        """Complete workflow: add blog from URL, download Medium content, and convert to HTML"""
        print("🔄 Running full blog workflow...")
        
        # Step 1: Add blog from URL
        if not self.add_blog_from_url(url, blog_id, category, image_path):
            print("❌ Failed to add blog from URL")
            return False
        
        # Step 2: Download Medium content
        if not self.download_medium_content():
            print("⚠️  Failed to download Medium content, but blog was added")
            return False
        
        # Step 3: Convert to HTML
        if not self.convert_blogs_to_html():
            print("⚠️  Failed to convert to HTML, but blog and Medium content were added")
            return False
        
        print("✅ Full workflow completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Blog Manager - Master script for Public-Assets repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add blog from URL
  python blog_manager.py add-url --url "https://medium.com/@author/blog-title" --category "AWS"
  
  # Add blog manually
  python blog_manager.py add-manual
  
  # Download Medium content for all blogs
  python blog_manager.py download
  
  # Convert blogs to HTML
  python blog_manager.py convert
  
  # Full workflow (add + download + convert)
  python blog_manager.py full-workflow --url "https://medium.com/@author/blog-title"
  
  # List all blogs
  python blog_manager.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add URL command
    add_url_parser = subparsers.add_parser('add-url', help='Add blog from Medium URL')
    add_url_parser.add_argument('--url', required=True, help='Medium blog URL')
    add_url_parser.add_argument('--id', help='Custom blog ID')
    add_url_parser.add_argument('--category', help='Blog category')
    add_url_parser.add_argument('--image', help='Path to custom image')
    
    # Add manual command
    subparsers.add_parser('add-manual', help='Add blog manually (interactive)')
    
    # Add image command
    add_image_parser = subparsers.add_parser('add-image', help='Add/update image for existing blog')
    add_image_parser.add_argument('--id', required=True, help='Blog ID')
    add_image_parser.add_argument('--image', required=True, help='Path to image file')
    
    # Download command
    subparsers.add_parser('download', help='Download Medium HTML content for all blogs')
    
    # Convert command
    subparsers.add_parser('convert', help='Convert blogs to HTML with Medium styling')
    
    # Full workflow command
    full_workflow_parser = subparsers.add_parser('full-workflow', help='Complete workflow: add + download + convert')
    full_workflow_parser.add_argument('--url', required=True, help='Medium blog URL')
    full_workflow_parser.add_argument('--id', help='Custom blog ID')
    full_workflow_parser.add_argument('--category', help='Blog category')
    full_workflow_parser.add_argument('--image', help='Path to custom image')
    
    # List command
    subparsers.add_parser('list', help='List all blogs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BlogManager()
    
    if args.command == 'add-url':
        success = manager.add_blog_from_url(
            args.url, 
            args.id, 
            args.category, 
            args.image
        )
    elif args.command == 'add-manual':
        success = manager.add_blog_manual()
    elif args.command == 'add-image':
        success = manager.add_blog_image(args.id, args.image)
    elif args.command == 'download':
        success = manager.download_medium_content()
    elif args.command == 'convert':
        success = manager.convert_blogs_to_html()
    elif args.command == 'full-workflow':
        success = manager.full_workflow(
            args.url, 
            args.id, 
            args.category, 
            args.image
        )
    elif args.command == 'list':
        success = manager.list_blogs()
    else:
        print(f"❌ Unknown command: {args.command}")
        success = False
    
    if success:
        print("\n✅ Operation completed successfully!")
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

