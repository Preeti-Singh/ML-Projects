import json
#import import_ipynb
from ast import parse
from ast2json import ast2json
import sys

keywords=['print','False','await','else','import','pass','None','break','except','in','raise','True','class','finally','is','return','and','continue','for','lambda','try','as','def','from','nonlocal','while','assert','del','global','not','with','async','elif','if','or','yield'];
seperators=['(',')','{','}','[',']',';',',','.','\\','#','@',':','=']
operators=["-",'+',"*","/","//",'**','%','>','<','>=','<=','==','!=','and','or','not in','not','is','is not','&','|','~','^','>>','<<'];

actualUsed=[]
allVariables=[]
lineType=""
Variables=[]
variables=[]
used=[]
defined=[]
actualUseduptoBlock={}

def UsedVariableAnalysis(keysList,basicBlocks,edgeList,lineNumDict,whileStartEnd):
    global actualUsed
    global allVariables
    global actualUseduptoBlock
    #previousitem
    keysList.reverse()
    for item in keysList:
        #print(item)
        block=basicBlocks[item];
        lst=block.split('\n');
        while("" in lst) : 
            lst.remove("")
        lst.reverse()
        for line in lst:
            #print(line)
            returnfromwhile = analyseLine(line)
            actualUsed = unique(actualUsed)
            allVariables = unique(allVariables)
        if returnfromwhile:
            i=item
            j=whileStartEnd[item]
            for k in range(i,j+1):
                if k in keysList:
                    actualUseduptoBlock[k]=unique(actualUsed)
        actualUseduptoBlock[item]=unique(actualUsed)
        #previousitem=item
    faintVariables=[]
    for item in allVariables:
        if item not in actualUsed:
            faintVariables.append(item)
    #print("actualUsed",actualUsed)
    #print("allVariables",allVariables)
    #print("faintVariables",faintVariables)


def unique(list1): 
      
    # insert the list to the set 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set))
    return unique_list 

def analyseLine(line):
    global variables
    global defined 
    global used
    global prevUseful
    global lineType
    global actualUsed
    global allVariables

    used=[];
    defined=[];
    variables=[];
    #print(line);
    if line.find('branch[')==0:
        #print("con",line);
        line=line[7:len(line)-1]
        #print("con",line);
        if 'not' in line:
            line=line[3:]
        if line not in keywords:
            
            allVariables+=[str(line)]
            actualUsed+=[str(line)]
            # allVariables=unique(allVariables)
            # actualUsed=unique(actualUsed)
        return;
                
        
    if line.find('while[')==0:
        #print("con",line);
        line=line[6:len(line)-1];
        #print("con",line);
        if line not in keywords:
            allVariables+=[str(line)]
            actualUsed+=[str(line)]
            # allVariables.append(str(line))
            # actualUsed.append(str(line))
            #print(actualUsed)
            # allVariables=unique(allVariables)
            # actualUsed=unique(actualUsed)
        return 1;

    code=ast2json(parse(line));
    runForList(code["body"])
    

def runForDict(node):
    global defined 
    global used
    global lineType
    global variables
    global Variables
    global allVariables
    global actualUsed
    
    if node['_type']=='Call':
        if lineType=='notset':
            lineType='call';
        for arg in node['args']:
                extractVariables(arg)
                variables+=Variables
                used+=Variables
                actualUsed+=Variables
                allVariables+=Variables


    if node['_type']=='AugAssign':
        if lineType=='notset':
            lineType='Augassign';

        if node['target']["_type"]=="Subscript":
            extractVariables(node['target']["value"])
            #print(Variables)
            defined+=Variables
            used+=Variables
            variables+=Variables
            allVariables+=Variables
            Variables=[]
            extractVariables(node['target']["slice"])
            used+=Variables
            variables+=Variables
            allVariables+=Variables
            Variables=[]
        else:
            extractVariables(node['target'])
            defined+=Variables
            used+=Variables
            variables+=Variables
            allVariables+=Variables
            Variables=[]

        extractVariables(node["value"]) 
        used+=Variables
        for var in defined:
            if var in actualUsed:
                #print("true")
                actualUsed+=used
        variables+=Variables

    if node['_type']=='Assign':
        if lineType=='notset':
            lineType='assign';
        for target in node['targets']:
            if target["_type"]=="Subscript":
                extractVariables(target["value"])
                #print(Variables)
                defined+=Variables
                variables+=Variables
                allVariables+=Variables
                Variables=[]
                extractVariables(target["slice"])
                used+=Variables
                variables+=Variables
                allVariables+=Variables
                Variables=[]   
            else :
                extractVariables(target)
                defined+=Variables
                variables+=Variables
                allVariables+=Variables
                Variables=[]
            Variables=[]

        extractVariables(node['value'])
        used+=Variables
        for var in defined:
            if var in actualUsed:
                #print("true")
                actualUsed+=used
        variables+=Variables
        allVariables+=Variables
                
        
    Variables=[]
    for key,value in node.items():
        nodeType=str(type(value));
        if nodeType=='<class \'dict\'>':
            runForDict(value);

        elif nodeType=='<class \'list\'>':
            runForList(value);


