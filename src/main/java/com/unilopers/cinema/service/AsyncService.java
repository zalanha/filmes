package com.unilopers.cinema.service;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class AsyncService {

    @Async
    public void prepararSalaTecnica(Long salaId, String nomeSala) {
        System.out.println("[ASYNC] Iniciando preparação técnica para a sala: " + nomeSala);
        try {
            // Simula um processo demorado de configuração de som, imagem e ar-condicionado
            Thread.sleep(8000); 
            System.out.println("[ASYNC] ✅ Sala " + nomeSala + " (ID: " + salaId + ") pronta para uso!");
        } catch (InterruptedException e) {
            System.err.println("[ASYNC] ❌ Erro na preparação da sala " + salaId);
        }
    }

    @Async
    public void sincronizarGeneroExterno(Long generoId, String nomeGenero) {
        System.out.println("[ASYNC] Sincronizando novo gênero '" + nomeGenero + "' com bancos de dados externos...");
        try {
            // Simula integração com APIs internacionais de cinema para catalogar o gênero
            Thread.sleep(5000);
            System.out.println("[ASYNC] ✅ Gênero '" + nomeGenero + "' sincronizado e catalogado globalmente!");
        } catch (InterruptedException e) {
            System.err.println("[ASYNC] ❌ Falha na sincronização do gênero " + generoId);
        }
    }
}
