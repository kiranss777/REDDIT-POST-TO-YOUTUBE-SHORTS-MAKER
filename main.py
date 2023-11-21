#main.py
from moviepy.editor import *
import reddit, screenshot, time, subprocess, random, configparser, sys, math
from os import listdir
from os.path import isfile, join
# Import the necessary modules
from moviepy.config import change_settings
import textwrap  

# Specify the path to the magick.exe executable
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if (len(sys.argv) == 2):
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        script = reddit.getContent(outputDir, postOptionCount)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshots(fileName, script)

    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)
    bgIndex = random.randint(0, bgCount-1)
    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4", 
        audio=False).subclip(0, script.getDuration())
    w, h = backgroundVideo.size

    desired_width = 9
    desired_height = 16    
    def __createClip2(screenShotFile, audioClip, marginSize, overlayText):
        imageClip = ImageClip(screenShotFile, duration=audioClip.duration).set_position(("center","top"))
        imageClip = imageClip.resize(width=desired_width * (h - marginSize) / desired_height)

        subtitle_clip = TextClip(
            overlayText,
            fontsize=20,
            color='white',
            font='Arial',  # Change the font to your preferred font

        )
        subtitle_clip = subtitle_clip.set_duration(audioClip.duration).set_position(('center', 'bottom'))

        # Create a video clip for the subtitle
        subtitle_video_clip = CompositeVideoClip([subtitle_clip.set_start(0)])

        videoClip = CompositeVideoClip([imageClip.set_start(0)]).set_audio(audioClip)
        videoClip = videoClip.set_duration(audioClip.duration)

        final_clip = clips_array([[videoClip], [subtitle_video_clip]])
        final_clip.fps = 1

        return final_clip
    def __createClipworks(screenShotFile, audioClip, marginSize, overlayText):
        imageClip = ImageClip(screenShotFile, duration=audioClip.duration).set_position(("center","top"))
        imageClip = imageClip.resize(width=desired_width * (h - marginSize) / desired_height)

        # Split the overlay text into lines
        lines = textwrap.wrap(overlayText, width=30)  # Adjust the width as needed

        # Create subtitle clips for each line
        subtitle_clips = []
        start_time = 0
        char_display_speed = 0.1  # Adjust the speed as needed (in seconds per character)
        for line in lines:
            subtitle_line = TextClip(
                line,
                fontsize=20,
                color='white',
                font='Arial',
            )
            line_duration = len(line) * char_display_speed
            subtitle_line = subtitle_line.set_duration(line_duration).set_position(('center', 'bottom'))
            subtitle_clips.append(subtitle_line)
            start_time += line_duration

        # Create a video clip for the subtitles
        subtitle_video_clip = concatenate_videoclips(subtitle_clips, method="compose")

        videoClip = CompositeVideoClip([imageClip.set_start(0)]).set_audio(audioClip)
        videoClip = videoClip.set_duration(audioClip.duration)

        final_clip = clips_array([[videoClip], [subtitle_video_clip]])
        final_clip.fps = 1

        return final_clip
    
    def __createClip(screenShotFile, audioClip, marginSize, overlayText):
        imageClip = ImageClip(screenShotFile, duration=audioClip.duration).set_position(("center","top"))
        imageClip = imageClip.resize(width=desired_width * (h - marginSize) / desired_height)

        # Split the overlay text into lines
        lines = textwrap.wrap(overlayText, width=30)  # Adjust the width as needed

        # Create subtitle clips for each line
        subtitle_clips = []
        start_time = 0
        char_display_speed = 0.1  # Adjust the speed as needed (in seconds per character)
        for line in lines:
            subtitle_line = TextClip(
                line,
                fontsize=20,
                color='white',
                font='Arial',
            )
            line_duration = len(line) * char_display_speed
            subtitle_line = subtitle_line.crossfadein(0.5).set_duration(line_duration).set_position(('center', 'bottom'))
            subtitle_clips.append(subtitle_line)
            start_time += line_duration

        # Create a video clip for the subtitles
        subtitle_video_clip = concatenate_videoclips(subtitle_clips, method="compose")

        videoClip = CompositeVideoClip([imageClip.set_start(0)]).set_audio(audioClip)
        videoClip = videoClip.set_duration(audioClip.duration)

        final_clip = clips_array([[videoClip], [subtitle_video_clip]])
        final_clip.fps = 1

        return final_clip




    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    clips.append(__createClip(script.titleSCFile, script.titleAudioClip, marginSize, script.title))
    for comment in script.frames:
        clips.append(__createClip(comment.screenShotFile, comment.audioClip, marginSize, comment.text))

    # Merge clips into a single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay], 
        size=backgroundVideo.size).set_audio(contentOverlay.audio)
    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    # Write output to a file
    print("Rendering the final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4"
    final.write_videofile(
        outputFile, 
        codec='mpeg4',
        threads=threads, 
        bitrate=bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

    # Preview in VLC for approval before uploading
    if (config["General"].getboolean("PreviewBeforeUpload")):
        vlcPath = config["General"]["VLCPath"]
        p = subprocess.Popen([vlcPath, outputFile])
        print("Waiting for video review. Type anything to continue")
        wait = input()

    print("Video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")

if __name__ == "__main__":
    createVideo()

