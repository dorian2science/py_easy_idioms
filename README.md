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
- [x] create python library package it and upload it
- [x] get a list of most frequent words by reading wikipedia articles(not perfect)
- [x] build dataframe with translations to arabic/german/french from a list of english words
- [x] generate pictures and audios
- [x] do not regenerate them if already available
- [x] generate video.
- [ ] adjust check words to sort out ar/en/iteration words from video.
  - [ ] add feature to modify field by pressing enter and be able to modify text of cell
  - [ ] add edge tts by double clicking on ar cell 
- [ ] make routine to generate new_words and new_videos_based on dataframe with iterations.
    - [ ] from new fresh words iteration>1
    - [ ] from known words
    - [ ] from unkown words among most frequent words batch of 15 minutes video
- [ ] full routine using last_words after check_words
- [ ] get captions of video
- [ ] from a new text determine the list of new words that are not in the glossary
- [ ] from a youtube video automatically build video of new words not known
- [ ] try to embed in a full software


# installation
## Create a new environment called 'myenv'
python -m venv myenv

## Activate it
### Windows
```shell
myenv\Scripts\activate
```
### macOS/Linux
```shell
source myenv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

pip install ipykernel
python -m ipykernel install --user --name=myenv --display-name "arabic"

```
## build .env of the project
should contain field <DATA_FOLDER> with the path of where all data will be stored.
