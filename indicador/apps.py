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

        load_dotenv()

        
        desk = Desk()
       
        def carga_chamado(id):
            chamado = desk.relatorio(id)
            if chamado:
                for i in chamado.get("root"):
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
                    )
                    data.save()
                    print(i)
        
        def carga_interacao(id):
            interacao = desk.relatorio("141") # 141
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


        # carga_chamado("140")


        carga_interacao("141")

