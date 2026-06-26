# Deploying the app live

The app runs on **Streamlit Community Cloud** (free). It deploys from a GitHub
repo, so the one-time cost is putting this folder on GitHub. The live Toronto
Open Data pull works on the cloud, since outbound HTTPS is allowed, and nothing
about the app needs a paid tier or special hardware.

## Recommended: a dedicated repo (app at the repo root)

This app lives in a subfolder of a multi-site repo, so the cleanest path is a new
repo containing just this app, with `app.py` and `requirements.txt` at the root.

1. On github.com, create a new empty repo (e.g. `reclaimed-lumber-intelligence`).
   Don't add a README or .gitignore, since this folder already has them. A public
   or private repo works the same with Streamlit Cloud.

2. From this folder (`RSM2700/app`), in a terminal:

   ```bash
   git init -b main
   git add .
   git commit -m "Reclaimed lumber intelligence app"
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

3. Go to https://share.streamlit.io, sign in with GitHub, click **New app**:
   - Repository: your new repo
   - Branch: `main`
   - Main file path: `app.py`
   - Advanced settings: set Python version to **3.12**
   - Click **Deploy**

   First build takes a few minutes (it installs `requirements.txt`). You then get
   a public `https://<app-name>.streamlit.app` URL. Every `git push` auto-redeploys.

## Alternative: deploy from the existing Portfolio repo

If the Portfolio repo is already on GitHub, you can skip the new repo and point
Streamlit Cloud at it with Main file path `RSM2700/app/app.py`. Streamlit looks
for `requirements.txt` in the app's directory, which is present here.

## Things to know once it's live

- **Project store is ephemeral.** Streamlit Cloud resets the filesystem on reboot,
  so projects saved in the Projects tab don't persist across restarts. That's fine
  for a demo. For durable storage, swap the JSON store in `pipeline/projects.py` for
  a hosted database (e.g. Supabase/Postgres) behind the same `add_project` interface.
- **Live Toronto pull** is off by default (sidebar toggle). It works on the cloud,
  and if Toronto Open Data is briefly unreachable it falls back to the cached figure.
- **No secrets needed.** This app uses only public open data, so there's nothing to
  put in Streamlit secrets.

## No-GitHub options

Every good free Streamlit host (Streamlit Cloud, Hugging Face Spaces, Render)
deploys from git, so GitHub (or another git remote) is effectively required.
Hugging Face Spaces is the closest alternative and also supports Streamlit.
