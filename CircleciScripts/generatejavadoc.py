
import os
import sys
import demjson
import functions.py

def getCommandline(dest, root, modules, packages,subpackages,excludes, groups, otheroptions, otherargs):


    commandline = "javadoc " + \
                " -d '{0}'".format(dest) + \
                " -sourcepath  '{0}'".format(':'.join(map(lambda module: (root + "/" + module + "/src/main/java/"), modules)))  + \
                " " + ' '.join(packages)  +  \
                " -subpackages '{0}' ".format(':'.join(subpackages)) + \
                " -exclude '{0}' ".format(':'.join(excludes)) + \
                " ".join(map(lambda group:(" -group '{0}' '{1}' ".format(group['title'], ':'.join(group['packages']))), groups)) +  \
                " ".join(map(lambda otheroption:(' -{0} "{1}" '.format(otheroption[0], otheroption[1])), otheroptions.items()))  + \
                " ".join(map(lambda otherarg: ('-' + otherarg), otherargs))
    return commandline 

def  getWords(pattern):
    firstPos = pattern.find(".")
    if firstPos == -1 :
        firstWord = pattern
    else:
        firstWord = pattern[0:firstPos]
    if firstPos == -1 :
        secondWord = ""
        leftWord = ""
    else:
        leftWord = pattern[firstPos+1 : len(pattern)]
        secondPos = pattern.find(".",firstPos + 1)
        if secondPos == -1 :
            secondWord = leftWord
        else:
            secondWord = pattern[firstPos+1 : secondPos]

    return (firstWord, secondWord, leftWord)

def getPackagesWithPattern(root, pattern):
    # ipdb.set_trace()  ######### Break Point ###########
    packages = set()
    (firstWord, secondWord, leftWord) = getWords(pattern)
    for folder in os.listdir(root):
        folderpath = os.path.join(root,folder)
        if os.path.isdir(folderpath):
            if firstWord == "*" :
                if leftWord == "" :
                    packages.add(folder)
                elif secondWord == folder:
                    (firstWord1, secondWord1, leftWord1) = getWords(leftWord)
                    if leftWord1 == "" :
                        packages.add(folder)
                    else :
                        subpackages = getPackagesWithPattern(folderpath, leftWord1)
                        for subpackage in subpackages:
                            packages.add(folder + "." + subpackage)
                else:
                    subpackages = getPackagesWithPattern(folderpath, pattern)
                    for subpackage in subpackages:
                        packages.add(folder + "." + subpackage)
            elif firstWord == folder :
                if leftWord == "" :
                    packages.add(folder)
                else :
                    subpackages = getPackagesWithPattern(folderpath, leftWord)
                    for subpackage in subpackages:
                        packages.add(folder + "." + subpackage)
    return packages

def getAllPackagesWithPattern(root, modules, pattern):
    packages = set()
    sourthpaths = ""
    for module in modules:
        sourthpath = root + "/" + module + "/src/main/java/"
        p = getPackagesWithPattern(sourthpath, pattern);
        packages.update(p);
    return packages

variableDict = {}
def resolveVaraibles(str):
    for k,v in variableDict.items():
        str = str.replace("${" + k + "}" , v)
    return str
def resolveList(list):
    newlist = []
    for e in list:
        newlist.append(resolveVaraibles(e))
    return newlist


def resolveDict(dict):
    for k in dict:
        dict[k] = resolveVaraibles(dict[k])      
    return dict

def printset(s):
    for e in s:
        print(e)

def copylib(root, modules, target):
    for module in modules:
        sourthpath = os.path.join(root, module, "build/libs")
        if os.path.isdir(sourthpath):
            runcommand('cp "{0}/*.jar" "{1}"'.format(sourthpath, target))


jsonfilename=sys.argv[1]
root = sys.argv[2]
dest = sys.argv[3]
with open(jsonfilename, 'r') as jsonfile:
    jsonstring = jsonfile.read()

docConfigure =  demjson.decode(jsonstring)
variableDict = docConfigure["variables"] 

# sourthpaths = getSourthPaths(root, resolveList(docConfigure["modules"]))


# print(sourthpaths)
# (firstWord, secondWord, leftWord) = getWords("")
# print("test1", firstWord,secondWord,leftWord)
# (firstWord, secondWord, leftWord) = getWords("word1")
# print("test2", firstWord,secondWord,leftWord)
# (firstWord, secondWord, leftWord) = getWords("word1.word2")
# print("test3", firstWord,secondWord,leftWord)
# (firstWord, secondWord, leftWord) = getWords("word1.word2.word3")
# print("test4", firstWord,secondWord,leftWord)
#
# (firstWord, secondWord, leftWord) = getWords("word1.word2.word3.word4")
# print("test5", firstWord,secondWord,leftWord)
#
# (firstWord, secondWord, leftWord) = getWords("*")
# print("test5", firstWord,secondWord,leftWord)

# ss = getPackagesWithPattern("/Users/sdechunq/Documents/github/android/aws-sdk-android/aws-android-sdk-s3/src/main/java/", "com.*.s3")
# printset(ss);

modules = resolveList(docConfigure["modules"])
packages = set()
# packagess = docConfigure["packages"]
# print(packagess)
for package in resolveList(docConfigure["packages"]):
    if package.find("*") == -1 :
        packages.add(package);
    else:
        packageset = getAllPackagesWithPattern(root, docConfigure["modules"], package);
        packages.update(packageset) 

subpackages = set()
for subpackage in resolveList(docConfigure["subpackages"]):
    if subpackage.find("*") == -1 :
        subpackages.add(subpackage);
    else:
        subpackageset = getAllPackagesWithPattern(root, docConfigure["modules"], subpackage);
        subpackages.update(subpackageset)

excludes = set()
for exclude in resolveList(docConfigure["excludes"]):
    if exclude.find("*") == -1 :
        excludes.add(exclude);
    else:
        excludepackageset = getAllPackagesWithPattern(root, docConfigure["modules"], exclude);
        excludes.update(excludepackageset)



groups = docConfigure["groups"]
for group in groups:
    group['packages'] = resolveList(group['packages'])

otheroptions = resolveDict(docConfigure["otheroptions"])
otherargs = resolveList(docConfigure["otherargs"])

copylib(root, modules. os.path.join(root, "libs")) 

commandline = getCommandline(dest, root, modules, packages,subpackages,excludes, groups, otheroptions, otherargs)
print(commandline)
