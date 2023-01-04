def parseTranslations():
    file = open("test3.txt", 'r', encoding="utf8")
    contents = file.read()
    contentSplit = contents.split("`")
    headers = []
    body = []  # ["Robbery|In your...", ...]
    bodyFinal = []  # [["Robbery", "In your..."], ["Send Fence", "Whenever another..."], ...]
    for i in range(len(contentSplit)):
        if i % 2 == 0:
            headers.append(contentSplit[i])
        else:
            body.append(contentSplit[i].replace("\n", ""))
    for desc in body:
        temp = desc.split("|")
        tempStore = []
        temptemp = []
        for i in range(len(temp)):
            if i % 2 == 0:
                tempLst = ["^", temp[i] + "@"] + list(filter(lambda x: x != "", [x.replace(
                    "â™\xa0", "♠").replace("\xa0", "") for x in temp[i+1].split(" ")]))
                tempStore.append(tempLst)
        for i in range(len(tempStore)):
            temptemp = temptemp + tempStore[i]
        bodyFinal.append(temptemp)
    for desc in bodyFinal:
        for i, word in enumerate(desc):
            if "â™¦" in word:
                desc[i] = "♦"
            if "â™£" in word:
                desc[i] = "♣"
            if "â™\xa0" in word:
                desc[i] = "♠"
            if "â™¥" in word:
                desc[i] = "♥"
            if "ðŸ—²" in word:
                desc[i] = "🗲"
            if "â˜¯" in word:
                desc[i] = "☯"
            if "â€¢" in word:
                desc[i] = "•"
            if "â—†" in word or "◆" in word:
                desc[i] = "♦"
    return headers, bodyFinal
