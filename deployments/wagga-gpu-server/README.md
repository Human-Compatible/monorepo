# Wagga GPU Server deployment

The server at Wagga is in Australia NSW. It has two 3090s and 128GB of RAM.

The server is running Ubuntu 22.04 LTS.

Reach out to simon@humancompatible.co if you need access.

## Nginx

Deploying this repos nginx config to the server:

```bash
sudo ln -s $HOME/git/human-compatible-monorepo/deployments/wagga-gpu-server/nginx-site.conf /etc/nginx/sites-enabled/human-compatible
sudo nginx -s reload
```

When adding a new domain you'll need to re-run certbot:

```bash
sudo certbot --nginx
```

## Supervisor

```bash
sudo ln -s $HOME/git/human-compatible-monorepo/deployments/wagga-gpu-server/supervisor.conf /etc/supervisor/conf.d/human-compatible.conf

sudo supervisorctl reread
sudo supervisorctl update
```

```bash
sudo supervisorctl status assistance
```
