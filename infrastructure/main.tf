terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ECR Repository to store our Docker image
resource "aws_ecr_repository" "gold_trader_repo" {
  name = "gold-quant-trader"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "gold-trader-cluster"
}

# Task Definition
resource "aws_ecs_task_definition" "gold_trader_task" {
  family                   = "gold-trader"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "gold-trader"
    image = "${aws_ecr_repository.gold_trader_repo.repository_url}:latest"
    environment = [
      { name = "OANDA_API_KEY", value = var.oanda_api_key },
      { name = "OANDA_ACCOUNT_ID", value = var.oanda_account_id },
      { name = "OANDA_ENV", value = var.oanda_environment },
      { name = "REDIS_HOST", value = aws_elasticache_cluster.redis.cache_nodes[0].address },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/gold-trader"
        awslogs-region        = "us-east-1"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])
}

# Fargate Service (serverless compute)
resource "aws_ecs_service" "gold_trader_service" {
  name            = "gold-trader-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.gold_trader_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }
}
