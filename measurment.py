from pypylon import pylon
import keyboard
import time
import os
import re


def get_next_image_index(filepath = "data",prefix="image_", extension=".png"):
    # List files and extract numbers
    existing_files = [f for f in os.listdir(filepath) if f.startswith(prefix) and f.endswith(extension)]   
    indices = []

    for f in existing_files:
        match = re.search(rf"{prefix}(\d+){extension}", f)
        if match:
            indices.append(int(match.group(1)))

    return max(indices, default=0) + 1

def main(fileprefix="image_",filepath = "/data/",ExpTime = 5000.0):
    # Initialize camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("Using device:", camera.GetDeviceInfo().GetModelName())
    camera.Open()
    camera.ExposureTime.Value = ExpTime
    print("Press 'space' to take a picture. Press 'esc' to exit.")

    image_index = get_next_image_index(prefix=fileprefix)
    img = pylon.PylonImage()
    tlf = pylon.TlFactory.GetInstance()
    imageWindow = pylon.PylonImageWindow()
    imageWindow.Create(1)
    while True:
        if keyboard.is_pressed('space'):
            print("Capturing image...")
            camera.StartGrabbingMax(1)

            while camera.IsGrabbing(): 
                with camera.RetrieveResult(2000) as result:
                    img.AttachGrabResultBuffer(result)
                    # quality (100 -> best quality, 0 -> poor quality).
                    ipo = pylon.ImagePersistenceOptions()
                    quality = 100
                    ipo.SetQuality(quality)
                    filename = filepath+'/'+fileprefix+"_%d.jpeg" % image_index
                    img.Save(pylon.ImageFileFormat_Jpeg, filename, ipo)
                    image_index +=1
                    imageWindow.SetImage(result)
                    imageWindow.Show()
                    print("Press 'space' to take a picture. Press 'esc' to exit.")

        elif keyboard.is_pressed('esc'):
            print("Exiting...")
            break

        time.sleep(0.1)
    imageWindow.Close()
    camera.Close()
 
fileprefix = "test_"
filepath = "data"
ExpTime = 100000.0 # [us]
if __name__ == "__main__":
    main(fileprefix, filepath, ExpTime)
