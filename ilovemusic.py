#!/usr/bin/env python

#!/usr/bin/env python

from requests import get
from json import loads
from time import sleep
import subprocess
import curses

playlist_url="https://www.ilovemusic.de/typo3conf/ext/ep_channel/Scripts/playlist.php"
channel_url="https://streams.iloveradio.de/iloveradioCHANNEL_ID.mp3?hadpreroll"

translation_layer = {
  "iloveradio": "I Love Radio",
  "ilove2dance": "I Love 2 Dance",
  "ilovehiphop": "I Love HipHop",
  "ilovedancefirst": "I Love Dance First",
  "top100chartsdeutschland": "Top 100 Charts Deutschland",
  "ilovethedj": "I Love The DJ",
  "ilovedeutschrapbeste": "I Love Deutschrap Beste",
  "top40hiphop": "Top 40 HipHop",
  "ilovemashup": "I Love Mashup",
  "top100dance2020": "Top 100 Dance 2020",
  "ilovetop100charts": "I Love Top 100 Charts",
  "ilovemusicandchill": "I Love Music And Chill",
  "ilovehitshistory": "I Love Hits History",
  "ilovehits2020": "I Love Hits 2020",
  "ilovexmas": "I Love Xmas",
  "ilovethebeach": "I Love The Beach",
  "ilovebigfmurbanclubbeats": "I Love BigFM Urban Club Beats",
  "ilovebigfmgroovenight": "I Love BigFM Groove Night",
  "ilovebigfmnitroxdeep": "I Love BigFM Nitro x Deep",
  "ilovebigfmnitroxedm": "I Love BigFM Nitro x EDM",
  "ilovenewpop": "I Love New Pop",
  "iloveusonlyrapradio": "I Love US Only Rap Radio",
  "bobbyfritz": "Bobby Fritz",
  "ilovedeutschrapfirst": "I Love Deutschrap First",
  "ilovepartyhard": "I Love Party Hard",
  "ilovethesun": "I Love The Sun",
  "iloverobinschulz": "I Love Robin Schulz",
  "ilovegreatesthits": "I Love Greatest Hits",
  "ilovehardermusic":  "I Love Harder Music",
  "top100hiphop2020": "Top 100 HipHop 2020",
  "tomorrowland": "Tomorrowland",
  "ilovetrashpop": "I Love Trashpop",
  "ilovetheclub": "I Love The Club",
  "ilovemainstagemadness": "I Love Main Stage Madness",
  "ilovehardstyle": "I Love Hardstyle",
  "ilovechillnation": "I Love Chill Nation",
  "ilovetrapnation": "I Love Rap Nation",
  "ilovechillhop": "I Love Chill Hop",
  "": "Invalid"
}

id_overwrite = {
  "ilovehiphop": "3",
  "ilovethedj": "4",
  "ilovehitshistory": "12",
  "ilovenewpop": "11",
  "iloveusonlyrapradio": "13",
  "ilovepartyhard": "14",
  "ilovethesun": "15",
  "iloverobinschulz": "18",
  "ilovegreatesthits": "16",
  "ilovetheclub": "20",
  "ilovemainstagemadness": "22",
  "ilovehardstyle": "21",
  "ilovechillhop": "17"
}

