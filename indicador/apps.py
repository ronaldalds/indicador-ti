from django.apps import AppConfig


class IndicadorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'indicador'

    def ready(self) -> None:
        from .util import Desk
        from datetime import datetime
        from .models import Chamado
        from .models import Interacao
        import os
        from dotenv import load_dotenv
        from apscheduler.schedulers.background import BackgroundScheduler

        load_dotenv()

        desk = Desk()
        
        def carga_chamado():
            chamado = desk.relatorio(os.getenv("ID_RELATORIO_DESK_CHAMADO"))
            print("Atualizando chamados...")
            if chamado:
                for i in chamado.get("root"):
                    item = Chamado.objects.filter(id=i.get("CodChamado")).first()
                    if not item:
                        print(item)
                        data_criacao: datetime = datetime.strptime(i.get("DataCriacao"), "%d-%m-%Y")
                        data_finalizacao: datetime = datetime.strptime(i.get("DataFinalizacao"), "%d-%m-%Y")
                        data = Chamado(
                            id=i.get("CodChamado"),
                            data_criacao=data_criacao,
                            data_finalizacao=data_finalizacao,
                            assunto=i.get("Assunto"),
                            nome_categoria=i.get("NomeCategoria"),
                            total_horas_1_2_atendimento_str=i.get("TotalHorasPrimeiroSegundoAtendimento"),
                            nome_sla_status_atual=i.get("NomeSlaStatusAtual"),
                            sla_2_expirado=i.get("Sla2Expirado"),
                            first_call=i.get("FirstCall"),
                            nome_operador=i.get("NomeOperador"),
                            nome_status=i.get("NomeStatus"),
                        )
                        data.save()
                        print(i)
        
        def carga_interacao():
            interacao = desk.relatorio(os.getenv("ID_RELATORIO_DESK_INTERACAO"))
            print("Atualizando interações...")
            if interacao:
                for i in interacao.get("root"):
                    chamado = Chamado.objects.filter(id=i.get("NChamado")).first()
                    if chamado:
                        item = Interacao.objects.filter(chamado=chamado.id, seguencia=i.get("Sequencia")).first()
                        if not item:
                            data = Interacao(
                                chamado=chamado,
                                status_acao_nome_relatorio=i.get("StatusAcaoNomeRelatorio"),
                                fantasia_fornecedor=i.get("FantasiaFornecedor", ""),
                                seguencia=int(i.get("Sequencia")),
                            )
                            data.save()
                            print(i)

        sheduler = BackgroundScheduler(daemon=True)
        sheduler.configure(timezone="america/fortaleza")
        sheduler.add_job(carga_chamado, 'interval', minutes=10)
        sheduler.add_job(carga_interacao, 'interval', minutes=10)

        sheduler.start()

        # carga_chamado()

        # carga_interacao()