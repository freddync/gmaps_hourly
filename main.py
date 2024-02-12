from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

df_total = pd.DataFrame()

gmaps_malls = {'PARQUE ARAUCO':'https://maps.app.goo.gl/5mf9YyCCaBU1tNYr8', 'COSTANERA CENTER':'https://maps.app.goo.gl/C1XZFy9nYByC3NJh6',
               'ALTO LAS CONDES':'https://maps.app.goo.gl/im2dE5W8HujPkRWA6', 'PLAZA EGAÑA': 'https://maps.app.goo.gl/g11DN3iKXNDYS6Fy6', ###<----- CHILE
               'SHOPPING ARICANDUVA': 'https://maps.app.goo.gl/enRSL3A38QnjE1Ei6', 'PATIO PAULISTA MALL': 'https://maps.app.goo.gl/JaYf8jb3qw45h91LA', ###<------- BRASIL
               'UNICENTER' : 'https://maps.app.goo.gl/XtDTZf4uf9Fj98EZ6', 'PALMAS DEL PILAR': 'https://maps.app.goo.gl/WVn4Mm4vVLYVFy6d7', ###<------ ARGENTINA
               'JOCKEY PLAZA' : 'https://maps.app.goo.gl/uARTEEtETvb49JY98', 'REAL PLAZA PURUCHUCO': 'https://maps.app.goo.gl/21qx6TBgPXWPQu4A7',
               'LARCOMAR': 'https://maps.app.goo.gl/hVAwKxbPXCCEaySr5', #### <-------- PERÚ
               'CENTRO MAYOR' : 'https://maps.app.goo.gl/5UUfC9pfA9fg6cim7', 'EL EDÉN': 'https://maps.app.goo.gl/ohrUuLdjUfP3PfQ27',
               'MILLA DE ORO': 'https://maps.app.goo.gl/PTmXjtiZxboW1Hbi7', ### <----- COLOMBIA
               'CENTRO SANTA FE' : 'https://maps.app.goo.gl/yMV2UPZzptMBWbFr8', 'TOREO PARQUE CENTRAL' : 'https://maps.app.goo.gl/bww6ANtLgTW6Zdwg9',
               'MALL ANTARA':'https://maps.app.goo.gl/SPiZuAfxgfp6MWmX7', 'GALERIA INSURGENTES': 'https://maps.app.goo.gl/2dUxo3nJjJBCy3rGA' ###<---- MÉXICO
               }

for mall, link in gmaps_malls.items():
   ## EXTRACTOR GOOGLE MAPS
#   options = webdriver.ChromeOptions()
#   options.add_argument("--headless")
#   options.add_argument('--disable-dev-shm-usage')
#   options.add_argument("--no-sandbox")
#   options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
#   driver = webdriver.Chrome(options=options)
  driver.set_window_size(1920, 1400)
  driver.get(link)
#   time.sleep(2)
#   driver.save_screenshot('sdhsds.png')

  # Obtiene el código fuente HTML
  html = driver.page_source

  driver.close()

  # Crear una sopa con BeautifulSoup
  soup = BeautifulSoup(html, 'html.parser')

  # Supongamos que 'soup' es tu objeto BeautifulSoup
  html_doc = str(soup)

  # Buscar el script en la cadena
  script_tag = '<script id="base-js" nonce=""'
  script_index = html_doc.index(script_tag)

  # Extraer todo desde el script en adelante
  rest_of_doc = html_doc[script_index:]

  # Busca el índice donde aparece la palabra '(Original)' por primera vez
  end_index = rest_of_doc.find('(Original)')

  # Si se encontró la palabra
  if end_index != -1:
      # Extrae todo hasta la palabra '(Original)'
      substring = rest_of_doc[:end_index]

  # Busca el índice donde aparece la etiqueta '<div' por primera vez
  start_index = substring.find('<div class="C7xf8b"')

  # Si se encontró la etiqueta
  if start_index != -1:
      # Extrae todo desde la etiqueta '<div' en adelante
      substring_from_div = substring[start_index:]

  # Parsea el string con BeautifulSoup
  soup = BeautifulSoup(substring_from_div, 'html.parser')

  # Encuentra todos los divs con un atributo 'aria-label' y guarda el valor de 'aria-label' en una lista
  labels = [div.get('aria-label') for div in soup.find_all('div', attrs={'aria-label': True})]

  # Crea un DataFrame de pandas con los datos
  dfxxx = pd.DataFrame(labels, columns=['Label'])

  # Supongamos que df es tu DataFrame y 'columna' es la columna que quieres dividir
  dfxxx = dfxxx[dfxxx['Label'].str.contains('%')]  # Elimina las filas que no contienen un porcentaje
  dfxxx = dfxxx[dfxxx['Label'].str[0].str.isdigit()]

  # Divide la columna en dos
  dfxxx[['PORCENTAJE', 'HORA']] = dfxxx['Label'].str.split(' busy at ', expand=True)

  # Elimina la columna original
  dfxxx = dfxxx.drop(columns=['Label'])

  # Convertimos la columna 'Hora' a formato datetime
  dfxxx['HORA'] = dfxxx['HORA'].str.strip('.')

  dfxxx['LOC'] = mall

  # Obtén el número de la semana actual
  semana_actual = datetime.now().isocalendar()[1]

  # Agrega la columna con el número de la semana actual
  dfxxx['SEMANA'] = semana_actual

  # Crear una lista con los días de la semana
  dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

  # Repetir cada día 18 veces
  dias_repetidos = [dia for dia in dias for _ in range(18)]

  # Asignar los días al dataframe
  dfxxx['DIA'] = dias_repetidos

  df_total = pd.concat([df_total, dfxxx])

df_total.reset_index(drop=True, inplace=True)
df_total['PORCENTAJE'] = df_total['PORCENTAJE'].str.rstrip('%').astype('float') / 100.0

def asignar_pais(nombre_local):
    locales_chile = ['PARQUE ARAUCO', 'COSTANERA CENTER', 'ALTO LAS CONDES', 'PLAZA EGAÑA']
    locales_brasil = ['SHOPPING ARICANDUVA', 'PATIO PAULISTA MALL']
    locales_argentina = ['UNICENTER', 'PALMAS DEL PILAR']
    locales_peru = ['JOCKEY PLAZA', 'REAL PLAZA PURUCHUCO', 'LARCOMAR']
    locales_mexico = ['CENTRO SANTA FE', 'TOREO PARQUE CENTRAL', 'MALL ANTARA', 'GALERIA INSURGENTES']
    locales_colombia = ['CENTRO MAYOR', 'EL EDÉN', 'MILLA DE ORO']

    if nombre_local in locales_chile:
        return 'Chile'
    elif nombre_local in locales_brasil:
        return 'Brasil'
    elif nombre_local in locales_argentina:
        return 'Argentina'
    elif nombre_local in locales_mexico:
        return 'México'
    elif nombre_local in locales_peru:
        return 'Perú'
    elif nombre_local in locales_colombia:
        return 'Colombia'
    else:
        return 'Desconocido'

df_total['PAIS'] = df_total['LOC'].apply(asignar_pais)

df_total.to_excel('gmaps_info.xlsx')