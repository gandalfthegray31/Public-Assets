#!/bin/bash

# Blog Management Shell Script
# Quick access to blog management commands

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/blog_manager.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Blog manager script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Function to show help
show_help() {
    echo "🚀 Blog Management System"
    echo ""
    echo "Usage: ./blog.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  add-url <url> [category]     Add blog from Medium URL"
    echo "  add-manual                   Add blog manually (interactive)"
    echo "  download                     Download Medium content for all blogs"
    echo "  convert                      Convert blogs to HTML"
    echo "  full <url> [category]        Complete workflow (add + download + convert)"
    echo "  list                         List all blogs"
    echo "  help                         Show this help"
    echo ""
    echo "Examples:"
    echo "  ./blog.sh add-url 'https://medium.com/@author/blog' 'AWS'"
    echo "  ./blog.sh full 'https://medium.com/@author/blog' 'AWS'"
    echo "  ./blog.sh list"
    echo "  ./blog.sh download"
}

# Main command handling
case "$1" in
    "add-url")
        if [ -z "$2" ]; then
            echo "❌ URL required for add-url command"
            echo "Usage: ./blog.sh add-url <url> [category]"
            exit 1
        fi
        
        if [ -n "$3" ]; then
            python3 "$PYTHON_SCRIPT" add-url --url "$2" --category "$3"
        else
            python3 "$PYTHON_SCRIPT" add-url --url "$2"
        fi
        ;;
    
    "add-manual")
        python3 "$PYTHON_SCRIPT" add-manual
        ;;
    
    "download")
        python3 "$PYTHON_SCRIPT" download
        ;;
    
    "convert")
        python3 "$PYTHON_SCRIPT" convert
        ;;
    
    "full")
        if [ -z "$2" ]; then
            echo "❌ URL required for full workflow command"
            echo "Usage: ./blog.sh full <url> [category]"
            exit 1
        fi
        
        if [ -n "$3" ]; then
            python3 "$PYTHON_SCRIPT" full-workflow --url "$2" --category "$3"
        else
            python3 "$PYTHON_SCRIPT" full-workflow --url "$2"
        fi
        ;;
    
    "list")
        python3 "$PYTHON_SCRIPT" list
        ;;
    
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

