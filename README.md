# CatSimba wireframe

Static, clickable CatSimba website prototype with 20 HTML pages. Forms, payments,
and registrations are demonstrations and do not submit data to a backend.

Open `CatSimba_Home.html` locally, or build the deployable site:

```sh
python scripts/build.py
```

The generated `dist/` directory includes the homepage as `index.html`.

## Deployment

Pushes to `main` trigger GitHub Actions deployment to an Apache Hostinger VPS serving
`https://cashbasis.catsimba.com`. Pull requests validate the site without deploying.

Complete the one-time VPS, DNS, HTTPS, and GitHub secrets setup in
[DEPLOYMENT.md](DEPLOYMENT.md) before expecting a successful deployment.

See [README.txt](README.txt) for the original design notes.
