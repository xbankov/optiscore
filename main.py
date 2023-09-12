import pandas as pd
import torch
from googleapiclient.discovery import build
from PIL import Image
from tqdm.auto import tqdm

from image_assessment import (
    blur_score,
    is_visual_duplicate,
    noise_score,
    pyiqa_single_image_score,
    sharpness_score,
)
from interactions import select_album
from settings import CREDENTIALS_DESKTOP_PATH, PYIQA_MODELS, SCOPES, TOKEN_PATH
from utils import auth, download_image


def main():
    creds = auth(
        credentials_path=CREDENTIALS_DESKTOP_PATH, token_path=TOKEN_PATH, scopes=SCOPES
    )
    google_photos = build(
        "photoslibrary", "v1", credentials=creds, static_discovery=False
    )

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # Select the album you want to check the quality of photos for
    album = select_album(google_photos)

    # Adjust this to your desired page size
    page_size = 10

    # Iterate over the album
    # Define the request parameters to search for media items in the album
    request_body = {
        "albumId": album["id"],
        "pageSize": page_size,  # Adjust the pageSize as needed
    }

    total = int(album["mediaItemsCount"])
    # Calculate the number of iterations based on the total and page size
    num_iterations = (total + page_size - 1) // page_size

    # Create an empty DataFrame with desired column names
    # Try to load an existing CSV file
    try:
        df = pd.read_csv("image_metrics.csv")
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=[
                "id",
                "width",
                "height",
                "creationTime",
                "cameraMake",
                "cameraModel",
                "exposureTime",
                "apertureFNumber",
                "isoEquivalent",
                "focalLength",
            ]
        )

    previous_image = None
    previous_image_id = None
    page_token = None
    # Get the quality assessment for all images in the batch
    pbar = tqdm(total=total)
    for _ in range(num_iterations):
        if page_token:
            request_body["pageToken"] = page_token

        response = google_photos.mediaItems().search(body=request_body).execute()

        # Process the media items in the response
        for media_item in response.get("mediaItems", []):
            media_item_id = media_item["id"]
            # Skip media items if the ID is already in the DataFrame
            if media_item_id in df["id"].values:
                continue

            baseUrl = media_item["baseUrl"] + "=d"

            # Process the media item or store it as needed
            image = download_image(baseUrl)

            metrics = {}
            metrics["id"] = media_item_id

            # 4. Given the duplicates

            # if previous_image and is_visual_duplicate(image, previous_image):
            #     metrics["visual_duplicate"] = True
            #     metrics["visual_duplicate_with"] = previous_image_id

            # 1. Given the bluriness, noise, sharpness, ...
            # metrics["blur"] = blur_score(image)
            # metrics["sharpness"] = sharpness_score(image)
            # metrics["noise"] = noise_score(image)

            # 2. Given the capture metadata: focus, iso, exposure ...
            metrics["width"] = int(media_item["mediaMetadata"]["width"])
            metrics["height"] = int(media_item["mediaMetadata"]["height"])
            metrics["creationTime"] = media_item["mediaMetadata"]["creationTime"]
            metrics["cameraMake"] = media_item["mediaMetadata"]["photo"]["cameraMake"]
            metrics["cameraModel"] = media_item["mediaMetadata"]["photo"]["cameraModel"]

            metrics["exposureTime"] = float(
                media_item["mediaMetadata"]["photo"]["exposureTime"][:-1]
            )
            metrics["apertureFNumber"] = float(
                media_item["mediaMetadata"]["photo"]["apertureFNumber"]
            )
            metrics["isoEquivalent"] = int(
                media_item["mediaMetadata"]["photo"]["isoEquivalent"]
            )
            metrics["focalLength"] = float(
                media_item["mediaMetadata"]["photo"]["focalLength"]
            )

            # 3. Given the PYIQA Deep learning Quality assessment
            # for model in PYIQA_MODELS:
            #     downsampled = image.resize(
            #         (metrics["width"] // 10, metrics["height"] // 10), Image.LANCZOS
            #     )
            #     metrics[model] = pyiqa_single_image_score(downsampled, model, device)

            # Append the metrics as a new row to the DataFrame
            df = df.append(metrics, ignore_index=True)

            previous_image = image
            previous_image_id = media_item_id

            pbar.update()

        # Save the DataFrame to a CSV file after each iteration
        df.to_csv("image_metrics.csv", index=False)
        # Check if there are more pages
        page_token = response.get("nextPageToken")

    # Save the final DataFrame to a CSV file if needed
    df.to_csv("image_metrics.csv", index=False)

    # For finding a duplicates in a numpy array of images
    # https://github.com/idealo/imagededup/blob/4e0b15f4cd82bcfa321eb280b843e57ebc5ff154/imagededup/methods/hashing.py#L135

    # First show very bad pictures with the super bad threshold and duplicates.
    # Suggest deletion: I should store the photos that were removed.


if __name__ == "__main__":
    main()
