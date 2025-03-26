provider "aws" {
	  region = "us-east-1"
	}

	resource "aws_instance" "jenkins_master" {
	  ami           = "ami-084568db4383264d4"  # Ubuntu AMI
	  instance_type = "t2.medium"
	  key_name      = "KeyThree.pem"
	  tags = {
		Name = "Jenkins-Master"
	  }
	}

	resource "aws_instance" "jenkins_agent" {
	  ami           = "ami-08b5b3a93ed654d19"  # Amazon Linux AMI
	  instance_type = "t2.micro"
	  key_name      = "KeyThree.pem"
	  tags = {
		Name = "Jenkins-Agent"
	  }
	}

	resource "aws_instance" "mysql_server" {
	  ami           = "ami-0c15e602d3d6c6c4a"  # CentOS AMI
	  instance_type = "t2.micro"
	  key_name      = "KeyThree.pem"
	  tags = {
		Name = "MySQL-Server"
	  }
	}
