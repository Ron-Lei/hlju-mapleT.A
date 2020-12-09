from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import re



class HdMath:

    __charpterId=Queue(maxsize=0) #章节id
    __answerCList=Queue(maxsize=0) #选择题答案
    __answerFList=Queue(maxsize=0) #填空题答案
    __userid:str
    __password:str
    __timeoutCountrol:int=1

    def __init__(self):
       self.option=webdriver.ChromeOptions() 
       self.option.add_argument('--ignore-certificate-errors')
       #self.option.add_argument('--headless')    #去掉以下三个#即为无头模式，不显示浏览器窗口
       #self.option.add_argument('--disable-gpu')
       #self.option.add_argument('--no-sandbox') 
       try:
           self.driver=webdriver.Chrome(options=self.option)
       except:
           self.driver.quit()
           raise     

    def loginHD(self):
        try:
            self.__userid=input("-----请输入学号,输入0退出：\n")
            if self.__userid=="0":
               self.driverQuit()
               return 0
            else:
               self.__password=input("-----请输入密码: \n")
               self.__timeoutCountrol=input("-----请输入超时等待，默认为1(即1s).  若出现上机人数过多导致脚本运行不正常，请尝试将此项调节为5或更高: \n")

            self.driver.get("http://125.223.1.242/mapleta/login/login.do")
            WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
            useridText=self.driver.find_element_by_id("LoginActionForm.login")
            useridText.clear()
            useridText.send_keys(self.__userid)

            passwordText=self.driver.find_element_by_id("LoginActionForm.password")
            passwordText.clear()
            passwordText.send_keys(self.__password)
    
            self.driver.find_element_by_id("loginButton").submit()       
            try:
                time.sleep(1)
                self.driver.switch_to.alert.accept()  # 若弹出警告弹窗，则进行确认
            except:   
                return
            return 1        
        except Exception:
            raise Exception("-----登录失败，请检查学号和密码")

            


    def getTestId(self):    
        print("-----登陆成功，开始获取章节数\n")
        WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
        self.driver.find_element_by_class_name("odd").click()
        WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
        courseList=self.driver.find_elements_by_class_name("noBorder.name")   #在selenium中 标签属性值中有空格则用.代替

        chapterNumber:int=1
        for course in courseList:
            try:   #获取已解锁章节的id以及显示章节名称
                chapterHref=course.find_element_by_xpath("a").get_attribute("href")
                chapterName=course.find_element_by_xpath("a").text
                print(str(chapterNumber)+"  "+str(chapterName))
                pattern="testId=(\w)*"
                testIdNumber=re.search(pattern,chapterHref).group(0)
                self.__charpterId.put(testIdNumber)
                chapterNumber=chapterNumber+1
            except:
                continue



    #指定章节刷取            
    def doAnswer(self):
        while 1:
            mode=input("-----请输入章节序号刷取特定章节,或输入all进行全已解锁章节刷取  输入0结束刷取并切换账号:\n")
            try:
                #判断模式
                if(str(mode)=="0"):
                    break 
                elif(str(mode).lower()!="all"):
                    for i in range(1,int(mode)+1):
                        testId=self.__charpterId.get()
                    self.doAnswerWithMode(testId)
                elif(str(mode).lower()=="all"):
                    # 章节循环
                    while 1:
                        testId=self.__charpterId.get()
                        self.doAnswerWithMode(testId)
                        if self.__charpterId.empty():    
                            print("-----章节为空")        
                            break    
            except Exception as e:
                print(e)             

    #开始
    # 从_charpterherf中取出对应url，组装章节url，组装答案url
    # 分题目类型提取答案，分题目类型提交答案，提交测试
    def doAnswerWithMode(self,testId):
            try:
                testUrl="http://125.223.1.242/mapleta/modules/test.Test?"+testId  # url部分删除了launch_presentation_document_target=window来禁止maple开启新窗口

                # 防止答题到一半，先直接提交一次保证从头开始
                print("-----正在初始化章节")
                self.driver.get(testUrl)
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                time.sleep(1)
                for check in range(2):
                    self.driver.find_element_by_id("MenuItem.actions.assignment.grade").click()
                    WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                    time.sleep(1)

                # 从零开始
                print("-----准备开始")
                self.driver.get(testUrl)
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                time.sleep(1)
                self.driver.find_element_by_id("MenuItem.actions.assignment.grade").click()
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                time.sleep(1)    
                self.driver.find_element_by_id("MenuItem.actions.assignment.back").click()
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)   # 先跳转到提交页面再回到第一题，确保接下来的答案页面生成正确的答案

                answerUrl="window.open(\"http://125.223.1.242:80/mapleta/modules/gradeProctoredTest.Login?currPage=1&"+testId+"&actionID=viewdetails\");"
                self.driver.execute_script(answerUrl)
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)

                handleArray=self.driver.window_handles
                self.driver.switch_to_window(handleArray[1]) # 切换至答案窗口
                

                # 获取answer
                print("-----开始获取答案")
                WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                charpterQuestions=self.driver.find_elements_by_class_name("questionstyle")
                questionControl=2
                questionNumber=1
                for question in charpterQuestions:
                    fanswerList=question.find_elements_by_class_name("part-answer")
                    if(len(fanswerList)==0):    
                        # 部分答案不在p标签中
                        time.sleep(int(self.__timeoutCountrol))
                        try:
                            canswer=question.find_element_by_xpath("//*[@id=\"pageContainer\"]/form/div/div[2]/div["+str(questionControl)+"]/table[2]/tbody/tr[2]/td[2]/p").text
                            canswer=repr(str(canswer).replace('\n',"").replace(' ',""))
                            print(str(questionNumber)+"     "+canswer)
                            self.__answerCList.put(canswer)
                        except:
                            fanswer=question.find_element_by_xpath("//*[@id=\"pageContainer\"]/form/div/div[2]/div["+str(questionControl)+"]/table[2]/tbody/tr[2]/td[2]").text
                            fanswer=str(fanswer).replace('\n',"").replace(' ',"")
                            print(str(questionNumber)+"     "+fanswer)
                            self.__answerFList.put(fanswer)
                    else:
                        for fanswer in fanswerList:
                            print(str(questionNumber)+"     "+fanswer.text)
                            self.__answerFList.put(fanswer.text)
                    questionControl=questionControl+1
                    questionNumber=questionNumber+1    
                self.driver.close()       
                print("-----获取结束")


                # 开始填写answer
                print("-----开始填写answer")
                self.driver.switch_to_window(handleArray[0])
                time.sleep(1)
                answerNumber=1
                while 1:
                    # 根据题目类型做相应处理
                    WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                    textBlankList=self.driver.find_elements_by_class_name("blankenabled.form-control")
                    if(len(textBlankList)==0):
                        print("--选择题")
                        choicesGroup=self.driver.find_element_by_class_name("response.multiCh.multiChVertical")
                        canswer=self.__answerCList.get()
                        trControl=1  
                        while 1:
                            try:    
                                choicesContent=choicesGroup.find_element_by_xpath(".//tbody/tr["+str(trControl)+"]/td[3]/label/p").text
                                choicesContent=repr(str(choicesContent).replace('\n',"").replace(' ',""))
                                print(choicesContent)
                                if canswer==choicesContent:
                                    choicesGroup.find_element_by_xpath(".//tbody/tr["+str(trControl)+"]/td[2]").find_element_by_tag_name("input").click()
                                    print(str(answerNumber)+"     "+canswer)
                                    break
                                trControl=trControl+1
                            except:
                                break
                                pass
                    else:
                        for textBlank in textBlankList:
                            print("--填空题")
                            fanswer=self.__answerFList.get()
                            textBlank.send_keys(fanswer)
                            print(str(answerNumber)+"     "+fanswer)
                    answerNumber=answerNumber+1
                                    
                    if self.__answerCList.empty() and self.__answerFList.empty():
                        self.driver.find_element_by_id("MenuItem.actions.assignment.grade").click()
                        break    
                    self.driver.find_element_by_id("MenuItem.actions.assignment.next").click()
                    WebDriverWait(self.driver,timeout=10).until(EC.presence_of_all_elements_located)
                    time.sleep(int(self.__timeoutCountrol))
                print("-----填写结束")                     
            except Exception as e:
                raise
       

    def start(self):
        try:
            while self.loginHD():
                self.getTestId()
                self.doAnswer()
        except Exception as e:
            print("-----运行出错，尝试重新启动脚本")
            self.driverQuit()

            
    #对应资源释放        
    def driverQuit(self):
        self.__userid=None
        self.__password=None
        self.driver.quit()      

    
    
      
