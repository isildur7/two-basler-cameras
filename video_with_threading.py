from threading import Thread
from multiprocessing import Process
from time import sleep
from pypylon import pylon
import imageio as iio


FPS = 20
RECORDING_TIME = 10  # in seconds
NUM_IMAGES = FPS * RECORDING_TIME


def camera_video(cam, fname):
    # tlf = pylon.TlFactory.GetInstance()

    # # See all the available devices
    # di = pylon.DeviceInfo()

    # devs = tlf.EnumerateDevices([di, ])
    # cam = pylon.InstantCamera()
    # cam.Attach(tlf.CreateDevice(devs[i]))
    cam.Open()
    cam.PixelFormat = "Mono8"
    cam.AcquisitionFrameRateEnable.SetValue(True)
    cam.AcquisitionFrameRate.SetValue(FPS)
    cam.ExposureTime.SetValue(40000)

    # sleep for a bit
    sleep(1)

    with iio.get_writer(
        fname,  # mkv players often support H.264
        fps=FPS,  # FPS is in units Hz; should be real-time.
        codec='libx264',  # When used properly, this is basically
                          # "PNG for video" (i.e. lossless)
        quality=None,  # disables variable compression
        pixelformat='gray',  # keep it as RGB colours
        ffmpeg_params=[  # compatibility with older library versions
            '-preset',  # set to faster, veryfast, superfast, ultrafast
            'fast',     # for higher speed but worse compression
            '-crf',  # quality; set to 0 for lossless, but keep in mind
            '11'     # that the camera probably adds static anyway
                     ]) as writer:

        cam.StartGrabbingMax(NUM_IMAGES, pylon.GrabStrategy_LatestImageOnly)
        buffer = []
        while cam.IsGrabbing():
            res = cam.RetrieveResult(1000)
            buffer.append(res.Array)
            res.Release()
        for image in buffer:
            writer.append_data(image)
    cam.Close()


if __name__ == "__main__":
    tlf = pylon.TlFactory.GetInstance()

    # See all the available devices
    di = pylon.DeviceInfo()

    devs = tlf.EnumerateDevices([di, ])
    print(devs)

    # make two camera objects and attach the devices to them
    cam1 = pylon.InstantCamera()
    cam1.Attach(tlf.CreateDevice(devs[0]))

    cam2 = pylon.InstantCamera()
    cam2.Attach(tlf.CreateDevice(devs[1]))

    Thread(target=camera_video, args=(cam1, "E:\\samplevidc1.avi")).start()
    Thread(target=camera_video, args=(cam2, "E:\\samplevidc2.avi")).start()
    # p1 = Process(target=camera_video, args=(0, "E:\\samplevidc1.avi"))
    # p2 = Process(target=camera_video, args=(1, "E:\\samplevidc2.avi"))

    # p1.start()
    # p2.start()
