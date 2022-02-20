resource "aws_vpc" "main" {
    cidr_block       = "10.0.0.0/16"
    tags = {
       Name = "main"
    }
}
resource "aws_subnet" "main" {
    vpc_id     = aws_vpc.main.id
    cidr_block = "10.0.0.0/24"

    tags = {
        Name = "Main"
    }
}
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main"
  }
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "allow inbound ssh straf"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "Allow ssh"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = [ "${var.my_ip}/32" ]
  }

  tags = {
    Name = "allow_tls"
  }
}
