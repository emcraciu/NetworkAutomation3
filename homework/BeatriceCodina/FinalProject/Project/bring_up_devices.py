from gns3fy import Gns3Connector, Project

def main():
    server = Gns3Connector("http://92.81.55.146:3080")
    project = Project(project_id="31b097ba-b719-4025-8d54-e4a11d53b734", connector=server)
    project.get()

    for node in project.nodes:
        node.get()
        if node.status != "started":
            print(f" Starting {node.name} (initial status: {node.status})...")
            node.start()
            print(f" {node.name} is now started!")
        else:
            print(f" {node.name} is already running, skipping.")

if __name__ == "__main__":
    main()
