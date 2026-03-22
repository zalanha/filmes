from locust import HttpUser, task, between
from faker import Faker
import random

fake = Faker('pt_BR')

class IngressoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.token = None
        self.id_usuario = None
        self.id_sessao = None
        self.id_tipo = None

        headers_xml = {"Content-Type": "application/xml", "Accept": "application/xml"}
        self.email = f"load_{fake.uuid4()[:8]}@test.com"
        self.password = "pass123"

        reg_payload = f"<?xml version='1.0' encoding='UTF-8'?><usuario><nome>{fake.name()}</nome><email>{self.email}</email><password>{self.password}</password></usuario>"
        self.client.post("/auth/register", data=reg_payload, headers=headers_xml)

        login_json = {"email": self.email, "password": self.password}
        with self.client.post("/auth/login", json=login_json) as log_resp:
            if log_resp.status_code == 200:
                resp_data = log_resp.json()
                self.token = resp_data.get("token")
                self.id_usuario = resp_data.get("id")

        if self.token and self.id_usuario:
            auth_h = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/xml", "Accept": "application/xml"}

            f_xml = f"<?xml version='1.0' encoding='UTF-8'?><filme><titulo>F_{fake.uuid4()[:8]}</titulo><duracaoMin>120</duracaoMin><ano>2024</ano></filme>"
            with self.client.post("/filmes", data=f_xml, headers=auth_h) as rf:
                f_id = rf.headers.get("Location", "/1").split("/")[-1]

            s_xml = f"<?xml version='1.0' encoding='UTF-8'?><sala><nome>S_{fake.uuid4()[:8]}</nome><capacidade>10</capacidade></sala>"
            with self.client.post("/salas", data=s_xml, headers=auth_h) as rs:
                s_id = rs.headers.get("Location", "/1").split("/")[-1]

            t_xml = f"<?xml version='1.0' encoding='UTF-8'?><tipoIngresso><descricao>T_{fake.uuid4()[:4]}</descricao><fatorPreco>1.0</fatorPreco><categoriaTecnica>2D</categoriaTecnica></tipoIngresso>"
            with self.client.post("/tipos-ingresso", data=t_xml, headers=auth_h) as rt:
                self.id_tipo = rt.headers.get("Location", "/1").split("/")[-1]

            h_xml = f"<?xml version='1.0' encoding='UTF-8'?><homologacao><idFilme>{f_id}</idFilme><idSala>{s_id}</idSala><requisitoTecnico>2D</requisitoTecnico><statusValidacao>Aprovado</statusValidacao></homologacao>"
            self.client.post("/homologacoes", data=h_xml, headers=auth_h)

            ss_xml = f"<?xml version='1.0' encoding='UTF-8'?><sessao><idFilme>{f_id}</idFilme><idSala>{s_id}</idSala><dataHora>2026-12-01T20:00:00</dataHora><precoBase>25.00</precoBase><tipoExibicao>2D</tipoExibicao></sessao>"
            with self.client.post("/sessoes", data=ss_xml, headers=auth_h) as r_sess:
                if r_sess.status_code == 201:
                    self.id_sessao = r_sess.headers.get("Location").split("/")[-1]

    @task
    def fluxo_ingresso(self):
        if not (self.token and self.id_usuario and self.id_sessao):
            return

        auth_h = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/xml", "Accept": "application/xml"}
        assento = random.randint(1, 10)
        payload = f"<?xml version='1.0' encoding='UTF-8'?><compraIngresso><idUsuario>{self.id_usuario}</idUsuario><idSessao>{self.id_sessao}</idSessao><idTipoIngresso>{self.id_tipo}</idTipoIngresso><numeroAssento>{assento}</numeroAssento></compraIngresso>"

        with self.client.post("/ingressos", data=payload, headers=auth_h, catch_response=True, name="POST /ingressos") as resp:
            if resp.status_code == 201:
                loc = resp.headers.get("Location")
                if loc:
                    self.client.get(loc, headers=auth_h, name="GET /ingressos/[id]")
                resp.success()
            else:
                resp.failure(f"Status: {resp.status_code}")