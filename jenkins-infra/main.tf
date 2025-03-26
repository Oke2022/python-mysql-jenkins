provider "aws" {
	  region = "us-east-1"
	}


resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins-security-group"
  description = "Allow SSH and Jenkins traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allows SSH from anywhere (restrict this in production)
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allows Jenkins UI access (Restrict in production)
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allows MySQL access (Restrict to your internal network)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "jenkins_master" {
	ami           = "ami-084568db4383264d4"  # Ubuntu AMI
	instance_type = "t2.medium"
  key_name      = "KeyThree.pem"
  security_groups = [aws_security_group.jenkins_sg.id]
	tags = {
	Name = "Jenkins-Master"
	}
}

resource "aws_instance" "jenkins_agent" {
	ami           = "ami-08b5b3a93ed654d19"  # Amazon Linux AMI
	instance_type = "t2.micro"
	key_name      = "KeyThree.pem"
  security_groups = [aws_security_group.jenkins_sg.id]
	tags = {
	Name = "Jenkins-Agent"
	}
}

resource "aws_instance" "mysql_server" {
	ami           = "ami-0c15e602d3d6c6c4a"  # CentOS AMI
	instance_type = "t2.micro"
	key_name      = "KeyThree.pem"
  security_groups = [aws_security_group.jenkins_sg.id]
	tags = {
	Name = "MySQL-Server"
	}
}

