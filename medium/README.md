# Medium Articles Download

This folder contains downloaded Medium articles with clean HTML content and images that you can style with your own CSS.

## 📁 Structure

Each article has its own folder with the following structure:
```
{article-id}/
├── article.html          # Clean HTML content
├── images/               # Downloaded images
│   ├── image_001.png
│   ├── image_002.jpg
│   └── ...
└── metadata.json         # Article metadata
```

## 📊 Download Summary

- **Total Articles**: 11
- **Downloaded**: 11 ✅
- **Failed**: 0 ❌
- **Download Date**: 2025-09-13

## 📋 Available Articles

1. **Building a Personalized AI Co-Pilot for Automotive: A Complete AWS Architecture Guide**
   - Folder: `building-a-personalized-ai-co-pilot-for-automotive-a-complete-aws-architecture-guide/`
   - Images: 1

2. **Petabyte-Scale Legacy-to-AWS: A Serverless Lakehouse You Can Actually Run**
   - Folder: `petabyte-scale-legacy-to-aws-a-serverless-lakehouse-you-can-actually-run/`
   - Images: 1

3. **From Phone Call to AI-Powered Scoring: How to Screen Candidates' Speaking Skills with AWS Serverless**
   - Folder: `from-phone-call-to-ai-powered-scoring-how-to-screen-candidates-speaking-skills-with-aws/`
   - Images: 1

4. **Ship Happens: How to Build a Real-Time Sensitive Cargo Tracking System with AWS, Starlink, and Off-the-Shelf IoT**
   - Folder: `Ship-Happens-How-to-Build-a-Real-Time-Sensitive-Cargo-Tracking-System-with-AWS-Starlink-and-Off-the-/`
   - Images: 1

5. **Build Production-Ready GenAI Apps in Days: A Deep Dive into AWS's "Generative AI Application Builder"**
   - Folder: `Build-Production-Ready-GenAI-Apps-in-Days_-A-Deep-Dive-into-AWSs-GAAB/`
   - Images: 1

6. **Building a Zero-Hardware Fleet-Telemetry Pipeline with Connected Mobility Solution (CMS) on AWS**
   - Folder: `building-a-zero-hardware-fleet-telemetry-pipeline-with-connected-mobility-solution-cms-on-aws/`
   - Images: 1

7. **Rein in Your R&D Spend with Innovation Sandbox on AWS**
   - Folder: `innovation-sandbox-aws-rd-spend/`
   - Images: 1

8. **Your Brand New FAQ Whisperer: QnABot on AWS**
   - Folder: `qnabot-aws-faq-whisperer/`
   - Images: 1

9. **From Raw Events to Real-Time Insight: Building Serverless Data Pipelines on AWS**
   - Folder: `serverless-data-pipelines-real-time-insights/`
   - Images: 1

10. **How to Create a WMS Web Map Service Using AWS S3**
    - Folder: `wms-web-map-service-aws-s3/`
    - Images: 1

11. **Kick-start Your Connected Vehicle Journey with AWS Solutions**
    - Folder: `connected-vehicle-aws-journey/`
    - Images: 1

## 🎨 HTML Content Features

Each `article.html` file contains:

- **Clean HTML structure** - No Medium-specific classes or IDs
- **Responsive design** - Mobile-friendly layout
- **Local image references** - All images point to local `images/` folder
- **Semantic markup** - Proper heading hierarchy and structure
- **Inline CSS** - Basic styling included for immediate viewing

## 📄 Metadata

Each `metadata.json` file contains:
```json
{
  "original_url": "https://medium.com/...",
  "title": "Article Title",
  "author": "Author Name",
  "pub_date": "Publication Date",
  "read_time": "Reading Time",
  "tags": ["tag1", "tag2"],
  "downloaded_at": "2025-09-13T08:53:25.359964",
  "image_count": 1
}
```

## 🔧 How to Use

### View Articles
Open any `article.html` file in your web browser to view the content with basic styling.

### Custom Styling
Replace the inline CSS in `article.html` files with your own stylesheet:
```html
<link rel="stylesheet" href="your-custom-styles.css">
```

### Integration
Use the clean HTML content in your website by:
1. Copying the HTML from `article.html`
2. Updating image paths to match your site structure
3. Applying your own CSS styling

## 🔄 Regenerating Content

To download fresh content from Medium:

```bash
cd /Users/saif/Projects/Public-Assets
python3 download_medium_articles.py
```

This will:
- Download all articles from the blog index
- Extract clean HTML content
- Download and organize images
- Update metadata files

## 📝 Notes

- **Image Processing**: Some images may not have `src` attributes (lazy loading) and are skipped
- **Content Extraction**: The script extracts the main article content and removes Medium-specific elements
- **Rate Limiting**: 2-second delay between downloads to be respectful to Medium
- **Error Handling**: Failed downloads are logged but don't stop the process

## 🛠️ Technical Details

- **HTML Parser**: BeautifulSoup4
- **HTTP Client**: Requests
- **Image Formats**: PNG, JPG, JPEG
- **Character Encoding**: UTF-8
- **File Naming**: Sanitized for filesystem compatibility

## 📞 Support

For issues or questions about the download process, check the main project documentation or the Python script source code.
