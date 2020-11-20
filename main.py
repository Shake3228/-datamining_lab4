import math
import re
import networkx as nx
import matplotlib.pyplot as plt
import operator
from bs4 import BeautifulSoup
import requests

badExtensions = ['.digital', '.hash', '.eps', '.ppt', '.pptx', '.pdf', '.jpeg', '.jpg', '.png', '.gif', '.rar',
                 '._gromad', '.doc', '.txt', '.xls', '.xml', '.zip']
d = 0.5
E = 0.001
allKink = []
G = nx.DiGraph()
dictNumToLink = dict()
dictNumToCountOfLink = dict()
checkedLink = []


def cleanFromHTTPorHTTPS(url):
    if url[4] == 's':
        return url[5:]
    else:
        return url[4:]


def validation(href, mHref, internalLink):
    for i in badExtensions:
        if i in href:
            return False
    if '#' in href:
        return False
    if '?' in href:
        return False
    if href == mHref:
        return False
    if href in internalLink:
        return False
    return True


numOfLink = 0


def recursion(mHref):
    global numOfLink
    global dictNumToLink
    checkedLink.append(mHref)
    internalLink = []
    page = requests.get(mHref)
    data = page.text
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all('a', href=re.compile('^(/)')):  # this for /j/j/j/j
        href = link.get('href')
        href = url + href[1:]
        if validation(href, mHref, internalLink):
            if href not in dictNumToLink.keys():
                dictNumToLink[href] = numOfLink
                numOfLink = numOfLink + 1
            internalLink.append(href)

            G.add_edge(dictNumToLink[mHref], dictNumToLink[href])
            if href in checkedLink:
                continue

            print("mhref = " + mHref)
            print("href = " + href)
            recursion(href)

    allSoup = soup.find_all('a', href=re.compile('^http[s]{0,1}' + urlCut + '.*\.html'))
    allSoup = allSoup + soup.find_all('a', href=re.compile('^http[s]{0,1}' + urlCut + '.*$'))
    for link in allSoup:
        href = link.get('href')
        if validation(href, mHref, internalLink):
            internalLink.append(href)
            if href not in dictNumToLink.keys():
                dictNumToLink[href] = numOfLink
                numOfLink = numOfLink + 1

            G.add_edge(dictNumToLink[mHref], dictNumToLink[href])
            if href in checkedLink:
                continue

            print("mhref = " + mHref)
            print("href = " + href)
            recursion(href)
    dictNumToCountOfLink[dictNumToLink[mHref]] = len(internalLink)
    G.add_node(dictNumToLink[mHref])
    return


def printGraf():
    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all('a', href=re.compile('^(/)')):
        href = link.get('href')
        print(url + href)
    allSoup = soup.find_all('a', href=re.compile('http[s]{0,1}.' + urlCut + '*\.html'))
    allSoup = allSoup + soup.find_all('a', href=re.compile('http[s]{0,1}' + urlCut + '.*/$'))
    for link in allSoup:
        href = link.get('href')
        print(href)


def jakobian(B):
    global dictNumToLink
    solveVector = []
    newvector = []
    for i in range(0, len(B)):
        solveVector.append(B[i][len(B)])
    eps = 1
    while eps > E:
        for i in range(0, len(B)):
            sum = 0
            for j in range(0, len(solveVector)):
                sum = sum + solveVector[j] * B[i][j]
            sum = sum + B[i][len(B)]
            newvector.append(sum)
        eps = 0
        for j in range(0, len(solveVector)):
            eps = eps + math.fabs(newvector[j] - solveVector[j])

        solveVector = newvector.copy()
        newvector.clear()
    finalDict = dict()
    for j in range(0, len(solveVector)):
        finalDict[j] = solveVector[j]
    finalDict = sorted(finalDict.items(), key=operator.itemgetter(1), reverse=True)
    print(finalDict)
    print("Max")
    for j in range(0, 10):
        print('| ', j + 1, ".", list(dictNumToLink.keys())[list(dictNumToLink.values()).index(finalDict[j][0])],
              "Range:", finalDict[j][1])
    print("_____________________________________")


url = input('Enter website: ')
urlCut = cleanFromHTTPorHTTPS(url)
dictNumToLink[url] = numOfLink
numOfLink = numOfLink + 1
recursion(url)
nx.draw(G, with_labels=True)
plt.show()
print(dictNumToLink)
B = [[0 for x in range(len(G.nodes) + 1)] for y in range(len(G.nodes))]
for n in G.edges:
    B[n[1]][n[0]] = d / dictNumToCountOfLink[n[0]]
print(len(G.nodes))
for i in range(0, len(G.nodes)):
    B[i][len(G.nodes)] = 1 - d

jakobian(B)
pr = nx.pagerank(G)
print(pr)
