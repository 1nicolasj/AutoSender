import os
import time
import psycopg2
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Carrega variáveis de ambiente
load_dotenv()

class WhatsAppSender:
    def __init__(self):
        self.db_connection = None
        self.driver = None
        self.setup_database()
        self.setup_driver()

    def setup_database(self):
        """Configura conexão com o banco de dados PostgreSQL"""
        try:
            self.db_connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'AutoSenderDb'),  # valor padrão igual ao appsettings.json
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres')
            )
            print("Conexão com o banco de dados estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def setup_driver(self):
        """Configura o driver do Chrome para automação"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Driver do Chrome configurado com sucesso!")
        except Exception as e:
            print(f"Erro ao configurar o driver: {e}")
            raise

    def get_contacts(self):
        """Obtém contatos do banco de dados"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT nome, telefone, mensagem_personalizada 
                    FROM contatos 
                    ORDER BY data_cadastro DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter contatos: {e}")
            return []

    def send_message(self, phone, message):
        """Envia mensagem para um número específico"""
        try:
            # Formata o número do telefone (remove caracteres especiais)
            phone = ''.join(filter(str.isdigit, phone))
            
            # Abre o WhatsApp Web
            self.driver.get(f"https://web.whatsapp.com/send?phone={phone}")
            
            # Aguarda o carregamento da página
            wait = WebDriverWait(self.driver, 60)
            message_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            ))
            
            # Envia a mensagem
            message_box.send_keys(message)
            send_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[@data-icon="send"]')
            ))
            send_button.click()
            
            # Aguarda um pouco para garantir que a mensagem foi enviada
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Erro ao enviar mensagem para {phone}: {e}")
            return False

    def process_all_contacts(self):
        """Processa todos os contatos e envia mensagens"""
        contacts = self.get_contacts()
        success_count = 0
        fail_count = 0

        for contact in contacts:
            nome, telefone, mensagem = contact
            print(f"Enviando mensagem para {nome} ({telefone})...")
            
            if self.send_message(telefone, mensagem):
                success_count += 1
                print(f"Mensagem enviada com sucesso para {nome}")
            else:
                fail_count += 1
                print(f"Falha ao enviar mensagem para {nome}")
            
            # Aguarda um pouco entre as mensagens para evitar bloqueio
            time.sleep(3)

        print(f"\nResumo do envio:")
        print(f"Total de mensagens: {len(contacts)}")
        print(f"Enviadas com sucesso: {success_count}")
        print(f"Falhas: {fail_count}")

    def close(self):
        """Fecha as conexões e o driver"""
        if self.db_connection:
            self.db_connection.close()
        if self.driver:
            self.driver.quit()

def main():
    sender = WhatsAppSender()
    try:
        print("Iniciando processo de envio de mensagens...")
        sender.process_all_contacts()
    except Exception as e:
        print(f"Erro durante o processo: {e}")
    finally:
        sender.close()

if __name__ == "__main__":
    main()