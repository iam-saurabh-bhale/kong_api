
provider "aws" {
  region = "ap-south-1"
}

resource "aws_eks_cluster" "secure_api" {
  name     = "secure-api-cluster"
  role_arn = "REPLACE_WITH_ROLE_ARN"

  vpc_config {
    subnet_ids = ["subnet-xxxxxxxx"]
  }
}
