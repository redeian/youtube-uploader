# AI-Powered Metadata Generation Guide

## Overview

The YouTube Video Uploader now includes AI-powered metadata generation using Google Generative AI (gemini-2.0-flash-exp model). This feature automatically generates optimized titles, descriptions, and tags for your videos.

## Setup

### 1. Install Dependencies

The required package is already included in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Add your Google Generative AI API key to your `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Google Generative AI API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## How to Use

### Step 1: Upload Your Video

1. Select a video file from your computer
2. The file will be temporarily saved for upload

### Step 2: Generate AI Metadata

1. In the "AI-Powered Metadata Generation" section, describe your video content
2. Provide details about the topic, main points, or what viewers will learn
3. Click the "✨ Generate with AI" button
4. Wait for the AI to generate optimized metadata

### Step 3: Review and Edit

The AI will generate:
- **Title**: Catchy, SEO-optimized title (max 100 characters)
- **Description**: Engaging description with hooks, keywords, and call-to-action (500-1000 characters)
- **Tags**: 5-7 relevant tags merged with your existing tags

You can edit any of the generated content before uploading.

### Step 4: Complete Metadata

Fill in additional settings:
- Category (default: Education)
- Privacy Status (default: Private)
- Recording Date (default: Today)
- Video Language (default: Thai)
- Altered Content declaration
- Paid Promotion checkbox

### Step 5: Upload

Click the "🚀 Upload Video" button to upload your video with all the metadata.

## AI Generation Features

### Title Generation
- Creates attention-grabbing titles
- Includes relevant SEO keywords
- Uses power words to increase click-through rate
- Avoids clickbait while remaining compelling
- Maximum 100 characters

### Description Generation
- Starts with a strong hook to engage viewers
- Includes relevant keywords naturally
- Provides value and sets expectations
- Includes a call-to-action
- Adds relevant hashtags (3-5)
- Formatted with paragraphs for readability
- Mentions key topics covered
- 500-1000 characters

### Tag Generation
- Generates 5-7 relevant tags
- Merges with your existing tags
- Removes duplicates automatically
- Based on video content and category

## Best Practices for Video Context

To get the best AI-generated metadata:

✅ **Good Examples:**
- "A tutorial about Python programming for beginners covering variables, loops, and functions"
- "Travel vlog exploring Tokyo's best street food markets and hidden gems"
- "Productivity tips for remote workers including time management and workspace setup"

❌ **Poor Examples:**
- "A video about coding"
- "My trip to Japan"
- "How to work from home"

The more specific and detailed your video context, the better the AI-generated metadata will be.

## Integration with Upload Workflow

The AI-generated metadata seamlessly integrates with the existing upload workflow:

1. AI-generated values are stored in `st.session_state`
2. Values automatically populate the form fields
3. You can edit them before uploading
4. All metadata (including AI-generated) is sent to YouTube during upload

## Error Handling

If you encounter errors:

### "Google Generative AI API key not configured"
- Add `GEMINI_API_KEY` to your `.env` file
- Restart the application

### "Failed to generate AI metadata"
- Check your internet connection
- Verify your API key is valid
- Check the logs in `logs/youtube_uploader.log` for details

## Technical Details

### AI Model
- Model: `gemini-2.0-flash-exp`
- Fast response times
- Optimized for content generation

### Prompt Engineering
The system uses carefully crafted prompts that:
- Follow YouTube SEO best practices
- Generate engaging, click-worthy content
- Include relevant keywords naturally
- Provide actionable value to viewers

### Tag Merging Logic
```python
existing_tags = [tag.strip() for tag in current_tags.split(',') if tag.strip()]
ai_tags = [tag.strip() for tag in ai_result['tags'].split(',') if tag.strip()]
merged_tags = list(set(existing_tags + ai_tags))  # Removes duplicates
```

## Session State Variables

The AI generator uses these session state variables:
- `video_title`: Stores AI-generated title
- `video_description`: Stores AI-generated description
- `video_tags`: Stores merged tags (existing + AI-generated)

## Customization

You can customize the AI generation by editing `ai_metadata_generator.py`:

- Modify the prompt template in `_build_prompt()` method
- Adjust parsing logic in `_parse_response()` method
- Change the model in `_initialize_model()` method

## Troubleshooting

### Tags Not Updating
- Ensure you clicked "Generate with AI" after entering video context
- Check browser console for JavaScript errors
- Verify the API key is correct

### Poor Quality Results
- Provide more detailed video context
- Specify your video category before generating
- Include existing tags to guide the AI

### Slow Generation
- Check your internet connection
- The AI model may take 5-15 seconds to generate metadata
- Large prompts may take longer

## Future Enhancements

Potential improvements:
- Generate thumbnails using AI
- Suggest optimal upload times
- Analyze video content directly (video-to-text)
- Multi-language support for descriptions
- A/B testing for titles

## Support

For issues or questions:
1. Check the logs in `logs/youtube_uploader.log`
2. Review the troubleshooting section above
3. Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
