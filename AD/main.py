import simpy
import random
# SIMULÇAO DE UM AEROPORTO
# TESTES COM VARIAVELS FIXAS COM POSSIBILIDADE DE AUMENTO DE CARGA DE TRABALHO 
# AUMENTO DAS MESMAS PARA A SIMULAÇÃO


#Variavéis da Simulação
RANDOM_SEED = 42
FILA_PISTA = []
FILA_ABASTECIMENTO = []
FILA_FINGERS = []

''' Com carga PESADA'''
TEMPO_POUSO = 7 #EM MINUTOS
TEMPO_DECOLAGEM = 8
TEMPO_ABASTECIMENTO = 15
TEMPO_DESEMBARQUE = 20

INTERACAO_AVIAO = 13 
TEMPO_SIMULACAO = 60*24

QTDE_PISTAS = 2
QTDE_PONTES = 2
QTDE_TANQUES = 1






class Simulacao:
 

    def __init__(self):
        self.num_chegadas = 0  
        self.num_pousos = 0 
        self.num_abastecimentos = 0 
        self.num_desembarques = 0
        self.tempo_total_abastecimento = 0
        self.num_decolagens = 0
        self.tempo_total_solo = 0

    def new_chegada(self):
        self.num_chegadas += 1

    def new_abastecimento(self, time):
        self.num_abastecimentos += 1
        self.tempo_total_abastecimento += time

    def new_decolagem(self,tempoEmSolo):
        self.num_decolagens += 1
        self.tempo_total_solo += tempoEmSolo


    def new_pouso(self):
        self.num_pousos += 1

    def new_desembarque(self):
        self.num_desembarques += 1

    def report(self):

        media_chegadas = float(self.num_chegadas) / (TEMPO_SIMULACAO/60)
        

        #utilização das pontes
        x_pontes = float(self.num_desembarques)/float(TEMPO_SIMULACAO)
        u_pontes = float(x_pontes)*float(TEMPO_DESEMBARQUE)

        #pistas
        x_pistas = float(self.num_pousos+self.num_decolagens)/float(TEMPO_SIMULACAO)
        u_pistas = float(x_pistas)*float(TEMPO_DESEMBARQUE+TEMPO_DESEMBARQUE)

        u4 = float(self.num_pousos*TEMPO_POUSO)/float(TEMPO_SIMULACAO)
        u5 = float(self.num_decolagens*TEMPO_DECOLAGEM)/float(TEMPO_SIMULACAO)
        u_pista = u4+u5

        #tanques
        x_tanque = float(self.num_abastecimentos)/float(TEMPO_SIMULACAO)
        
        print("##########################################################")
        print("Métricas")
        print ('\n ##RESULTADOS OBTIDOS DO AEROPORTO##\n')
        print ('Tempo de simualção: %.1f (min)' % TEMPO_SIMULACAO)
        print ('Quantidade de aeronaves: %d (aviões)' % self.num_chegadas)
        print ('Total Desembarque: %d' % self.num_decolagens)
        print ('Total reabastecimento: %d' % self.num_abastecimentos)
        print ('Media de chegadas: %f/h' % media_chegadas)
        print("#########################################################")
        print ('Tempo médio por avião no solo: %f min por aviao' % (self.tempo_total_solo/self.num_decolagens))
        print('Throughput-> utilização das pontes de desemb e embarque.: %.2f/min,%.2f %%'%(x_pontes,u_pontes*100))
        print('Throughput-> utilização das pistas : %.2f,%.2f%% ' % (x_pistas, u_pista*100))
        print("#########################################################")
        
        
class Aeroporto(object):
    def __init__(self, env,qtde_pistas,qtde_pontes,qtde_tanques,tempo_abastecimento,tempo_pouso,tempo_decolagem,tempo_desembarque):
        self.env = env
        self.pistas = simpy.Resource(env, qtde_pistas)
        self.pontes_desembarque = simpy.Resource(env,qtde_pontes)
        self.tanques = simpy.Resource(env,qtde_tanques)
        self.tempo_abastecimento = tempo_abastecimento
        self.tempo_pouso = tempo_pouso
        self.tempo_desembarque = tempo_desembarque
        self.tempo_decolagem = tempo_decolagem


   
