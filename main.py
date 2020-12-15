import requests
import time
import json
import random
import hashlib
from colorama import Fore, Back, Style, init

# dev
# yun -> 50ad6d79df38dda1d5d52398ee5c0966
# lei -> 3e953f253116cfe0a16676af3577fdbd
TOKEN = '3e953f253116cfe0a16676af3577fdbd'
ERROR_RATE = 20    # 0-100之间 错误概率百分比，设置为 0 可能导致被封号！
VERSION = 1.3

init()
session = requests.Session()
requests.packages.urllib3.disable_warnings()

headers = {
    'UserToken': TOKEN,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1301.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
    'Content-Type': 'application/json;charset=UTF-8',
    'Referer': 'https://app.vocabgo.com/student/',
    'Origin': 'https://app.vocabgo.com'
}


def sign(p):
    lst = []

    def format(s):
        if type(s) == list or type(s) == dict:
            return json.dumps(s, separators=(',', ':'))
        else:
            return str(s)

    [lst.append(key + '=' + format(p[key])) for key in p.keys()]
    temp = '&'.join(sorted(lst))
    temp = temp + 'ajfajfamsnfaflfasakljdlalkflak'  # key
    md5sign = hashlib.md5()
    md5sign.update(temp.encode('utf-8'))
    p['sign'] = md5sign.hexdigest()
    return json.dumps(p)


def apipost(uri, pat):
    while True:
        try:
            pat['timestamp'] = int(time.time() * 1000)
            pat['versions'] = '1.2.0'
            return session.post('https://gateway.vocabgo.com' + uri, headers=headers, data=sign(pat), verify=False)
        except:
            print(Fore.RED, 'apipost:', 'Error!', 'Retrying...')
            time.sleep(10)


def apiget(uri):
    while True:
        try:
            return session.get('https://gateway.vocabgo.com' + uri
                               + '&timestamp=' + str(int(time.time() * 1000))
                               + '&versions=1.2.0', headers=headers, verify=False)
        except:
            print(Fore.RED, 'apiget:', 'Error!', 'Retrying...')
            time.sleep(10)


# topic_mode = 0


def getUserTasks(course_id):
    tasks = []
    req = apiget('/Student/StudyTask/List?course_id=' + course_id)
    ret = json.loads(req.content.decode())
    print(Fore.YELLOW + '[*] UserTasks:')
    for task in ret['data']['task_list']:
        if task['progress'] != 100:
            tasks.append(task)
            print(Fore.YELLOW + '    -', task['task_name'], '(id:' + str(task['task_id']) + ')')
    return tasks


def getClassTasks():
    tasks = []
    req = apiget('/Student/ClassTask/List?page_count=1&page_size=50')
    ret = json.loads(req.content.decode())
    print(Fore.YELLOW + '[*] ClassTasks:')
    for task in ret['data']['task_list']:
        if task['start_time'] + task['over_time'] > int(time.time() * 1000) and task['progress'] != 100:
            tasks.append(task)
            print(Fore.YELLOW + '    -', task['task_name'], '(id:' + str(task['task_id']) + ')')
    return tasks


def chooseWord(taskid, task_type, course_id='', list_id='', grade=-1):
    if course_id != '':
        uri = '/Student/StudyTask/ChoseWordList'
    else:
        uri = '/Student/ClassTask/ChoseWordList'

    chosedWords = {}

    req = apiget(uri + '?task_id=' + str(taskid) + '&task_type=' + str(task_type)
                 + ('&course_id=' + course_id if course_id != '' else '')
                 + ('&list_id=' + list_id if list_id != '' else '')
                 + ('&grade=' + str(grade) if grade >= 0 else ''))

    ret = json.loads(req.content.decode())
    for word in ret['data']['word_list']:
        if word['progress'] != 100:
            key = word['course_id'] + ':' + word['list_id']
            if key not in chosedWords:
                chosedWords[key] = []
            chosedWords[key].append(word['word'])

    print(Fore.WHITE + 'Choosing Words <==', json.dumps(chosedWords))

    data = {
        'task_id': taskid,
        'word_map': chosedWords,
        'chose_err_item': 2,
        'reset_chose_words': 1
    }

    req = apipost('/Student/ClassTask/SubmitChoseWord', data)
    ret = json.loads(req.content.decode())
    print(Fore.WHITE + 'Chosed', '->', ret)
    return ret['data']['task_id']


