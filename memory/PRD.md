# Travel Phrase Companion - PRD

## Original Problem Statement
Build a Travel Phrase Companion feature as the main app for learn-english-5-11. Users select a destination country and learn common everyday travel phrases with audio pronunciation in BOTH English AND the native language. 

Target languages: Japanese, Korean, Taiwanese, Thai, Vietnamese, Indonesian, Mandarin Chinese, Traditional Chinese, Cantonese, Tamil, Hindi, Sinhala, Urdu, Bengali (14 languages total).

## User Personas
1. **International Traveler** - Someone planning to visit Asian countries who needs quick access to essential phrases
2. **Language Learner** - Users wanting to learn basic conversational phrases in multiple languages
3. **Business Traveler** - Professionals needing common phrases for meetings and daily interactions abroad

## Core Requirements (Static)
- 14 language support with native script display
- 8 phrase categories: Greetings, Shopping, Food & Dining, Directions, Emergency, Social, Transportation, Accommodation
- English + Native language display for each phrase
- Audio pronunciation for both English and native language
- Search functionality to filter phrases
- Category filtering

## What's Been Implemented
### Jan 2026 - MVP Complete
- ✅ Backend API with FastAPI
  - `/api/languages` - Returns 14 languages with code, name, native_name, flag
  - `/api/categories` - Returns 8 phrase categories
  - `/api/phrases` - Returns all 55 phrases for selected language
  - `/api/phrases/{category_id}` - Returns category-specific phrases
  - `/api/tts/generate` - OpenAI TTS integration for audio generation
- ✅ Frontend React App
  - Hero section with travel illustration
  - Language selector dropdown (14 languages)
  - Category grid with icons (Phosphor Icons)
  - Phrase cards with English + Native text
  - Audio playback buttons (English & Native)
  - Search input for filtering phrases
  - Responsive design with Organic & Earthy theme
- ✅ 55 common travel phrases across 8 categories
- ✅ OpenAI TTS integration via Emergent LLM key

## Tech Stack
- **Frontend**: React 19, Phosphor Icons, Framer Motion, Tailwind CSS
- **Backend**: FastAPI, Python 3.x
- **Database**: MongoDB (configured but phrases are hardcoded)
- **TTS**: OpenAI TTS via emergentintegrations library

## Prioritized Backlog

### P0 - Critical
- None currently

### P1 - High Priority
- [ ] Add more phrases per category (currently 6-8 each)
- [ ] Romanization/pronunciation guide for non-Latin scripts
- [ ] Offline audio caching

### P2 - Medium Priority
- [ ] Favorites/bookmarks for phrases
- [ ] Progress tracking
- [ ] Quiz mode for practice
- [ ] Download phrases for offline use

### P3 - Future
- [ ] User accounts
- [ ] Custom phrase additions
- [ ] Speech recognition for pronunciation practice
- [ ] More languages (Arabic, Russian, French, Spanish, etc.)

## Next Tasks
1. Add romanization (phonetic spelling) for all phrases
2. Implement phrase favorites functionality
3. Add more phrases to each category
