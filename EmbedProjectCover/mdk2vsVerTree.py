import xml.etree.ElementTree as ET
import uuid
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
    fileType = {
        "c" :   1,
        "s" :   2,
        "lib":   3,
        "h" :   5,
        "txt":  5,
        "other": 5
    }

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
            targetDefinedList = (_target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("Define").text).replace(" ","").split(',')
            targetIncludePathList = (_target.find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath").text).replace(" ","").split(';')
            _targetItem = [ _target.find("TargetName").text,
                            targetDefinedList,
                            targetIncludePathList]
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
        if directoryItemGroup is None:
            directoryItemGroup = ET.Element("ItemGroup")
            nodeProject.insert(0, directoryItemGroup)

        #print(directoryItemGroup)

        
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
            #如果没找到 那么新建
            if projectConfigurationsLabel is None:
                projectConfigurationsLabel = ET.Element("ItemGroup", attrib={"Label" : "ProjectConfigurations"})
                nodeProject.insert(0, projectConfigurationsLabel)

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
                <NMakePreprocessorDefinitions>__CC_ARM;CPU_MIMXRT1052DVL6B;NDEBUG;PRINTF_FLOAT_ENABLE=0</NMakePreprocessorDefinitions>
                <NMakeIncludeSearchPath>D:\Keil_v5\ARM\ARMCLANG\include;F:\biyesheji\software\RT1052Pro\Libraries\imxrt1052_Lib\drivers\;$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
                <IncludePath>D:\Keil_v5\ARM\ARMCLANG\include</IncludePath>
            </PropertyGroup>
            """
            newPropertyGroupB = ET.Element("PropertyGroup", attrib={"Condition" : "'$(Configuration)|$(Platform)'=='"+ buildItemName +"'"})
            ET.SubElement(newPropertyGroupB, "NMakePreprocessorDefinitions").text = "__CC_ARM;" + ';'.join(buildItem[1])#"__ICCARM__;CPU_MIMXRT1052DVL6B;NDEBUG;PRINTF_FLOAT_ENABLE=0"
            ET.SubElement(newPropertyGroupB, "NMakeIncludeSearchPath").text = r"D:\Keil_v5\ARM\ARMCC\include;D:\Keil_v5\ARM\ARMCLANG\include;" + ';'.join(buildItem[2])#r"D:\Keil_v5\ARM\ARMCLANG\include;F:\biyesheji\software\RT1052Pro\Libraries\imxrt1052_Lib\drivers\;"
            ET.SubElement(newPropertyGroupB, "IncludePath").text = r"D:\Keil_v5\ARM\ARMCLANG\include" #需要自动的搜索设置!?
            nodeProject.insert( 1,newPropertyGroupB)


            # Condition="'$(Configuration)|$(Platform)'=='Debug|ARM'"

        
        #print(ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8'))
        #print(ET.canonicalize(ET.tostring(nodeProject, encoding="utf-8", method="xml")))
        with open(saveFileName, 'w') as f:
            f.write( ET.tostring(nodeProject, encoding="utf-8", method="xml").decode('utf-8') )
            f.close
    

    def InitByVS(self, fileUri):
        vcxprojFileUri = fileUri + "/ProjectTemplate.vcxproj"
        filtersFileUri = fileUri + "/ProjectTemplate.vcxproj.filters"
        
        tree = ET.parse(vcxprojFileUri)
        root = tree.getroot()

        print(tree)
        print(root)

        
        targetList = {}
        for prj in root.findall("ItemGroup[@Label='ProjectConfigurations']/ProjectConfiguration[@Include]"):
            #_targetName = 0
            if prj.find("Platform") is not None and prj.find("Platform").text == "ARM":
                targetList[prj.find("Configuration").text] = None

        for conf in root.findall("PropertyGroup[@Condition][IncludePath][NMakePreprocessorDefinitions][NMakeIncludeSearchPath]"):
            for targetName in targetList:
                #简单的方法匹配
                if (targetName + "|ARM") not in conf.get("Condition"):
                    continue
                _targetDefinedList = conf.find("NMakePreprocessorDefinitions").text.replace("__CC_ARM;","").split(';')
                _targetIncludeList = conf.find("NMakeIncludeSearchPath").text.replace(r"D:\Keil_v5\ARM\ARMCC\include;D:\Keil_v5\ARM\ARMCLANG\include;",'').split(';')
                targetList[targetName] = [ _targetDefinedList, _targetIncludeList]

        # 整理
        for targetName,targetConf in targetList.items():
            #可能还需要处理一下,把默认参数剔除
            self.buildTarget.append( [targetName, targetConf[0], targetConf[1]] )
        
        #print(self.buildTarget)

        fileTree = ET.parse(filtersFileUri)
        fileRoot = fileTree.getroot()

        dirent = {}
        for dirItem in fileRoot.findall("ItemGroup/Filter[@Include]"):
            if dirItem.get("Include") is not None:
                dirent[dirItem.get("Include")] = []
        #print(dirent)
        #还需要修复bug
        """
        以下格式 是在顶级目录下,但是没有Filter属性
        <ClInclude Include="123.h" />
        """
        for fileItem in fileRoot.findall("ItemGroup/*[@Include][Filter]"):
            fileUri = fileItem.get("Include").replace('\\','/')
            #可能要加入是否为空的判断?
            fileDir = fileItem.find("Filter").text
            #print(fileUri)
            if fileDir is not None:
                dirent[fileDir].append(fileUri)
        #print(dirent)

        self.fileDirent = []
        for dirName,fileList in dirent.items():
            self.fileDirent.append( [dirName, fileList] )
    
    def CoverElementToString(self, elm):
        return ET.tostring(elm, encoding="utf-8", method="xml").decode('utf-8')

    def CoverToMDKPrj(self, templateUri, saveFileName):
        tree = ET.parse(templateUri)
        root = tree.getroot()
    
    def UpdateMDKPrj(self, targetUri):
        if os.path.exists(targetUri) is False:
            print("file Err")
            return

        # 备份文件
        
        with open(targetUri,'rb') as FD,open (targetUri+'.PYbak','wb') as newFD:
            content = FD.read()
            newFD.write(content)
            #FD.close()
            #newFD.close
        root = ET.fromstring(content)
        #root = tree.getroot()

            

        #print(ET.tostring(root, encoding="utf-8", method="xml").decode('utf-8'))

        print("===========================================\n----------> StartBuild")
        #构建全新的Group
        builtGroupsElm = ET.Element("Groups")
        for groupItem in self.fileDirent:
            groupElm = ET.SubElement(builtGroupsElm, "Group")
            ET.SubElement(groupElm, "GroupName").text = groupItem[0]
            filesElm = ET.SubElement(groupElm, "Files")
            for fileItemUri in groupItem[1]:
                fileElm = ET.SubElement(filesElm, "File")
                ET.SubElement(fileElm, "FileName").text = os.path.basename(fileItemUri)
                fileItemPrefix = fileItemUri.split('.')[-1]
                if self.fileType.get(fileItemPrefix) is not None:
                    #print(self.fileType.get(fileItemPrefix))
                    ET.SubElement(fileElm, "FileType").text = str(self.fileType.get(fileItemPrefix))
                else:
                    ET.SubElement(fileElm, "FileType").text = str(self.fileType["other"])

                #ET.SubElement(fileElm, "FileType").text = "1"#fileType
                #fileItemUri.split('.')[-1]
                ET.SubElement(fileElm, "FilePath").text = fileItemUri

        # buildGroupElm = ET.Element("Group")
        # ET.SubElement(buildGroupElm, "FileName").text = "name"
        # ET.SubElement(buildGroupElm, "FileType").text = "type"
        # ET.SubElement(buildGroupElm, "FilePath").text = "path"
        

        #print(self.CoverElementToString(builtGroupsElm))

        targetsInfo = {}
        for info in self.buildTarget:
            targetsInfo[info[0]] = info[1:]

        oldTargetInfos = []
        oldTargetGroups = []
        """
        Python处理绝对路径和相对路径
            Python os.path 模块提供了一些函数，可以实现绝对路径和相对路径之间的转换，以及检查给定的路径是否为绝对路径，比如说：
            调用 os.path.abspath(path) 将返回 path 参数的绝对路径的字符串，这是将相对路径转换为绝对路径的简便方法。
            调用 os.path.isabs(path)，如果参数是一个绝对路径，就返回 True，如果参数是一个相对路径，就返回 False。
            调用 os.path.relpath(path, start) 将返回从 start 路径到 path 的相对路径的字符串。如果没有提供 start，就使用当前工作目录作为开始路径。
            调用 os.path.dirname(path) 将返回一个字符串，它包含 path 参数中最后一个斜杠之前的所有内容；调用 os.path.basename(path) 将返回一个字符串，它包含 path 参数中最后一个斜杠之后的所有内容。
        os.path.exists(test_file.txt)
        os.path.exists(directory)
        """
        for elm in root.findall("Targets/Target"):
            targetName = elm.find("TargetName").text
            targetInfosElm = elm.find("TargetOption/TargetArmAds/Cads/VariousControls")

            # 如果不存在 那么排除
            if targetName not in targetsInfo:
                continue

            
            targetInfosElm.find("Define").text = ", ".join(targetsInfo[targetName][0])
            targetInfosElm.find("IncludePath").text = ";".join(targetsInfo[targetName][1])

            targetGroups = elm.find("Groups")
            #print(targetGroups)

            ## 新增模式/修改模式
            # for group in targetGroups:
            #     print(group.find("GroupName").text)
            #     #需要增添路径修改模式 转换相对路径关系
            #     filePath = group.find("Files/File/FilePath").text
            #     #print(os.path.relpath(filePath,".../biyesheji/learn/rt1052/"))

            #print(self.buildTarget)
            elm.remove(targetGroups)
            elm.append(builtGroupsElm)
        
        print(self.CoverElementToString(elm))
        with open(targetUri, 'w') as f:
            f.write( '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n' + ET.tostring(root, encoding="utf-8", method="xml").decode('utf-8') )
            f.close

master = ProjectMaster()
# master.InitByMdk("./hello_world.uvprojx")
# master.CoverToVSFilters("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj.filters","ProjectTemplate.vcxproj.filters")
# master.CoverToVSVcxproj("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj","ProjectTemplate.vcxproj")

master.InitByVS("./vs/")
#master.CoverToVSFilters("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj.filters","ProjectTemplate2.vcxproj.filters")
#master.CoverToVSVcxproj("./vsProjectTemplate/ProjectTemplate/ProjectTemplate.vcxproj","ProjectTemplate2.vcxproj")
#master.CoverToMDKPrj("./mdk/template.uvprojx", "./mdk/build.uvprojx")
master.UpdateMDKPrj("./mdk/hello_world.uvprojx")



# with open("hello_world.uvprojx",'r',encoding='utf8') as fh:
#     template = fh.read()
#     tree = ET.fromstring(template)
#     print(tree)