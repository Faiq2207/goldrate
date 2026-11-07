GOLD RATE IN PAKISTAN – SETUP (one time, about 10 minutes)
===========================================================

EVERYTHING RUNS BY ITSELF AFTER THIS:
- Live gold, silver and dollar prices: update in the visitor's browser.
- Rawalpindi Sarafa market rates: checked automatically by Netlify.
- Official Sarafa association rate: a GitHub robot reads it from ARY News and
  Pakistan Observer every hour from 2 PM to 10 PM, checks it against the live
  world price, saves it, and Netlify rebuilds all pages (titles, prices, history).

STEP 1 – Upload to GitHub
1. Open your GitHub repository. Delete the old files (or make a new repository).
2. Unzip this file on your computer.
3. Click "Add file" > "Upload files" and drag in EVERYTHING you unzipped,
   including the folder named ".github". Click "Commit changes".
4. Check that ".github" appears in the file list.
   (On Windows, if you can't see it: File Explorer > View > tick "Hidden items".)

STEP 2 – Let the robot save changes (only if Step 3 shows a red X)
   Repository > Settings > Actions > General > Workflow permissions >
   choose "Read and write permissions" > Save.

STEP 3 – Test the robot once
   Repository > Actions tab > "Update official gold rate" > "Run workflow".
   A green tick means it works. After that it runs on its own every day.

STEP 4 – Netlify
   Already connected? Nothing to do. It rebuilds automatically after every upload.

STEP 5 – Google Search Console
   Sitemaps > submit "sitemap.xml". Then use URL Inspection > Request indexing
   for the home page and a few main pages (about 10 per day).

YOU NEVER NEED TO EDIT ANYTHING. If you ever want to correct a rate by hand,
edit rates.json on GitHub; the robot continues normally afterwards.
