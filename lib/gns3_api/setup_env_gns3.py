from gns3fy.projects import Project
from gns3fy.connector import Connector
from gns3fy.nodes import Node
from gns3fy.templates import Template



server = Connector(url='http://192.168.0.100:3080')
project = Project(connector=server, name='untitled', project_id='8e5b953d-f9f9-4f33-86e4-469ab8b5eab8')
result = project.get()
project.open()

t = Template(connector=server, template_id='8e67860c-4a55-45e0-b025-c7b0297908bc', name='test')
print(t)

node = Node(
    project_id=project.project_id,
    node_id="8e5b953d-f9f9-4f33-86e5-468bb8b5eab8",
    connector=server,
    name= "Router3",
    # template='Cisco IOSv 15.9(3)M6',
    # x=0,
    # y=0,
    # z=1,
    # console=5066,
    # height=50,
    # console_type='telnet'
)
result = node.update()
# node.create()
print(result)