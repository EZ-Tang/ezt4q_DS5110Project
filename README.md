The app is available here:
https://sentimentdeployment-vn2tjleo3q-ue.a.run.app/




To build on Google Cloud, replace keys and Reddit account ID in python files, then run the following commands (replace [ID] and [NAME] from the Google Cloud Project):

gcloud builds submit --tag gcr.io/[ID]/[NAME]  --project=[ID]

gcloud run deploy --image gcr.io/[ID]/[NAME] --project=[ID] --allow-unauthenticated
