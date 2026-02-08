# Blog Management System

This document explains the complete blog management system for the Public-Assets repository. The system consists of several Python scripts that work together to manage blog content from Medium URLs to your website.

## 🚀 Quick Start

### Master Script (Recommended)
Use the `blog_manager.py` script for most operations:

```bash
# Add blog from URL and download Medium content
python blog_manager.py full-workflow --url "https://medium.com/@author/blog-title" --category "AWS"

# List all blogs
python blog_manager.py list

# Download Medium content for all existing blogs
python blog_manager.py download

# Convert all blogs to HTML
python blog_manager.py convert
```

## 📁 Script Overview

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `blog_manager.py` | **Master script** - Unified interface for all operations | `python blog_manager.py <command>` |
| `add_blog_from_url.py` | Add blog from Medium URL | `python add_blog_from_url.py --url <url>` |
| `download_medium_articles.py` | Download Medium HTML content | `python download_medium_articles.py` |
| `convert_blogs_to_html.py` | Convert blogs to HTML with Medium styling | `python convert_blogs_to_html.py` |

### Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `add_blog_manual.py` | Add blog manually (interactive) | `python add_blog_manual.py` |
| `add_blog_image.py` | Add/update image for existing blog | `python add_blog_image.py --id <id> --image <path>` |

## 🎯 Complete Workflow

### 1. Adding a New Blog from Medium URL

**Option A: Using Master Script (Recommended)**
```bash
# Complete workflow: add + download + convert
python blog_manager.py full-workflow \
  --url "https://medium.com/@author/blog-title" \
  --category "AWS" \
  --image "/path/to/custom-image.svg"
```

**Option B: Step by Step**
```bash
# Step 1: Add blog from URL
python add_blog_from_url.py \
  --url "https://medium.com/@author/blog-title" \
  --category "AWS"

# Step 2: Download Medium HTML content
python download_medium_articles.py

# Step 3: Convert to HTML with Medium styling
python convert_blogs_to_html.py
```

### 2. Adding a Blog Manually

```bash
# Interactive mode - script will prompt for all details
python add_blog_manual.py
```

### 3. Managing Existing Blogs

```bash
# List all blogs
python blog_manager.py list

# Add/update image for existing blog
python add_blog_image.py --id "blog-id" --image "/path/to/image.svg"

# Download Medium content for all blogs
python download_medium_articles.py

# Convert all blogs to HTML
python convert_blogs_to_html.py
```

## 📂 File Structure

After running the scripts, your blog structure will look like this:

```
Blogs/
├── index.json                                    # Blog index
├── allBlogs/                                     # Individual blog folders
│   ├── blog-slug-1/
│   │   ├── blog.json                            # Blog metadata
│   │   ├── cover-image.svg                      # Cover image
│   │   └── medium/                              # Medium content
│   │       ├── article.html                     # Clean HTML content
│   │       ├── images/                          # Downloaded images
│   │       │   └── image_001.png
│   │       └── metadata.json                    # Medium metadata
│   └── blog-slug-2/
│       └── ...
└── Blogs-html/                                  # Generated HTML files
    ├── index.html                               # Main blog listing
    ├── posts/                                   # Individual HTML files
    │   ├── blog-slug-1.html
    │   └── blog-slug-2.html
    └── styles/
        └── medium-style.css                     # Medium-inspired styling
```

## 🛠️ Script Details

### `blog_manager.py` - Master Script

**Commands:**
- `add-url` - Add blog from Medium URL
- `add-manual` - Add blog manually (interactive)
- `add-image` - Add/update image for existing blog
- `download` - Download Medium HTML content for all blogs
- `convert` - Convert blogs to HTML with Medium styling
- `full-workflow` - Complete workflow (add + download + convert)
- `list` - List all blogs

**Examples:**
```bash
# Add blog from URL
python blog_manager.py add-url --url "https://medium.com/@author/blog" --category "AWS"

# Add blog manually
python blog_manager.py add-manual

# Download Medium content
python blog_manager.py download

# Convert to HTML
python blog_manager.py convert

# Full workflow
python blog_manager.py full-workflow --url "https://medium.com/@author/blog"

# List all blogs
python blog_manager.py list
```

### `add_blog_from_url.py` - URL Importer

