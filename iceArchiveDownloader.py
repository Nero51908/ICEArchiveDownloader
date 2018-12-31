import requests
from bs4 import BeautifulSoup
import re
import time
import os
ice2017 = 'http://ice-archive2017.xjtlu.edu.cn/login/index.php'
headers = {
'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
}
payload = {
 'username':'',
 'password':''
}
iceS = requests.session()
indexPage = iceS.post(ice2017, headers=headers, data=payload)
print('> Current position: '+indexPage.url)
# get module information
soup = BeautifulSoup(indexPage.content,features="html5lib")
seen = set()
moduleLinks = list()
moduleNames = list()
for page in soup.find_all('a', string=re.compile(r'EEE'), href=True):
    if not (page.string in seen):
        moduleLinks.append(page['href'])
        moduleNames.append(page.string)
        seen.add(page.string)
        print(f'target: {page.string} added.')
print(f'{len(moduleLinks)} targets loaded. Searching for downloadable courseworks.')
# iterate moduleLinks
for moduleIndex,moduleLink in enumerate(moduleLinks):
    print(moduleNames[moduleIndex], f'[{moduleLink}]')
    modulePage = iceS.get(moduleLink, headers=headers, stream=True)
    soup = BeautifulSoup(modulePage.content,features="html5lib")
    # for one modulePage, find assignment pages
    if os.path.exists(f'./{moduleNames[moduleIndex].replace("/","-")}'):
        continue
    else:
        for assignmentIndex, assignmentLink in enumerate(soup.find_all(class_='activity assign modtype_assign ')):
            assignmentPage = iceS.get(assignmentLink.a['href'], headers=headers, stream=True)
            soup = BeautifulSoup(assignmentPage.content,features="html5lib")
            try:
                downloadLinks = soup.find_all('a',href=re.compile('forcedownload'))
                for downloadLink in downloadLinks:
                    fileName = downloadLink.string
                    pathName = f'./{moduleNames[moduleIndex].replace("/","-")}/Assingment{assignmentIndex+1}/'
                    # save the downloaded file
                    if not os.path.exists(pathName):
                        os.makedirs(pathName)
                    try:
                        downloadFile = iceS.get(downloadLink['href'], headers=headers, stream=True)
                        print(f'{moduleNames[moduleIndex]} submitted coursework is downloading from page: '+downloadFile.url)
                        file = open(os.path.join(pathName,fileName),'wb')
                        for chunk in downloadFile.iter_content(100000):
                            file.write(chunk)
                        file.close()
                        print('Cooling down the linke between this downloader and the server')
                        time.sleep(2)
                    except Exception as e:
                        print('Error when downloading')

            except Exception as e:
                print('This assignment doesn\'t have a download link')
                continue
