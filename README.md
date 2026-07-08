# Selangor Blood Donation Forecasting — Streamlit Website

An interactive web dashboard that forecasts blood donation trends in Selangor
using an XGBoost machine learning model. Built with Streamlit.

## Pages
1. **Home** — project overview and key metrics
2. **Historical Analysis** — actual vs predicted, weekly patterns
3. **30-Day Forecast** — future prediction, shortage risk
4. **Download Center** — download CSV data and PDF report

---

## Files in this folder
```
streamlit_app/
├── Home.py                          ← main page (run this)
├── blood_donation_data.csv          ← your forecast data
├── requirements.txt                 ← list of libraries needed
├── README.md                        ← this file
└── pages/
    ├── 1_📊_Historical_Analysis.py
    ├── 2_🔮_30_Day_Forecast.py
    └── 3_📥_Download_Center.py
```

---

## PART A — Run it on your own laptop (localhost) first

### Step 1 — Install Python libraries
Open a terminal / command prompt inside this folder and run:
```
pip install -r requirements.txt
```

### Step 2 — Run the app
```
streamlit run Home.py
```
Your web browser will open automatically at `http://localhost:8501`.
You now have the website running on your laptop. Use the left sidebar
to move between the 4 pages.

To stop it, go back to the terminal and press `Ctrl + C`.

---

## PART B — Publish it online for FREE (Streamlit Community Cloud)

This gives you a real public web link to share with your supervisor.

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free) if you don't have one.

### Step 2 — Create a new repository
1. Click the **+** icon (top right) → **New repository**
2. Name it something like `blood-donation-dashboard`
3. Set it to **Public**
4. Click **Create repository**

### Step 3 — Upload your files
1. On the new repository page, click **uploading an existing file**
2. Drag in ALL these files, keeping the folder structure:
   - `Home.py`
   - `blood_donation_data.csv`
   - `requirements.txt`
   - the entire `pages/` folder (with its 3 files inside)
3. Click **Commit changes**

> Important: the `pages` folder must stay a folder. If GitHub's web
> uploader flattens it, create the folder manually: click
> **Add file → Create new file**, type `pages/1_Historical.py` and it
> will create the folder for you, then upload the page files into it.

### Step 4 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your **GitHub account**
3. Click **New app** → **Deploy a public app from GitHub**
4. Select your `blood-donation-dashboard` repository
5. Set **Main file path** to `Home.py`
6. Click **Deploy**

Wait 2–3 minutes. Streamlit installs everything and gives you a public
link like:
```
https://your-app-name.streamlit.app
```

### Step 5 — Share the link
Send that link to your supervisor. It works on any device, any browser,
no installation needed. All 4 pages, all charts, and both download
buttons work online exactly as they do on your laptop.

---

## Updating the data later
If you retrain your model and produce a new CSV:
1. Rename it to `blood_donation_data.csv`
2. Upload it to your GitHub repository (replacing the old one)
3. Streamlit Cloud automatically rebuilds the site within a minute

---

## Troubleshooting
- **"ModuleNotFoundError"** → make sure `requirements.txt` was uploaded to GitHub
- **Emojis in page filenames cause issues** → you can rename the page files to
  remove emojis (e.g. `1_Historical_Analysis.py`); the app still works, the
  sidebar just won't show the icon
- **App is slow on first load** → normal; Streamlit Cloud "wakes up" the app
  after inactivity, takes a few seconds
