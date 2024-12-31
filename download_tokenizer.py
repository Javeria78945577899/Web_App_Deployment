import os
import requests

def download_file_from_google_drive(id, destination):
    """
    Download a file from Google Drive by its ID and save it to the destination.
    """
    URL = "https://drive.google.com/uc?export=download"

    print(f"Attempting to download file with ID: {id}")
    with requests.Session() as session:
        response = session.get(URL, params={"id": id}, stream=True)
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                response = session.get(URL, params={"id": id, "confirm": value}, stream=True)
                break

        with open(destination, "wb") as f:
            print(f"Writing to {destination}...")
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)

if __name__ == "__main__":
    # Set the Google Drive file ID and destination path
    file_id = "1C449DJGOx6WiD4c-m1gozC3hJGbWA55-"  # Replace with your actual file's ID
    output_dir = "./bert_weapon_classifier"
    output_path = os.path.join(output_dir, "model.safetensors")  # Saving as 'model.safetensors'

    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download the file
    print(f"Downloading the file to {output_path}...")
    download_file_from_google_drive(file_id, output_path)
    print("Download complete!")
