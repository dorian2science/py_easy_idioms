import pandas as pd
import os
import io
import re
import asyncio
import edge_tts
import nest_asyncio
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS
import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from googletrans import Translator
from pydub import AudioSegment
import dotenv
from tqdm import tqdm
dotenv.load_dotenv()

translator = Translator()

CONF_FOLDER = os.path.join(os.path.dirname(__file__),'conf')
DATA_FOLDER = os.getenv("DATA_FOLDER")

OUTPUT_IMAGE_FOLDER = os.path.join(DATA_FOLDER,"word_images")
OUTPUT_AUDIO_FOLDER = os.path.join(DATA_FOLDER,"word_audios")
OUTPUT_VIDEO_FOLDER = os.path.join(DATA_FOLDER,"videos")
os.makedirs(CONF_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_IMAGE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_AUDIO_FOLDER, exist_ok=True)
PATH_VOICES = os.path.join(CONF_FOLDER,"voices_edge.json")
EDGE_VOICES = pd.read_json(PATH_VOICES).squeeze().str.strip().str.replace(', ','-')
EDGE_VOICES_SELECTED = {
    lang:EDGE_VOICES[EDGE_VOICES.str.contains(f'{lang}-.*{name}')].squeeze()
    for lang,name in {
        'en':'Thomas',
        'ar':'Salma',
        'fr':"Denise",
        # 'fr':'Vivienne'
        }.items()
}

async def download_list_voices_edge():
    async def list_voices():
        voices = await edge_tts.list_voices()
        return [v['Name'] for v in voices]
    voices_list = await list_voices()
    import json
    with open(PATH_VOICES,'w') as f:
        json.dump(voices_list,f)


def tts_sync_edge(text, voice="en-US-GuyNeural", output="output.mp3"):
    """
    Generate TTS using edge_tts, works in both Jupyter and scripts.
    """
    async def main():
        await edge_tts.Communicate(text, voice).save(output)

    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # If loop is running (e.g., in Jupyter), create a task and wait for it
        return asyncio.ensure_future(main())
    except RuntimeError:
        # If no loop is running (standalone script), run normally
        return asyncio.run(main())


async def generate_all_tts_samples():
    # Patch asyncio to allow nested loops in Jupyter
    nest_asyncio.apply()

    # Directory to save all MP3s
    OUTPUT_DIR = os.path.join(DATA_FOLDER,"tts_samples")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Dummy sentences per language
    dummy_sentences = {
        "en": "Hello, this is a test.",
        "de": "Hallo, dies ist ein Test.",
        "ar": "جلس عبد القادر عند جدول كبير يقرأ قصصاً عن عجائب قديمة."
    }

    voices = await edge_tts.list_voices()

    for v in voices:
        locale = v["Locale"]
        lang_code = locale.split("-")[0]  # 'en', 'de', 'ar', etc.
        if lang_code in dummy_sentences:
            text = dummy_sentences[lang_code]
            filename = f"{v['Name']}_{lang_code}.mp3"
            output_path = os.path.join(OUTPUT_DIR, filename)
            print(f"Generating: {filename}")
            tts_sync_edge(text, v["Name"], output_path)


async def tts_text(text,lang,output_path="output.mp3",model="edge"):
    """"
    model : one of {'edge','google','tts-coqui-ai}
    """
    if model=='google':
        tts_ar = gTTS(text=arabic_word, lang="ar")
        tts_ar.save(audio_ar)
        tts_en = gTTS(text=english_word, lang="en")
        tts_en.save(audio_en)
    elif model=='edge':
        await tts_sync_edge(text, EDGE_VOICES_SELECTED[lang], output_path)


def list_words_stored_as_clips():
    return [m.groups()[0] for f in os.listdir(OUTPUT_IMAGE_FOLDER) if (m := re.search(r"word_([a-zA-Z]+)\.png",f))]

def build_dataframe_words(list_words, translate=['ar','fr','de']):
    """
    Build a DataFrame with English words and their translations
    into specified languages.

    Args:
        list_words (list[str]): List of English words to translate.
        translate (list[str]): Target language codes (default: ['ar','fr','de']).

    Returns:
        pd.DataFrame: DataFrame with columns [word_en, <lang1>, <lang2>, ...]
    """
    translator = Translator()
    data = {"en": list_words}

    for lang in translate:
        translations = []
        for w in tqdm(list_words, desc=f"{lang}", unit="word"):
            try:
                result = translator.translate(w, src="en", dest=lang)
                translations.append(result.text)
            except Exception as e:
                translations.append(None)  # in case of failure
        data[lang] = translations

    df = pd.DataFrame(data)
    return df