def runForList(lst):
    for item in lst:
        nodeType=str(type(item));
        if nodeType=='<class \'dict\'>':
            runForDict(item);
        elif nodeType=='<class \'list\'>':
            runForList(item);
            


def extractVariables(node):

    global Variables
    #print(node)
    if node==None:
        return "";
    if node['_type']=='Name':
        Variables.append(str(node["id"]))
        
    elif node['_type']=='Starred':
        extractVariables(node['value'])
    elif node['_type']=="Subscript":
        extractVariables(node['value'])
        extractVariables(node['slice'])

    elif node['_type']=='Index':
        extractVariables(node['value'])

    elif node['_type']=='Slice':
        extractVariables(node['lower'])
        extractVariables(node['upper'])
        if str(node['step'])!='None':
            extractVariables(node['step'])

    elif node['_type']=='Delete':
        extractVariables(node['targets'][0])

    elif node['_type']=='Dict':
        index=0;
        for k in node['keys']:
            if len(node['keys'])==index+1:
                extractVariables(k)
                extractVariables(node['values'][index])
            else:
                extractVariables(k)
                extractVariables(node['values'][index])
                
            index+=1;
        

    elif node['_type']=='List':
        lst='[';
        index=1;
        for item in node['elts']:
            if len(node['elts'])==index:
                extractVariables(item)
            else:
                extractVariables(item)
            index+=1;


    elif node['_type']=='Tuple':
        lst='(';
        index=1;
        for item in node['elts']:
            if len(node['elts'])==index:
                extractVariables(item)
            else:
                extractVariables(item)
            index+=1;


    elif node['_type']=='Set':
        lst='{';
        index=1;
        for item in node['elts']:
            if len(node['elts'])==index:
                extractVariables(item)
            else:
                extractVariables(item)
            index+=1;


    elif node['_type']=='BinOp':
        exp='';
        if node['left']['_type']=='BinOp':
            extractVariables(node['left'])
        else:
            extractVariables(node['left'])
        

        extractVariables(node['right'])


    elif node['_type']=='UnaryOp':
        extractVariables(node['operand'])
     

    elif node['_type']=='Compare':
        extractVariables(node['left'])
        
        extractVariables(node['comparators'][0])


    elif node['_type']=='BoolOp':
        extractVariables(node['values'][0])
        extractVariables(node['values'][1])

    elif node['_type']=='Attribute':
        extractVariables(node['value'])


    elif node['_type']=='Call':
        #extractVariables(node['func'])
        index=1;
        for arg in node['args']:
            if len(node['args'])==index:
                extractVariables(arg)
            else:
                extractVariables(arg)
            index+=1;

def CompareFaint(node):
    global defined 
    global used
    global lineType
    global variables
    global Variables
    
    if node['_type']=='Call':
        if lineType=='notset':
            lineType='call';
        for arg in node['args']:
                extractVariables(arg)
                variables+=Variables
                used+=Variables

    if node['_type']=='AugAssign':
        if lineType=='notset':
            lineType='Augassign';

        if node['target']["_type"]=="Subscript":
            extractVariables(node['target']["value"])
            #print(Variables)
            defined+=Variables
            used+=Variables
            variables+=Variables
            Variables=[]
            extractVariables(node['target']["slice"])
            used+=Variables
            variables+=Variables
            Variables=[]
        else:
            extractVariables(node['target'])
            defined+=Variables
            used+=Variables
            variables+=Variables
            Variables=[]

        extractVariables(node["value"])
        used+=Variables
        variables+=Variables

    if node['_type']=='Assign':
        if lineType=='notset':
            lineType='assign';
        for target in node['targets']:
            if target["_type"]=="Subscript":
                extractVariables(target["value"])
                #print(Variables)
                defined+=Variables
                variables+=Variables
                Variables=[]
                extractVariables(target["slice"])
                used+=Variables
                variables+=Variables
                Variables=[]   
            else :
                extractVariables(target)
                defined+=Variables
                variables+=Variables
                Variables=[]
            Variables=[]

        extractVariables(node['value'])
        used+=Variables
        variables+=Variables
                
        
    Variables=[]
    for key,value in node.items():
        nodeType=str(type(value));
        if nodeType=='<class \'dict\'>':
            CompareFaint(value);

        elif nodeType=='<class \'list\'>':
            FindFaintAssignment(value);


