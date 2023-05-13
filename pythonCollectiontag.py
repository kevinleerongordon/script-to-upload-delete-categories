import json

import numpy as np
import requests
import pandas as pd
import datetime
import time

overwritecollections = True
fileDownload = True
manualCollectionData = True


def createCollection(website, password, inputPath, outputPath,collectionskip,manualCollectionPath):
    global overwritecollections
    global fileDownload
    extData = []
    # Replace <SHOP_NAME> with your Shopify store name
    # Replace <ACCESS_TOKEN> with your Shopify access token
    website = str(website)
    shop_url = f"https://{website}/admin/api/2023-01/smart_collections"
    shop_url_manual = f"https://{website}/admin/api/2023-01/custom_collections"
    headers = {
        # "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"
        "X-Shopify-Access-Token": str(password),
        "Content-Type": "application/json"
    }
    x = datetime.datetime.now()

    # Read the data from an Excel file
    filePath = str(inputPath)
    df = pd.read_csv(filePath)
    df = df.replace(np.nan, None)
    errorResponse = ""
    exsitingData = []
    manualData = []
    count = 0
    # Loop through the rows in the dataframe
    for index, row in df.iterrows():
        # global count
        # global count
        newRules = []

        # print(row["Rules"])
        # checking the collection if exists or not
        def deleteData(removeCheck, handle1):
            deleteResponse = requests.get(shop_url + ".json", headers=headers)
            deleteCollections = deleteResponse.json()



            def deleteCollection(ID):
                deleteCollectionResponce = requests.delete(shop_url + "/" + str(ID) + ".json", headers=headers)
                # print(deleteCollectionResponce.status_code)
                time.sleep(2)
                if deleteCollectionResponce.status_code == 200:
                    return "Deleted"

            for deleteCollectionsData in deleteCollections['smart_collections']:
                if removeCheck:
                    if deleteCollectionsData['id'] == handle1:
                        dele = deleteCollection(deleteCollectionsData['id'])
                        return dele


        def deleteManualData(removeCheck, handle1):
            print("here")
            deleteResponse = requests.get(shop_url_manual + ".json", headers=headers)
            deleteCollections = deleteResponse.json()



            def deleteCollection(ID):
                deleteCollectionResponce = requests.delete(shop_url_manual + "/" + str(ID) + ".json", headers=headers)
                # print(deleteCollectionResponce.status_code)
                if deleteCollectionResponce.status_code == 200:
                    return "Manual Deleted"

            for deleteCollectionsData in deleteCollections['custom_collections']:
                if removeCheck:
                    if deleteCollectionsData['id'] == handle1:
                        dele = deleteCollection(deleteCollectionsData['id'])
                        return dele

        # count = 0
        def overWrite(overWriteCheck, handle1):
            collectionResponses = requests.get(shop_url + ".json", headers=headers)
            smartCollections = collectionResponses.json()
            for smartCollectionDatas in smartCollections['smart_collections']:
                if smartCollectionDatas['handle'] == handle1:
                    def deleteCollections(ID):
                        # print(ID)
                        deleteCollectionResponce = requests.delete(shop_url + "/" + str(ID) + ".json", headers=headers)
                        # print(deleteCollectionResponce.json())
                        if deleteCollectionResponce.status_code == 200:
                            return "DeletedOver"

                    if overWriteCheck:
                        return deleteCollections(smartCollectionDatas['id'])
                    else:
                        print("No need")

        count += 1
        if row['Remove'] and row['id']:

            deleteStatus = deleteData(row['Remove'], row['id'])

            print(deleteStatus)

            if deleteStatus == None :
                deleteStatusmanual  = deleteManualData(row['Remove'], row['id'])
                print(deleteStatusmanual)
        else:
            deleteStatus = "No Need"
        if not row['Remove'] and overwritecollections:
            odel = overWrite(overwritecollections, row['Handle'])
        else:
            odel = "Not Delete"
        # if count == 1:
        # checkCollection()

        try :
            if deleteStatus != "Deleted" or odel == 'Deleted':
                print(row["Rules"])

                Rule = row["Rules"]
                parentRule = Rule.replace('*', '')
                childRule = "and"

                if childRule in parentRule:
                    rulesNew = parentRule.split(childRule)
                    for r in rulesNew:
                        rulesNew1 = r.split("|")
                        print(rulesNew1[0].strip())
                        dictionary = {"column": str(rulesNew1[0].strip()), "relation": str(rulesNew1[1]),
                                      "condition": str(rulesNew1[2])}
                        newRules.append(dictionary)
                else:
                    Rules = row["Rules"].split("|")
                    rulesNew2 = {"column": str(Rules[0]), "relation": str(Rules[1]), "condition": str(
                        Rules[2])}
                    newRules.append(rulesNew2)
                # Define the data for the smart collection
                if row["Body (HTML)"]:
                    html = row["Body (HTML)"]
                else:
                    html = ''
                if row["Template Suffix"]:
                    template = row["Template Suffix"]
                else:
                    template = ''
                if row["Image"]:
                    image = row["Image"]
                else:
                    image = ''
                if row["Disjunctive"]:
                    disjunctive = 1
                else:
                    disjunctive = 0
                if row["Published"]:
                    published = 1
                else:
                    published = 0
                # print(str(image))
                data = {
                    "smart_collection": {
                        "title": row["Title"],
                        "handle": row["Handle"],
                        "disjunctive": disjunctive,
                        "sort_order": row["Sort Order"],
                        "rules": newRules,
                        "published": published,
                        "published_scope": row["Published_Scope"],
                        "image": {

                            "alt": row["Handle"],
                            "width": 1,
                            "height": 1,
                            "src": str(image)
                        }
                    }
                }
                data = json.dumps(data)

                # Make a POST request to create the smart collection
                response = requests.post(shop_url + ".json", headers=headers, data=data)
                print(response.json())

                # Check if the request was successful
                if response.status_code == 201:
                    print(response.json())
                    newId = response.json()
                    # print(newId)
                    newCollectionID = newId['smart_collection']['id']

                    def createMetaFields(nId):
                        for xId in range(2):
                            if xId == 0:
                                # print(SEO Title)
                                payload = json.dumps({
                                    "metafield": {
                                        "namespace": "global",
                                        "key": "SEO Title",
                                        "type": "single_line_text_field",
                                        "value": str(row['SEO Title'])
                                    }
                                })
                                urlM = "https://" + str(website) + "/admin/api/2023-01/smart_collections/" + str(
                                    nId) + "/metafields.json"
                                responseMeta = requests.request("POST", urlM, headers=headers, data=payload)
                                if responseMeta.status_code == 201:
                                    print("success")
                                else:
                                    print(responseMeta.json())
                            elif xId == 1:
                                # print(SEO description)
                                payload = json.dumps({
                                    "metafield": {
                                        "namespace": "global",
                                        "key": "SEO Description",
                                        "type": "single_line_text_field",
                                        "value": str(row['SEO Description'])
                                    }
                                })
                                urlM = "https://" + str(website) + "/admin/api/2023-01/smart_collections/" + str(
                                    nId) + "/metafields.json"
                                responseMeta = requests.request("POST", urlM, headers=headers, data=payload)
                                if responseMeta.status_code == 201:
                                    print("success")
                                else:
                                    print(responseMeta.json())

                    createMetaFields(newCollectionID)
                    errorResponse += "Collection Name: " + str(row["Title"]) + ",Smart Collection created successfully"
                    errorResponse += "--"
                    # print("Smart Collection created successfully")
                    # return "Collection Created"
                elif response.status_code == 422:
                    eData = {
                        "id": str(row['id']),
                        "handle": str(row['Handle']),
                        "title": str(row['Title']),
                        "body_html": ("" if (str(row['Body (HTML)']) == 'None') else str(
                            row['Body (HTML)'])),
                        "sort_order": str(row['Sort Order']),
                        "template_suffix": ("" if (str(row['Template Suffix']) == 'None') else str(
                            row['Template Suffix'])),
                        "disjunctive": str(row['Disjunctive']),
                        "rules": str(row['Rules']),
                        "published_scope": str(row['Published_Scope']),
                        "image": ("" if (str(row['Image']) == 'null') else str(row['Image'])),
                        "SEO Title": row['SEO Title'],
                        "SEO Description": str(row['SEO Description'])

                    }
                    extData.append(eData)
                else:
                    errorResponse += "Collection Name: " + str(row["Title"]) + ", Error creating Smart Collection:" + str(
                        response.json())
                    errorResponse += "--"
                    # print("Collection Name: " + row["Title"])
                    print(response.status_code)
                    print("Error creating Smart Collection:", response.json())
            elif deleteStatus == "Deleted":
                print("deleted")
        except :
            print("")

    def checkCollection():
        collectionResponse = requests.get(shop_url + ".json", headers=headers)
        smartCollection = collectionResponse.json()
        print(smartCollection)
        for smartCollectionData in smartCollection['smart_collections']:
            if fileDownload:
                def getMetaFields(sid):
                    responseMeta = requests.get(shop_url + "/" + str(sid) + "/metafields.json", headers=headers)
                    rm = responseMeta.json()
                    # columnName = []
                    columnValue = []
                    title = ''
                    description = ''
                    for r in rm['metafields']:
                        if r['key'] == "SEO Title":
                            title = r['value']
                        if r['key'] == "SEO Description":
                            description = r['value']
                    thisdict = {
                        "title": title,
                        "description": description
                    }
                    return thisdict

                val = getMetaFields(smartCollectionData['id'])
                rules = ''
                count = 0

                for sr in smartCollectionData['rules']:
                    count += 1
                    if count > 1:
                        rules += "*and*"
                        rules += sr['column'] + "|" + sr['relation'] + "|" + sr['condition']
                    else:
                        rules += sr['column'] + "|" + sr['relation'] + "|" + sr['condition']

                if 'image' in smartCollectionData:
                    imageData = smartCollectionData['image']['src']
                else:
                    imageData = "null"

                smartData = {
                    "id": "\t"+str(smartCollectionData['id'])+"\t",
                    "handle": str(smartCollectionData['handle']),
                    "title": str(smartCollectionData['title']),
                    "updated_at": str(smartCollectionData['updated_at']),
                    "body_html": ("" if (str(smartCollectionData['body_html']) == 'None') else str(
                        smartCollectionData['body_html'])),
                    "published_at": str(smartCollectionData['published_at']),
                    "sort_order": str(smartCollectionData['sort_order']),
                    "template_suffix": ("" if (str(smartCollectionData['template_suffix']) == 'None') else str(
                        smartCollectionData['template_suffix'])),
                    "disjunctive": str(smartCollectionData['disjunctive']),
                    "rules": str(rules),
                    "published_scope": str(smartCollectionData['published_scope']),
                    "admin_graphql_api_id": str(smartCollectionData['admin_graphql_api_id']),
                    "image": ("" if (str(imageData) == 'null') else str(imageData)),
                    "SEO Title": val['title'],
                    "SEO Description": val['description'],
                    "Remove": False

                }
                exsitingData.append(smartData)
                # return "Exists"

    def manualCollection():
        collectionResponse = requests.get(shop_url_manual + ".json", headers=headers)
        smartCollection = collectionResponse.json()
        for smartCollectionData in smartCollection['custom_collections']:
            if manualCollectionData:
                def getMetaFields(sid):
                    responseMeta = requests.get(shop_url_manual + "/" + str(sid) + "/metafields.json", headers=headers)
                    rm = responseMeta.json()
                    # columnName = []
                    columnValue = []
                    title = ''
                    description = ''
                    for r in rm['metafields']:
                        if r['key'] == "title_tag":
                            title = r['value']
                        if r['key'] == "description_tag":
                            description = r['value']
                    thisdict = {
                        "title": title,
                        "description": description
                    }
                    return thisdict

                val = getMetaFields(smartCollectionData['id'])
                rules = ''
                count = 0

                # for sr in smartCollectionData['rules']:
                #     count += 1
                #     if count > 1:
                #         rules += "*and*"
                #         rules += sr['column'] + "|" + sr['relation'] + "|" + sr['condition']
                #     else:
                #         rules += sr['column'] + "|" + sr['relation'] + "|" + sr['condition']

                if 'image' in smartCollectionData:
                    imageData = smartCollectionData['image']['src']
                else:
                    imageData = "null"

                smartData = {
                    "id": "\t"+str(smartCollectionData['id'])+"\t",
                    "handle": str(smartCollectionData['handle']),
                    "title": str(smartCollectionData['title']),
                    "updated_at": str(smartCollectionData['updated_at']),
                    "body_html": ("" if (str(smartCollectionData['body_html']) == 'None') else str(
                        smartCollectionData['body_html'])),
                    "published_at": str(smartCollectionData['published_at']),
                    "sort_order": str(smartCollectionData['sort_order']),
                    "template_suffix": ("" if (str(smartCollectionData['template_suffix']) == 'None') else str(
                        smartCollectionData['template_suffix'])),
                    # "disjunctive": str(smartCollectionData['disjunctive']),
                    # "rules": str(rules),
                    "published_scope": str(smartCollectionData['published_scope']),
                    "admin_graphql_api_id": str(smartCollectionData['admin_graphql_api_id']),
                    "image": ("" if (str(imageData) == 'null') else str(imageData)),
                    "SEO Title": val['title'],
                    "SEO Description": val['description']

                }
                manualData.append(smartData)

    if manualCollection:
        manualCollection()
        # print(manualData)
        asf = pd.DataFrame(manualData)
        # print(asf)
        filePath3 = str(manualCollectionPath)  # 'dataextPaath.csv'
        'No file found to write' if (filePath3 == '') else (asf.to_csv(filePath3, index=False))
    else:
        print("No need to download")
    if fileDownload:
        checkCollection()
    # d = json.loads(exsitingData)
    wdf = pd.DataFrame(exsitingData)
    # wdf['id'] = wdf.astype({'id': str})
    # print(wdf)
    filePath1 = str(outputPath)
    wdf.to_csv(filePath1, index=False)
    if not overwritecollections:
        asd = pd.DataFrame(extData)
        filePath2 = str(collectionskip)  # 'dataextPaath.csv'
        'No file found to write' if (filePath2 == '') else (asd.to_csv(filePath2, index=False))

    return errorResponse


createCollection('xxx.myshopify.com', 'xxx', 'collections.csv',
                 'output.csv','reportskip.csv','manualcollections.csv')