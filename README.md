Create venv:
   py -m venv .venv 
   
Activate the venv:
  .\.venv\Scripts\activate
  
Set the location:
  pulumi config set azure-native:location uksouth
  
Install the Requirements:
  pip install -r .\requirements.txt
  
Preview:
  pulumi pre
  
Create the Resources:
  pulumi up -y
  
