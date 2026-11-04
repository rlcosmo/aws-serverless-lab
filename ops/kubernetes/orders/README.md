# Current Orders baseline

These manifests capture the healthy live workloads and ConfigMaps before the candidate runtime deployment. They preserve existing namespace and service-account ownership. They are an observed baseline, not instructions to reinstall the EKS cluster or reset applications. The protected `deploy-dev` workflow updates existing Deployment images only after real approvals. Do not blindly apply these older image declarations after a successful new rollout.
