from gns3fy import Gns3Connector, Project

def main():

    server = Gns3Connector("http://92.81.55.146:3080")


    project = Project(project_id="3f21d606-ec29-4bac-848e-aa61602b54d0", connector=server)
    project.get()


    for node in project.nodes:
        node.get()
        if node.status != "started":
            print(f" Start {node.name} (initial status: {node.status})...")
            node.start()
            print(f" {node.name} it's on!")
        else:
            print(f" {node.name} it's already on, skip it")

if __name__ == "__main__":
    main()