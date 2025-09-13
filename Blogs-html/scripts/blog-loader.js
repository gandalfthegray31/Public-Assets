// Blog loader script for dynamic content loading
class BlogLoader {
    constructor() {
        this.blogs = [];
        this.init();
    }

    async init() {
        try {
            await this.loadBlogs();
            this.renderBlogGrid();
        } catch (error) {
            console.error('Error loading blogs:', error);
            this.showError();
        }
    }

    async loadBlogs() {
        // Load the blog index
        const response = await fetch('../Blogs/index.json');
        if (!response.ok) {
            throw new Error('Failed to load blog index');
        }
        this.blogs = await response.json();
    }

    renderBlogGrid() {
        const blogGrid = document.getElementById('blog-grid');
        if (!blogGrid) return;

        blogGrid.innerHTML = this.blogs.map(blog => this.createBlogCard(blog)).join('');
        
        // Add click handlers
        document.querySelectorAll('.blog-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                const blogId = card.dataset.blogId;
                this.loadBlogPost(blogId);
            });
        });
    }

    createBlogCard(blog) {
        const publishedDate = new Date(blog.publishedDate).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        return `
            <div class="blog-card" data-blog-id="${blog.id}">
                <img src="../Blogs/${blog.coverImage}" alt="${blog.title}" class="blog-image" onerror="this.style.display='none'">
                <div class="blog-content">
                    <div class="blog-meta">
                        <span class="blog-category">${blog.category}</span>
                        <span class="blog-date">${publishedDate}</span>
                    </div>
                    <h2 class="blog-title">${blog.title}</h2>
                    <p class="blog-excerpt">${blog.excerpt}</p>
                    <div class="blog-footer">
                        <span class="read-time">2 min read</span>
                        <span class="read-more">Read more →</span>
                    </div>
                </div>
            </div>
        `;
    }

    async loadBlogPost(blogId) {
        try {
            const response = await fetch(`../Blogs/allBlogs/${blogId}/blog.json`);
            if (!response.ok) {
                throw new Error('Blog post not found');
            }
            const blog = await response.json();
            this.renderBlogPost(blog);
        } catch (error) {
            console.error('Error loading blog post:', error);
            this.showError('Blog post not found');
        }
    }

    renderBlogPost(blog) {
        const publishedDate = new Date(blog.publishedDate).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Create blog post HTML
        const blogPostHTML = `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>${blog.title} - Solutions GSI</title>
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
                                <h1 class="blog-post-title">${blog.title}</h1>
                                <div class="blog-post-meta">
                                    <span class="author">By ${blog.author}</span>
                                    <span class="date">${publishedDate}</span>
                                    <span class="read-time">${blog.readTime || '2 min read'}</span>
                                </div>
                                ${blog.image ? `<img src="../Blogs/${blog.image}" alt="${blog.title}" class="blog-post-image">` : ''}
                            </header>
                            
                            <div class="blog-content">
                                ${this.convertMarkdownToHTML(blog.content)}
                            </div>
                            
                            ${blog.tags && blog.tags.length > 0 ? `
                                <div class="blog-tags">
                                    ${blog.tags.map(tag => `<span class="blog-tag">${tag}</span>`).join('')}
                                </div>
                            ` : ''}
                            
                            ${blog.mediumUrl ? `
                                <div style="text-align: center; margin: 2rem 0;">
                                    <a href="${blog.mediumUrl}" target="_blank" class="blog-tag" style="background: var(--primary-color); color: white; padding: 0.75rem 1.5rem; text-decoration: none;">
                                        Read on Medium →
                                    </a>
                                </div>
                            ` : ''}
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
            </html>
        `;

        // Open in new window or replace current content
        const newWindow = window.open('', '_blank');
        newWindow.document.write(blogPostHTML);
        newWindow.document.close();
    }

    convertMarkdownToHTML(markdown) {
        // Simple markdown to HTML converter
        let html = markdown
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Line breaks
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');

        // Wrap in paragraphs
        html = '<p>' + html + '</p>';
        
        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p><br><\/p>/g, '');
        
        return html;
    }

    showError(message = 'Failed to load blogs') {
        const blogGrid = document.getElementById('blog-grid');
        if (blogGrid) {
            blogGrid.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                    <p>${message}</p>
                    <button onclick="location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Retry
                    </button>
                </div>
            `;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BlogLoader();
});
