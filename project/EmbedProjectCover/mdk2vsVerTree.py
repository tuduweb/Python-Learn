import xml.etree.ElementTree as ET
ET.register_namespace("http://schemas.microsoft.com/developer/msbuild/2003","ns")


# tree = ET.parse('hello_world.uvprojx')
# print(tree)

# root = tree.getroot()
# print(root)



# for group in root.iter("Group"):
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

#     print( group.find("GroupName").text )
#     for item in group.find("Files").iter("File"):
#         print(item.find("FileName").text)
#         print("FileType:  " + ( ".c" if item.find("FileName").text == "1" else ".h"))
#         print(item.find("FilePath").text)
#         print("------------------------------")

#def MDKReader(projectFile):

import os
import re

class ProjectMaster:
    buildTarget = []
    fileDirent = []
    rootDir = 0
    nodeTags = {}

    def __init__(self):
        nodeTags = { "ClInclude" : ["h"] , "ClCompile" : ["c"], "Text" : ["txt", "md"], "Library" : ["lib"], "None" : []}
        groupTagRules = {}
        for nodeTagName, nodeTagPrefixs in nodeTags.items():
            for tagPrefix in nodeTagPrefixs:
                groupTagRules[tagPrefix] = nodeTagName
        self.nodeTags = nodeTags
        self.groupTagRules = groupTagRules


    def InitByMdk(self, fileUri):
        
        tree = ET.parse(fileUri)
        root = tree.getroot()

        # 构建Target信息 Target的区别只去 #define 和 #includePath, 里面的分组内容不管
        for _target in root.iter("Target"):
            # print(_target.find("TargetName").text)
            # print(_target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("Define").text)
            # print(_target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath").text)
            _targetItem = [ _target.find("TargetName").text,
                            _target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("Define").text,
                            _target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath").text]
            self.buildTarget.append(_targetItem)

        print(self.buildTarget)
        print("////////////////////////")

        for group in root.find("Targets/Target").iter("Group"):
            files = []
            for item in group.find("Files").iter("File"):
                #print(item.find("FilePath").text)
                files.append(item.find("FilePath").text)
            self.fileDirent.append([group.find("GroupName").text, files])
        
        print(self.fileDirent)
        #print(os.path.dirname(fileUri))


    def CoverToVSFilters(self, templateUri, saveFileName):
        #with open(templateUri, 'rb') as fd:
        fd = open(templateUri, 'rb')
        content = fd.read()
        content = content.decode('utf-8')
        self.xmlnsHeader = re.findall('xmlns="(.*?)"', content, re.S)
        content = re.sub('xmlns="(.*?)"', "", content)
        #print(content)

        nodeProject = ET.fromstring(content)# Element 'project'

        directoryItemGroup = nodeProject.find("ItemGroup[Filter]")

        print(directoryItemGroup)

        
        itemGroupElements = {}
        for tag in self.nodeTags:
            elm = nodeProject.find("ItemGroup[" + tag + "]")
            if elm is None:
                elm = ET.Element("ItemGroup")
                nodeProject.insert(1, elm)
            itemGroupElements[tag] = elm

        for groupItem in self.fileDirent:
            #目录 Filter
            ET.SubElement(directoryItemGroup, "Filter",attrib={"Include" : groupItem[0]})
            #文件
            for fileItem in groupItem[1]:
                prefix = fileItem.split(".")[-1]
                #if prefix in groupTagRules:
                #print("move %s to %s" % (fileItem , groupTagRules.get(prefix,"None")))
                #插入到对应的ItemGroup中
                tagElm = ET.Element(self.groupTagRules.get(prefix,"None"), attrib = {"Include" : fileItem})
                elm = ET.Element("Filter")
                elm.text =  groupItem[0]
                tagElm.append( elm )
                itemGroupElements[self.groupTagRules.get(prefix,"None")].append(tagElm)
                #ET.SubElement( itemGroupElements[self.groupTagRules.get(prefix,"None")], self.groupTagRules.get(prefix,"None"), attrib = {"Include" : fileItem})
            


        # for nodeItemGroup in nodeProject:# Element 'ItemGroup' Item
        #     #print(nodeItemGroup.tag)
        #     if nodeItemGroup[0].tag == "Filter":#文件夹
        #         #print(child)
        #         #child.append()
        #         #b1 = ET.Element("Filter",attrib={"Include" : "test"})
        #         #b2 = ET.Element()
        #         for groupItem in self.fileDirent:
        #             ET.SubElement(nodeItemGroup, "Filter",attrib={"Include" : groupItem[0]})
        #     elif nodeItemGroup[0].tag == "ClInclude":
        #         for groupItem in self.fileDirent:
        #             #ET.SubElement(nodeItemGroup, "ClInclude",attrib={"Include" : groupItem[0]})
        #             if len(groupItem[1]) > 0:
        #                 for fileItem in groupItem[1]:
        #                     if fileItem.split(".")[-1] != "h":
        #                         continue
        #                     elm = ET.SubElement(nodeItemGroup, "ClInclude",attrib={"Include" : fileItem})
        #                     elm = ET.SubElement(elm, "Filter")
        #                     elm.text = groupItem[0]

        #     elif nodeItemGroup[0].tag == "ClCompile":
        #         for groupItem in self.fileDirent:
        #             #ET.SubElement(nodeItemGroup, "ClInclude",attrib={"Include" : groupItem[0]})
        #             if len(groupItem[1]) > 0:
        #                 for fileItem in groupItem[1]:
        #                     if fileItem.split(".")[-1] == "h":
        #                         continue
        #                     elm = ET.SubElement(nodeItemGroup, "ClCompile",attrib={"Include" : fileItem})
        #                     elm = ET.SubElement(elm, "Filter")
        #                     elm.text = groupItem[0] 
        #print(ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8'))
        with open(saveFileName, 'w') as f:
            f.write( ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8') )
            f.close

    def CoverToVSVcxproj(self, templateUri, saveFileName):
        fd = open(templateUri, 'rb')
        content = fd.read()
        content = content.decode('utf-8')
        self.xmlnsHeader = re.findall('xmlns="(.*?)"', content, re.S)
        content = re.sub('xmlns="(.*?)"', "", content)
        #print(content)
        """
        .vcxproj文件中
        .h,.c文件在 ItemGroup节点下，以 ClInclude,ClCompile 为标签，内容于属性Inlcude下
        <ItemGroup>
            <ClInclude Include="header1.h" />
            <ClInclude Include="header2.h" />
        </ItemGroup>
        <ItemGroup>
            <ClCompile Include="file1.cpp" />
            <ClCompile Include="file2.cpp" />
        </ItemGroup>
        """
        nodeProject = ET.fromstring(content)# Element 'project'

        nodeTags = { "ClInclude" : ["h"] , "ClCompile" : ["c"], "Text" : ["txt", "md"], "Library" : ["lib"], "None" : []}

        groupTagRules = {}
        for nodeTagName, nodeTagPrefixs in nodeTags.items():
            for tagPrefix in nodeTagPrefixs:
                groupTagRules[tagPrefix] = nodeTagName

        itemGroupElements = {}
        for tag in nodeTags:
            elm = nodeProject.find("ItemGroup[" + tag + "]")
            if elm is None:
                elm = ET.Element("ItemGroup")
                nodeProject.insert(1, elm)
            itemGroupElements[tag] = elm

        for groupItem in self.fileDirent:
            for fileItem in groupItem[1]:
                prefix = fileItem.split(".")[-1]
                #if prefix in groupTagRules:
                #print("move %s to %s" % (fileItem , groupTagRules.get(prefix,"None")))
                #插入到对应的ItemGroup中
                ET.SubElement( itemGroupElements[groupTagRules.get(prefix,"None")], groupTagRules.get(prefix,"None"), attrib = {"Include" : fileItem})

        # for names,groupElement in itemGroupElements.items():
        #     print(" %s size %s " % (names , len(groupElement)) )

        # for groupElement in itemGroupElements.values():
        #     #里面有元素 那么就添加
        #     if len(groupElement) > 0:
        #         print(groupElement.find(".."))
                


        # print(len(nodeProject.findall("PropertyGroup[@Condition]")))
        # #查找插入点
        # for item in nodeProject:
        #     print(item.attrib)

        for buildItem in self.buildTarget:
            print("===================================================")
            print("Build Target : " + buildItem[0])

            #只有一项A,下属设置多个配置项
            projectConfigurationsLabel = nodeProject.find("ItemGroup[@Label='ProjectConfigurations']")
            #print(projectConfigurationsLabel)

            # #对应配置项A的下属的多个配置项的Property
            # configurationPropertyGroupLabel = nodeProject.findall("PropertyGroup[@Label='Configuration']")
            # print(configurationPropertyGroupLabel)

            # 生成新项

            """
            <ProjectConfiguration Include="Debug|ARM">
                <Configuration>Debug</Configuration>
                <Platform>ARM</Platform>
            </ProjectConfiguration>
            """
            buildItemName = buildItem[0] + "|ARM"

            newProjectConfiguration = ET.Element("ProjectConfiguration", attrib={"Include" : buildItemName})
            ET.SubElement(newProjectConfiguration, "Configuration").text = buildItem[0]
            ET.SubElement(newProjectConfiguration, "Platform").text = "ARM"
            
            projectConfigurationsLabel.append(newProjectConfiguration)
            
            # 以下两项的插入地点要特别注意 需要放在靠前的地方 那么直接放在Configuration后面好了

            """
            <PropertyGroup Label="Configuration" Condition="'$(Configuration)|$(Platform)'=='Debug|ARM'">
                <PlatformToolset>v142</PlatformToolset>
                <ConfigurationType>Makefile</ConfigurationType>
            </PropertyGroup>
            """
            newPropertyGroupA = ET.Element("PropertyGroup", attrib={"Label" : "Configuration" , "Condition" : "'$(Configuration)|$(Platform)'=='"+ buildItemName +"'"})
            ET.SubElement(newPropertyGroupA, "PlatformToolset").text = "v142"
            ET.SubElement(newPropertyGroupA, "ConfigurationType").text = "Makefile"
            nodeProject.insert( 1,newPropertyGroupA)

            """
            <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|ARM'">
                <NMakePreprocessorDefinitions>__ICCARM__;CPU_MIMXRT1052DVL6B;NDEBUG;PRINTF_FLOAT_ENABLE=0</NMakePreprocessorDefinitions>
                <NMakeIncludeSearchPath>D:\Keil_v5\ARM\ARMCLANG\include;F:\biyesheji\software\RT1052Pro\Libraries\imxrt1052_Lib\drivers\;$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
            </PropertyGroup>
            """
            newPropertyGroupB = ET.Element("PropertyGroup", attrib={"Condition" : "'$(Configuration)|$(Platform)'=='"+ buildItemName +"'"})
            ET.SubElement(newPropertyGroupB, "NMakePreprocessorDefinitions").text = "__ICCARM__;CPU_MIMXRT1052DVL6B;NDEBUG;PRINTF_FLOAT_ENABLE=0"
            ET.SubElement(newPropertyGroupB, "NMakeIncludeSearchPath").text = r"D:\Keil_v5\ARM\ARMCLANG\include;F:\biyesheji\software\RT1052Pro\Libraries\imxrt1052_Lib\drivers\;"
            nodeProject.insert( 1,newPropertyGroupB)


            # Condition="'$(Configuration)|$(Platform)'=='Debug|ARM'"

        
        #print(ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8'))
        #print(ET.canonicalize(ET.tostring(nodeProject, encoding="utf-8", method="xml")))
        with open(saveFileName, 'w') as f:
            f.write( ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8') )
            f.close



master = ProjectMaster()
master.InitByMdk("./hello_world.uvprojx")
master.CoverToVSFilters("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj.filters","ProjectTemplate.vcxproj.filters")
master.CoverToVSVcxproj("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj","ProjectTemplate.vcxproj")

# with open("hello_world.uvprojx",'r',encoding='utf8') as fh:
#     template = fh.read()
#     tree = ET.fromstring(template)
#     print(tree)