**Purpose:** Extracts blog information from Medium URLs and creates the blog structure.

**Usage:**
```bash
python add_blog_from_url.py --url <medium_url> [--id <blog_id>] [--category <category>]
```

**Features:**
- Extracts title, content, author, and publish date from Medium
- Generates blog ID from title if not provided
- Creates blog.json and updates index.json
- Handles image placement
- Sanitizes filenames for cross-platform compatibility

### `download_medium_articles.py` - Medium Content Downloader

**Purpose:** Downloads clean HTML content and images from Medium articles.

**Usage:**
```bash
python download_medium_articles.py
```

**Features:**
- Downloads all blogs with Medium URLs from index.json
- Extracts clean HTML content (removes Medium-specific elements)
- Downloads and organizes images locally
- Creates medium subfolder in each blog directory
- Generates metadata.json for each article
- Handles rate limiting (2-second delays)

### `convert_blogs_to_html.py` - HTML Converter

**Purpose:** Converts blog markdown content to HTML with Medium-style formatting.

**Usage:**
```bash
python convert_blogs_to_html.py
```

**Features:**
- Converts markdown content to HTML
- Applies Medium-inspired CSS styling
- Creates responsive blog grid layout
- Generates individual HTML files for each blog
- Handles image references and formatting

### `add_blog_manual.py` - Manual Blog Creator

**Purpose:** Interactive script to add blogs manually.

**Usage:**
```bash
python add_blog_manual.py
```

**Features:**
- Interactive prompts for all blog details
- Opens default editor for content writing
- Generates blog structure automatically
- Updates index.json

### `add_blog_image.py` - Image Manager

**Purpose:** Add or update images for existing blogs.

**Usage:**
```bash
python add_blog_image.py --id <blog_id> --image <image_path>
```

**Features:**
- Updates blog.json with new image path
- Updates index.json with new cover image
- Copies image to blog directory

## 🎨 Output Files

### HTML Output (`Blogs-html/`)

- **`index.html`** - Main blog listing page with responsive grid
- **`posts/*.html`** - Individual blog post pages
- **`styles/medium-style.css`** - Medium-inspired CSS styling

### Medium Content (`Blogs/allBlogs/*/medium/`)

- **`article.html`** - Clean HTML content from Medium
- **`images/`** - Downloaded images from Medium
- **`metadata.json`** - Medium article metadata

## 🔧 Configuration

### Environment Variables

No environment variables are required. All scripts use relative paths.

### Dependencies

```bash
pip install requests beautifulsoup4
```

### File Permissions

Ensure the scripts have execute permissions:
```bash
chmod +x *.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Colon in folder names**: Fixed automatically by filename sanitization
2. **Missing Medium content**: Run `download_medium_articles.py`
3. **Image not loading**: Check image paths in blog.json
4. **HTML not generated**: Run `convert_blogs_to_html.py`

### Error Messages

- **"Blog not found"**: Check blog ID exists in index.json
- **"Image not found"**: Verify image file path
- **"Medium URL not found"**: Check if blog has mediumUrl in index.json
- **"Failed to extract content"**: Medium page structure may have changed

### Debug Mode

For detailed logging, modify the scripts to add more print statements or use Python's logging module.

## 📈 Best Practices

1. **Use the master script** (`blog_manager.py`) for most operations
2. **Run full workflow** for new blogs to get complete setup
3. **Check blog list** regularly to see what's available
4. **Keep images organized** in the blog directories
5. **Update index.json** manually if needed for special cases

## 🔄 Automation

### Shell Scripts

Create shell scripts for common workflows:

```bash
#!/bin/bash
# add_new_blog.sh
python blog_manager.py full-workflow --url "$1" --category "$2"
```

### Cron Jobs

Set up cron jobs for regular updates:

```bash
# Download Medium content daily at 2 AM
0 2 * * * cd /path/to/Public-Assets && python download_medium_articles.py
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Check file permissions and paths
4. Review the script output for error messages

## 🎯 Summary

The blog management system provides a complete workflow from Medium URLs to your website:

1. **Add blogs** from Medium URLs or manually
2. **Download clean content** from Medium
3. **Convert to HTML** with beautiful styling
4. **Manage images** and metadata
5. **Generate website-ready** content

Use `blog_manager.py` as your primary interface for all blog management tasks!