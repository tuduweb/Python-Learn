# -*- coding: UTF-8 -*-
 
#from xml.dom.minidom import parseString
import xml.dom.minidom

# with open('hello_world.uvprojx','r',encoding='utf8') as fh:
#     fileContent = fh.read()
#     fh.close()
# #fileContent = fileContent.replace(' ', '')

# print(fileContent)



DOMTree = xml.dom.minidom.parse("hello_world.uvprojx")


# first test ,get project file uri

# ContentNodes = DOMTree.getElementsByTagName("FilePath")

# print(ContentNodes)

# for node in ContentNodes:
#     print(node.firstChild.data)


# [Attribute] is dom ""
# childNodes is included in node
# [Attribute] 是DOM节点的属性 比如 <Group id="1"> 这里就有名为id的attr
# [childNodes] 是DOM节点的子节点，比如<Group><Item>1</Item><Item>2</Item></Group>这样


def GetGroupName(node):
    return node[0].childNodes[0].data

def GetFileList(node):
    lists = []
    for dom in node[0].childNodes:
        #去除 Node.TEXT_NODE 类型，为换行符和空格
        if dom.nodeType == 3:
            continue
        lists.append(dom.firstChild.data)
    return lists

groupItems = []

groupNodes = DOMTree.getElementsByTagName("Group")
for group in groupNodes:
    #print(group.getElementsByTagName("GroupName")[0].childNodes[0].data)
    #print(group.getElementsByTagName("File")[0].childNodes)
    #childNodes[0] -> empty space [1]->GroupName

    # GroupName , [FileName , FileType, FilePath]
    item = [ GetGroupName( group.getElementsByTagName("GroupName") ) , GetFileList( group.getElementsByTagName("File") )]
    groupItems.append( item )
    #print(group.getElementsByTagName("GroupName")[0].childNodes[0].data)
#print(groupItems)

#print(groupNameNodes[0].nextSibling.nextSibling)

import xml.etree.ElementTree as ET
tree = ET.parse('hello_world.uvprojx')
print(tree)

root = tree.getroot()
print(root)
for fileName in root.iter("File"):
    print(fileName.find("FileName"))