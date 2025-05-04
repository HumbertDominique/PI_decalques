from pypylon import pylon
import time

def main(fileprefix="image_",filepath = "/data/",ExpTime = 5000.0,bitdepth=12):
    # TODO: docstring
    # TODO: arg checks
    RUN = True
    # Initialize camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("Using device:", camera.GetDeviceInfo().GetModelName())
    camera.Open()
    camera.ExposureMode.SetValue("Timed")
    camera.ExposureAuto.SetValue("Off")
    camera.ExposureTime.Value = ExpTime
    camera.GainAuto.Value = "Off"
    camera.Gain.Value = 1.

    if bitdepth==8:
        camera.PixelFormat.SetValue("Mono8")
    elif bitdepth==12:
        camera.PixelFormat.SetValue("Mono12")
    print("sensor format: {camera.PixelFormat.Value}")

    main_menu_string = "\n1) Press 'enter' to take a picture, 2)\nInput 'e' to adjust exposure time\n3) Input 'bpp' to adjust pixel bit depth,\n4) Input 'q' to exit."
    image_index = 1
    img = pylon.PylonImage()
    tlf = pylon.TlFactory.GetInstance()
    imageWindow = pylon.PylonImageWindow()
    imageWindow.Create(1)
    print(main_menu_string)
    while RUN ==True:
        user_input = input()
        if user_input=='':
            print("Capturing image...")
            camera.StartGrabbingMax(1)
            while camera.IsGrabbing(): 
                with camera.RetrieveResult(2000) as result:
                    img.AttachGrabResultBuffer(result)
                    

                    max_value = result.Array.max()
                    print(f"Image pixel max value: {max_value}")
                    if max_value >= 2**bitdepth-5:
                        print("Image is overexposed. Decrease exposure time.")
                    imageWindow.SetImage(result)
                    imageWindow.Show()
                    # quality (100 -> best quality, 0 -> poor quality).
                    ipo = pylon.ImagePersistenceOptions()
                    quality = 100
                    ipo.SetQuality(quality)
                    filename = filepath+'/'+fileprefix+"_%d.bmp" % image_index
                    img.Save(pylon.ImageFileFormat_Jpeg, filename, ipo)
                    image_index +=1
                    print(main_menu_string)
        elif user_input=="e":
            print(f"curent exposure time:{float(ExpTime):.3e} us")
            print("Input new exposure time in microseconds: 16.0 <= Exposure time <= 10e7")
            ExpTime = input()
            if (float(ExpTime) > 16.0) or (float(ExpTime) < 1e7):
                camera.ExposureTime.Value = float(ExpTime)
                print(f"New exposure time:{float(ExpTime):.3e} us")
            else:
                print(f"Invalid input")

            print(main_menu_string)
        elif user_input=="bpp":
            print(f"curent pixel bit depth:{bitdepth} us")
            print("Input new pixel bit depth: bpp = {8, 12}")
            bitdepth = int(input())
            if bitdepth==8:
                camera.PixelFormat.SetValue("Mono8")
            elif bitdepth==12:
                camera.PixelFormat.SetValue("Mono12")
            print("sensor format: {camera.PixelFormat.Value}")
            print(main_menu_string)
        elif user_input=='q':
            print("Exiting...")
            RUN = False
        time.sleep(0.1)
    imageWindow.Close()
    camera.Close()
    print("Program terminated")
 
fileprefix = "30mm_WonB"
filepath = "data"
bitdepth = 12
ExpTime = 120.0 # [us]
print(filepath,'/', fileprefix)
print(f"Exposure time: {ExpTime:.3e} us") 

if __name__ == "__main__":
    main(fileprefix, filepath, ExpTime, bitdepth)
