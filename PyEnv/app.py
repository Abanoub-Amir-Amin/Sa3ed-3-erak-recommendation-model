from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
from flask import Flask
from flask_cors import CORS
import requests

cred = credentials.Certificate(
    'E:\Study material\\4th Year\GP\sa3ed-3-erak-8097c-firebase-adminsdk-xwgr7-8368bfecfb.json')

firebase_admin.initialize_app(cred)
db = firestore.client()
posts_ref = db.collection(u'Posts')
docs = posts_ref.stream()
lst = []

for doc in docs:
    lst.append(doc.to_dict())
df = pd.DataFrame(data=lst)
dfBackUp = df
#print(df)
df = df.drop_duplicates(subset='description')


df2 = df.drop(['available', 
              'numberofproducts', 'pointsofproduct', 'postimage1', 'postimage2', 'postimage3', 'postimage4', 'time', 'useraddress',
               'userid', 'username', 'usernumber'], axis=1)

df2['data'] = df2[df2.columns[1:]].apply(
    lambda x: ' '.join(x.dropna().astype(str)),
    axis=1
)
#print(df2['data'].to_string())

vectorizer = CountVectorizer()
vectorized = vectorizer.fit_transform(df2['data'])
#print(vectorized)
similarities = cosine_similarity(vectorized)
print(similarities)

df = pd.DataFrame(similarities, index=df['description'], columns=df['description']).reset_index()

#print(df.to_string())
# rec = []
# item = db.collection(u"Posts").document('bHmgkfI3vpP7Eo2o7NF6')
# desc = item.get()
# desc = desc.to_dict().get('description')
# recommendations = pd.DataFrame(df.nlargest(7, desc)['description'])
# recommendations = recommendations[recommendations['description'] != desc]
# recommendations = recommendations.to_dict().get('description')
# rec = list(recommendations.values())
# print(rec)
# dfBackUp2 = pd.DataFrame()
# for item in rec:
#     temp = dfBackUp[dfBackUp['description'] == item]
#     dfBackUp2 = pd.concat([dfBackUp2, temp])

# print(dfBackUp2)    



app = Flask(__name__)
CORS(app)


@app.route('/recommendations/<id>', methods=['GET'])
def Get(id):
    
    try:
        rec = []
        item = db.collection(u"Posts").document(id)
        desc = item.get()
        desc = desc.to_dict().get('description')
        recommendations = pd.DataFrame(df.nlargest(7, desc)['description'])
        recommendations = recommendations[recommendations['description'] != desc]
        recommendations = recommendations.to_dict().get('description')
        rec = list(recommendations.values())
        print(rec)
        dfBackUp2 = pd.DataFrame()
        for item in rec:
            temp = dfBackUp[dfBackUp['description'] == item]
            dfBackUp2 = pd.concat([dfBackUp2, temp])

        #print(dfBackUp2)

        return dfBackUp2.T.to_dict()
    except:
        return 'Not Found!'


if __name__ == '__main__':
    port = 8000  # the custom port you want
    app.run(host='0.0.0.0', port=port)
