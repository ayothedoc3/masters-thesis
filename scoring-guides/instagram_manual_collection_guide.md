# Instagram Manual Data Collection Guide

## Before You Start

**Time estimate:** 45-60 minutes for 50 items
**What you need:**
- Your master spreadsheet open (rows IG-01 to IG-50)
- A browser (Chrome incognito recommended)
- Instagram account logged in (Instagram limits search without login)
- Phone nearby as backup if desktop blocks results

---

## Setup (2 minutes)

1. Open Chrome > New Incognito Window (Ctrl+Shift+N)
2. Go to `https://www.instagram.com`
3. Log in with your account (or a secondary/throwaway account)
4. Set the spreadsheet to the IG-01 row so you're ready to enter data

---

## Collection Process (repeat for each of 5 search terms)

### Search Terms & Row Assignments

| Search Term | Instagram Rows | Item IDs |
|---|---|---|
| "how to start exercising" | Rows for IG-01 to IG-10 | IG-01 through IG-10 |
| "best exercises to lose weight" | Rows for IG-11 to IG-20 | IG-11 through IG-20 |
| "strength training for beginners" | Rows for IG-21 to IG-30 | IG-21 through IG-30 |
| "physical activity guidelines" | Rows for IG-31 to IG-40 | IG-31 through IG-40 |
| "home workout routine" | Rows for IG-41 to IG-50 | IG-41 through IG-50 |

---

### Step-by-Step for Each Search Term

#### Step 1: Search (30 seconds)
1. Click the **Search** icon (magnifying glass) in the left sidebar
2. Type the search term exactly as written (e.g., `how to start exercising`)
3. Instagram will show tabs: **Top**, **Accounts**, **Reels**, **Tags**, etc.
4. Click **"Top"** or **"Reels"** tab (these give the most relevant PA content)
   - Prefer **Reels** if available — this is where most fitness content lives
   - If Reels gives less than 10 results, supplement from **Top**

#### Step 2: Record the top 10 results (8-9 minutes per term)

For each of the 10 results, record in this order:

**A. Get the URL (15 sec)**
- Click on the post/reel to open it
- Click the three dots (**...**) menu > **Copy link**
- Paste into the **URL** column in your spreadsheet
- Alternative: look at the browser URL bar — it will show `instagram.com/reel/XXXXX/` or `instagram.com/p/XXXXX/`

**B. Title/Caption (15 sec)**
- Copy the first 1-2 sentences of the caption
- Paste into the **Title_Caption** column
- If no caption or just emojis, write "No caption" or copy the emojis

**C. Creator Name (10 sec)**
- Copy the username displayed above the post (e.g., @fitnesswithamy)
- Paste into the **Creator_Name** column

**D. Creator Credentials (30 sec)**
- Click the creator's username to visit their profile
- Read their **bio** — look for:
  - "MD", "PT", "DPT", "RD", "CSCS", "CPT", "NASM", "ACE certified"
  - "Doctor", "Physiotherapist", "Nutritionist", "Certified trainer"
  - Any university or medical affiliation
  - Verified badge (blue checkmark)
- Copy relevant credentials into **Creator_Credentials** column
- If none found, write "None stated"

**E. Date Posted (5 sec)**
- On the post, look for the date below the caption or below the likes count
- It may show "3 days ago", "2w", "March 15, 2025", etc.
- Enter the actual date or approximate date into **Date_Posted**
- For relative dates, calculate the actual date from today

**F. Engagement Metrics (15 sec)**
- **Views:** Shown on Reels (e.g., "1.2M views"). For image posts, this may not exist — leave blank
- **Likes:** Click "liked by..." or look for the heart count. Enter number in **Likes** column
- **Comments:** Shown below the post. Enter number in **Comments** column
- **Shares:** Instagram doesn't always show share count publicly. If visible, record it; if not, leave blank
- For numbers like "12.5K", enter 12500. For "1.2M", enter 1200000

**G. Creator Type (10 sec)**
Based on the bio and content, classify using the dropdown:
- **Healthcare professional** — MD, RN, physiotherapist, dietitian with clinical credentials
- **Certified fitness professional** — CPT, CSCS, NASM, ACE, or other fitness certifications
- **Fitness influencer** — Large following, fitness-focused content, no stated credentials
- **General user** — Regular person sharing workout content, small following
- **Organization** — Brand, gym chain, health organization, government health body

**H. Content Format (5 sec)**
Select from the dropdown:
- **Short video (<60s)** — Most Reels
- **Long video (>5min)** — Rare on Instagram, but IGTV-style content
- **Image+caption** — Static image with text caption
- **Carousel** — Multiple slides (look for dots at bottom of post)

**I. Screenshot (10 sec)**
- With the post open, press **Ctrl+Shift+S** (Firefox) or use Snipping Tool (**Win+Shift+S**)
- Save as `IG-XX.png` in `data/screenshots/instagram/`
- Capture the full post including caption and engagement metrics

#### Step 3: Move to next result
- Press browser back button or close the post modal
- Scroll to the next result
- Repeat Steps 2A-2I

#### Step 4: Move to next search term
- After recording 10 results, go back to search
- Enter the next search term
- Repeat

---

## Inclusion/Exclusion Checklist (check for each item)

Before recording, quickly verify:
- [ ] Is it in **English**? (Skip non-English content)
- [ ] Is it **primarily about physical activity/exercise**? (Skip pure diet/supplement content)
- [ ] Is it **publicly accessible**? (Should be, since you can see it)
- [ ] Was it **posted within the last 3 years**? (Skip anything before March 2023)
- [ ] Is it **substantive**? (Skip pure ads with no educational content)
- [ ] Is it a **duplicate** of something already captured on another platform? (Unlikely but check)

If an item fails any check, skip it and take the next result in the search ranking.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Instagram shows "Login to continue" | Log in with your account; incognito without login won't work well |
| Search returns fewer than 10 results | Try the "Tags" tab and search related hashtags (e.g., #howtostarexercising, #beginnerworkout) |
| Can't see view count | Only Reels show view counts; for image posts, leave Views blank |
| Can't see share count | Instagram often hides this; leave Shares blank |
| Post is an ad/sponsored | Skip it, take the next organic result |
| Content is borderline (partly about diet, partly exercise) | Include it if exercise is at least 50% of the content |
| Creator has no bio info | Enter "None stated" for credentials; classify as "General user" unless content clearly shows expertise |
| Same creator appears multiple times | Record each post separately (different Item IDs). Note in the Notes column "Same creator as IG-XX" |

---

## Speed Tips

- **Don't read content deeply** — you're just collecting metadata now. You'll score quality later during DISCERN.
- **Copy-paste is your friend** — URLs, captions, creator names. Don't retype.
- **Batch screenshots** — you can screenshot all 10 results for one search term in a batch if you keep tabs open.
- **Use Tab key** to move between spreadsheet cells quickly.
- **If an item takes more than 2 minutes to record**, something's wrong. Move on.

---

## After Collection

- [ ] Verify all 50 rows (IG-01 to IG-50) have: URL, Title/Caption, Creator_Name, Creator_Type, Content_Format
- [ ] Spot-check: open 3 random URLs to confirm they're still accessible
- [ ] Save the spreadsheet
- [ ] Back up to cloud (OneDrive/Google Drive)

**Total items when done:** 50 Instagram items ready for DISCERN scoring
