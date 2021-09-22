terraform {
  backend "remote" {
    organization = "OpenProjects"

    workspaces {
      name = "Voice2Text"
    }
  }
}