class ILoveMusic:
  
  def __init__(self): 
    self.volume = 30
    self.playing = False
    self.channels = {}
    self.updatePlaylist()

  def updatePlaylist(self):
    r = get(playlist_url)
    
    if r.status_code == 200:
      self.channels = loads(r.text)

    self.fixChannelIds()

  def fixChannelIds(self):
    for channel in self.channels:
      channel_segmentname = self.channels[channel]["segmentname"]
      if channel_segmentname in id_overwrite:
        self.channels[channel]["channel_id"] = id_overwrite[channel_segmentname]

  def getChannelMax(self):
    return len(self.channels)-1

  def getChannelMin(self):
    return 0

  def channelNbrToIdx(self, nbr):
    if int(nbr) > self.getChannelMax():
      return
    if int(nbr) < self.getChannelMin():
      return

    channel_list = list(self.channels)
    return channel_list[int(nbr)]

  def getChannel(self, idx):
    return self.channels[idx]

  def getChannelSong(self, idx):
    song = self.getChannel(idx)["title"].title()
    if song == "Livestream" or song == "":
      return "N/A"
    return song

  def getChannelArtist(self, idx):
    artist = self.getChannel(idx)["artist"].title()
    if artist == "Livestream" or artist == "":
      return "N/A"
    return artist

  def getChannelName(self, idx):
    return self.getChannel(idx)["segmentname"]

  def playChannelByIdx(self, idx):
    channel_id = self.getChannel(idx)["channel_id"]
    radio_url = channel_url.replace("CHANNEL_ID", channel_id)
    if self.playing == True:
      self.stopCurrentChannel()
    
    subprocess.run(['screen', '-mdS', 'pyplayer', 'mpv', '--volume='+str(self.volume), radio_url])
    self.playing = True
  
  def stopCurrentChannel(self):
    subprocess.run(['screen', '-S', 'pyplayer', '-X', 'quit'])
    self.playing = False

  def playChannelByNbr(self, nbr):
    idx = self.channelNbrToIdx(nbr)
    self.playChannelByIdx(idx)

  def volumeUp(self):
    if self.volume < 100:
      subprocess.run(['screen', '-S', 'pyplayer', '-X', 'stuff', '\'0\\n\''])
      self.volume += 2

  def volumeDown(self):
    if self.volume > 0:
      subprocess.run(['screen', '-S', 'pyplayer', '-X', 'stuff', '\'9\\n\''])
      self.volume -= 2

  def getVolume(self):
    return self.volume
  
  def getPlaying(self):
    return self.playing


