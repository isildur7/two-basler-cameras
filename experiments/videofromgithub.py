from FFMPEGwriter import FFMPEGVideoWriter

if __name__ == '__main__':

    # sample program for a GEV camera
    # target is to write the YUV video data without further conversion
    ##
    import pypylon.pylon as py

    cam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
    cam.Open()

    cam.PixelFormat = "Mono8"
    FPS = 20
    RECORDING_TIME = 10  # in seconds
    NUM_IMAGES = FPS * RECORDING_TIME

    with FFMPEGVideoWriter("E:/samplevid.avi",
                           (cam.Height(), cam.Width()),
                           fps=20, pixfmt="gray") as writer:

        cam.StartGrabbingMax(NUM_IMAGES)
        while cam.IsGrabbing():
            res = cam.RetrieveResult(1000)
            writer.write_frame(res.Array)
            res.Release()

    cam.Close()
