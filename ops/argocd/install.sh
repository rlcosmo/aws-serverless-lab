#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export AWS_DEFAULT_REGION=us-east-1
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
[[ "$EUID" == 0 ]] || exit 1
if ! command -v curl >/dev/null || ! command -v unzip >/dev/null; then
  sed -i -E 's@http://[^ /]*ec2.archive.ubuntu.com/ubuntu@https://archive.ubuntu.com/ubuntu@g; s@http://@https://@g' /etc/apt/sources.list.d/ubuntu.sources
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq curl unzip ca-certificates iptables
fi
command -v aws >/dev/null || snap install aws-cli --classic
install -d -m 0700 /etc/rancher/k3s /opt/cosmotech/argocd /opt/cosmotech/backups/argocd
install -m 0600 "$source_dir/k3s-config.yaml" /etc/rancher/k3s/config.yaml
install -m 0600 "$source_dir/audit.yaml" /etc/rancher/k3s/audit.yaml
if ! command -v k3s >/dev/null; then
  curl --fail --location --retry 3 https://raw.githubusercontent.com/k3s-io/k3s/v1.37.1%2Bk3s1/install.sh -o /opt/cosmotech/argocd/install-k3s.sh
  INSTALL_K3S_VERSION=v1.37.1+k3s1 sh /opt/cosmotech/argocd/install-k3s.sh
fi
systemctl enable --now k3s
kubectl wait node --all --for=condition=Ready --timeout=180s
if ! command -v helm >/dev/null; then
  curl --fail --location --retry 3 https://get.helm.sh/helm-v4.3.1-linux-amd64.tar.gz -o /opt/cosmotech/argocd/helm.tar.gz
  curl --fail --location --retry 3 https://get.helm.sh/helm-v4.3.1-linux-amd64.tar.gz.sha256sum -o /opt/cosmotech/argocd/helm.sha256
  (cd /opt/cosmotech/argocd && sed 's@helm-v4.3.1-linux-amd64.tar.gz@helm.tar.gz@' helm.sha256 | sha256sum -c -)
  tar -xzf /opt/cosmotech/argocd/helm.tar.gz -C /opt/cosmotech/argocd
  install -m 0755 /opt/cosmotech/argocd/linux-amd64/helm /usr/local/bin/helm
fi
helm repo add argo https://argoproj.github.io/argo-helm --force-update >/dev/null
helm repo update argo >/dev/null
helm upgrade --install argocd argo/argo-cd --version 10.12.1 --namespace argocd --create-namespace \
  -f "$source_dir/values.yaml" --wait --timeout 10m
# No credential ever enters Helm values or Terraform state.
python3 "$source_dir/configure.py"
install -m 0700 "$source_dir/backup.sh" /opt/cosmotech/argocd/backup.sh
install -m 0644 "$source_dir/cosmotech-argocd-backup.service" /etc/systemd/system/
install -m 0644 "$source_dir/cosmotech-argocd-backup.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now cosmotech-argocd-backup.timer
systemctl start cosmotech-argocd-backup.service
kubectl -n argocd get pods
