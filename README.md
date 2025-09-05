# Description
It is possible in youtube to find videos that spells word in arabic like this one.
[link to video](https://www.youtube.com/watch?v=aIjICgCI9jo&pp=ygUYMTAwMCBhcmFiaWMgd29yZHMgcGFydCAx)
Inconvenients :
- word not spelled in english so not possible to use the video if not able to watch the screen
- only 1000 words in this video
- Some other videos have less good quality so not usable.
- not custom. If you need to memorize words you need to make shorter videos and filter out known words.

The goal of this project is exactly to enable to generate those kind of videos but tailored to fit the needs of self.

# features
- extract words from random articles in wikipedia to determine most occurences of words.
- generate a dataframe of english words translated into other languages
- generate sounds and pictures and put them in data folders without havnig
- generate a video spelling with words  
- check_words.html js app to filter out words

# Limitations
- Not fully embedded in a single software to trigger actions. Some manual steps.

## Steps to Improve
- [ ] create python library package it and upload it
- [x] get a list of most frequent words by reading wikipedia articles
- [x] build dataframe with translations to arabic/german/french from a list of english words
- [x] generate pictures and audios
- [x] do not regenerate them if already available
- [ ] sort out words that are known from the long list
- [x] generate video.
- [ ] make routine to generate new_words and new_videos_based on dataframe with iterations.
    - [ ] from new fresh words iteration >1
    - [ ] from known words
    - [ ] from unkown words among most frequent words batch of 15 minutes video
- [ ] full routine using last_words after check_words
- [ ] try to embed in a full software

# installation
## Create a new environment called 'myenv'
python -m venv myenv

## Activate it
### Windows
myenv\Scripts\activate
### macOS/Linux
source myenv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

pip install ipykernel
python -m ipykernel install --user --name=myenv --display-name "arabic"
