# Cashbasis deployment

Target: **https://cashbasis.catsimba.com**. You push this folder to GitHub;
GitHub Actions publishes pushes to `main` to your Hostinger VPS.

## What this project actually contains

28 standalone HTML pages (Collaboration V2.23) with inline CSS/JavaScript. No package installation,
Node server, Docker, database, or build framework is required. The waitlist,
beta, payment, and referral screens are demonstrations: hosting does not make
them functional. The existing prototype notices remain visible. Search indexing
is discouraged with robots.txt and an Apache header; this does not restrict access.

`python scripts/build.py` validates local links and generates `dist/` with an
`index.html` copied from `CatSimba_Home.html`. Only public HTML and robots.txt
are deployed. Source documentation, scripts, credentials, and Git metadata are
not placed in the web root. All existing HTML filenames remain valid URLs.

## 1. Check the VPS before changing it

The following commands assume **Ubuntu/Debian with Apache 2.4** and an
administrator with sudo access. Do not apply them unchanged to a VPS managed by
CloudPanel, Plesk, cPanel, an existing reverse proxy, or a Docker ingress: create
the equivalent virtual host through that stack instead. Do not reinstall the OS.

Inspect the OS, active listeners, and current sites:

```bash
cat /etc/os-release
sudo ss -ltnp
sudo apache2ctl -S
sudo apache2ctl -M
```

Confirm Apache owns ports 80/443 and inspect existing virtual hosts for the
target hostname. Preserve existing sites and their configuration. On RHEL-based
systems the service is usually `httpd` and config paths/package commands differ;
adapt these instructions to the installed OS before proceeding.

For a compatible VPS:

```bash
sudo apt-get update
sudo apt-get install -y curl certbot python3-certbot-apache
sudo adduser --disabled-password --gecos '' cashbasis-deploy
sudo install -d -o cashbasis-deploy -g cashbasis-deploy -m 755 /var/www/cashbasis
sudo install -d -o cashbasis-deploy -g cashbasis-deploy -m 755 /var/www/cashbasis/releases
sudo install -d -o cashbasis-deploy -g cashbasis-deploy -m 700 /home/cashbasis-deploy/.ssh
```

Use an existing dedicated user if already created. This deployment user needs no
sudo access. Retain releases for rollback; periodically review disk usage and
remove old releases manually, keeping the current and previous good release.

Allow TCP 80 and 443 in the Hostinger firewall and the VPS firewall. Allow your
actual SSH port too. Do not enable/change a firewall without preserving SSH access.
GitHub-hosted runners must be able to reach the SSH port; a firewall restricted to
your home IP will block deployments. A private runner/network is an alternative.

## 2. Add DNS in Spaceship

Live inspection on 2026-09-29 found `launch1.spaceship.net` and
`launch2.spaceship.net` as the domain's nameservers; `cashbasis.catsimba.com`
did not resolve. Recheck if configuration has changed.

Open **Spaceship → Advanced DNS Manager → catsimba.com → DNS records →
Custom records**, then add:

| Type | Host/name | Value | TTL |
| --- | --- | --- | --- |
| A | cashbasis | Your Hostinger VPS public IPv4 | Default |

Keep the root domain, `www`, nameservers, and mail records unchanged. Do not add
an AAAA record unless the VPS has working IPv6 and Apache/firewalls are configured
for it; an incorrect AAAA can break access and certificate validation.

Verify from your computer:

```powershell
Resolve-DnsName cashbasis.catsimba.com -Type A
```

## 3. Configure Apache and HTTPS

Copy `deploy/apache.conf` to `/etc/apache2/sites-available/cashbasis.conf` on the VPS.
Check for an existing file/virtual host with that name before installing it.
Create a temporary page so HTTPS can be verified before the first deployment:

```bash
sudo -u cashbasis-deploy mkdir /var/www/cashbasis/releases/bootstrap
printf '%s\n' 'Cashbasis deployment pending' | sudo -u cashbasis-deploy tee /var/www/cashbasis/releases/bootstrap/index.html
sudo -u cashbasis-deploy ln -s /var/www/cashbasis/releases/bootstrap /var/www/cashbasis/current
sudo a2enmod headers
sudo a2ensite cashbasis.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

These initialization commands are for the first setup only; do not replace an
existing `current` symlink or enabled site on subsequent deployments.
Once DNS resolves to this VPS and port 80 is reachable, obtain TLS:

```bash
sudo certbot --apache -d cashbasis.catsimba.com --redirect
sudo apache2ctl configtest
sudo certbot renew --dry-run
curl --fail https://cashbasis.catsimba.com/
```

Certbot requests your email and agreement to its terms interactively. Verify its
renewal timer is enabled (`systemctl list-timers --all`). If issuance fails, check
DNS, IPv6, ports 80/443, and any inherited CAA records allowing Let's Encrypt.
Keep Certbot's HTTPS modifications; do not overwrite the live config with the
original HTTP template on future deployments. The workflow requires working TLS
and performs a local HTTPS check through `127.0.0.1` before accepting a release.

The virtual host allows symlinks for atomic releases and disables directory
listings and `.htaccess` overrides. Missing pages return Apache's normal 404.
Certbot creates/configures the HTTPS virtual host; verify that its DocumentRoot
is `/var/www/cashbasis/current` and it retains the Directory and Header directives.
Apache must listen on loopback port 443 for the workflow's local check. If your
existing configuration binds only a specific IP, adapt that check to the listening
IP. Ordinary HTML releases require no Apache reload or sudo privileges.

## 4. Set up deployment SSH access

On your own computer, generate a dedicated key (outside this repository):

```powershell
ssh-keygen -t ed25519 -C github-cashbasis-deploy -f "$env:USERPROFILE\.ssh\cashbasis_actions"
```

Use an empty passphrase for this automation key. Put the **public** `.pub` key in
`/home/cashbasis-deploy/.ssh/authorized_keys` on the VPS, prefixed with `restrict `
on the same line. This disables forwarding and interactive PTY access while
allowing the workflow's remote commands. Set file ownership to
`cashbasis-deploy:cashbasis-deploy` and permissions to `600`.

Obtain the server's public host key through the trusted Hostinger console:

```bash
sudo cat /etc/ssh/ssh_host_ed25519_key.pub
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Build a known_hosts line using that verified public key:

