# CatSimba wireframe

CatSimba Collaboration V2.23: a static, clickable prototype with 28 HTML pages. Forms, payments,
and registrations are demonstrations and do not submit data to a backend.

Open `CatSimba_Home.html` locally, or build the deployable site:

```sh
python scripts/build.py
```

The generated `dist/` directory preserves the supplied `index.html` and all
wireframe pages unchanged. The original entry page redirects to `CatSimba_Home.html`.

## Deployment

Pushes to `main` trigger GitHub Actions deployment to an Apache Hostinger VPS serving
`https://cashbasis.catsimba.com`. Pull requests validate the site without deploying.

Complete the one-time VPS, DNS, HTTPS, and GitHub secrets setup in
[DEPLOYMENT.md](DEPLOYMENT.md) before expecting a successful deployment.

### Publishing updates

After deployment setup, edit the HTML files and push to `main`:

```sh
git add .
git commit -m "Update website"
git push origin main
```

GitHub Actions validates the pages, uploads a new release, checks Apache configuration,
restarts Apache, and checks HTTPS.
Follow the run in the repository's **Actions** tab. Failed validation prevents
deployment; a failed server content check restores the previous release.

Live site: https://cashbasis.catsimba.com

See [README.txt](README.txt) for the original design notes.
See [COLLABORATION_CHANGE_NOTES.md](COLLABORATION_CHANGE_NOTES.md) for the V2.23 changes.