class Display:
  
  def __init__(self, stdscr):
    self.stdscr = stdscr
    self.music = ILoveMusic()
    self.counter = 0
    self.selected_channel = 0
    self.current_channel = -1
    self.updateDisplay()

  def selectionUp(self):
    if self.selected_channel < self.music.getChannelMax():
      while True:
        self.selected_channel += 1
        channel = self.getChannelStr(self.getSelectedIndex(0))
        if channel == "Invalid":
          continue
        else:
          break

  def selectionDown(self):
    if self.selected_channel > self.music.getChannelMin():
      while True:
        self.selected_channel -= 1
        channel = self.getChannelStr(self.getSelectedIndex(0))
        if channel == "Invalid":
          continue
        else:
          break

  def volumeUp(self):
    self.music.volumeUp()

  def volumeDown(self):
    self.music.volumeDown()

  def increaseCounter(self):
    self.counter += 1

  def checkCounter(self):
    if self.counter >= 200:
      self.music.updatePlaylist()
      self.updateDisplay()
      self.counter = 0
  
  def getCurrentIndex(self):
    return self.getIndex(self.current_channel)

  def getSelectedIndex(self, offset):
    return self.getIndex(self.selected_channel+offset)

  def getIndex(self, nbr):
    return self.music.channelNbrToIdx(nbr)

  def getCurrentChannelStr(self):
    if self.music.getPlaying() == False:
      return "None"

    return self.getChannelStr(self.getCurrentIndex())

  def getChannelStr(self, index):
    raw_name = self.music.getChannelName(index)
    channel = translation_layer[raw_name]
    return channel

  def getVolumeStr(self):
    volume = self.music.getVolume() 
    return str(volume)

  def getCurrentArtistStr(self):
    if self.music.getPlaying() == False:
      return "None"

    return self.getArtistStr(self.getCurrentIndex())

  def getArtistStr(self, index):
    artist = self.music.getChannelArtist(index)
    return artist
  
  def getCurrentSongStr(self):
    if self.music.getPlaying() == False:
      return "None"
    
    return self.getSongStr(self.getCurrentIndex())

  def getSongStr(self, index):
    song = self.music.getChannelSong(index)
    return song

  def updateDisplay(self):
    self.stdscr.clear()
    self.displayCurrentChannel()
    self.displayCurrentVolume()
    self.displayCurrentArtist()
    self.displayCurrentSong()
    self.displaySelection() 

  def displaySelection(self):
    for i in range(-1, 2):
      tmp = i
      if self.selected_channel+i < self.music.getChannelMin():
        row_str = ""
      elif self.selected_channel+i > self.music.getChannelMax():
        row_str = ""
      else:
        channel = self.getChannelStr(self.getSelectedIndex(tmp))
        while channel == "Invalid":
          if tmp < 0:
            tmp -= 1
          elif i > 0:
            tmp += 1
          channel = self.getChannelStr(self.getSelectedIndex(tmp))
        artist = self.getArtistStr(self.getSelectedIndex(tmp))
        song = self.getSongStr(self.getSelectedIndex(tmp))

        row_str = "{} ( {} - {} )".format(channel, artist, song)

      if i == 0:
        prefix = "> "
        self.stdscr.addstr(8+i, 1, prefix)
        if self.current_channel == self.selected_channel+i:
          self.stdscr.addstr(8+i, 1+len(prefix), row_str, curses.color_pair(3))
        else:
          self.stdscr.addstr(8+i, 1+len(prefix), row_str, curses.color_pair(2))
      else:
        if self.current_channel == self.selected_channel+i:
          self.stdscr.addstr(8+i, 1, row_str, curses.color_pair(3))
        else:
          self.stdscr.addstr(8+i, 1, row_str, curses.color_pair(1))

  def displayCurrentChannel(self):
    channel = self.getCurrentChannelStr()
    channel_prefix = "Current Channel: "
    
    self.displayCurrent(1, channel_prefix, channel)

  def displayCurrentVolume(self):
    volume = self.getVolumeStr()
    volume_prefix = "Volume: "

    self.displayCurrent(2, volume_prefix, volume)

  def displayCurrentArtist(self):
    artist = self.getCurrentArtistStr()
    artist_prefix = "Artist: "

    self.displayCurrent(4, artist_prefix, artist)

  def displayCurrentSong(self):
    song = self.getCurrentSongStr()
    song_prefix = "Song: "

    self.displayCurrent(5, song_prefix, song)

  def displayCurrent(self, row, prefix, value):
    self.stdscr.addstr(row, 1, prefix) 
    self.stdscr.addstr(row, 1+len(prefix), value, curses.color_pair(3))

  def playSelectedChannel(self):
    self.current_channel = self.selected_channel
    self.music.playChannelByNbr(self.selected_channel)

  def stopCurrentChannel(self):
    self.current_channel = -1
    self.music.stopCurrentChannel()


def main(stdscr):
  curses.use_default_colors()
  curses.init_pair(1, curses.COLOR_RED, -1)
  curses.init_pair(2, curses.COLOR_YELLOW, -1)
  curses.init_pair(3, curses.COLOR_GREEN, -1)
  
  curses.curs_set(0)

  display = Display(stdscr)

  while True:
    stdscr.timeout(100)
    try:
      c = stdscr.getch()
      
      if c == -1:
        display.checkCounter()
        display.increaseCounter()
        continue

      if c == 259:
        display.selectionDown()
      elif c == 258:
        display.selectionUp()
      elif c == 43:
        display.volumeUp()
      elif c == 45:
        display.volumeDown()
      elif c == 10:
        display.playSelectedChannel()
      elif c == 127:
        display.stopCurrentChannel()
      elif c == 113:
        display.stopCurrentChannel()
        break
        
      display.updateDisplay()
    except KeyboardInterrupt as e:
      display.stopCurrentChannel()
      break

curses.wrapper(main)
