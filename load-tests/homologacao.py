from locust import HttpUser, task, between
from faker import Faker
import random

fake = Faker('pt_BR')

class HomologacaoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.token = None
        self.filme_id = None
        self.sala_id = None

        self.email = f"load_{fake.uuid4()[:8]}@test.com"
        self.password = "pass123"
        headers_xml = {"Content-Type": "application/xml", "Accept": "application/xml"}

        reg_payload = f"<?xml version='1.0' encoding='UTF-8'?><usuario><nome>{fake.name()}</nome><email>{self.email}</email><password>{self.password}</password></usuario>"

        with self.client.post("/auth/register", data=reg_payload, headers=headers_xml, catch_response=True) as resp:
            if resp.status_code not in [200, 201]:
                return

        login_json = {"email": self.email, "password": self.password}
        with self.client.post("/auth/login", json=login_json, catch_response=True) as log_resp:
            if log_resp.status_code == 200:
                try:
                    self.token = log_resp.json().get("token")
                except Exception:
                    return
            else:
                return

        if self.token:
            self.prepare_data()

    def prepare_data(self):
        auth_h = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/xml", "Accept": "application/xml"}

        f_xml = f"<?xml version='1.0' encoding='UTF-8'?><filme><titulo>Movie_{fake.uuid4()[:5]}</titulo><duracaoMin>120</duracaoMin><ano>2024</ano></filme>"
        with self.client.post("/filmes", data=f_xml, headers=auth_h, catch_response=True) as f_res:
            if f_res.status_code == 201:
                location = f_res.headers.get("Location")
                if location:
                    self.filme_id = location.split("/")[-1]

        s_xml = f"<?xml version='1.0' encoding='UTF-8'?><sala><nome>Sala_{fake.random_int(1, 999999)}</nome><capacidade>{fake.random_int(50, 200)}</capacidade></sala>"
        with self.client.post("/salas", data=s_xml, headers=auth_h, catch_response=True) as s_res:
            if s_res.status_code == 201:
                location = s_res.headers.get("Location")
                if location:
                    self.sala_id = location.split("/")[-1]

    @task
    def ciclo_criacao_homologacao(self):
        if not self.token or not self.filme_id or not self.sala_id:
            return

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/xml", "Accept": "application/xml"}
        
        requisitos = ["2D", "3D", "IMAX"]
        status_lista = ["Aprovado", "Pendente"]

        xml = f"""<?xml version='1.0' encoding='UTF-8'?>
        <homologacao>
            <idFilme>{self.filme_id}</idFilme>
            <idSala>{self.sala_id}</idSala>
            <requisitoTecnico>{random.choice(requisitos)}</requisitoTecnico>
            <statusValidacao>{random.choice(status_lista)}</statusValidacao>
        </homologacao>"""

        with self.client.post("/homologacoes", data=xml, headers=headers, catch_response=True, name="POST /homologacoes") as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Erro POST: {response.status_code}")