#ORDEM DOS SERVIÇOS PROPOSTO PELO AEROPORTO
# Com dados referentes aos tempos de cada servico

    def liberar_pouso(self,aviao):
        yield self.env.timeout(self.tempo_pouso)
        print ('%s terminou pouso - > %.2f.' % (aviao, env.now))
        
    def liberar_ponte(self, aviao):
        yield self.env.timeout(self.tempo_desembarque)
        print ('%s terminou desembarque em -> %.2f.' % (aviao, env.now))

    def liberar_abastecimento(self,aviao):
        yield self.env.timeout(self.tempo_abastecimento)
        print("abastecimento -  %s at %.2f ." % (aviao, env.now))

    def liberar_decolagem(self,aviao):
        yield self.env.timeout(self.tempo_decolagem)
        print("%s terminou desembarque em -> %.2f." %(aviao, env.now))
        
        
    def desembarcar_abastecer(self,aviao): # possibilidade de abastercer 
        tempo_desembarque = random.randint(*TEMPO_DESEMBARQUE)
        tempo_abastecimento = 0
        abastercer = random.randint(0,1) #Se for abastecer ou não(0 ou 1)
        if(abastercer==1): #Se abastecer
            print("%s abastecendo" %aviao)
            tempo_abastecimento = random.randint(*TEMPO_ABASTECIMENTO)
        yield self.env.timeout(tempo_desembarque+tempo_abastecimento)    


def aviao(env, nome, aeroporto):
    # Simulação em todos os processos relizado pelo aeroporto, chegada, pouso, desembarque e decolagem
    
    
    
    
    print('%s Aeronave chegou ao aeroporto em  %.2f.' % (nome, env.now))
    simulacao.new_chegada()
    tempo_chegada = env.now
    horario_pouso = 0

    # todo processo de verificar quais pistas estao disponiveis, caso tenham uma pista é solicitada
    # caso não, é inserido em uma fila de espera, assim como oss demais processos
    with aeroporto.pistas.request() as request:
        yield request
        print('%s ENTRADO NO AEROPORTO ÁS %.1f. espera: %.2f' % (nome, env.now, env.now - tempo_chegada))
        FILA_PISTA.append(env.now - tempo_chegada)
        horario_pouso = env.now
        yield env.process(aeroporto.liberar_pouso(nome))
        #print(FILA_PISTA)
        simulacao.new_pouso()

    with aeroporto.pontes_desembarque.request() as request:
        yield request
        print('%s  necessario a requisição de finger para %.2f. espera: %.2f' % (nome, env.now, env.now - tempo_chegada))
        FILA_FINGERS.append(env.now - tempo_chegada)
        yield env.process(aeroporto.liberar_ponte(nome))
        simulacao.new_desembarque()

 

    with aeroporto.pistas.request() as request: #no caso, so temos uma pista
        yield request
        start = env.now
        estadia = env.now - horario_pouso
        print('% sai do aeroporto at %.2f. Wait: %.2f tempo em solo:%.2f' % (nome, env.now, env.now - tempo_chegada,estadia))
        yield env.process(aeroporto.liberar_decolagem(nome))
        simulacao.new_decolagem(estadia)

    

def setup(env, qtde_pistas,qtde_pontes,qtde_tanques,tempo_abastecimento,tempo_pouso,tempo_decolagem,tempo_desembarque, a_inter):

    aeroporto = Aeroporto(env, qtde_pistas,qtde_pontes,qtde_tanques, tempo_abastecimento, tempo_pouso, tempo_decolagem,tempo_desembarque)

    
    for i in range(5):
        env.process(aviao(env, 'Aviao %d' % i, aeroporto))

    # ADIÇÃO DE AERONVA
    while True:
        yield env.timeout(random.randint(a_inter-2, a_inter+2))
        i += 1
        env.process(aviao(env, 'Airplane %d' % i, aeroporto))

# INICIALIZAÇÃO DA SIMULAÇÃO
print('===== ***** aeroporto *****=====')
random.seed(RANDOM_SEED)  


simulacao = Simulacao()


env = simpy.Environment()
env.process(setup(env, QTDE_PISTAS,QTDE_PONTES,QTDE_TANQUES, TEMPO_ABASTECIMENTO, TEMPO_POUSO, TEMPO_DECOLAGEM,TEMPO_DESEMBARQUE, INTERACAO_AVIAO))


env.run(until=TEMPO_SIMULACAO)

simulacao.report()