def FindFaintAssignment(lst):
    for item in lst:
        nodeType=str(type(item));
        if nodeType=='<class \'dict\'>':
            CompareFaint(item);
        elif nodeType=='<class \'list\'>':
            FindFaintAssignment(item);

def codeOptimization(keysList,lineNumDict,file):
    
    global actualUseduptoBlock
    programpoints={}
    #keysList.reverse()
    #print(keysList)
    for v in keysList:
        temp=lineNumDict[v]

        for item in temp:
            programpoints[item]=actualUseduptoBlock[v]

    if file==1:
        origList=open("test_case_1.py").read().split('\n')
    elif file==2:
        origList=open("test_case_2.py").read().split('\n')
    elif file==3:
        origList=open("test_case_3.py").read().split('\n')
    elif file==4:
        origList=open("test_case_4.py").read().split('\n')
    elif file==5:
        origList=open("test_case_5.py").read().split('\n')
    else:
        print("Something wrong: No matching input file")
        return
    optimizedCodeIndex=0;

    finalCode='';
    global variables
    global defined 
    global used
    global faintVariables
    global actualUsed
    global allVariables
    global Variables
    global lineType

    used=[];
    defined=[];
    variables=[];
    optStartline=lineNumDict[next(iter(lineNumDict))][0]
    #print(optStartline)
    i=0
    for line in origList:
        if line.find('while')>=0 or line.find('if')>=0 or line.find('elif')>=0 or line.find('else')>=0 or line.find('def')>=0:
            finalCode+=line+"\n";
            optimizedCodeIndex+=1;
        elif len(line)==0:
            #print("len",optimizedList[optimizedCodeIndex]);
            pass;
        else:
            used=[];
            defined=[];
            variables=[];
            # origCode=line.replace(' ','');
            # origCode=line.replace(';','');
            line1=line.lstrip()
            #print(line1)
            j=i+1
            if j>=int(optStartline):

                code=ast2json(parse(line1));

                FindFaintAssignment(code["body"])
                #print('defined:',defined)
                if defined:
                    temp=programpoints[j]
                    #print(i)
                    #print(temp)
                    for item in defined:
                        if item in temp:
                            finalCode+=line+"\n";
                            optimizedCodeIndex+=1;
                else:
                    finalCode+=line+"\n";
                    optimizedCodeIndex+=1;
            else:
                finalCode+=line+"\n";
                optimizedCodeIndex+=1;

        i+=1
    correctCode=""
    tempList=finalCode.split('\n')
    
    #print(tempList)
    i=0
    l=len(tempList)
    for item in tempList:
        if item.endswith(':'):
            if i+1>=l:
                tempList[i]+='pass'
            else:
            
                indenti=len(tempList[i])-len(tempList[i].lstrip())
                indentj=len(tempList[i+1])-len(tempList[i+1].lstrip())

                # print(indenti)
                # print(indentj)
                if indenti>=indentj:
                    #print("True")
                    tempList[i]+='pass'
        i+=1

    #print(tempList)
    finalCode=''
    for line in tempList:
        finalCode+=line+"\n";
    print("\n____________________________________________________________")

    print("Optimized Code for file :",file)
    print(finalCode)
    if file==1:
        outputFile=open('output1.py', 'w');
        outputFile.write(finalCode)
        outputFile.close()
    elif file==2:
        outputFile=open('output2.py', 'w');
        outputFile.write(finalCode)
        outputFile.close()
    elif file==3:
        outputFile=open('output3.py', 'w');
        outputFile.write(finalCode)
        outputFile.close()
    elif file==4:
        outputFile=open('output4.py', 'w');
        outputFile.write(finalCode)
        outputFile.close()
    elif file==5:
        outputFile=open('output5.py', 'w');
        outputFile.write(finalCode)
        outputFile.close()
    actualUsed=[]
    allVariables=[]
    lineType=""
    Variables=[]
    variables=[]
    used=[]
    defined=[]
    actualUseduptoBlock={}


