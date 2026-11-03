#!/usr/bin/env bash
set -Eeuo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get install -y apt-transport-https gpg

curl --fail --silent --show-error https://apt.releases.hashicorp.com/gpg \
  | gpg --dearmor --yes -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
chmod 0644 /usr/share/keyrings/hashicorp-archive-keyring.gpg
. /etc/os-release
printf 'deb [arch=amd64 signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com %s main\n' "$VERSION_CODENAME" \
  > /etc/apt/sources.list.d/hashicorp.list
apt-get update
apt-get install -y terraform=1.17.1-1

HELM_VERSION=v4.3.0
HELM_ARCHIVE="helm-${HELM_VERSION}-linux-amd64.tar.gz"
curl --fail --silent --show-error "https://get.helm.sh/${HELM_ARCHIVE}" -o "/tmp/${HELM_ARCHIVE}"
curl --fail --silent --show-error "https://get.helm.sh/${HELM_ARCHIVE}.sha256sum" -o "/tmp/${HELM_ARCHIVE}.sha256sum"
(cd /tmp && sha256sum --check "${HELM_ARCHIVE}.sha256sum")
tar -xzf "/tmp/${HELM_ARCHIVE}" -C /tmp linux-amd64/helm
install -o root -g root -m 0755 /tmp/linux-amd64/helm /usr/local/bin/helm
rm -rf /tmp/linux-amd64

KUBECTL_VERSION="$(curl --fail --silent --show-error https://dl.k8s.io/release/stable.txt)"
curl --fail --silent --show-error "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /tmp/kubectl
curl --fail --silent --show-error "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" -o /tmp/kubectl.sha256
printf '%s  %s\n' "$(cat /tmp/kubectl.sha256)" /tmp/kubectl | sha256sum --check
install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl
rm -f /tmp/kubectl /tmp/kubectl.sha256 "/tmp/${HELM_ARCHIVE}" "/tmp/${HELM_ARCHIVE}.sha256sum"

terraform version | head -n 1
helm version --short
kubectl version --client --output=yaml >/dev/null
aws --version
