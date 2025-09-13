#!/bin/bash

# Blog HTML Regeneration Script
# This script converts all blog markdown content to HTML with Medium-style formatting

echo "🔄 Regenerating blog HTML files..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Run the conversion script
python3 convert_blogs_to_html.py

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Blog HTML files regenerated successfully!"
    echo ""
    echo "📁 Files created in: Blogs-html/"
    echo "🌐 Open Blogs-html/index.html in your browser to view the blogs"
    echo ""
    echo "📊 Summary:"
    echo "   - Main index: Blogs-html/index.html"
    echo "   - Individual posts: Blogs-html/posts/"
    echo "   - Styling: Blogs-html/styles/medium-style.css"
else
    echo ""
    echo "❌ Error occurred during conversion. Check the output above for details."
    exit 1
fi
