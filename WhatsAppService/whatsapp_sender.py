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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import urllib.parse

# Carrega variáveis de ambiente
try:
    load_dotenv(encoding='utf-8')
except:
    load_dotenv()

class WhatsAppSender:
    def __init__(self):
        self.db_connection = None
        self.driver = None
        self.is_logged_in = False
        self.setup_database()
        self.setup_driver()

    def setup_database(self):
        """Configura conexão com o banco de dados PostgreSQL"""
        try:
            connection_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'AutoSenderDb'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'root'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'client_encoding': 'utf8'
            }
            
            self.db_connection = psycopg2.connect(**connection_params)
            print("[OK] Conexao com banco estabelecida!")
        except Exception as e:
            print(f"[ERRO] Problema no banco: {e}")
            raise

    def setup_driver(self):
        """Configura Chrome - versão que estava funcionando"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            
            # Manter sessão ativa
            chrome_options.add_argument("--keep-alive-for-test")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            
            # Configurar user data para manter sessão
            user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                print(f"ChromeDriver baixado em: {driver_path}")
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("[OK] ChromeDriver configurado!")
            except Exception as e:
                print(f"Erro com webdriver-manager: {e}")
                print("[AVISO] Tentando ChromeDriver do sistema...")
                self.driver = webdriver.Chrome(options=chrome_options)
                print("[OK] ChromeDriver do sistema configurado!")
            
            # Configurações de timeout
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            print(f"[ERRO] Problema no driver: {e}")
            raise

    def get_contacts(self):
        """Obtém contatos do banco de dados"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT "Nome", "Telefone", "MensagemPersonalizada" 
                FROM "Contatos" 
                ORDER BY "DataCadastro" DESC
            """)
            contacts = cursor.fetchall()
            cursor.close()
            print(f"[OK] {len(contacts)} contatos carregados")
            return contacts
        except Exception as e:
            print(f"[ERRO] Problema ao carregar contatos: {e}")
            return []

    def login_whatsapp(self):
        """Login único no WhatsApp"""
        if self.is_logged_in:
            return True
            
        try:
            print("Abrindo WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            wait = WebDriverWait(self.driver, 60)
            
            # Verificar se já está logado (sessão salva)
            try:
                print("Verificando se ja esta logado...")
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]')),
                    EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')),
                    EC.presence_of_element_located((By.XPATH, '//span[@data-testid="default-user"]'))
                ))
                print("[OK] Ja logado! Pulando QR Code...")
                self.is_logged_in = True
                return True
                
            except TimeoutException:
                # Precisa fazer login
                print("QR Code detectado - faca o login manual")
                print("Escaneie o QR Code no WhatsApp do seu celular")
                
                # Aguardar login manual
                input("Pressione ENTER apos escanear o QR Code...")
                
                # Verificar se login foi bem-sucedido
                try:
                    wait.until(EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]')),
                        EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]'))
                    ))
                    print("[OK] Login realizado com sucesso!")
                    self.is_logged_in = True
                    return True
                except TimeoutException:
                    print("[ERRO] Falha no login - tente novamente")
                    return False
                    
        except Exception as e:
            print(f"[ERRO] Problema no login: {e}")
            return False

    def format_phone(self, phone):
        """Formata número de telefone corretamente"""
        # Remove tudo que não é número
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país (55 - Brasil) se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone
            
        return phone

    def send_message(self, phone, message):
        """Envia mensagem SEM duplicação - CORREÇÃO PRINCIPAL"""
        try:
            phone = self.format_phone(phone)
            print(f"Enviando para: {phone}")
            
            # CORREÇÃO: URL direta com mensagem, mas SÓ clicar no botão
            message_encoded = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={message_encoded}"
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Aguardar página carregar
            time.sleep(4)
            
            # ESTRATÉGIA ÚNICA: Só clicar no botão de enviar
            # A mensagem já está preenchida pela URL
            try:
                send_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//span[@data-icon="send" or @data-testid="send"]'
                )))
                send_button.click()
                print("[OK] Enviado via botao")
                time.sleep(3)
                return True
                
            except TimeoutException:
                print("[AVISO] Botao nao encontrado - tentando Enter na caixa")
                
                # FALLBACK: Se não achou botão, apertar Enter no campo
                # (SEM digitar novamente - só Enter)
                try:
                    message_box = wait.until(EC.element_to_be_clickable((
                        By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
                    )))
                    message_box.click()
                    time.sleep(1)
                    # NÃO digitar mensagem novamente - só apertar Enter
                    message_box.send_keys(Keys.ENTER)
                    print("[OK] Enviado via Enter")
                    time.sleep(3)
                    return True
                    
                except TimeoutException:
                    print("[ERRO] Numero invalido ou WhatsApp nao carregou")
                    return False
                        
        except WebDriverException as e:
            if "invalid session id" in str(e).lower():
                print("[AVISO] Sessao perdida - reconectando...")
                self.is_logged_in = False
                if self.login_whatsapp():
                    return self.send_message(phone, message)  # Retry
            print(f"[ERRO] Problema WebDriver: {e}")
            return False
            
        except Exception as e:
            print(f"[ERRO] Problema geral: {e}")
            return False

    def process_all_contacts(self):
        """Processa todos os contatos"""
        print("Iniciando processamento...")
        
        # Carregar contatos
        contacts = self.get_contacts()
        if not contacts:
            print("Nenhum contato encontrado!")
            return
            
        print(f"Total: {len(contacts)} contatos")
        
        # Login único
        if not self.login_whatsapp():
            print("[ERRO] Falha no login - abortando")
            return
            
        # Processamento
        success_count = 0
        fail_count = 0
        start_time = time.time()
        
        for i, (nome, telefone, mensagem) in enumerate(contacts, 1):
            print(f"\n[{i}/{len(contacts)}] {nome} ({telefone})")
            
            # Mensagem padrão se não tiver personalizada
            if not mensagem or mensagem.strip() == "":
                mensagem = f"Ola {nome}! Esta e uma mensagem automatica do sistema AutoSender."
            
            # Tentar enviar
            if self.send_message(telefone, mensagem):
                success_count += 1
                print(f"[SUCESSO] Enviado para {nome}")
            else:
                fail_count += 1
                print(f"[FALHA] Erro para {nome}")
            
            # Progresso
            progress = (i / len(contacts)) * 100
            print(f"Progresso: {progress:.1f}% | Sucesso: {success_count} | Falhas: {fail_count}")
            
            # Intervalo entre mensagens
            if i < len(contacts):
                print("Aguardando 8 segundos...")
                time.sleep(8)

        # Relatório final
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"RELATORIO FINAL")
        print(f"{'='*60}")
        print(f"Total de contatos: {len(contacts)}")
        print(f"Enviadas com sucesso: {success_count}")
        print(f"Falhas: {fail_count}")
        print(f"Taxa de sucesso: {(success_count/len(contacts)*100):.1f}%")
        print(f"Tempo total: {total_time/60:.1f} minutos")
        print(f"{'='*60}")

    def close(self):
        """Cleanup"""
        try:
            if self.db_connection:
                self.db_connection.close()
                print("[OK] Conexao BD fechada")
        except:
            pass
            
        try:
            if self.driver:
                self.driver.quit()
                print("[OK] Driver fechado")
        except:
            pass

def main():
    sender = None
    try:
        print("AutoSender - WhatsApp Automation")
        print("=" * 50)
        
        sender = WhatsAppSender()
        sender.process_all_contacts()
        
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario")
    except Exception as e:
        print(f"Erro critico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if sender:
            sender.close()
        print("Processo finalizado!")

if __name__ == "__main__":
    main()