import time
import sqlite3
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WhatsAppSender:
    def __init__(self):
        self.driver = None
        self.db_connection = None
        self.setup_database()
        self.setup_driver()

    def setup_database(self):
        """Conecta ao SQLite (mesmo banco que a aplicação web)"""
        try:
            # Caminho para o banco SQLite
            db_path = os.path.join(os.path.dirname(__file__), "..", "AutoSender", "autosender.db")
            self.db_connection = sqlite3.connect(db_path)
            print(f"[OK] Conectado ao SQLite: {db_path}")
        except Exception as e:
            print(f"[ERRO] Problema no banco: {e}")
            raise

    def setup_driver(self):
        """Configura Chrome com correções para WhatsApp Web"""
        try:
            chrome_options = Options()
            
            # User-Agent real para evitar detecção
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Desabilitar detecção de automação
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Configurações de segurança
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            
            # Salvar sessão do WhatsApp
            user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Remover propriedades de automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("[OK] Chrome configurado")
        except Exception as e:
            print(f"[ERRO] Problema ao configurar Chrome: {e}")
            raise

    def connect_whatsapp(self):
        """Conecta ao WhatsApp Web"""
        try:
            print("[INFO] Acessando WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Aguardar QR code ou carregamento
            time.sleep(10)
            
            # Verificar se já está logado
            try:
                # Se encontrar a caixa de pesquisa, já está logado
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                print("[OK] WhatsApp já conectado!")
                return True
            except:
                print("[INFO] QR code disponível. Escaneie com seu celular.")
                print("[INFO] Aguardando login...")
                
                # Aguardar login (até 60 segundos)
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                print("[OK] Login realizado com sucesso!")
                return True
                
        except Exception as e:
            print(f"[ERRO] Problema ao conectar WhatsApp: {e}")
            return False

    def get_contacts(self):
        """Busca contatos no banco SQLite"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT Nome, Telefone, MensagemPersonalizada 
                FROM Contatos 
                ORDER BY DataCadastro DESC
            """)
            contacts = cursor.fetchall()
            cursor.close()
            print(f"[OK] {len(contacts)} contatos carregados")
            return contacts
        except Exception as e:
            print(f"[ERRO] Problema ao carregar contatos: {e}")
            return []

    def send_message(self, phone_number, message):
        """Envia mensagem para um contato"""
        try:
            from selenium.webdriver.common.keys import Keys
            
            # Formatar número (remover caracteres especiais)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # URL direta para o contato
            url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={message}"
            self.driver.get(url)
            
            # Aguardar carregar
            time.sleep(5)
            
            # Encontrar campo de mensagem e enviar com Enter
            message_box = WebDriverWait(self.driver, 12).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            message_box.send_keys(Keys.ENTER)
            
            print(f"[OK] Mensagem enviada para {phone_number}")
            time.sleep(random.randint(4,8))  # Delay entre mensagens (entre 4 e 8 segundos)
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao enviar para {phone_number}: {e}")
            return False

    def run(self):
        """Executa o envio de mensagens"""
        try:
            # Conectar ao WhatsApp
            if not self.connect_whatsapp():
                return
            
            # Buscar contatos
            contacts = self.get_contacts()
            if not contacts:
                print("[INFO] Nenhum contato encontrado")
                return
            
            # Enviar mensagens
            for contact in contacts:
                nome, telefone, mensagem = contact
                print(f"[INFO] Enviando para {nome} ({telefone})")
                
                if mensagem:
                    self.send_message(telefone, mensagem)
                else:
                    print(f"[AVISO] {nome} não tem mensagem personalizada")
            
            print("[OK] Envio concluído!")
            
        except Exception as e:
            print(f"[ERRO] Problema durante execução: {e}")
        finally:
            input("Pressione Enter para fechar...")
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    sender = WhatsAppSender()
    sender.run()