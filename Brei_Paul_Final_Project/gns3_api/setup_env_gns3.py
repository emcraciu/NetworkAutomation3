from tempfile import template

from gns3fy.projects import Project
from gns3fy.connector import Connector
from gns3fy.nodes import Node

server=Connector(url='http://92.81.55.146:3080')
project=Project(connector=server,name='Brei Paul',project_id='e8034bf9-a3b9-436d-a5fd-df165d3c6249')
result=project.get()
project.open()

node=Node(
    project_id=project.project_id,
    node_id="096a88ee-d93f-4beb-be18-757977ba59e07",
    connector=server,
    name='Router2',
    node_template='Cisco IOSv 15.9(3)M6',
    x=0,
    y=0,
    z=1,
    console=5066,
    height=50,
    console_type='telnet',


)

print(result)