resource "aws_instance" "alfred" {
  ami           = "ami-0dd555eb7eb3b7c82"
  instance_type = "t2.micro"

  network_interface {
    network_interface_id = aws_network_interface.alfred_intrfact.id
    device_index         = 0
  }
  key_name = var.key_name


  tags = {
    Name = "alfred"
  }
}

resource "aws_network_interface" "alfred_intrfact" {
  subnet_id   = aws_subnet.main.id
  private_ips = ["10.0.0.100"]
  security_groups = [aws_security_group.allow_ssh.id]

  tags = {
    Name = "primary_network_interface"
  }
}

resource "aws_eip" "lb" {
  instance = aws_instance.alfred.id
  vpc      = true
}