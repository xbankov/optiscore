from googleapiclient.discovery import build

import sys
from utils import auth
from settings import TOKEN_PATH, CREDENTIALS_DESKTOP_PATH, SCOPES




def main():
    
    creds = auth(credentials_path=CREDENTIALS_DESKTOP_PATH, token_path=TOKEN_PATH, scopes=SCOPES)
    google_photos = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    
    
    # Select the album you want to check the quality of photos for
    
    # Fetch the album
    
    # Get the quality assessment for all images
    # 1. Given the capture metadata: focus, iso, exposure ... 
    # 2. Given the bluriness, noise, sharpness, ... 
    # 3. Given the Deep (learning) Quality assessment (In the future my own! :D )
    # 4. Given the duplicates
    
    # First show very bad pictures with the super bad threshold and duplicates.
    # Suggest deletion: I should store the photos that were removed.
    # DONE


if __name__ == "__main__":
    
    main()

    