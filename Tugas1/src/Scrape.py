from bs4 import BeautifulSoup
import requests
import time
import json

#Header untuk memperkenalkan diri
headers = {'User-Agent': 'Mozilla/5.0'}

#Fungsi ini akan mereturn sebuah dictionary yang berisi data yang diperlukan
#untuk suatu pekerjaan
#Yaitu: Judul, Perusahaan, Pendidikan min, Pengalaman min, Tipe (Full-time, part-time, dll.),
#       Jumlah pelamar, detail syarat (berupa list), deskripsi pekerjaan(berupa list)
def getInsideData(url_inside):
    #Melakukan get, dan parsing dengan BeautifulSoup
    page_html_inside = requests.get(url_inside, headers)
    soup_result_inside = BeautifulSoup(page_html_inside.text, 'html.parser')
    
    #Judul dari Lowongan Pekerjaan
    title = soup_result_inside.find('div', class_="page-wrap").h1.get_text()
    
    #Perusahaan yang mencari lowongan
    company = soup_result_inside.find('div', class_="page-wrap").h2.get_text()
    
    #Mencari persyaratan
    prequisites = []
    prequisite_raw = soup_result_inside.find('div', class_="page-wrap").find_all('div', class_='col-md-12')[1]
    for prequisite in prequisite_raw.find_all('li'):
        prequisites.append(prequisite.get_text())

    #Mencari Deskripsi
    descriptions = []
    try:
        desc_raw = soup_result_inside.find('div', class_="page-wrap").find_all('div', class_='col-md-12')[2]
        for description in desc_raw.find_all('li'):
            descriptions.append(description.get_text())
    except IndexError:
        description = []

    #Kolom 1 dari overview pekerjaan
    col1 = soup_result_inside.find('div', class_="col-md-6")
    last_education = col1.findAll('td')[5].get_text().strip()
    experience = col1.findAll('td')[7].get_text().strip()

    #Kolom 2 dari overview pekerjaan
    col2 = soup_result_inside.find('div', class_='col-md-5')
    job_type = col2.findAll('td')[1].get_text().strip()
    temp = soup_result_inside.findAll('tr')[9].get_text().strip()
    n_seeker = [int(s) for s in temp.split() if s.isdigit()][0]

    #Konstruksi dictionary data
    input_data = {'judul': title, 'perusahaan': company, 'persyaratan': prequisites, 'deskripsi': descriptions,
    'pendidikan': last_education, 'pengalaman_min': experience, 'tipe': job_type, 'jumlah_pelamar': n_seeker}
    return input_data


#Main function dari program
def main():
    #Inisialisasi list data kosong
    data = []

    #Looping dari webpage utama
    for i in range(1,20):
        #URL dari page yg akan dicari
        url = "https://jobindo.com/index.php?lang=in&mod=search&location=9-328&num=" + str(i)
        page_html = requests.get(url, headers)

        #Melakukan parsing dengan library Beautiful Soup
        soup_result = BeautifulSoup(page_html.text, 'html.parser')
        page_wrap = soup_result.find('div', class_='page-wrap')

        #Untuk setiap row yang menyimpan data lowongan pekerjaan di webpage     
        for job in page_wrap.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['row']):
            #URL yang akan mendapatkan detail dari pekerjaan
            url_inside = 'https://jobindo.com/' + job.find('a')['href']
            input_data = getInsideData(url_inside)
            data.append(input_data)
            time.sleep(0.5)
        time.sleep(1)

    print("Scraping done!")
    #Membentuk file json
    with open('../data/result.json', 'w') as fp:
        json.dump(data, fp)
   
if __name__ == '__main__':
    main()