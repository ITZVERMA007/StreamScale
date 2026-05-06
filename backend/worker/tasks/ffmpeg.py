import os

DEFAULT_RESOLUTIONS = {
    "360":"640:360",
    "720":"1280:720",
    "1080":"1920:1080"
}

def parse_resolutions(env_str=None):
    if not env_str:
        return DEFAULT_RESOLUTIONS
    
    resolutions = {}
    for item in env_str.split(","):
        parts = item.split(":")
        if len(parts) == 3:
            name, width, height = parts
            resolutions[name] = f"{width}:{height}"
    return resolutions if resolutions else DEFAULT_RESOLUTIONS

RESOLUTIONS = parse_resolutions(os.getenv("TRANSCODE_RESOLUTIONS"))