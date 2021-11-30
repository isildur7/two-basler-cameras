import time
import os
from pypylon import pylon
from videofromgithub import FFMPEGVideoWriter

FPS = 20
RECORDING_TIME = 10  # in seconds
NUM_IMAGES = FPS * RECORDING_TIME

# Start emulation with two cameras
# Set the variable in below line to 0 to stop using emulation
os.environ["PYLON_CAMEMU"] = "0"  # Number of cameras to emulate

tlf = pylon.TlFactory.GetInstance()

# See all the available devices
di = pylon.DeviceInfo()

devs = tlf.EnumerateDevices([di, ])
print(devs)

# Create a camera array object and attach the emulated cameras to it
cam_arr = pylon.InstantCameraArray(2)
for idx, cam in enumerate(cam_arr):
    cam.Attach(tlf.CreateDevice(devs[idx]))

# Open the devices
cam_arr.Open()

# store a unique number for each camera to identify the incoming images
for idx, cam in enumerate(cam_arr):
    camera_serial = cam.DeviceInfo.GetSerialNumber()
    print(f"set context {idx} for camera {camera_serial}")
    cam.SetCameraContext(idx)
    cam.PixelFormat = "Mono8"
    cam.AcquisitionFrameRateEnable.SetValue(True)
    cam.AcquisitionFrameRate.SetValue(FPS)
    cam.ExposureTime.SetValue(50000)


frames_to_grab = NUM_IMAGES
frame_counts = [0, 0]  # frames grabbed by each camera
writer1 = FFMPEGVideoWriter("E:/samplevidc1.avi",
                            (cam.Height(), cam.Width()),
                            fps=20, pixfmt="gray")
writer2 = FFMPEGVideoWriter("E:/samplevidc2.avi",
                            (cam.Height(), cam.Width()),
                            fps=20, pixfmt="gray")

cam_arr.StartGrabbing()
while True:
    with cam_arr.RetrieveResult(1000) as res:
        if res.GrabSucceeded():
            img_nr = res.ImageNumber
            cam_id = res.GetCameraContext()
            frame_counts[cam_id] = img_nr
            if cam_id == 0:
                writer1.write_frame(res.Array)
                res.Release()
            else:
                writer2.write_frame(res.Array)
                res.Release()

            # check if all cameras have reached 100 images
            if min(frame_counts) >= frames_to_grab:
                print(f"all cameras have acquired {frames_to_grab} frames")
                break

cam_arr.StopGrabbing()


cam.Close()
