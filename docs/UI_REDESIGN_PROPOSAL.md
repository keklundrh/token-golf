# Token Golf - UI Redesign Proposal

**Version:** 1.0  
**Date:** 2026-09-22  
**Target Audience:** Professional conference attendees (desktop-focused)  
**Design Philosophy:** Modern game UI with professional polish

---

## Executive Summary

This redesign transforms Token Golf from a functional web app into a polished, game-like experience that maintains professional credibility while creating engaging, competitive gameplay. The design emphasizes:

1. **Competitive Focus** - Token counts, ranks, and leaderboards front and center
2. **Clean Information Hierarchy** - Less clutter, more focus on current challenge
3. **Game Feel** - Progress visualization, achievement moments, smooth animations
4. **Professional Polish** - Modern card-based UI, depth, sophisticated color use

---

## Design Principles

### 1. Golf-Inspired Minimalism
- Clean fairway greens as backgrounds
- Strategic use of gold accents for achievement/success
- Navy for trust and professionalism
- Generous whitespace (like a golf course)

### 2. Competitive Visibility
- Token count always visible and emphasized
- Live rank updates
- Par comparison at every step
- Visual feedback on performance (under par = green, over par = warning colors)

### 3. Progressive Disclosure
- Show what's needed now, hide complexity
- Expandable sections for advanced options
- Clear primary actions, subtle secondary actions

### 4. Delightful Interactions
- Smooth transitions (not jarring)
- Micro-animations on success
- Tactile button feedback
- Loading states that entertain

---

## Color Palette Refinement

### Primary Colors
```
Fairway Green:    #4a7c2c  (Primary actions, success)
Championship Gold: #d4af37  (Achievements, highlights)
Professional Navy: #1a2332  (Text, headers)
Crisp White:      #ffffff  (Cards, backgrounds)
```

### Secondary Colors
```
Light Fairway:    #f0f4ec  (Page background)
Sand Trap:        #f5f1e8  (Secondary backgrounds)
Rough Green:      #7d8f69  (Disabled states, borders)
Sky Blue:         #3b82f6  (Info, links)
```

### Semantic Colors
```
Success (Birdie):  #10b981  (Under par)
Warning (Bogey):   #f59e0b  (Over par)
Error (Penalty):   #ef4444  (Errors, failures)
Info (Tip):        #3b82f6  (Helpful information)
```

