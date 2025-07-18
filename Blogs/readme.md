# Blog Content Repository

This directory contains all blog posts and related assets for the SolutionGSI website.

## Structure

- `index.json`: Contains metadata for all blog posts
- `allBlogs/{blog-id}/`: Individual blog directories
  - `blog.json`: Full blog content and metadata
  - Image files: Blog-specific images

## Adding New Blogs

1. Create a new directory under `allBlogs/` with a unique blog ID
2. Add a `blog.json` file with the blog content and metadata
3. Add any images to the blog directory
4. Update `index.json` with the blog metadata

## Format

Blog content is stored in Markdown format within the `content` field of each `blog.json` file.
