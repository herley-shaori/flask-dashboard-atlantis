import os
import cv2
import pandas as pd
import time
import progressbar
from pydub import AudioSegment
import glob

# Masukan Video. Harus ada thread yang terus menerus memeriksa apakah video sudah disediakan atau belum. Pemrosesan sekuensial.
def konversi_video_net_ke_citra(file_to_read='net_video_input/car_stop.mkv', output_folder='traffic_input_images/',fps=1):
	perintah = 'ffmpeg -i '+file_to_read+  ' -vf fps='+str(fps)+' -vsync 0 ' +output_folder+'image%d.jpg -y'
	os.system(perintah)	

# Konversi ke video.
def konversi_video(nama_berkas_luaran_video='tensorflow_object_counting_api/input_images_and_videos/video.avi', ukuran_frame_video=(800,600), folder_citra=None, ekstensi_citra='.png', keterangan='keterangan.csv'):
	fps = 1
	output=nama_berkas_luaran_video
	shape=ukuran_frame_video
	if(len(os.listdir(folder_citra)) > 0):
		data = pd.read_csv(keterangan)
		data.sort_values('citra')
		image_list = data['citra']
		class_list = data['kelas']
		if(len(image_list) == len(class_list)):
			fourcc = cv2.VideoWriter_fourcc(*'DIVX')
			video = cv2.VideoWriter(output, fourcc, fps, shape)
			for index in range(0,len(image_list)):
				kelas_saat_ini = class_list[index]
				image = image_list[index]
				image = 'img_'+str(image)+ekstensi_citra
				image_path = os.path.join(folder_citra, image)
				image = cv2.imread(image_path)
				resized=cv2.resize(image,shape)
				video.write(resized)
			video.release()
		else:
			print('Jumlah citra dan jumlah kelas pada citra tidak sama.')
	else:
		print('Tidak ada citra pada folder tersebut.')

def luaran_media(dir_path='tf_counting_output_images'):
	data1 = pd.read_csv('keterangan_1.csv')
	data1.sort_values('citra')
	image_list1 = data1['citra']
	class_list1 = data1['kelas']

	data25 = pd.read_csv('keterangan_25.csv')
	data25.sort_values('citra')
	image_list25 = data25['citra']
	class_list25 = data25['kelas']

	# Pengambilan keputusan berdasarkan 25 frame yang lain.
	index25_sekarang=0
	for x in range(0, len(class_list1)):
		kelas1 = class_list1[x]
		jumlah_kelas0 = 0
		jumlah_kelas1 = 0
		for k in range(index25_sekarang, (index25_sekarang+24)): # minus 1 karena ada 25 frame.
			kelas25 = class_list25[k]
			if(kelas25 == 0):
				jumlah_kelas0+=1
			else:
				jumlah_kelas1+=1
		index25_sekarang+=24

		if(jumlah_kelas0 > jumlah_kelas1):
			class_list1[x]=0
		else:
			class_list25[x]=1

	class_list=class_list1
	# Kejadian 1 detik akan dihapus dan menyesuaikan dengan kelompok besar (noise removal). PERHATIAN, gunakan dengan saksama.
	for x in range(1,len(class_list)):
		index_sebelum=x-1
		index_sesudah=x+1
		if(x < (len(class_list)-1)):
			if(class_list[index_sebelum] == class_list[index_sesudah]):
				class_list[x]=class_list[index_sebelum]
	# Jika ada kejadian dan kurang dari 4 frame, maka ikut kelas yang berkebalikan.
	for x in range(0,len(class_list)):
		x_satu=x+1
		x_dua=x+2
		x_tiga=x+3
		x_empat=x+4
		x_lima=x+5
		if(x_tiga < (len(class_list)-6)):
			if((class_list[x] != class_list[x_satu]) or (class_list[x] != class_list[x_dua]) or (class_list[x] != class_list[x_tiga])):
				if(class_list[x] == 0):
					class_list[x] = 1
				else:
					class_list[x] = 0
	print('noise removal complete')


	# Pelanggaran didefinisikan pada kelas 1.
	kelas_pelanggaran = 1

	# Suara.
	durasi_suara = 4 # durasi halo.mp3 4 detik.
	fps = 25 # fps.
	waktu_jeda = durasi_suara * fps
	suara = AudioSegment.from_mp3("audio/halo.mp3")
	detik = 0.5
	senyap = AudioSegment.silent(duration=(detik*1000))
	suara_gabungan = None

	jeda=0
	print('Penulisan suara dimulai.')
	for index in range(0,len(class_list)):
		kelas_saat_ini = class_list[index]
		if((kelas_saat_ini == kelas_pelanggaran)):
			if(jeda == 0):
				if(suara_gabungan is None):
					suara_gabungan = suara
				else:
					suara_gabungan += suara
		else:
			if(suara_gabungan is None):
				suara_gabungan = senyap
			else:
				suara_gabungan += senyap
		
		jeda+=1
		if(jeda == 5):
			jeda=0
	# Luaran video.
	suara_gabungan.export("suara_gabungan.mp3", format="mp3")
	# os.system('ffmpeg -i video.avi video.mp4 -y')
	# os.system('ffmpeg -i video.mp4 -i suara_gabungan.mp3 -c:v copy -c:a aac video_jadi.mp4 -y')
	print('proses menulis suara telah selesai.')
	# os.remove("video.mp4")
	# os.remove("video.avi")
	# os.remove("suara_gabungan.mp3")
	# os.rename('video_jadi.mp4', 'net_video_output/video.mp4')
	# files = glob.glob('tf_counting_output_images/*')
	# for f in files:
	# 	os.remove(f)

# Video to images.
# konversi_video_net_ke_citra(fps=1)

# # Deteksi lampu-lalu lintas/lampu pejalan kaki.
# os.chdir('Traffic-Light-Detection-And-Color-Recognition')
# os.system('python main.py')
# os.chdir('..')

# # Konversi citra lampu lalu-lintas ke video deteksi kendaraan.
# konversi_video(folder_citra='./traffic_output_images')

# # Deteksi kendaraan.
# os.chdir('tensorflow_object_counting_api')
# os.system('python single_image_object_counting.py')
# os.chdir('..')


# Penyusunan media.
luaran_media()

# Jumlah framenya sama, sekarang coba dengan jumlah frame yang lebih banyak.