def getFirstTopic(taskid, task_type, release_id=-1, course_id='', list_id='', grade=-1):
    if course_id != '':
        uri = '/Student/StudyTask/StartAnswer'
    else:
        uri = '/Student/ClassTask/StartAnswer'

    req = apiget(uri + '?task_id=' + str(taskid) + '&task_type=' + str(task_type)
                 + ('&release_id=' + str(release_id) if release_id >= 0 else '')
                 + ('&course_id=' + course_id if course_id != '' else '')
                 + ('&list_id=' + list_id if list_id != '' else '')
                 + ('&grade=' + str(grade) if grade >= 0 else '')
                 + '&opt_img_w=2920&opt_font_size=162&opt_font_c=%23000000&it_img_w=3432&it_font_size=184')
    ret = json.loads(req.content.decode())
    print(Fore.WHITE + 'Init First Topic <==', ret)

    if ret['code'] == 20001:
        return getFirstTopic(chooseWord(taskid, task_type, course_id=course_id, list_id=list_id, grade=grade),
                             task_type, release_id=release_id, course_id=course_id, list_id=list_id, grade=grade)

    elif ret['code'] != 1:
        handle_err(-98, '出现未知错误！\n', ret)
    if ret['data']['topic_mode'] == 0:
        data = {
            'topic_code': ret['data']['topic_code'],
            'opt_img_w': '2920',
            'opt_font_size': '162',
            'opt_font_c': '#000000',
            'it_img_w': '3432',
            'it_font_size': '184'
        }

        req = apipost('/Student/ClassTask/SkipNowTopicMode', data)
        ret = json.loads(req.content.decode())
        print(Fore.WHITE + 'SKIPING', '<==', ret)

    return ret['data']['topic_code']


def verifyAnswer(topic, answer, study_task=False):
    if study_task:
        uri = '/Student/StudyTask/VerifyAnswer'
    else:
        uri = '/Student/ClassTask/VerifyAnswer'

    data = {
        'answer': answer,
        'topic_code': topic
    }

    req = apipost(uri, data)
    ret = json.loads(req.content.decode())
    print(Fore.WHITE + 'VERIFY', answer, '<==', ret)
    return ret


def getAnswer(topic, study_task=False):
    while True:
        answer = random.randrange(0, 3)

        ret = verifyAnswer(topic, answer, study_task=study_task)
        topic = ret['data']['topic_code']

        if 'answer_corrects' in ret['data']:
            temp = ret['data']['answer_corrects']
            if type(temp) == list and len(temp) == 1 and type(temp[0]) == str:
                return [','.join(temp[0].replace('...', '').split(' '))]
            return temp


def getProcess(n, total):
    num = int(n/total*20)
    return '['+'█'*num+' '*(20-num)+'] ' + str(n) + '/' + str(total)


def isError():
    r = random.randrange(1, 100)
    if r <= ERROR_RATE:
        return True
    return False


def getErrAnswer(answer):
    if type(answer) == list:
        if type(answer[0]) == str and len(answer) == 1:
            temp = answer[0].replace('...', '').split(' ')
            random.shuffle(temp)
            return ','.join(temp)
        if type(answer[0]) == int and len(answer) >= 1:
            return random.randrange(0, max(answer)+5)   # 这里 +5 是为了增大错误概率

    return random.randrange(0, 3)


def submitAnswer(topic, study_task=False):
    answers = getAnswer(topic, study_task=study_task)
    print(Fore.GREEN + '==> Get Answer: ', answers)

    temp_topic = topic

    if isError():
        while True:
            errAnswer = getErrAnswer(answers)
            ret = verifyAnswer(temp_topic, errAnswer, study_task=study_task)
            temp_topic = ret['data']['topic_code']

            # 1=true 2=false    over_status=1 and clean_status=1才能提交
            if ret['data']['over_status'] == 1 and ret['data']['clean_status'] == 1:
                # print(Fore.GREEN + '==> Submited')
                print(Fore.GREEN + '==> Submit Error Answer:', errAnswer)
                return temp_topic
    else:
        for answer in answers:
            ret = verifyAnswer(temp_topic, answer, study_task=study_task)
            temp_topic = ret['data']['topic_code']

            # 1=true 2=false    clean_status=1才能提交
            if ret['data']['answer_result'] == 1 and ret['data']['clean_status'] == 1:
                # print(Fore.GREEN + '==> Submited')
                return temp_topic

    return None


def handle_err(code, *args):
    print(Fore.RED + '======ERROR ' + str(code) + '======\n', *args)
    exit(code)


