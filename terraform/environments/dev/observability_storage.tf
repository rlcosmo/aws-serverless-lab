data "aws_iam_policy" "ebs_csi_driver" {
  arn = "arn:aws:iam::aws:policy/AmazonEBSCSIDriverPolicyV2"
}

data "aws_iam_policy_document" "ebs_csi_pod_identity" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
    ]

    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/kubernetes-namespace"
      values   = ["kube-system"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/kubernetes-service-account"
      values   = ["ebs-csi-controller-sa"]
    }
  }
}

resource "aws_iam_role" "ebs_csi_driver" {
  name               = "aws-eks-istio-lab-dev-ebs-csi-driver"
  assume_role_policy = data.aws_iam_policy_document.ebs_csi_pod_identity.json

  tags = {
    Name      = "aws-eks-istio-lab-dev-ebs-csi-driver"
    Component = "eks-storage"
  }
}

resource "aws_iam_role_policy_attachment" "ebs_csi_driver" {
  role       = aws_iam_role.ebs_csi_driver.name
  policy_arn = data.aws_iam_policy.ebs_csi_driver.arn
}

resource "aws_eks_pod_identity_association" "ebs_csi_driver" {
  cluster_name    = data.aws_eks_cluster.lab.name
  namespace       = "kube-system"
  service_account = "ebs-csi-controller-sa"
  role_arn        = aws_iam_role.ebs_csi_driver.arn
}

resource "aws_eks_addon" "ebs_csi_driver" {
  cluster_name                = data.aws_eks_cluster.lab.name
  addon_name                  = "aws-ebs-csi-driver"
  addon_version               = "v1.67.2-eksbuild.1"
  resolve_conflicts_on_create = "NONE"
  resolve_conflicts_on_update = "PRESERVE"
  tags                        = local.common_tags

  depends_on = [
    aws_eks_pod_identity_association.ebs_csi_driver,
    aws_iam_role_policy_attachment.ebs_csi_driver,
  ]
}
