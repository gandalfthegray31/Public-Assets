# Public-Assets Blog Management System

A comprehensive system for managing blog content from Medium URLs to your website with clean HTML output and Medium-inspired styling.

## 🚀 Quick Start

### Using the Shell Script (Easiest)
```bash
# Add blog from Medium URL with complete workflow
./blog.sh full "https://medium.com/@author/blog-title" "AWS"

# List all blogs
./blog.sh list

# Download Medium content for all blogs
./blog.sh download

# Convert blogs to HTML
./blog.sh convert
```

### Using Python Scripts Directly
```bash
# Master script with all commands
python3 blog_manager.py full-workflow --url "https://medium.com/@author/blog-title" --category "AWS"

# Individual scripts
python3 add_blog_from_url.py --url "https://medium.com/@author/blog-title" --category "AWS"
python3 download_medium_articles.py
python3 convert_blogs_to_html.py
```

## 📁 What You Get

### 1. Blog Structure
```
Blogs/
├── index.json                                    # Blog index
├── allBlogs/                                     # Individual blogs
│   ├── blog-slug/
│   │   ├── blog.json                            # Blog metadata
│   │   ├── cover-image.svg                      # Cover image
│   │   └── medium/                              # Medium content
│   │       ├── article.html                     # Clean HTML
│   │       ├── images/                          # Downloaded images
│   │       └── metadata.json                    # Medium metadata
└── Blogs-html/                                  # Generated HTML
    ├── index.html                               # Main listing
    ├── posts/                                   # Individual pages
    └── styles/medium-style.css                  # Medium styling
```

### 2. Generated Assets
- **Clean HTML content** from Medium articles
- **Downloaded images** organized locally
- **Medium-inspired styling** for your website
- **Responsive blog grid** layout
- **Complete metadata** for each article

## 🛠️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `blog.sh` | **Shell interface** (recommended) | `./blog.sh <command>` |
| `blog_manager.py` | **Master Python script** | `python3 blog_manager.py <command>` |
| `add_blog_from_url.py` | Add blog from Medium URL | `python3 add_blog_from_url.py --url <url>` |
| `download_medium_articles.py` | Download Medium content | `python3 download_medium_articles.py` |
| `convert_blogs_to_html.py` | Convert to HTML | `python3 convert_blogs_to_html.py` |
| `add_blog_manual.py` | Add blog manually | `python3 add_blog_manual.py` |
| `add_blog_image.py` | Manage images | `python3 add_blog_image.py --id <id> --image <path>` |

## 🎯 Common Workflows

### Add New Blog from Medium
```bash
# Complete workflow (recommended)
./blog.sh full "https://medium.com/@author/blog-title" "AWS"

# Or step by step
./blog.sh add-url "https://medium.com/@author/blog-title" "AWS"
./blog.sh download
./blog.sh convert
```

### Manage Existing Blogs
```bash
# List all blogs
./blog.sh list

# Download fresh Medium content
./blog.sh download

# Regenerate HTML
./blog.sh convert
```

### Add Blog Manually
```bash
# Interactive mode
python3 add_blog_manual.py
```

## 📋 Current Status

✅ **11 blogs** successfully managed  
✅ **All Medium content** downloaded  
✅ **HTML conversion** working  
✅ **Medium styling** applied  
✅ **Image management** functional  

## 🔧 Requirements

- Python 3.6+
- Required packages: `requests`, `beautifulsoup4`
- Install with: `pip install requests beautifulsoup4`

## 📚 Documentation

- **Complete guide**: `BLOG_MANAGEMENT.md`
- **Career roles**: `career/` folder
- **HTML output**: `Blogs-html/` folder

## 🎨 Features

- **Medium-style design** with clean typography
- **Responsive layout** for all devices
- **Image optimization** and local storage
- **SEO-friendly** HTML structure
- **Cross-platform** filename handling
- **Error handling** and validation
- **Rate limiting** for Medium requests

## 🚨 Troubleshooting

### Common Issues
1. **Colon in filenames**: Fixed automatically
2. **Missing Medium content**: Run `./blog.sh download`
3. **HTML not generated**: Run `./blog.sh convert`
4. **Image not loading**: Check image paths

### Get Help
```bash
# Show help for shell script
./blog.sh help

# Show help for Python script
python3 blog_manager.py --help
```

## 🎯 Next Steps

1. **Add your first blog**: `./blog.sh full "https://medium.com/@author/blog" "AWS"`
2. **Check the results**: Open `Blogs-html/index.html` in your browser
3. **Customize styling**: Edit `Blogs-html/styles/medium-style.css`
4. **Integrate with your site**: Use the generated HTML files

## 📞 Support

For detailed documentation, see `BLOG_MANAGEMENT.md` or run `./blog.sh help`.

---

**Ready to manage your blogs efficiently!** 🚀

