import time
import re
import configparser
import datetime
import xml.etree.ElementTree as et
import os.path
import codecs

config = configparser.ConfigParser()
config.read('config.ini')

sleepTime = int(config.get('settings', 'sleepTime'))
xmlPath = config.get("output", "xmlPath")
logPath = config.get("output", "logPath")


def process_file(config):
    logFileName = config.get('logfile', 'logFileName')
    currentDay = config.get("logfile", "currentDay")
    lastLineCount = int(config.get('settings', 'totalLineRead'))
    logFilePath = config.get("logfile", "logFilePath")
    logFileNamePrefix = config.get("logfile", "logFileNamePrefix")
    logFileNameExtension = config.get("logfile", "logFileNameExtension")

    BLOCKSIZE = os.path.getsize(logFileName)
    with codecs.open(logFileName, "r", "utf-16") as sourceFile:
        with codecs.open(logPath + logFileNamePrefix + currentDay + '_UTF_8.' + logFileNameExtension, "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)

    with open(logPath + logFileNamePrefix + currentDay + '_UTF_8.' + logFileNameExtension, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        newLineCount = len(lines)


        #nextDay = (datetime.datetime.now() + timedelta(days=1)).strftime("%d")
        if int(currentDay)< 10:
            nextDay = '0' + str(int(currentDay) + 1)
        else: nextDay = str(int(currentDay) + 1)


        currentDayLogFileName = (logFilePath + logFileNamePrefix + currentDay + '.' + logFileNameExtension)
        nextDayLogFileName = (logFilePath + logFileNamePrefix + nextDay + '.' + logFileNameExtension)

        currentDayLogFileExist = os.path.exists(currentDayLogFileName)
        nextDayLogFileExist = os.path.exists(nextDayLogFileName)
        logFilesList = os.listdir(logFilePath)

        if currentDayLogFileExist is True:
            currentLogFileModifiedTimeSec = int(os.path.getmtime(currentDayLogFileName))
        else: currentLogFileModifiedTimeSec = 0

        if currentDayLogFileExist is True:
            currentLogFileModifiedTime = datetime.datetime.fromtimestamp(currentLogFileModifiedTimeSec).strftime(
                '%Y-%m-%d %H:%M:%S')
        else: currentLogFileModifiedTime = '1970-01-01 00:00:00'

        if nextDayLogFileExist is True:
            nextDayLogFileModifiedTimeSec = int(os.path.getmtime(nextDayLogFileName))
        else:
            nextDayLogFileModifiedTimeSec = 0

        if nextDayLogFileExist is True:
            nextDayLogFileModifiedTime = datetime.datetime.fromtimestamp(nextDayLogFileModifiedTimeSec).strftime(
            '%Y-%m-%d %H:%M:%S')
        else: nextDayLogFileModifiedTime = '1970-01-01 00:00:00'

        if currentLogFileModifiedTimeSec > nextDayLogFileModifiedTimeSec:
            logFileName = currentDayLogFileName
            config.set('logfile', 'logFileName', logFileName)
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
            whatFileNewestText = "In current log file:"

        else:
            logFileName = nextDayLogFileName
            currentDay = logFileName[slice(-6, -4)]
            config.set('logfile', 'currentDay', currentDay)
            config.set('logfile', 'logFileName', logFileName)
            config.set('settings', 'totalLineRead', '1')
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
            whatFileNewestText = "Next Day file is newest"
            return

        print("Current file:", currentDayLogFileName, "Exist:", currentDayLogFileExist,
              ", Modified:", currentLogFileModifiedTime)
        print("Next file:", nextDayLogFileName, "Exist:", nextDayLogFileExist,
              ", Modified:", nextDayLogFileModifiedTime)
        print( 'File in work:', logFileName, )
        print(whatFileNewestText, newLineCount, 'lines')
        print(logFilesList)
        #print('Slice:', logFileName[slice(-6, -4)])

        if newLineCount > lastLineCount:
            with open(logPath + "output_MCS_Log.log", 'a', encoding='utf-8') as output_file:
                for line in lines[lastLineCount:]:
                    match = re.search(r'^(\S+);+\s(\S+);+\s(\S+);+\s(\S+);+\s(\S+);+\s(.*)$', line)
                    if match:
                        data1 = match.group(1)
                        time1 = match.group(2)
                        eventCode = match.group(3)
                        eventType1 = match.group(4)
                        eventType2 = match.group(5)
                        message = match.group(6)
                    # Проверяем каждую новую строку по условию
                    whatconfig = config.get('settings', 'searchmask')
                    what = r"\bCProdList::\b"
                    #what = config.get('settings', 'searchmask')
                    #what =  whatconfig
                    check = re.search(what, line)
                    # Здесь можно добавить условие, по которому выбираются нужные строки
                    if check is not None:
                        output_file.write(line)
                        dateTimeMacineEvent = data1 + ' ' + time1
                        dateTimeMacineEventFormat = datetime.datetime.strptime(dateTimeMacineEvent, "%d.%m.%y %H:%M:%S:%f")
                        dateTimeMacineEventInsight = dateTimeMacineEventFormat.strftime("%Y-%m-%d %H:%M:%S")
                        # print(dt_now)
                        # print(dt_obj)
                        # print('dt_new',dt_new)
                        # dt_now_str = datetime.datetime.now().strftime("%Y%m%d_%H%m%S")
                        # вермя с мс, для формирования различных имён файлов XML
                        dateTimeMacineEventFormatString = dateTimeMacineEventFormat.strftime("%Y%m%d_%H%M%S.%f")
                        # поля для заполнения XML
                        # mcnCode = "Schelling AH8"
                        mcnCode = config.get("machine", "mcnCode")
                        # возможно, сделать получение из типа строи в логе, когда получим ошибку или еще что то
                        # mcnetCode = "INFO"
                        mcnetCode = config.get("machine", "mcnetCode")
                        mcnepCode = "Message"
                        mcnepValue = line
                        insightVersion = config.get("machine", "insightversion")
                        filenamexml = (xmlPath + mcnCode + '_' + dateTimeMacineEventFormatString + '.xml')
                        # разбираем значащую строку : message для получения данных в отдельные параметры
                        message_parse = re.search(r'(\d{8})\D{6}(\d+)\D{9}(\d+)\D{10}(\d+)', mcnepValue)
                        if message_parse:
                            batchrun = message_parse.group(1)
                            scheme = message_parse.group(2)
                            boards = message_parse.group(3)
                            books = message_parse.group(4)
                            # print(batchrun)

                            # формируем XML
                            root = et.Element("root")
                            ident = et.SubElement(root, "Identity", DocumentType="Machine Event",
                                                  Version=insightVersion, Language="us_english")
                            me = et.SubElement(root, "MachineEvent", mcnCode=mcnCode,
                                               CreatedOn=dateTimeMacineEventInsight)
                            event = et.SubElement(me, mcnetCode, Message=message, BatchRun=batchrun, Scheme=scheme,
                                                  Books=books, Boards=boards)

                            # пишем XML
                            tree = et.ElementTree(root)
                            tree.write(f'{filenamexml}')

            config.set('settings', 'totalLineRead', str(newLineCount))
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
        return newLineCount
    #time.sleep(sleeptime)
while True:
    lastLineCount = process_file(config)
    time.sleep(sleepTime)

