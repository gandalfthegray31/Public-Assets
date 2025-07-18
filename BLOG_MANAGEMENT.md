# Blog Management for Public-Assets Repository

This document provides instructions on how to manage blog content in the Public-Assets repository.

## Directory Structure

The blog content is organized as follows:

- `Blogs/index.json`: Contains metadata for all blog posts
- `Blogs/allBlogs/{blog-id}/`: Individual blog directories
  - `blog.json`: Full blog content and metadata
  - Image files: Blog-specific images

## Adding New Blogs

There are several ways to add new blogs to the repository:

### Method 1: Manual Addition (Recommended for most cases)

Run the interactive script:

```bash
python add_blog_manual.py
```

This script will:
1. Prompt you for blog details (title, author, category, etc.)
2. Open your default text editor to enter the blog content in Markdown format
3. Create the necessary files and update the index.json

### Method 2: From URL (Experimental)

If you have a blog post URL (e.g., Medium), you can try to import it:

```bash
python add_blog_from_url.py --url https://medium.com/@author/blog-title-123456 --category "AWS Architecture"
```

Note: This method may not work perfectly for all blog platforms due to differences in HTML structure.

### Method 3: Manual File Creation

1. Create a directory for your blog: `Blogs/allBlogs/{blog-id}/`
2. Create a `blog.json` file with the following structure:

```json
{
  "id": "your-blog-id",
  "title": "Your Blog Title",
  "excerpt": "A short description of your blog",
  "content": "# Your Blog Title\n\nYour blog content in Markdown format...",
  "author": "Your Name",
  "publishedDate": "2024-07-18",
  "readTime": "5 min read",
  "tags": ["AWS", "Category"],
  "mediumUrl": "https://medium.com/@author/blog-title-123456",
  "image": "allBlogs/your-blog-id/image.svg",
  "category": "AWS Category"
}
```

3. Add your blog image to the directory
4. Update `Blogs/index.json` to include your blog metadata

## Adding Custom Images to Blogs

To add or update an image for an existing blog:

```bash
python add_blog_image.py --id your-blog-id --image /path/to/your/image.svg
```

This will:
1. Copy the image to the blog's directory
2. Update the image references in both blog.json and index.json

## Best Practices

1. **Blog IDs**: Use kebab-case for blog IDs (e.g., `serverless-data-pipelines`)
2. **Images**: Prefer SVG format for blog images for better scaling
3. **Content**: Write blog content in Markdown format
4. **Categories**: Try to use existing categories for consistency
5. **Medium URLs**: Always include Medium URLs when available for cross-referencing

## Troubleshooting

If you encounter issues:

1. Check that the blog ID is unique and properly formatted
2. Ensure all required fields are present in both blog.json and index.json
3. Verify that image paths are correct and relative to the repository root
4. Make sure the JSON files are valid (no syntax errors)

## Script Dependencies

The Python scripts require the following packages:

```bash
pip install requests beautifulsoup4
```
