# Digital Brain Service
The service provides an API to store and access data of the Digital Brain project. 

## Setup

1. Clone repo
```
git clone https://github.com/FrauBoes/digital-brain-service.git
cd digital-brain-service
```

### Configure Caddy

1. Run ansible playbook
   
   `ansible-playbook /applications/lts/user/frauboes/ansible/playbooks/install_caddy.yml`

2. Check reverse proxy is enabled here: 
   
   `/etc/caddy/Caddyfile`

3. Restart caddy to apply changes
   
   `sudo systemctl restart caddy`

Check the status of Caddy using:

`sudo systemctl status caddy`

### Run app as Docker container

1. Build docker image
Run inside repo: 

`docker build -t digital-brain .`

2. Run container
   
`docker run -d --name digital-brain -p 5000:5000 digital-brain`

3. Check status
   
`docker ps`

`docker logs -f digital-brain`

To stop and remove the container, use:
```
docker stop digital-brain
docker rm digital-brain
```

### Test the app

Sample POST request

`curl -X POST -F "file=@<absolute file path>" https://digitalbrain.techschool.lu/artifacts/<uuid>`
