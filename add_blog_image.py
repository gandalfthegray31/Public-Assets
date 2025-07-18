#!/usr/bin/env python3
"""
Blog Image Adder for Public-Assets Repository

This script helps you add a custom image to an existing blog in the Public-Assets repository.

Usage:
    python add_blog_image.py --id <blog_id> --image <image_path>

Example:
    python add_blog_image.py --id serverless-data-pipelines --image ~/Downloads/pipeline-diagram.svg
"""

import argparse
import json
import os
import shutil
import sys


def update_blog_image(blog_id, image_path):
    """Update the image for a blog post."""
    blogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Blogs')
    blog_dir = os.path.join(blogs_dir, 'allBlogs', blog_id)
    
    # Check if blog exists
    if not os.path.exists(blog_dir):
        print(f"Error: Blog with ID '{blog_id}' not found.")
        return False
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found.")
        return False
    
    # Get image filename
    image_filename = os.path.basename(image_path)
    dest_image_path = os.path.join(blog_dir, image_filename)
    
    # Copy image
    shutil.copy2(image_path, dest_image_path)
    
    # Update blog.json
    blog_json_path = os.path.join(blog_dir, 'blog.json')
    if os.path.exists(blog_json_path):
        with open(blog_json_path, 'r') as f:
            blog_data = json.load(f)
        
        # Update image path
        relative_image_path = f"allBlogs/{blog_id}/{image_filename}"
        blog_data['image'] = relative_image_path
        
        with open(blog_json_path, 'w') as f:
            json.dump(blog_data, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    # Update index.json
    index_path = os.path.join(blogs_dir, 'index.json')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        # Find and update blog entry
        for entry in index_data:
            if entry.get('id') == blog_id:
                entry['coverImage'] = relative_image_path
                break
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    print(f"Image '{image_filename}' successfully added to blog '{blog_id}'")
    print(f"Image path: {dest_image_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Add custom image to a blog in Public-Assets repository')
    parser.add_argument('--id', required=True, help='ID of the blog')
    parser.add_argument('--image', required=True, help='Path to the image file')
    
    args = parser.parse_args()
    
    if update_blog_image(args.id, args.image):
        print("Image update completed successfully.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
