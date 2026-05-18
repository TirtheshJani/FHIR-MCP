# Oracle Always Free ARM Deployment

## Prerequisites
- Oracle Cloud account (Always Free tier)
- DNS hostname pointing at the planned instance public IP

## Provision the instance
1. Console -> Compute -> Instances -> Create.
2. Shape: VM.Standard.A1.Flex, 4 OCPU, 24 GB RAM.
3. Image: Canonical Ubuntu 24.04 minimal aarch64.
4. Networking: public subnet, assign public IPv4.
5. SSH key: upload your public key.

## Open ports 80 and 443
1. Console -> Networking -> VCN -> Security Lists -> Default Security List.
2. Add ingress rules: tcp/80 from 0.0.0.0/0, tcp/443 from 0.0.0.0/0.
3. On the instance: `sudo iptables -I INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT` then persist via `netfilter-persistent save`.

## DNS
Point your hostname A record at the instance public IP.

## Install docker
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exec sg docker newgrp
```

## Deploy
```bash
git clone https://github.com/TirtheshJani/FHIR-MCP.git
cd FHIR-MCP
sed -i "s/fhir-mcp.example.com/<your-hostname>/" docker/Caddyfile
docker compose -f docker/docker-compose.yml up -d
```

## Systemd unit (auto-restart)
Create `/etc/systemd/system/fhir-mcp.service`:
```
[Unit]
Description=fhir-mcp via docker compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/FHIR-MCP
ExecStart=/usr/bin/docker compose -f docker/docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f docker/docker-compose.yml down

[Install]
WantedBy=multi-user.target
```
Then `sudo systemctl enable --now fhir-mcp`.

## Verify
```bash
curl -sf https://<your-hostname>/sse | head -1
```
Expected: SSE greeting line.

## Idle-reclaim mitigation
Oracle Always Free may reclaim idle Ampere instances. A cron heartbeat keeps it active:
```cron
*/15 * * * * curl -sf https://<your-hostname>/sse > /dev/null
```
