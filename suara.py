from gtts import gTTS
import numpy as np
import string 
import random
import os  

class Suara:
	def delete_audio_file(self):
		filename = 'app/static/berkas.txt'
		try:
			os.remove(filename)
		except OSError:
			pass

	def speak(self, text):

		tts = gTTS(text, lang='id')
		res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 10))
		res = str(res)

		file1 = open('app/static/berkas.txt', 'w')
		file2 = open('app/static/nama_audio.txt', 'w')
		target = 'app/static/audio/'+res+'.mp3'

		tts.save(target)

		nama_target = '/static/audio/'+res+'.mp3'
		file1.write(target)
		file2.write(nama_target)

		file1.close()
		file2.close()