async def generate_picture_and_sound(word,gap=80):
    ## check if word already exists
    list_existing_words = list_words_stored_as_clips()
    # print(list_existing_words,word['en'])
    if word['en'] in list_existing_words:
        print(f"word {word['en']} already available as clip.")
        return

    arabic_word = word['ar']
    english_word = word['en']

    arabic_font_path = os.path.join(CONF_FOLDER,"Amiri-1.002","Amiri-Regular.ttf")
    english_font_path = "arial.ttf"
    arabic_font = ImageFont.truetype(arabic_font_path, 100)
    english_font = ImageFont.truetype(english_font_path, 40)

    # --- Create image ---
    width, height = 800, 400
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Arabic text reshaped for proper RTL
    reshaped_text = arabic_reshaper.reshape(arabic_word)
    bidi_text = get_display(reshaped_text)

    # Compute bounding boxes
    arabic_bbox = draw.textbbox((0,0), bidi_text, font=arabic_font)
    arabic_width = arabic_bbox[2] - arabic_bbox[0]
    arabic_height = arabic_bbox[3] - arabic_bbox[1]

    english_bbox = draw.textbbox((0,0), english_word, font=english_font)
    english_width = english_bbox[2] - english_bbox[0]
    english_height = english_bbox[3] - english_bbox[1]

    arabic_x = (width - arabic_width)/2
    arabic_y = (height - arabic_height - english_height - gap)/2
    english_x = (width - english_width)/2
    english_y = arabic_y + arabic_height + gap

    # Draw texts
    draw.text((arabic_x, arabic_y), bidi_text, fill="black", font=arabic_font)
    draw.text((english_x, english_y), english_word, fill="red", font=english_font)

    # Save image
    img_path = os.path.join(OUTPUT_IMAGE_FOLDER, f"word_{english_word}.png")
    img.save(img_path)

    # --- Generate audio ---
    audio_ar = os.path.join(OUTPUT_AUDIO_FOLDER, f"word_{english_word}_ar.mp3")
    audio_en = os.path.join(OUTPUT_AUDIO_FOLDER, f"word_{english_word}_fr.mp3")
    await tts_text(arabic_word,'ar',audio_ar)
    await tts_text(english_word,'en',audio_en)

    # Combine audios
    sound_ar = AudioSegment.from_mp3(audio_ar)
    sound_fr = AudioSegment.from_mp3(audio_en)
    pause = AudioSegment.silent(duration=500)
    combined_sound = sound_ar + AudioSegment.silent(duration=200) + sound_ar + pause + sound_fr + pause
    combined_path = os.path.join(OUTPUT_AUDIO_FOLDER, f"word_{english_word}_combined.mp3")
    combined_sound.export(combined_path, format="mp3")

async def generate_pictures_and_sounds(df_words,**kwargs):
    clips = []
    pbs = []
    words = df_words.T.to_dict().values()
    # for word in words:
    for word in tqdm(words, unit="word"):
        try:
            await generate_picture_and_sound(word,**kwargs)
        except:
            pbs.append(word['en'])
    return pbs

def build_video(words_list_en,final_video_path="words_video.mp4"):
    clips = []
    for word in words_list_en:
        combined_path = os.path.join(OUTPUT_AUDIO_FOLDER, f"word_{word}_combined.mp3")
        img_path = os.path.join(OUTPUT_IMAGE_FOLDER, f"word_{word}.png")
        # --- Create video clip ---
        audio_clip = AudioFileClip(combined_path)
        duration = audio_clip.duration
        image_clip = ImageClip(img_path,duration=duration).with_audio(audio_clip)
        clips.append(image_clip)

    # --- Concatenate all clips ---
    final_video = concatenate_videoclips(clips, method="compose")
    final_video_full_path = os.path.join(OUTPUT_VIDEO_FOLDER,final_video_path)
    final_video.write_videofile(final_video_full_path, fps=24)
    print("✅ Video created:", final_video_path)
