import argparse
import os
import subprocess
from PIL import Image
import glob

def extract_frames(video_path, fps, tmp_dir):
    os.makedirs(tmp_dir, exist_ok=True)
    pattern = os.path.join(tmp_dir, 'frame_%04d.png')
    subprocess.run([
        'ffmpeg', '-i', video_path,
        '-vf', f'fps={fps},setsar=1',  # force square pixels
        pattern
    ], check=True)

def create_gif(tmp_dir, output_path, fps, scale):
    frames = sorted(glob.glob(os.path.join(tmp_dir, 'frame_*.png')))
    images = []

    for f in frames:
        img = Image.open(f).convert("RGBA")
        if scale != 1.0:
            new_size = (
                int(img.width * scale),
                int(img.height * scale)
            )
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        img = img.convert("P", palette=Image.ADAPTIVE)
        images.append(img)

    if images:
        duration = int(1000 / fps)
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            loop=0,
            duration=duration,
            optimize=False
        )

def cleanup(tmp_dir):
    for f in glob.glob(os.path.join(tmp_dir, 'frame_*.png')):
        os.remove(f)
    os.rmdir(tmp_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Input .mp4 or .mov file")
    parser.add_argument("output", help="Output .gif file")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second (default: 10)")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor for GIF size (default: 0.5)")
    args = parser.parse_args()

    tmp_dir = "tmp_frames"
    extract_frames(args.video, args.fps, tmp_dir)
    create_gif(tmp_dir, args.output, args.fps, args.scale)
    cleanup(tmp_dir)

if __name__ == "__main__":
    main()
