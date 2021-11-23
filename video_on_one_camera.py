from datetime import datetime
from pypylon import pylon
import imageio as iio

FPS = 20.0
RECORDING_TIME = 10  # in seconds
NUM_IMAGES = FPS * RECORDING_TIME


cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
print("Using device ", cam.GetDeviceInfo().GetModelName())
cam.Open()

cam.PixelFormat = "Mono8"

cam.AcquisitionFrameRateEnable.SetValue(True)
cam.AcquisitionFrameRate.SetValue(FPS)
cam.ExposureTime.SetValue(1000000*(1/FPS) - 1100)

start = datetime.now()

with iio.get_writer(
        'E:\\samplevid.avi',  # mkv players often support H.264
        fps=FPS,  # FPS is in units Hz; should be real-time.
        codec='libx264',  # When used properly, this is basically
                              # "PNG for video" (i.e. lossless)
        quality=None,  # disables variable compression
        pixelformat='yuv420p',  # keep it as RGB colours
        ffmpeg_params=[  # compatibility with older library versions
            '-preset',  # set to faster, veryfast, superfast, ultrafast
            'fast',     # for higher speed but worse compression
            '-crf',  # quality; set to 0 for lossless, but keep in mind
            '11'     # that the camera probably adds static anyway
        ]) as writer:
    images = 0
    cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    while images < NUM_IMAGES and cam.IsGrabbing():
        res = cam.RetrieveResult(1000)
        writer.append_data(res.Array)
        res.Release()
        images += 1
    cam.StopGrabbing()
end = datetime.now()
print("actual runtime {}".format(end - start))
cam.Close()
