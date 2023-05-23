# Sets up a free-tier postgres RDS w/ password
resource "aws_db_instance" "deloton-rds" {
  identifier             = "deloton-rds"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  username               = "postgres"
  password               = var.DB_PASSWORD
  publicly_accessible    = true
  skip_final_snapshot    = true
  db_subnet_group_name   = "c7-public-db-subnet-group"
  vpc_security_group_ids = ["sg-01745c9fa38b8ed68"]
  provisioner "local-exec" {

    command = "psql -h ${aws_db_instance.deloton-rds.address} -p 5432 -U \"postgres\" -d \"postgres\" -f \"create_db.sql\""

    environment = {
      PGPASSWORD = "${var.DB_PASSWORD}"
    }
  }

}