```text
YOUR_VPS_IPV4 ssh-ed25519 AAAA...server-public-host-key...
```

For a nonstandard SSH port, use `[YOUR_VPS_IPV4]:PORT` as the first field.
This key is the server's identity, not your deployment public key. The workflow
uses strict host checking and intentionally does not trust a runtime key scan.
Never commit or paste the private deployment key in chat.

## 5. Configure GitHub and push

In your GitHub repository, create an environment named **production** under
Settings → Environments. Restrict deployment branches to `main`. Add these
environment secrets (repository secrets also work):

| Secret | Value |
| --- | --- |
| `VPS_HOST` | VPS IPv4 address or SSH hostname, without protocol |
| `VPS_PORT` | SSH port, usually `22`; optional, defaults to 22 |
| `VPS_USER` | `cashbasis-deploy` |
| `VPS_SSH_KEY` | Entire dedicated private key, including BEGIN/END lines |
| `VPS_KNOWN_HOSTS` | Verified server host-key line from step 4 |

Environment protection features depend on your GitHub plan/repository visibility.
The job explicitly restricts deployment to `main` even without environment rules.
Configure the VPS, DNS, TLS, and secrets before the first push to avoid a failed
initial deployment. From this folder, for a new empty remote repository:

```powershell
python scripts/build.py
git init -b main
git add .
git commit -m "Prepare Cashbasis static site and VPS deployment"
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

Use your normal existing-repository workflow if the remote already has commits.
Pull requests validate HTML links without using deployment credentials. Pushes
to `main`, or manual workflow runs on `main`, validate and deploy. No files are
uploaded on pull requests. The pinned checkout action has read-only repository
permissions and does not retain Git credentials.

## Releases, verification, and rollback

Deployments upload into `/var/www/cashbasis/releases/COMMIT-RUN-ATTEMPT`, then
atomically switch `/var/www/cashbasis/current`. A local HTTPS check compares the
served homepage to the uploaded file; failure restores the previous symlink.
A separate GitHub-runner check verifies public DNS/HTTPS and homepage contents.
A failure of this external check marks the job failed but does not undo a release
that passed the VPS check (investigate public DNS/firewalls/proxy caching).

For manual rollback on the VPS, first inspect available releases and the current
target, then substitute a verified previous release directory below:

```bash
readlink /var/www/cashbasis/current
ls -lt /var/www/cashbasis/releases
sudo -u cashbasis-deploy ln -s /var/www/cashbasis/releases/PREVIOUS_RELEASE /var/www/cashbasis/current.rollback
sudo -u cashbasis-deploy mv -Tf /var/www/cashbasis/current.rollback /var/www/cashbasis/current
curl --fail https://cashbasis.catsimba.com/
```

An interrupted deployment may leave a `.next`/`.rollback` symlink. Inspect it
before removing it and rerunning; do not remove the `current` link.
Open the site and check navigation, pricing calculators, and prototype form flows
after the first successful deployment. Review `/var/log/apache2/cashbasis-error.log`
and `/var/log/apache2/cashbasis-access.log` if the workflow fails.

To use a different hostname, replace `cashbasis.catsimba.com` in the Apache
template, workflow (including health checks), DNS, and certificate command.

## References

- [Apache directory and symlink configuration](https://httpd.apache.org/docs/2.4/mod/core.html)
- [Certbot Apache plugin](https://eff-certbot.readthedocs.io/en/stable/using.html#apache)
- [Spaceship DNS record setup](https://www.spaceship.com/en-GB/knowledgebase/dns-records-types/)
- [Hostinger VPS domain pointing](https://www.hostinger.com/support/1583227-how-to-point-a-domain-to-your-vps-at-hostinger/)
- [GitHub deployment environments](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments)

Prepared locally; server compatibility, firewall reachability, TLS issuance,
GitHub secrets, and an actual deployment must be verified on your infrastructure.