def doMain(firstTopic, study_task=False):
    if study_task:
        uri = '/Student/StudyTask/SubmitAnswerAndSave'
    else:
        uri = '/Student/ClassTask/SubmitAnswerAndSave'

    topic = firstTopic

    while True:
        topic = submitAnswer(topic, study_task=study_task)

        if topic is None:
            handle_err(-99, '暂未支持该题型，请提交 issue 并附带所有输出信息！')

        delay = random.randrange(800, 12000)

        data = {
            'topic_code': topic,
            'time_spent': delay,
            'opt_img_w': '2920',
            'opt_font_size': '162',
            'opt_font_c': '#000000',
            'it_img_w': '3432',
            'it_font_size': '184'
        }

        print(Fore.GREEN + '[*] Sleeping:', delay)
        time.sleep(delay / 1000)

        req = apipost(uri, data)
        ret = json.loads(req.content.decode())

        print(Fore.GREEN + 'SUBMIT <==', Fore.WHITE, ret)

        if ret['code'] != 1 and ret['code'] != 20001:
            handle_err(-90, '未知错误！\n', data, '\n', ret)

        if 'topic_done_num' in ret['data'] and 'topic_total' in ret['data']:
            print(Fore.BLUE + 'Process:', getProcess(ret['data']['topic_done_num'], ret['data']['topic_total']))

        if 'topic_code' in ret['data']:
            topic = ret['data']['topic_code']
            continue

        print(Fore.YELLOW + 'DONE!')
        break


# grade: 模式 1=快速 2=普通 3=完整
def doUserTask(course_id, grade):
    for task in getUserTasks(course_id):
        req = apiget('/Student/StudyTask/Info?task_id=-1&course_id=' + course_id + '&list_id=' + task['list_id'])
        ret = json.loads(req.content.decode())
        print(Fore.YELLOW + '====== Doing User Task:', task['list_id'], '======')
        doMain(getFirstTopic(ret['data']['task_id'], task['task_type'], course_id=course_id, list_id=task['list_id'],
                             grade=grade), study_task=True)


def doClassTask():
    for task in getClassTasks():
        print(Fore.YELLOW + '====== Doing Class Task:', task['task_name'], '======')
        doMain(getFirstTopic(task['task_id'], task['task_type'], release_id=task['release_id']))
        time.sleep(10)


# ret = course_id
def getCourse():
    req = apiget('/Student/Course/List?')
    ret = json.loads(req.content.decode())
    print(Fore.YELLOW + '课本列表：')
    for (index, book) in enumerate(ret['data']['course_info_list']):
        print(Fore.YELLOW + '[' + str(index) + '] -', book['name'])
    index = int(input(Fore.BLUE + '[+] 请输入选择的课本序号：'))
    return ret['data']['course_info_list'][index]['course_id']

def getName():
    req = apiget('/Student/Main?')
    ret = json.loads(req.content.decode())
    if ret['code'] != 1 or 'user_info' not in ret['data']:
        handle_err(-97, '请检查TOKEN是否有效，Token一般是32位小写字符，请参考wiki修改token')
    return ret['data']['user_info']['student_name']

def printWelcome():
    print('''
              _____                    _____                    _____          
             /\    \                  /\    \                  /\    \         
            /::\    \                /::\    \                /::\    \        
           /::::\    \              /::::\    \              /::::\    \       
          /::::::\    \            /::::::\    \            /::::::\    \      
         /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \     
        /:::/  \:::\    \        /:::/  \:::\    \        /:::/__\:::\    \    
       /:::/    \:::\    \      /:::/    \:::\    \      /::::\   \:::\    \   
      /:::/    / \:::\    \    /:::/    / \:::\    \    /::::::\   \:::\    \  
     /:::/    /   \:::\    \  /:::/    /   \:::\ ___\  /:::/\:::\   \:::\____\ 
    /:::/____/     \:::\____\/:::/____/     \:::|    |/:::/  \:::\   \:::|    |
    \:::\    \      \::/    /\:::\    \     /:::|____|\::/   |::::\  /:::|____|
     \:::\    \      \/____/  \:::\    \   /:::/    /  \/____|:::::\/:::/    / 
      \:::\    \               \:::\    \ /:::/    /         |:::::::::/    /  
       \:::\    \               \:::\    /:::/    /          |::|\::::/    /   
        \:::\    \               \:::\  /:::/    /           |::| \::/____/    
         \:::\    \               \:::\/:::/    /            |::|  ~|          
          \:::\    \               \::::::/    /             |::|   |          
           \:::\____\               \::::/    /              \::|   |          
            \::/    /                \::/____/                \:|   |          
             \/____/                  ~~                       \|___|          
                                                                               ''')
    print('                            词达人自动化脚本 v' + str(VERSION))
    print(Fore.YELLOW+'你好', getName(),'，请选择功能：\n', '[0] - 自动完成课本练习\n', '[1] - 自动完成班级任务')
    mode = int(input())
    if mode == 0:
        doUserTask(getCourse(), 3)
    elif mode == 1:
        doClassTask()


printWelcome()