### Color Usage Rules
- **Green** = Primary actions, success states, completion
- **Gold** = Top rankings (1-3), achievements, special moments
- **Navy** = All body text, headers
- **White/Light** = Backgrounds, cards, clean space
- **Semantic** = Only for their specific meaning (don't use red for branding)

---

## Typography Hierarchy

### Font Stack
```css
Primary: 'Inter', system-ui, sans-serif
Mono:    'JetBrains Mono', 'Fira Code', Consolas, monospace
```

### Size Scale
```
Hero Heading:     text-5xl (48px)  - Page titles, welcome
Section Heading:  text-3xl (30px)  - Major sections
Card Title:       text-2xl (24px)  - Challenge names
Subheading:       text-xl (20px)   - Section labels
Body Large:       text-lg (18px)   - Important body text
Body:             text-base (16px) - Default text
Small:            text-sm (14px)   - Secondary info
Tiny:             text-xs (12px)   - Labels, metadata
```

### Weight Scale
```
Bold:      font-bold (700)    - Headings, emphasis
Semibold:  font-semibold (600) - Subheadings, labels
Medium:    font-medium (500)  - Buttons, CTAs
Regular:   font-normal (400)  - Body text
```

---

## Screen Designs

## 1. Home/Lobby Screen

### Layout Concept
Clean, inviting entry point with clear path to action. Hero section establishes game, CTA gets users playing immediately, leaderboard preview creates FOMO.

### ASCII Mockup
```
╔═══════════════════════════════════════════════════════════════════════════╗
║                          TOKEN GOLF NAVIGATION                            ║
║  ⛳ Token Golf          [Home] [Leaderboard] [How to Play]    [Profile]  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║                     ┌─────────────────────────────┐                      ║
║                     │    ⛳        🏆             │                      ║
║                     │         TOKEN GOLF          │                      ║
║                     └─────────────────────────────┘                      ║
║                                                                           ║
║               Master AI Efficiency Through Competitive Play               ║
║                                                                           ║
║          Just like golf, lower scores win. Craft precise prompts,        ║
║            minimize tokens, and compete for the top spot.                 ║
║                                                                           ║
║   ┌──────────────────────────┐     ┌──────────────────────────┐         ║
║   │   ⛳                     │     │   👤                     │         ║
║   │                          │     │                          │         ║
║   │   START NEW GAME         │     │   CONTINUE GAME          │         ║
║   │                          │     │                          │         ║
║   │ Generate username & play │     │ Sign in to your account  │         ║
║   └──────────────────────────┘     └──────────────────────────┘         ║
║                                                                           ║
║   ╔═══════════════════════════════════════════════════════════╗         ║
║   ║  🏆  TOP PLAYERS - Most Efficient Prompt Engineers        ║         ║
║   ╠═══════════════════════════════════════════════════════════╣         ║
║   ║  🥇  #1  Blue-Oakmont-42         2,547 tokens  [9 holes] ║         ║
║   ║  🥈  #2  Green-Augusta-17        2,891 tokens  [9 holes] ║         ║
║   ║  🥉  #3  Red-Pebble-99           3,102 tokens  [9 holes] ║         ║
║   ╚═══════════════════════════════════════════════════════════╝         ║
║                                                                           ║
║                        [View Full Leaderboard →]                         ║
║                                                                           ║
║   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        ║
║   │  📖              │  │  ✍️              │  │  📊              │        ║
║   │  Read Challenge  │  │  Craft Prompt    │  │  Minimize Tokens │        ║
║   │  Unique AI task  │  │  Efficient solve │  │  Lower is better │        ║
║   └─────────────────┘  └─────────────────┘  └─────────────────┘        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Design Specifications

**Hero Section:**
- Background: Subtle gradient from `golf-fairway` to `white`
- Icons: 96px size, positioned with 1rem gap
- Title: `text-5xl font-bold text-golf-navy` with subtle text shadow
- Subtitle: `text-2xl text-golf-navy-light`
- Description: `text-lg text-gray-600 max-w-3xl`

**CTA Cards:**
- Card: White background, `rounded-2xl shadow-golf-lg` hover: `shadow-gold-lg scale-105`
- Border: 4px solid on hover (green for new game, gold for sign in)
- Icons: 64px, centered above text
- Button text: `text-2xl font-bold`
- Transition: `transition-all duration-300 ease-out`

**Leaderboard Preview:**
- Container: `bg-gradient-to-br from-amber-50 to-yellow-50 rounded-2xl`
- Border: `border-2 border-gold`
- Header: `text-3xl font-bold text-golf-navy` with trophy icon
- Entries: White background cards with gold/silver/bronze left borders
- Trophy emojis: 40px size
- Token count: `text-2xl font-bold text-golf-gold`

**How It Works Cards:**
- Layout: 3-column grid, equal height
- Card: White background, `rounded-xl shadow-md border-2 border-golf-gray-light`
- Icons: 64px centered
- Title: `text-xl font-bold text-golf-navy`
- Description: `text-base text-gray-600`
- Hover: Subtle lift with `hover:shadow-lg hover:-translate-y-1`

---

## 2. Game Screen

### Layout Concept
Focus mode. Challenge takes center stage. Metrics visible but not overwhelming. Clear input area. Instant feedback.

### ASCII Mockup
```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ⛳ Token Golf > Beginner Course > Hole 3                    Blue-Oak-42  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐ ║
║  │ ◄ PREV      ━━━━━━━━━━━━━●●━━━━━━━━━━━━━━━━━━━━━       NEXT ►    │ ║
║  │              Hole 3 of 9  •  3 completed  •  33% done               │ ║
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                           ║
║  ┌──────────────────────────────────────────┐  ┌────────────────────┐   ║
║  │ ╔══════════════════════════════════════╗ │  │ 🏌️ YOUR STATS     │   ║
║  │ ║ 🏌️ Hole 3: String Reversal         ║ │  │                    │   ║
║  │ ╠══════════════════════════════════════╣ │  │ Blue-Oakmont-42    │   ║
║  │ ║ Difficulty: [MEDIUM]  Type: Coding  ║ │  │                    │   ║
║  │ ║ Par: 150 tokens                     ║ │  │ Total: 847 tokens  │   ║
║  │ ╚══════════════════════════════════════╝ │  │ Rank: #5 of 42     │   ║
║  │                                          │  │ Attempts: 12       │   ║
║  │ Challenge:                               │  │                    │   ║
║  │ Create a function that reverses a        │  │ [Status: ⚡ Active]│   ║
║  │ string without using built-in reverse.   │  └────────────────────┘   ║
║  │ Must handle edge cases (empty, single    │                           ║
║  │ char, special characters).               │  ┌────────────────────┐   ║
║  │                                          │  │ 🏆 LEADERBOARD     │   ║
║  │ Success Criteria:                        │  │                    │   ║
║  │ ✓ Handles empty strings                 │  │ 🥇 Green-Aug-17    │   ║
║  │ ✓ Reverses "hello" → "olleh"           │  │    121 tokens      │   ║
║  │ ✓ Handles special chars                 │  │                    │   ║
║  │ ...and 5 more test cases                │  │ 🥈 Red-Pebb-99     │   ║
║  │                                          │  │    138 tokens      │   ║
║  │ ┌──────────────────────────────────────┐ │  │                    │   ║
║  │ │ 📁 Context: string_utils.py          │ │  │ 🥉 Gold-Shin-5     │   ║
║  │ └──────────────────────────────────────┘ │  │    145 tokens      │   ║
║  │                                          │  │                    │   ║
║  ├──────────────────────────────────────────┤  │ 4. Pink-Tor-88     │   ║
║  │ Your Solution                            │  │    152 tokens      │   ║
║  │                                          │  │                    │   ║
║  │ ┌──────────────────────────────────────┐ │  │ 5. YOU ⭐          │   ║
║  │ │ System: You are a helpful coding... │ │  │    158 tokens      │   ║
║  │ └──────────────────────────────────────┘ │  │                    │   ║
║  │                                          │  │ [View All →]       │   ║
║  │ Your Prompt:                             │  └────────────────────┘   ║
║  │ ┌──────────────────────────────────────┐ │                           ║
║  │ │                                      │ │  ┌────────────────────┐   ║
║  │ │  Write a Python function that...    │ │  │ 📊 CHALLENGE STATS │   ║
║  │ │                                      │ │  │                    │   ║
║  │ │                                      │ │  │ Best: 121 tokens   │   ║
║  │ │                                      │ │  │ Avg:  167 tokens   │   ║
║  │ └──────────────────────────────────────┘ │  │ Your: 158 tokens   │   ║
║  │ Estimated: ~142 tokens | Par: 150       │  │                    │   ║
║  │                                          │  │ You're on pace! ✓  │   ║
║  │        [SUBMIT ATTEMPT - Ctrl+Enter]     │  └────────────────────┘   ║
║  └──────────────────────────────────────────┘                           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Design Specifications

**Progress Bar Section:**
- Container: White card, `rounded-xl shadow-md p-4`
- Progress bar: `h-4 rounded-full` gradient from green to gold
- Filled portion: Animated width transition `transition-all duration-500`
- Text: `text-sm font-semibold` with hole count, completion stats
- Navigation buttons: Disabled state uses gray-200, enabled uses golf-green
- Hover state: `scale-105` on enabled buttons

**Challenge Card (Left Column - 60%):**
- Container: White background, `rounded-2xl shadow-lg`
- Header: Dark gradient `bg-gradient-to-r from-golf-navy to-golf-navy-light`
- Title: `text-3xl font-bold text-white`
- Badges: Rounded pills with colored backgrounds
  - Easy: `bg-success`, Medium: `bg-warning`, Hard: `bg-error`
  - Task type: `bg-golf-green`
- Par display: `text-2xl font-bold text-golf-gold` on dark background
- Challenge text: `text-lg text-golf-navy-light leading-relaxed`
- Success criteria: Checkmark icons in golf-green, `text-base`
- Context files: `bg-golf-sand rounded-lg` with file icon

**Input Section:**
- System prompt pill: `bg-golf-navy text-white rounded-lg px-4 py-2`
- Click to edit indicator: `text-golf-gold text-sm`
- Prompt textarea: `border-2 border-golf-gray-light rounded-lg` 
  - Focus: `border-golf-green ring-2 ring-golf-green/20`
- Token estimate: Color-coded
  - Under par: `text-golf-green`
  - Near par (±15%): `text-golf-gold`  
  - Over par: `text-warning`
- Submit button: `bg-golf-green hover:bg-golf-green-dark` full width
  - `text-xl font-bold py-4 rounded-xl shadow-lg`
  - Hover: `scale-105 shadow-gold-lg`
  - Disabled: `opacity-50 cursor-not-allowed`

**Stats Panel (Right Column - 40%):**
- Container: Sticky position, `top-4`
- Individual cards: `bg-white rounded-xl shadow-md p-6 space-y-6`
- Player card: `bg-gradient-to-br from-golf-navy to-golf-navy-light text-white`
- Username: `text-2xl font-bold text-golf-gold`
- Stats: Grid layout, `text-3xl font-bold`
- Leaderboard entries: 
  - Top 3: Gold/silver/bronze medals (40px emojis)
  - Your position: Highlighted with star, `bg-golf-gold/10 border-l-4 border-golf-gold`
  - Tokens: `font-bold text-golf-navy`

---

## 3. Challenge Completion Screen (Modal)

### Layout Concept
Celebration moment! Full-screen modal overlay with stats, rank, and next actions.

### ASCII Mockup
```
╔═══════════════════════════════════════════════════════════════════════════╗
║                          [Darkened Background]                            ║
║                                                                           ║
║         ┌─────────────────────────────────────────────────┐              ║
║         │                                            [×]  │              ║
║         │                  ⛳                             │              ║
║         │                                                 │              ║
║         │            🎉 HOLE COMPLETE! 🎉                │              ║
║         │                                                 │              ║
║         │         Great job on this challenge!            │              ║
║         │                                                 │              ║
║         │  ╔═══════════════════════════════════════╗     │              ║
║         │  ║    Your Performance                   ║     │              ║
║         │  ╠═══════════════════════════════════════╣     │              ║
║         │  ║                                       ║     │              ║
║         │  ║  Attempts:        3                   ║     │              ║
║         │  ║  Total Tokens:    158                 ║     │              ║
║         │  ║  Par:             150                 ║     │              ║
║         │  ║  Score:           +8 (Bogey)          ║     │              ║
║         │  ║                                       ║     │              ║
║         │  ║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║     │              ║
║         │  ║                                       ║     │              ║
║         │  ║  Your Rank:       #5 of 42            ║     │              ║
║         │  ║  Percentile:      88th                ║     │              ║
║         │  ║                                       ║     │              ║
║         │  ╚═══════════════════════════════════════╝     │              ║
║         │                                                 │              ║
║         │           🎊  🏆  ⭐  🎊                       │              ║
║         │                                                 │              ║
║         │  ┌────────────────────┐  ┌─────────────────┐  │              ║
║         │  │                    │  │                 │  │              ║
║         │  │  🏆 VIEW           │  │  ⛳ NEXT        │  │              ║
║         │  │  LEADERBOARD       │  │  CHALLENGE      │  │              ║
║         │  │                    │  │                 │  │              ║
║         │  └────────────────────┘  └─────────────────┘  │              ║
║         │                                                 │              ║
║         └─────────────────────────────────────────────────┘              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Design Specifications

**Modal Overlay:**
- Background: `bg-black/60` (60% opacity black)
- Backdrop blur: `backdrop-blur-sm`
- Centered: `flex items-center justify-center`
- Z-index: `z-50`
- Click outside to close: Yes
- ESC to close: Yes

**Modal Card:**
- Background: White
- Size: `max-w-2xl w-full mx-4`
- Rounded: `rounded-2xl`
- Shadow: `shadow-2xl`
- Padding: `p-8`
- Animation: Scale in from 0.95 to 1.0, fade in

**Header Section:**
- Flag icon: 96px, animated gentle bounce
- Title: `text-4xl font-bold text-golf-green`
- Animation: Success pulse (scale 1.0 to 1.05 and back)
- Confetti emojis: Animated from center outward

**Performance Card:**
- Background: `bg-golf-sand`
- Border: `border-2 border-golf-green` if under par, `border-warning` if over
- Padding: `p-6`
- Rounded: `rounded-xl`
- Stats layout: Two-column grid
- Stats text: `text-xl font-semibold`
- Values: `text-2xl font-bold`
- Score display: Color-coded
  - Eagle/Birdie (under par): `text-golf-green`
  - Par: `text-golf-navy`
  - Bogey+ (over par): `text-warning`

**Rank Display:**
- Large text: `text-4xl font-bold text-golf-gold`
- Percentile: `text-lg text-gray-600`
- Icon if top 10: Trophy emoji 48px

**Action Buttons:**
- Layout: Two-column grid, equal width
- View Leaderboard: `bg-golf-navy hover:bg-golf-navy-light`
- Next Challenge: `bg-golf-gold hover:bg-golf-gold-dark`
- If no next challenge: `bg-gray-200 text-gray-400 cursor-not-allowed`
- Text: `text-xl font-bold text-white`
- Size: `py-4 px-6`
- Icons: 24px inline
- Hover: `scale-105 shadow-lg`

**Close Button:**
- Position: Absolute top-4 right-4
- Style: `text-golf-gray hover:text-golf-navy`
- Size: 32px
- Transition: Smooth color change

---

## 4. Leaderboard Screen

### Layout Concept
Competitive rankings with filtering, stats, and clear visual hierarchy. Podium-style top 3.

### ASCII Mockup
```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ⛳ Token Golf > Leaderboard                                              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║                        🏆 LEADERBOARD 🏆                                 ║
║                See how you stack up against other players                 ║
║                    Remember: Lower scores are better!                     ║
║                                                                           ║
║   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐              ║
║   │    🌍         │  │     ⛳        │  │     🏆        │              ║
║   │ GLOBAL        │  │  PER-HOLE     │  │  MY SESSION   │              ║
║   │ RANKINGS      │  │  RECORDS      │  │               │              ║
║   └───────────────┘  └───────────────┘  └───────────────┘              ║
║                                                                           ║
║  ┌─────────────────────────────────────┐  ┌──────────────────────┐     ║
║  │ ╔═══════════════════════════════╗   │  │  📊 STATISTICS       │     ║
║  │ ║ 🌍 Global Rankings            ║   │  │                      │     ║
║  │ ║ All-time best scores          ║   │  │  Total Players: 127  │     ║
║  │ ╚═══════════════════════════════╝   │  │  Best Score: 2,547   │     ║
║  │                                     │  │  Average: 3,891      │     ║
║  │          🥇                         │  │  Your Rank: #5       │     ║
║  │       Gold Medal                    │  │                      │     ║
║  │   ┌─────────────────────┐           │  │  ┌────────────────┐ │     ║
║  │   │ #1 Blue-Oakmont-42  │           │  │  │ Trophy Key:    │ │     ║
║  │   │ 2,547 tokens        │           │  │  │ 🥇 1st Place   │ │     ║
║  │   │ 9 holes • 27 tries  │           │  │  │ 🥈 2nd Place   │ │     ║
║  │   └─────────────────────┘           │  │  │ 🥉 3rd Place   │ │     ║
║  │                                     │  │  └────────────────┘ │     ║
║  │  🥈                 🥉              │  └──────────────────────┘     ║
║  │  Silver            Bronze           │                               ║
║  │  ┌──────────────┐  ┌──────────────┐│                               ║
║  │  │ #2 Green-17  │  │ #3 Red-99    ││                               ║
║  │  │ 2,891 tokens │  │ 3,102 tokens ││                               ║
║  │  └──────────────┘  └──────────────┘│                               ║
║  │                                     │                               ║
║  │  ─────────────────────────────────  │                               ║
║  │                                     │                               ║
║  │  4.  Pink-Torrey-88     3,247  ✓   │                               ║
║  │  5.  YOU ⭐ Blue-Oak-42  3,458  ✓   │ ← Highlighted                ║
║  │  6.  Teal-Whistling-3   3,502  ✓   │                               ║
║  │  7.  Orange-Kiawah-76   3,615  ✓   │                               ║
║  │  8.  Purple-Bethpage-11 3,788  ✓   │                               ║
║  │  9.  Gray-Pinehurst-55  3,901  ✓   │                               ║
║  │  10. Cyan-Chambers-29   4,012  ✓   │                               ║
║  │                                     │                               ║
║  │         [Load More Rankings →]      │                               ║
║  └─────────────────────────────────────┘                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Design Specifications

**Page Header:**
- Title: `text-5xl font-bold text-golf-navy` centered
- Subtitle: `text-xl text-golf-navy-light`
- Reminder text: `text-sm text-golf-green`
- Spacing: `space-y-4 mb-8`

**View Toggle Buttons:**
- Container: White card, `rounded-xl shadow-md p-4`
- Layout: Flex row, centered, gap-3
- Buttons: `rounded-lg font-semibold px-6 py-3`
- Active state: `bg-golf-green text-white shadow-lg scale-105`
- Inactive state: `bg-white text-golf-green border-2 border-golf-green hover:bg-golf-green/10`
- Icons: 24px emoji before text
- Transition: `transition-all duration-200`

**Podium Display (Top 3):**
- Layout: Three columns with center column elevated
- Card sizes: 
  - Gold (1st): Tallest, `min-h-64`
  - Silver/Bronze (2nd/3rd): Medium height, `min-h-48`
- Backgrounds:
  - Gold: `bg-gradient-to-br from-yellow-50 to-amber-100 border-4 border-gold`
  - Silver: `bg-gradient-to-br from-gray-50 to-slate-100 border-4 border-gray-400`
  - Bronze: `bg-gradient-to-br from-orange-50 to-amber-100 border-4 border-orange-400`
- Medal icons: 64px emoji centered at top
- Username: `text-2xl font-bold`
- Token count: `text-3xl font-bold text-golf-green`
- Metadata: `text-sm text-gray-600`

**Rankings List (4+):**
- Container: White background, divided by thin borders
- Row height: `py-4 px-6`
- Current user: `bg-golf-gold/10 border-l-4 border-golf-gold`
- Rank number: `text-xl font-bold text-gray-600`
- Username: `text-lg font-semibold text-golf-navy`
- Tokens: `text-lg font-bold text-golf-green`
- Completion checkmark: Green checkmark icon if completed
- Hover: `bg-gray-50` slight highlight

**Statistics Panel (Right Sidebar):**
- Container: `bg-white rounded-xl shadow-lg p-6 sticky top-4`
- Title: `text-xl font-bold text-golf-navy`
- Stat cards: Individual `rounded-lg p-4` with colored backgrounds
  - Total players: `bg-green-50 text-golf-green`
  - Best score: `bg-yellow-50 text-golf-gold`
  - Average: `bg-blue-50 text-blue-700`
  - Your rank: `bg-purple-50 text-purple-700`
- Stat value: `text-4xl font-bold`
- Stat label: `text-sm font-medium`

**Load More Button:**
- Style: `bg-golf-green hover:bg-golf-green-dark text-white`
- Text: `text-lg font-semibold`
- Padding: `py-3 px-8`
- Icon: Down arrow, 20px
- Hover: `scale-105 shadow-lg`

---

## Layout System

### Grid Structure
```
Desktop (1280px+):   12-column grid, 24px gap
Tablet (768px+):     8-column grid, 16px gap
Mobile (<768px):     4-column grid, 12px gap
```

### Spacing Scale
```
xs:  0.25rem (4px)   - Tight spacing within components
sm:  0.5rem  (8px)   - Small gaps, inline elements
md:  1rem    (16px)  - Standard spacing
lg:  1.5rem  (24px)  - Section spacing
xl:  2rem    (32px)  - Major sections
2xl: 3rem    (48px)  - Page sections
3xl: 4rem    (64px)  - Hero spacing
```

### Card Shadows
```
Default:  shadow-md     - Standard cards
Elevated: shadow-lg     - Hover states, important cards
Floating: shadow-2xl    - Modals, popovers
Gold:     shadow-gold   - Achievement cards
Green:    shadow-golf   - Primary action cards
```

### Border Radius
```
sm:   0.375rem (6px)   - Small elements (badges)
md:   0.5rem   (8px)   - Buttons, inputs
lg:   0.75rem  (12px)  - Cards
xl:   1rem     (16px)  - Large cards
2xl:  1.5rem   (24px)  - Hero cards
full: 9999px           - Pills, avatar
```

---

## Animations & Transitions

### Micro-interactions

**Button Hover:**
```css
transition: all 200ms ease-out;
hover: scale(1.05) shadow-lg;
active: scale(0.98);
```

**Card Hover:**
```css
transition: all 300ms ease-out;
hover: translateY(-4px) shadow-xl;
```

**Success Pulse:**
```css
@keyframes successPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
animation: successPulse 0.6s ease-in-out;
```

**Loading Spin:**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
animation: spin 1s linear infinite;
```

**Fade In:**
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
animation: fadeIn 0.3s ease-out;
```

**Slide Up:**
```css
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
animation: slideUp 0.4s ease-out;
```

**Confetti Pop:**
```css
@keyframes confetti {
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
}
animation: confetti 1.5s ease-out infinite;
```

### Loading States

**Skeleton Loader:**
```css
background: linear-gradient(
  90deg,
  #f0f0f0 0%,
  #e0e0e0 50%,
  #f0f0f0 100%
);
background-size: 200% 100%;
animation: shimmer 1.5s infinite;

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

**Progress Indicator:**
- Smooth width transition on progress bars
- Color gradient animation for active states
- Pulsing dot for "in progress"

**Spinner:**
```html
<div class="animate-spin h-8 w-8 border-4 border-golf-green border-t-transparent rounded-full"></div>
```

### Page Transitions
- Route changes: 200ms fade
- Modal open/close: 300ms scale + fade
- Tab switches: 250ms slide
- Accordion expand: 300ms height transition

---

## Responsive Breakpoints

### Desktop First Approach
Primary design at 1440px, scale down to tablet and mobile.

### Breakpoints
```
2xl: 1536px  - Large desktop
xl:  1280px  - Desktop (default design target)
lg:  1024px  - Small desktop / landscape tablet
md:  768px   - Tablet
sm:  640px   - Large phone
xs:  <640px  - Phone
```

### Key Responsive Changes

**Game Screen:**
- Desktop (lg+): Two-column (60/40 split)
- Tablet (md): Two-column (55/45 split), smaller fonts
- Mobile (<md): Single column, metrics collapsed/expandable

**Leaderboard:**
- Desktop (lg+): Sidebar + main
- Tablet (md): Stacked layout, sidebar below main
- Mobile (<md): Full-width cards, stats as expandable section

**Home Screen:**
- Desktop (lg+): Multi-column grid for features
- Tablet (md): Two-column grid
- Mobile (<md): Single column stack

### Mobile Specific Adjustments
- Increase touch target sizes (min 44px)
- Simplify navigation to hamburger menu
- Sticky headers for key info
- Bottom sheet modals instead of centered
- Reduce whitespace for content density
- Stack cards vertically
- Collapse secondary information by default

---

## Accessibility Standards

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Body text (navy on white): 14.8:1 (AAA)
- Large text minimum: 4.5:1
- UI components minimum: 3:1
- Interactive elements: Clear focus states

**Focus Indicators:**
```css
:focus-visible {
  outline: 2px solid var(--golf-green);
  outline-offset: 2px;
}
```

**Keyboard Navigation:**
- All interactive elements keyboard accessible
- Skip to main content link
- Tab order follows visual order
- ESC closes modals
- Enter/Space activates buttons
- Arrow keys for navigation where appropriate

**Screen Reader Support:**
- Semantic HTML (header, nav, main, section)
- ARIA labels on icon-only buttons
- ARIA live regions for dynamic updates
- Alt text on decorative images (empty alt="")
- Descriptive link text (no "click here")

**Motion Preferences:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Component Library

### Buttons

**Primary Button:**
```html
<button class="btn-primary">
  Submit Attempt
</button>
```
```css
.btn-primary {
  @apply bg-golf-green hover:bg-golf-green-dark 
         text-white font-semibold 
         px-6 py-3 rounded-lg 
         shadow-md hover:shadow-lg 
         transition-all duration-200 
         hover:scale-105
         disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100;
}
```

**Secondary Button:**
```html
<button class="btn-secondary">
  View Details
</button>
```
```css
.btn-secondary {
  @apply bg-white hover:bg-gray-50 
         text-golf-navy border-2 border-golf-green 
         font-semibold px-6 py-3 rounded-lg 
         shadow-sm hover:shadow-md 
         transition-all duration-200;
}
```

**Gold Button (Achievement):**
```html
<button class="btn-gold">
  Next Challenge
</button>
```
```css
.btn-gold {
  @apply bg-golf-gold hover:bg-golf-gold-dark 
         text-white font-bold 
         px-6 py-3 rounded-lg 
         shadow-gold hover:shadow-gold-lg 
         transition-all duration-200 
         hover:scale-105;
}
```

### Cards

**Standard Card:**
```html
<div class="card">
  <h2 class="card-title">Title</h2>
  <p class="card-body">Content</p>
</div>
```
```css
.card {
  @apply bg-white rounded-xl shadow-md p-6;
}
.card-title {
  @apply text-2xl font-bold text-golf-navy mb-4;
}
.card-body {
  @apply text-base text-golf-navy-light;
}
```

**Stat Card:**
```html
<div class="stat-card">
  <div class="stat-label">Total Tokens</div>
  <div class="stat-value">2,547</div>
</div>
```
```css
.stat-card {
  @apply bg-golf-sand rounded-lg p-4 border-2 border-golf-gray-light;
}
.stat-label {
  @apply text-xs font-semibold text-golf-gray uppercase tracking-wide mb-1;
}
.stat-value {
  @apply text-3xl font-bold text-golf-navy;
}
```

### Badges

**Difficulty Badge:**
```html
<span class="badge badge-easy">Easy</span>
<span class="badge badge-medium">Medium</span>
<span class="badge badge-hard">Hard</span>
```
```css
.badge {
  @apply inline-block px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide;
}
.badge-easy {
  @apply bg-success text-white;
}
.badge-medium {
  @apply bg-warning text-white;
}
.badge-hard {
  @apply bg-error text-white;
}
```

### Form Elements

**Input Field:**
```html
<input type="text" class="input-field" placeholder="Enter text...">
```
```css
.input-field {
  @apply w-full px-4 py-3 
         border-2 border-golf-gray-light rounded-lg 
         focus:border-golf-green focus:ring-2 focus:ring-golf-green/20 
         text-base text-golf-navy 
         transition-all duration-200 
         disabled:bg-gray-100 disabled:cursor-not-allowed;
}
```

**Textarea:**
```html
<textarea class="textarea-field" rows="6"></textarea>
```
```css
.textarea-field {
  @apply input-field resize-y font-mono text-sm;
}
```

### Progress Indicators

**Progress Bar:**
```html
<div class="progress-container">
  <div class="progress-bar" style="width: 33%"></div>
</div>
```
```css
.progress-container {
  @apply w-full bg-golf-gray-light rounded-full h-3 overflow-hidden;
}
.progress-bar {
  @apply bg-gradient-to-r from-golf-green to-golf-gold h-full rounded-full 
         transition-all duration-500 ease-out;
}
```

---

## Implementation Priorities

### Phase 1: Core Screens (Highest Priority)
1. Home page redesign
2. Game screen redesign
3. Completion modal
4. Leaderboard redesign

### Phase 2: Components & Interactions
1. Button styles
2. Card components
3. Form elements
4. Animations

### Phase 3: Polish & Refinement
1. Loading states
2. Error states
3. Empty states
4. Accessibility audit

### Phase 4: Testing & Iteration
1. Browser testing
2. User testing
3. Performance optimization
4. Final polish

---

## Design System Files

### Recommended File Structure
```
/static/css/
  ├── output.css (generated by Tailwind)
  └── custom.css (custom components)

/static/js/
  ├── animations.js
  └── interactions.js

/docs/
  ├── UI_REDESIGN_PROPOSAL.md (this file)
  └── DESIGN_SYSTEM.md (reference guide)
```

---

## Success Metrics

### User Experience Goals
- [ ] Time to first challenge < 30 seconds
- [ ] Challenge completion rate > 80%
- [ ] User confusion rate < 10%
- [ ] Return user rate > 60%

### Performance Goals
- [ ] Page load < 1 second
- [ ] Time to interactive < 2 seconds
- [ ] Animation frame rate 60fps
- [ ] Lighthouse score > 90

### Accessibility Goals
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation works everywhere
- [ ] Screen reader compatible
- [ ] Color contrast ratios meet standards

---

## Next Steps

1. **Review & Approve** - Stakeholder sign-off on design direction
2. **Component Build** - Create reusable component library
3. **Screen Implementation** - Build screens in priority order
4. **User Testing** - Test with 5-10 users, iterate
5. **Production Deploy** - Launch redesigned UI

---

## Appendix: Design Inspiration

**Game-like UIs:**
- Duolingo: Progress paths, achievement celebrations, friendly competition
- Kahoot: Live leaderboards, vibrant colors, game show energy
- Codecademy: Learning paths, progress tracking, skill trees

**Professional Design Systems:**
- Stripe: Clean, modern, trustworthy
- Linear: Fast, polished, attention to detail
- Notion: Flexible, organized, user-friendly

**Key Takeaways:**
- Balance playfulness with professionalism
- Make competition visible but not intimidating
- Celebrate achievements without being cheesy
- Keep information architecture clear
- Use animation purposefully, not gratuitously
